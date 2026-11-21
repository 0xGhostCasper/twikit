"""Jetfuel login flow: real pieces (TOTP, encoding, classification, state machine).

The one piece gated on a live capture — X's response framing — is injected here
as a scripted parser, so the orchestration is exercised without inventing that
wire format.
"""

import urllib.parse

import pyotp
import pytest

from twikit.login import (
    CallableCastleProvider,
    Challenge,
    JetfuelLogin,
    JetfuelResponse,
    LoginChallenge,
    LoginFailed,
    StaticCastleProvider,
    classify_action,
    encode_form,
    totp_now,
)
from twikit.login.jetfuel import parse_response


def test_totp_matches_pyotp():
    secret = "JBSWY3DPEHPK3PXP"
    assert totp_now(secret) == pyotp.TOTP(secret).now()
    assert totp_now("JBSW Y3DP EHPK 3PXP") == pyotp.TOTP(secret).now()  # spaces tolerated


def test_encode_form_appends_castle_token_last_and_drops_unset():
    body = encode_form({"username": "alice", "email": None, "password": "pw"}, "PFX|abc")
    pairs = urllib.parse.parse_qsl(body, keep_blank_values=True)
    assert pairs == [("username", "alice"), ("password", "pw"), ("$castle_token", "PFX|abc")]


@pytest.mark.parametrize(
    "action,expected",
    [
        ("LoginTwoFactorAuthChallenge", Challenge.TWO_FACTOR),
        ("login_verify_totp", Challenge.TWO_FACTOR),
        ("login_acid", Challenge.EMAIL_OR_PHONE),
        ("account_verification", Challenge.EMAIL_OR_PHONE),
        ("enter_alternate_identifier", Challenge.ALTERNATE_ID),
        ("ArkoseLogin", Challenge.ARKOSE),
        ("DenyLoginSubtask", Challenge.DENIED),
        ("login_enter_password", None),
        ("begin_login", None),
    ],
)
def test_classify_action(action, expected):
    assert classify_action(action) == expected


def _frame(*fields: tuple[str, str]) -> bytes:
    """Build a body in X's `<key><len><value>` framing (ASCII) for parse tests.

    Mirrors the framing read off a real login capture (2026-10-05): a field is
    its name, one length byte, then that many value bytes. Action availability is
    conveyed by the action name appearing anywhere in the body.
    """
    out = bytearray()
    for key, value in fields:
        out += key.encode()
        out += bytes([len(value)])
        out += value.encode()
    return bytes(out)


def test_parse_response_extracts_session_token_and_next_action():
    body = _frame(("session_token", "a" * 36), ("login_enter_password", ""))
    r = parse_response(body)
    assert r.session_token == "a" * 36
    assert "login_enter_password" in r.next_actions
    assert not r.logged_in and r.error is None


def test_parse_response_reads_two_factor_step():
    body = _frame(("session_token", "b" * 36)) + b"begin_two_factor_auth"
    r = parse_response(body)
    assert r.session_token == "b" * 36
    assert "begin_two_factor_auth" in r.next_actions


def test_parse_response_flags_error():
    r = parse_response(_frame(("session_token", "c" * 36)) + b"Wrong password!")
    assert r.error == "Wrong password!"


def test_parse_response_logged_in_when_no_action_or_error():
    assert parse_response(b"").logged_in is True


def test_parse_response_decodes_text_plain_utf8_transport():
    # bytes >127 arrive UTF-8-encoded over text/plain; the parser must recover them
    body = _frame(("session_token", "d" * 36)) + b"\xc2\xa0" + b"start_over"
    r = parse_response(body.decode("latin-1").encode("utf-8"))
    assert r.session_token == "d" * 36
    assert "start_over" in r.next_actions


def _login(scripted: list[JetfuelResponse], totp_secret=None):
    """A JetfuelLogin whose parser returns the next scripted response per call."""
    posted = []
    responses = iter(scripted)

    async def post(url, *, headers, data):
        posted.append((url.rsplit("/", 1)[-1], dict(urllib.parse.parse_qsl(data))))
        return b""

    seen_actions = []

    async def mint(action, context):
        seen_actions.append(action)
        return f"TOK|{action}"

    login = JetfuelLogin(
        post=post,
        castle=CallableCastleProvider(mint),
        guest_token="g",
        parse=lambda raw: next(responses),
    )
    return login, posted, seen_actions


async def test_login_happy_path_two_steps():
    login, posted, minted = _login([
        JetfuelResponse(session_token="s1", next_actions=["login_enter_password"]),
        JetfuelResponse(logged_in=True),
    ])
    result = await login.login("alice", "pw")
    assert result.logged_in
    assert [a for a, _ in posted] == ["begin_login", "login_enter_password"]
    # fresh token minted per step, password step carries the prior session token
    assert minted == ["begin_login", "login_enter_password"]
    assert posted[1][1]["session_token"] == "s1"
    assert posted[1][1]["$castle_token"] == "TOK|login_enter_password"


async def test_login_answers_2fa_with_totp():
    secret = "JBSWY3DPEHPK3PXP"
    login, posted, _ = _login([
        JetfuelResponse(session_token="s1", next_actions=["login_enter_password"]),
        JetfuelResponse(session_token="s2", next_actions=["LoginTwoFactorAuthChallenge"]),
        JetfuelResponse(logged_in=True),
    ])
    result = await login.login("alice", "pw", totp_secret=secret)
    assert result.logged_in
    assert [a for a, _ in posted] == ["begin_login", "login_enter_password", "LoginTwoFactorAuthChallenge"]
    assert posted[2][1]["code"] == pyotp.TOTP(secret).now()


async def test_login_raises_on_2fa_without_secret():
    login, _, _ = _login([
        JetfuelResponse(session_token="s1", next_actions=["login_enter_password"]),
        JetfuelResponse(session_token="s2", next_actions=["LoginTwoFactorAuthChallenge"]),
    ])
    with pytest.raises(LoginChallenge) as exc:
        await login.login("alice", "pw")
    assert exc.value.challenge is Challenge.TWO_FACTOR
    assert exc.value.session_token == "s2"


async def test_login_raises_on_arkose():
    login, _, _ = _login([
        JetfuelResponse(session_token="s1", next_actions=["login_enter_password"]),
        JetfuelResponse(session_token="s2", next_actions=["ArkoseLogin"]),
    ])
    with pytest.raises(LoginChallenge) as exc:
        await login.login("alice", "pw", totp_secret="JBSWY3DPEHPK3PXP")
    assert exc.value.challenge is Challenge.ARKOSE


async def test_login_raises_on_error():
    login, _, _ = _login([JetfuelResponse(error="Could not log you in now")])
    with pytest.raises(LoginFailed):
        await login.login("alice", "pw")


async def test_submit_without_guest_token_fails():
    login = JetfuelLogin(post=None, castle=StaticCastleProvider("T|x"))
    with pytest.raises(LoginFailed):
        await login.login("alice", "pw")

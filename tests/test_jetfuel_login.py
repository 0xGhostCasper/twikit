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


def test_parse_response_is_a_marked_boundary():
    with pytest.raises(NotImplementedError):
        parse_response(b"anything")


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

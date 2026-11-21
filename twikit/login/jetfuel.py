"""X web login via the Jetfuel onboarding flow.

X retired the classic ``onboarding/task.json`` flow for the web client: it now
answers 399 "Could not log you in now". The live web flow posts to
``https://x.com/i/jfapi/onboarding/web/actions/<action>`` with form fields plus a
fresh ``$castle_token`` ([[castle]]) on every step:

    begin_login(username_or_email)         -> session_token (+ next actions)
    login_enter_password(password, ...)     -> logged in, or a challenge action
    <challenge actions: 2FA code, email/phone code, Arkose, ...>

This module owns the request side of that flow — guest token, headers, form
encoding, step sequencing, TOTP, and challenge classification. It does NOT
embed X's anti-automation cipher: tokens come from a :class:`CastleTokenProvider`
(the hybrid wires that to the CloakBrowser farm).

One boundary is deliberately left to a live capture: :func:`parse_response`
turns X's Jetfuel response body into the next actions / session token / error.
The body is a length-framed chunk stream, and its exact framing must be read off
a real login (drive one through the farm with request+response capture) before
this flow can complete end to end. Everything around it is implemented and
tested; ``parse_response`` raises until that capture is wired in, so the failure
is loud and localized rather than a plausible-looking wrong guess.
"""

from __future__ import annotations

import urllib.parse
from dataclasses import dataclass, field
from enum import Enum

import pyotp

from .castle import CastleContext, CastleTokenProvider

ACTIONS_BASE = "https://x.com/i/jfapi/onboarding/web/actions"
GUEST_TOKEN_URL = "https://x.com/i/jf/onboarding/web"
# Pinned by the current x-web build; refreshed alongside the Castle bundle.
JETFUEL_VERSION = "1"


class Challenge(str, Enum):
    """A login step that needs input beyond username+password."""

    TWO_FACTOR = "two_factor"       # authenticator / SMS code
    EMAIL_OR_PHONE = "acid"         # emailed or texted confirmation code
    ALTERNATE_ID = "alternate"      # "confirm your phone/email"
    ARKOSE = "arkose"               # FunCaptcha / visual challenge
    DENIED = "deny"                 # server refused this login


# Substrings in a Jetfuel action name that mark each challenge class. Matched
# case-insensitively, longest-signal-first is not needed because the classes are
# disjoint in practice; kept as data so new names map without code changes.
_CHALLENGE_MARKERS: tuple[tuple[str, Challenge], ...] = (
    ("two_factor", Challenge.TWO_FACTOR),
    ("twofactor", Challenge.TWO_FACTOR),
    ("totp", Challenge.TWO_FACTOR),
    ("acid", Challenge.EMAIL_OR_PHONE),
    ("verification", Challenge.EMAIL_OR_PHONE),
    ("alternate", Challenge.ALTERNATE_ID),
    ("arkose", Challenge.ARKOSE),
    ("funcaptcha", Challenge.ARKOSE),
    ("deny", Challenge.DENIED),
)


def classify_action(action: str) -> Challenge | None:
    """The challenge an action represents, or ``None`` for a normal step."""
    name = action.lower()
    for marker, challenge in _CHALLENGE_MARKERS:
        if marker in name:
            return challenge
    return None


def encode_form(fields: dict[str, str], castle_token: str) -> str:
    """Form body for a Jetfuel action.

    The browser's ``URLSearchParams`` serializes the action fields first and
    appends ``$castle_token`` last; order is preserved because X reads the token
    positionally in some builds. Unset fields are dropped, not sent empty.
    """
    pairs = [(k, v) for k, v in fields.items() if v is not None]
    pairs.append(("$castle_token", castle_token))
    return urllib.parse.urlencode(pairs)


def totp_now(secret: str) -> str:
    """Current 6-digit TOTP code for a base32 2FA secret (spaces tolerated)."""
    return pyotp.TOTP(secret.replace(" ", "")).now()


@dataclass
class JetfuelResponse:
    """One parsed Jetfuel action response."""

    session_token: str | None = None
    next_actions: list[str] = field(default_factory=list)
    logged_in: bool = False
    error: str | None = None
    raw: bytes = b""


# Jetfuel action names the flow recognizes as "what to submit next". Derived from
# a real login capture (2026-10-05): each response names its available follow-up
# action(s) inline, so the flow reads the name off the response rather than
# assuming a fixed order.
_KNOWN_ACTIONS = (
    "login_enter_password",
    "begin_two_factor_auth",
    "finish_two_factor_auth",
    "login_enter_alternate_identifier_subtask",
    "login_acid",
    "begin_password_recovery",
    "start_over",
    "DenyLoginSubtask",
)
_ERROR_MARKERS = (b"DenyLoginSubtask", b"Could not log you in", b"Wrong password!",
                  b"The password you entered", b"suspended")


def _logical_bytes(raw: bytes) -> bytes:
    """Undo the text/plain UTF-8 transport: the SPA reads each code point as a 0-255 byte.

    X serves the chunk stream as ``text/plain; charset=UTF-8``, so a byte value
    >127 arrives UTF-8-encoded. Decoding then re-encoding latin-1 recovers the
    original framing bytes. If ``raw`` is not valid UTF-8 it is already logical.
    """
    try:
        return raw.decode("utf-8").encode("latin-1")
    except (UnicodeDecodeError, UnicodeEncodeError):
        return raw


def _extract_session_token(body: bytes) -> str | None:
    """Pull the session_token out of the framed body.

    Framing (from capture): the field name ``session_token`` is followed by one
    length byte, then that many bytes of value (0x24 = 36 for the observed
    tokens). Takes the first occurrence whose length byte yields a printable
    value of that exact length.
    """
    marker = b"session_token"
    start = 0
    while (i := body.find(marker, start)) != -1:
        start = i + len(marker)
        if start < len(body):
            length = body[start]
            value = body[start + 1:start + 1 + length]
            if len(value) == length and value.isascii() and value.decode().isprintable():
                return value.decode()
    return None


def parse_response(raw: bytes) -> JetfuelResponse:
    """Parse a Jetfuel action response into the next session token / actions / error.

    The body is X's framed chunk stream (``<key><len><value>`` fields, action
    names inline), served as text/plain. This reads exactly what the flow needs —
    the session token that chains to the next step and which action(s) are
    offered — rather than fully decoding the stream. Validated against a real
    4-step login capture (begin_login -> login_enter_password ->
    begin_two_factor_auth -> finish_two_factor_auth) on 2026-10-05.
    """
    body = _logical_bytes(raw)
    token = _extract_session_token(body)
    actions = [a for a in _KNOWN_ACTIONS if a.encode() in body]
    error = next((m.decode() for m in _ERROR_MARKERS if m in body), None)
    # Logged in: a completed step that offers no further action and reports no
    # error (the terminal finish_* response, or an empty body after redirect).
    logged_in = not actions and error is None
    return JetfuelResponse(
        session_token=token,
        next_actions=actions,
        logged_in=logged_in,
        error=error,
        raw=raw,
    )


class LoginChallenge(Exception):
    """Raised when the flow needs input it was not given (2FA with no secret, Arkose, ...)."""

    def __init__(self, challenge: Challenge, action: str, session_token: str | None) -> None:
        super().__init__(f"{challenge.value}: {action}")
        self.challenge = challenge
        self.action = action
        self.session_token = session_token


class LoginFailed(Exception):
    """Login was refused for a reason retrying will not fix (bad credentials, denied)."""


@dataclass
class JetfuelLogin:
    """Drives the web Jetfuel login for one account.

    ``post`` is an async ``(url, *, headers, data) -> bytes`` returning the raw
    response body (the caller owns the HTTP client, its proxy and cookie jar, so
    this module stays transport-agnostic). ``castle`` mints a token per step.
    ``parse`` defaults to :func:`parse_response` and is injectable for tests and
    for slotting in the capture-derived parser.
    """

    post: object
    castle: CastleTokenProvider
    guest_token: str | None = None
    parse: object = parse_response

    async def _submit(self, action: str, fields: dict[str, str], context: CastleContext) -> JetfuelResponse:
        if not self.guest_token:
            raise LoginFailed("guest_token not set; call fetch_guest_token first")
        token = await self.castle.token(action, context)
        headers = {
            "x-guest-token": self.guest_token,
            "x-jf-v": JETFUEL_VERSION,
            "x-jf-client-theme": "light",
            "x-twitter-active-user": "yes",
            "content-type": "application/x-www-form-urlencoded",
            "referer": f"{GUEST_TOKEN_URL}",
        }
        body = encode_form(fields, token)
        raw = await self.post(f"{ACTIONS_BASE}/{action}", headers=headers, data=body)
        return self.parse(raw)

    async def login(
        self,
        username: str,
        password: str,
        *,
        email: str | None = None,
        totp_secret: str | None = None,
    ) -> JetfuelResponse:
        """Run begin_login -> login_enter_password, answering a 2FA challenge via TOTP.

        Non-TOTP challenges (emailed code, Arkose, alternate id, denial) raise
        :class:`LoginChallenge` / :class:`LoginFailed` with the action and session
        token so a caller can resume out of band. A clean login returns the final
        :class:`JetfuelResponse`.
        """
        ctx: CastleContext = {"username": username}
        step = await self._submit(
            "begin_login", {"username_or_email": email or username}, ctx
        )
        if step.error:
            raise LoginFailed(step.error)

        step = await self._submit(
            "login_enter_password",
            {
                "username": username,
                "email": email,
                "password": password,
                "session_token": step.session_token,
            },
            ctx,
        )
        return await self._resolve(step, ctx, totp_secret)

    async def _resolve(
        self, step: JetfuelResponse, ctx: CastleContext, totp_secret: str | None
    ) -> JetfuelResponse:
        """Advance through challenge actions until logged in or blocked."""
        while not step.logged_in:
            if step.error:
                raise LoginFailed(step.error)
            action = next((a for a in step.next_actions if classify_action(a)), None)
            if action is None:
                return step  # nothing more to answer; caller inspects the result
            challenge = classify_action(action)
            if challenge is Challenge.TWO_FACTOR and totp_secret:
                step = await self._submit(
                    action,
                    {"session_token": step.session_token, "code": totp_now(totp_secret)},
                    ctx,
                )
                continue
            raise LoginChallenge(challenge, action, step.session_token)
        return step

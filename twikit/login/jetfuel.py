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


def parse_response(raw: bytes) -> JetfuelResponse:
    """Parse a Jetfuel action response body into :class:`JetfuelResponse`.

    BOUNDARY — not implemented until a live capture pins the framing. X returns a
    length-delimited chunk stream here, not plain JSON; guessing its layout would
    produce a parser that looks right and silently mis-reads session tokens and
    challenge actions. Capture one real login (farm render with
    ``capture_request`` + response body) and implement against those bytes, then
    delete this raise. The flow and its tests inject a parser, so wiring the real
    one in is a one-line change with no churn to the orchestration.
    """
    raise NotImplementedError(
        "Jetfuel response framing must be filled from a live capture; "
        "see parse_response docstring."
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

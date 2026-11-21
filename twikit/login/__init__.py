"""Web Jetfuel login flow and Castle token providers.

Login is intentionally decoupled from the rest of twikit: a working session is
still produced by ``Client.set_cookies`` / ``load_cookies``. This package builds
those cookies from credentials via X's current web login, with the Castle token
supplied by a provider (the ScrapeBadger hybrid wires it to the browser farm).
"""

from .castle import (
    CallableCastleProvider,
    CastleContext,
    CastleTokenProvider,
    StaticCastleProvider,
)
from .jetfuel import (
    Challenge,
    JetfuelLogin,
    JetfuelResponse,
    LoginChallenge,
    LoginFailed,
    classify_action,
    encode_form,
    parse_response,
    totp_now,
)

__all__ = [
    "CallableCastleProvider",
    "CastleContext",
    "CastleTokenProvider",
    "StaticCastleProvider",
    "Challenge",
    "JetfuelLogin",
    "JetfuelResponse",
    "LoginChallenge",
    "LoginFailed",
    "classify_action",
    "encode_form",
    "parse_response",
    "totp_now",
]

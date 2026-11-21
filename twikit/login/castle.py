"""Castle token provider for the web Jetfuel login flow.

Every step of X's current web login (`/i/jfapi/onboarding/web/actions/*`) carries
a fresh ``$castle_token`` — the output of Castle's anti-automation SDK, which runs
in the page and reads the live browser/device state. There is no supported way to
produce one from headers alone, so this module does not try to: it defines a
*provider* interface and leaves the actual minting to whatever can run Castle's
own SDK.

The ScrapeBadger hybrid wires :class:`CallableCastleProvider` to the CloakBrowser
farm — a real browser on x.com, on that account's own residential exit, invokes
Castle's loaded SDK per step and returns the token. Each account therefore gets
its own device fingerprint, which is the whole point of minting one per login
rather than replaying one capture across the pool.

Nothing here embeds Castle's cipher or any third-party implementation of it; the
provider is a boundary, so an alternative minter (a self-hosted token service, a
future pure-computation path) drops in without touching the flow.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Awaitable, Callable

# The login actions that request a token, in the order the flow issues them.
# A provider may key its browser state on the action (Castle folds the action
# name into the signal set), so it is passed through verbatim rather than
# collapsed to a single "login" call.
CastleContext = dict[str, object]


class CastleTokenProvider(ABC):
    """Produces one fresh Castle token per login action."""

    @abstractmethod
    async def token(self, action: str, context: CastleContext) -> str:
        """Return a ``$castle_token`` for ``action``.

        ``action`` is the Jetfuel action about to be submitted
        (``begin_login``, ``login_enter_password``, ...). ``context`` carries
        what the minter needs to bind the token to this login — at least
        ``{"username": ..., "proxy": ...}`` — so one browser session on one exit
        serves the whole sequence for one account. Implementations must return a
        token shaped ``"<prefix>|<base64>"``; the flow does not validate it, X
        does.
        """


class CallableCastleProvider(CastleTokenProvider):
    """Delegate minting to an async callable — the farm hook for the hybrid.

    ``fn(action, context)`` is expected to drive (or reuse) a browser session
    pinned to ``context["proxy"]`` for ``context["username"]`` and return the
    token string. Keeping it a plain callable means this library has no browser
    dependency: the caller owns the farm client.
    """

    def __init__(self, fn: Callable[[str, CastleContext], Awaitable[str]]) -> None:
        self._fn = fn

    async def token(self, action: str, context: CastleContext) -> str:
        return await self._fn(action, context)


class StaticCastleProvider(CastleTokenProvider):
    """Return a fixed token. For tests and for replaying one captured step."""

    def __init__(self, token: str) -> None:
        self._token = token

    async def token(self, action: str, context: CastleContext) -> str:
        return self._token

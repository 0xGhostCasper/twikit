"""A rate-limited account must raise TooManyRequests, not RecursionError.

``Client.request`` consults ``_get_user_state()`` on a 429 to tell "suspended"
from "rate limited". That check is itself an HTTP GET, so when it ALSO returns
429 — exactly what happens to a rate-limited account — it asked again, and
again:

    get -> request -> _get_user_state -> v11.user_state -> get -> ...

until ``RecursionError: maximum recursion depth exceeded``. Observed in
production 2026-08-10 on /twitter/tweets/advanced_search; the caller saw an
opaque RecursionError instead of TooManyRequests.
"""

import asyncio

import pytest

from twikit.client.client import _CHECKING_USER_STATE, Client


def _client_with_user_state(handler):
    client = Client.__new__(Client)  # bypass __init__: no network/session needed
    client.v11 = type("_V11", (), {"user_state": staticmethod(handler)})()
    return client


def test_guard_is_set_during_the_check_and_cleared_after():
    seen = {}

    async def user_state():
        seen["inside"] = _CHECKING_USER_STATE.get()
        return {"userState": "normal"}, None

    client = _client_with_user_state(user_state)
    assert asyncio.run(client._get_user_state()) == "normal"
    assert seen["inside"] is True, "the 429 branch must see the guard while checking"
    assert _CHECKING_USER_STATE.get() is False, "guard must not leak past the check"


def test_guard_is_cleared_even_when_the_check_fails():
    """A 429 on the check itself must still reset the flag, or every later
    request silently skips its suspension check."""

    async def user_state():
        raise RuntimeError("429 on the state check")

    client = _client_with_user_state(user_state)
    with pytest.raises(RuntimeError):
        asyncio.run(client._get_user_state())
    assert _CHECKING_USER_STATE.get() is False


def test_nested_check_is_suppressed():
    """Simulates the production cycle: the state check is itself rate limited.

    With the guard, the inner 429 must NOT start another check.
    """
    calls = {"n": 0}

    async def user_state():
        calls["n"] += 1
        # Re-entrant call, as the real 429 branch would have made.
        if not _CHECKING_USER_STATE.get():
            await client._get_user_state()
        return {"userState": "normal"}, None

    client = _client_with_user_state(user_state)
    asyncio.run(client._get_user_state())
    assert calls["n"] == 1, f"nested check ran {calls['n']}x — guard did not hold"

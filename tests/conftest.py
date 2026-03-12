"""Shared fixtures for twikit integration tests."""

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from twikit.client.client import Client

ACCOUNTS_PATH = Path(__file__).parent.parent / "accounts.txt"


def _load_first_account() -> dict:
    """Load the first account from accounts.txt."""
    with open(ACCOUNTS_PATH, "r", encoding="utf-8") as f:
        line = f.readline().strip()
    return json.loads(line)


@pytest.fixture
async def client() -> Client:
    """Create and authenticate a twikit Client using cookies from accounts.txt."""
    acct = _load_first_account()
    cookies = json.loads(acct["cookies"])
    proxy = acct.get("proxy")

    c = Client(language="en-US", proxy=proxy)
    c.set_cookies(cookies)
    return c

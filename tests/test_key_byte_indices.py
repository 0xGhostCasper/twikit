"""KEY_BYTE index parsing for the X-Client-Transaction-Id.

Pinned against the live logged-in ondemand.s bundle on 2026-10-05 (indices
[10, 5, 36, 42], 1-char variable names): strict and loose patterns agree, so the
loose pattern is a fallback only for a minifier change (upstream PR #432).
"""

from twikit.x_client_transaction.transaction import parse_key_byte_indices


def test_strict_pattern_matches_current_bundle_shape():
    js = "x=(a[10],16),y=(b[5],16),z=(c[36],16),w=(d[42],16)"
    assert parse_key_byte_indices(js) == [10, 5, 36, 42]


def test_loose_fallback_when_minifier_uses_longer_names():
    js = "x=(abc[10],16),y=(abc[5],16),z=(abc[136],16)"
    assert parse_key_byte_indices(js) == [10, 5, 136]


def test_no_indices_returns_empty():
    assert parse_key_byte_indices("nothing here") == []

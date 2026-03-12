"""Integration tests for trend-related read-only endpoints."""

import pytest

from twikit.client.client import Client
from twikit.trend import Trend
from twikit.user import User


class TestGetTrends:
    @pytest.mark.asyncio
    async def test_returns_trends(self, client: Client):
        trends = await client.get_trends("trending")
        assert isinstance(trends, list)
        # Trends may be empty due to Twitter API intermittent behavior
        if len(trends) > 0:
            assert all(isinstance(t, Trend) for t in trends)


async def _get_trend_id(client: Client) -> str | None:
    """Try to obtain a valid trendId from the trends API."""
    trends = await client.get_trends("trending")
    if not trends:
        return None
    # Trend metadata 'trendId' is embedded in the raw API response
    # but not exposed on the Trend dataclass. We need to get it from raw data.
    response, _ = await client.v11.guide("trending", 20, None)
    from twikit.utils import find_dict
    entries = [
        i for i in find_dict(response, "entries", find_one=True)[0]
        if i["entryId"].startswith("trends")
    ]
    if not entries:
        return None
    items = entries[-1]["content"]["timelineModule"]["items"]
    if not items:
        return None
    trend_data = items[0]["item"]["content"]["trend"]
    return trend_data.get("trendMetadata", {}).get("trendId")


class TestTrendHistory:
    @pytest.mark.asyncio
    async def test_returns_list(self, client: Client):
        trend_id = await _get_trend_id(client)
        if trend_id is None:
            pytest.skip("Trends API returned empty — cannot obtain a trendId")
        history = await client.get_trend_history(trend_id)
        assert isinstance(history, list)


class TestTrendRelevantUsers:
    @pytest.mark.asyncio
    async def test_returns_list(self, client: Client):
        trend_id = await _get_trend_id(client)
        if trend_id is None:
            pytest.skip("Trends API returned empty — cannot obtain a trendId")
        users = await client.get_trend_relevant_users(trend_id)
        assert isinstance(users, list)
        if len(users) > 0:
            assert all(isinstance(u, User) for u in users)

"""Integration tests for timeline read-only endpoints."""

import pytest

from twikit.client.client import Client
from twikit.tweet import Tweet
from twikit.utils import Result


class TestGetTimeline:
    @pytest.mark.asyncio
    async def test_returns_tweets(self, client: Client):
        tweets = await client.get_timeline(count=5)
        assert isinstance(tweets, Result)
        assert len(tweets) > 0
        assert all(isinstance(t, Tweet) for t in tweets)


class TestGetLatestTimeline:
    @pytest.mark.asyncio
    async def test_returns_tweets(self, client: Client):
        tweets = await client.get_latest_timeline(count=5)
        assert isinstance(tweets, Result)
        assert len(tweets) > 0

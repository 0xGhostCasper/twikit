"""Integration tests for list-related read-only endpoints."""

import pytest

from twikit.client.client import Client
from twikit.errors import TooManyRequests, NotFound
from twikit.tweet import Tweet
from twikit.list import List
from twikit.utils import Result

from .constants import TECH_NEWS_LIST_ID


class TestListByRestId:
    @pytest.mark.asyncio
    async def test_returns_list(self, client: Client):
        lst = await client.get_list(TECH_NEWS_LIST_ID)
        assert isinstance(lst, List)
        assert lst.id == TECH_NEWS_LIST_ID

    @pytest.mark.asyncio
    async def test_fields_populated(self, client: Client):
        """Verify key List fields are populated with real data."""
        from twikit.user import User

        lst = await client.get_list(TECH_NEWS_LIST_ID)
        # Identity
        assert lst.id != ''
        assert lst.name != ''
        assert lst.created_at != 0
        # Counters
        assert lst.member_count > 0
        assert isinstance(lst.subscriber_count, int)
        # Mode
        assert lst.mode in ('Private', 'Public')
        # Booleans — should be actual bools, not None
        assert isinstance(lst.following, bool)
        assert isinstance(lst.is_member, bool)
        assert isinstance(lst.muting, bool)
        assert isinstance(lst.pinning, bool)
        # New fields
        assert isinstance(lst.facepile_urls, list)
        assert lst.members_context is not None
        # Owner
        assert isinstance(lst.owner, User)
        assert lst.owner.id != ''
        assert lst.owner.screen_name != ''


class TestListLatestTweets:
    @pytest.mark.asyncio
    async def test_returns_tweets(self, client: Client):
        tweets = await client.get_list_tweets(TECH_NEWS_LIST_ID, count=5)
        assert isinstance(tweets, Result)
        assert len(tweets) > 0
        assert all(isinstance(t, Tweet) for t in tweets)


class TestListMembers:
    @pytest.mark.asyncio
    async def test_returns_users(self, client: Client):
        users = await client.get_list_members(TECH_NEWS_LIST_ID, count=5)
        assert isinstance(users, Result)
        assert len(users) > 0


class TestListSubscribers:
    @pytest.mark.asyncio
    async def test_returns_result(self, client: Client):
        users = await client.get_list_subscribers(TECH_NEWS_LIST_ID, count=5)
        assert isinstance(users, Result)


class TestListRankedTweets:
    @pytest.mark.asyncio
    async def test_returns_result(self, client: Client):
        try:
            tweets = await client.get_list_ranked_tweets(TECH_NEWS_LIST_ID, count=5)
        except (TooManyRequests, NotFound, Exception) as e:
            if "Timeout" in type(e).__name__ or "Rate limit" in str(e):
                pytest.skip("Endpoint timed out or rate limited")
            raise
        assert isinstance(tweets, Result)


class TestSearchListTweets:
    @pytest.mark.asyncio
    async def test_returns_result(self, client: Client):
        tweets = await client.search_list_tweets(
            TECH_NEWS_LIST_ID, "technology", count=5
        )
        assert isinstance(tweets, Result)

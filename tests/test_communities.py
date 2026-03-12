"""Integration tests for community-related read-only endpoints."""

import pytest

from twikit.client.client import Client
from twikit.tweet import Tweet
from twikit.utils import Result

from .constants import SOFTWARE_ENG_COMMUNITY_ID


class TestCommunityFields:
    @pytest.mark.asyncio
    async def test_fields_populated(self, client: Client):
        """Verify key Community fields are populated with real data."""
        from twikit.community import Community

        community = await client.get_community(SOFTWARE_ENG_COMMUNITY_ID)
        assert isinstance(community, Community)
        # Identity
        assert community.id != ''
        assert community.name != ''
        # Counters
        assert community.member_count > 0
        # Booleans
        assert isinstance(community.is_nsfw, bool)
        assert isinstance(community.is_member, bool)
        # Metadata
        assert community.join_policy is not None
        assert community.created_at is not None and community.created_at > 0
        assert community.description is not None
        # New fields
        assert community.primary_community_topic is not None
        # Creator
        assert community.creator is not None
        # Banner — at least one should be present
        assert community.banner or community.custom_banner
        # Rules — should be a list or None
        assert community.rules is None or isinstance(community.rules, list)


class TestSearchCommunity:
    @pytest.mark.asyncio
    async def test_returns_results(self, client: Client):
        communities = await client.search_community("python")
        assert isinstance(communities, (list, Result))


class TestCommunityTweets:
    @pytest.mark.asyncio
    async def test_top(self, client: Client):
        tweets = await client.get_community_tweets(
            SOFTWARE_ENG_COMMUNITY_ID, "Top", count=5
        )
        assert isinstance(tweets, Result)
        assert len(tweets) > 0
        assert all(isinstance(t, Tweet) for t in tweets)

    @pytest.mark.asyncio
    async def test_media(self, client: Client):
        tweets = await client.get_community_tweets(
            SOFTWARE_ENG_COMMUNITY_ID, "Media", count=5
        )
        assert isinstance(tweets, Result)


class TestExploreCommunities:
    @pytest.mark.asyncio
    async def test_returns_result(self, client: Client):
        communities = await client.explore_communities(count=5)
        assert isinstance(communities, Result)


class TestCommunityHashtags:
    @pytest.mark.asyncio
    async def test_returns_result(self, client: Client):
        tweets = await client.get_community_hashtags(
            SOFTWARE_ENG_COMMUNITY_ID, hashtags=["programming"], count=5
        )
        assert isinstance(tweets, Result)


class TestCommunityNotesStats:
    @pytest.mark.asyncio
    async def test_returns_dict(self, client: Client):
        stats = await client.get_community_notes_stats()
        assert isinstance(stats, dict)


class TestCommunityNotesTimeline:
    @pytest.mark.asyncio
    async def test_returns_result(self, client: Client):
        notes = await client.get_community_notes_timeline(count=5)
        assert isinstance(notes, Result)

"""Integration tests for audio space read-only endpoints."""

import re

import pytest

from twikit.audiospace import AudioSpace
from twikit.client.client import Client
from twikit.errors import NotFound, TooManyRequests
from twikit.utils import Result


async def _find_space_id(client: Client) -> str | None:
    """Dynamically discover a live/recent space ID via filter:spaces search."""
    try:
        tweets = await client.search_tweet("filter:spaces", "Top", count=5)
    except (TooManyRequests, NotFound):
        return None

    for tweet in tweets:
        for u in tweet._legacy.get('entities', {}).get('urls', []):
            expanded = u.get('expanded_url', '')
            m = re.search(r'/i/spaces/(\w+)', expanded)
            if m:
                return m.group(1)
    return None


class TestAudioSpaceById:
    @pytest.mark.asyncio
    async def test_returns_space(self, client: Client):
        space_id = await _find_space_id(client)
        if not space_id:
            pytest.skip("No space ID discoverable (search rate-limited or no live spaces)")
        space = await client.get_audio_space(space_id)
        assert isinstance(space, AudioSpace)
        assert space.id == space_id

    @pytest.mark.asyncio
    async def test_fields_populated(self, client: Client):
        """Verify key AudioSpace fields are populated with real data."""
        space_id = await _find_space_id(client)
        if not space_id:
            pytest.skip("No space ID discoverable (search rate-limited or no live spaces)")
        space = await client.get_audio_space(space_id)
        assert space.id != ''
        assert space.title != ''
        assert space.state in ('Running', 'Ended', 'NotStarted', 'TimedOut', '')
        assert space.created_at > 0
        assert isinstance(space.is_locked, bool)
        assert isinstance(space.total_live_listeners, int)


class TestSearchAudioSpaces:
    @pytest.mark.asyncio
    async def test_returns_result(self, client: Client):
        try:
            spaces = await client.search_audio_spaces("technology", count=5)
        except NotFound:
            pytest.skip("AudioSpaceSearch endpoint returns 404 (may be deprecated)")
        assert isinstance(spaces, Result)

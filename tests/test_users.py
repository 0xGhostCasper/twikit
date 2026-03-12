"""Integration tests for user-related read-only endpoints."""

import pytest

from twikit.client.client import Client
from twikit.errors import TooManyRequests, NotFound
from twikit.user import User
from twikit.utils import Result

from .constants import (
    ELON_USER_ID,
    ELON_SCREEN_NAME,
    BILL_GATES_USER_ID,
    BILL_GATES_SCREEN_NAME,
)


class TestUserByScreenName:
    @pytest.mark.asyncio
    async def test_returns_user(self, client: Client):
        user = await client.get_user_by_screen_name(ELON_SCREEN_NAME)
        assert isinstance(user, User)
        assert user.id == ELON_USER_ID
        assert user.screen_name.lower() == ELON_SCREEN_NAME

    @pytest.mark.asyncio
    async def test_has_profile_data(self, client: Client):
        user = await client.get_user_by_screen_name(ELON_SCREEN_NAME)
        assert user.name is not None
        assert user.followers_count > 0
        assert user.following_count > 0

    @pytest.mark.asyncio
    async def test_fields_populated(self, client: Client):
        """Verify key User fields are populated with real data."""
        user = await client.get_user_by_screen_name(ELON_SCREEN_NAME)
        # Identity fields — always present
        assert user.id != ''
        assert user.screen_name != ''
        assert user.name != ''
        assert user.created_at != ''
        # Profile fields
        assert user.profile_image_url != ''
        assert user.description is not None
        # Counters — Elon should have substantial numbers
        assert user.followers_count > 0
        assert user.following_count > 0
        assert user.favourites_count >= 0
        assert user.statuses_count > 0
        assert user.media_count > 0
        assert user.listed_count > 0
        # Verification
        assert isinstance(user.is_blue_verified, bool)
        assert isinstance(user.verified, bool)
        # Profile shape (Circle or Square)
        assert user.profile_image_shape in ('Circle', 'Square', 'Hexagon', '')
        # Boolean relationship fields should be bool, not None
        assert isinstance(user.following, bool)
        assert isinstance(user.followed_by, bool)
        assert isinstance(user.blocking, bool)
        assert isinstance(user.muting, bool)


class TestUserById:
    @pytest.mark.asyncio
    async def test_returns_user(self, client: Client):
        user = await client.get_user_by_id(ELON_USER_ID)
        assert isinstance(user, User)
        assert user.id == ELON_USER_ID


class TestUsersByIds:
    @pytest.mark.asyncio
    async def test_returns_multiple_users(self, client: Client):
        user_ids = [ELON_USER_ID, BILL_GATES_USER_ID]
        try:
            users = await client.get_users_by_ids(user_ids)
        except (NotFound, TooManyRequests):
            pytest.skip("Endpoint temporarily unavailable")
        assert isinstance(users, list)
        assert len(users) >= 1
        assert all(isinstance(u, User) for u in users)
        returned_ids = {u.id for u in users}
        assert ELON_USER_ID in returned_ids


class TestUsersByScreenNames:
    @pytest.mark.asyncio
    async def test_returns_multiple_users(self, client: Client):
        screen_names = [ELON_SCREEN_NAME, BILL_GATES_SCREEN_NAME]
        users = await client.get_users_by_screen_names(screen_names)
        assert isinstance(users, list)
        assert len(users) >= 1
        assert all(isinstance(u, User) for u in users)
        returned_names = {u.screen_name.lower() for u in users}
        assert ELON_SCREEN_NAME in returned_names


class TestFollowers:
    @pytest.mark.asyncio
    async def test_returns_users(self, client: Client):
        try:
            users = await client.get_user_followers(ELON_USER_ID, count=5)
        except NotFound:
            pytest.skip("Followers endpoint returned transient 404")
        assert isinstance(users, Result)
        assert len(users) > 0
        assert all(isinstance(u, User) for u in users)


class TestFollowing:
    @pytest.mark.asyncio
    async def test_returns_users(self, client: Client):
        users = await client.get_user_following(ELON_USER_ID, count=5)
        assert isinstance(users, Result)
        assert len(users) > 0
        assert all(isinstance(u, User) for u in users)


class TestVerifiedFollowers:
    @pytest.mark.asyncio
    async def test_returns_result(self, client: Client):
        users = await client.get_user_verified_followers(ELON_USER_ID, count=5)
        assert isinstance(users, Result)

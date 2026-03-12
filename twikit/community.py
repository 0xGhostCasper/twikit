from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Literal, NamedTuple

from .tweet import Tweet
from .user import User
from .utils import Result, b64_to_str

if TYPE_CHECKING:
    from .client.client import Client


class CommunityCreator(NamedTuple):
    id: str
    screen_name: str
    verified: bool


class CommunityRule(NamedTuple):
    id: str
    name: str


@dataclass(eq=False, repr=False)
class CommunityMember:
    _client: Client = field(repr=False, compare=False)
    id: str = ''
    community_role: str = ''
    super_following: bool = False
    super_follow_eligible: bool = False
    super_followed_by: bool = False
    smart_blocking: bool = False
    is_blue_verified: bool = False
    screen_name: str = ''
    name: str = ''
    follow_request_sent: bool = False
    protected: bool = False
    following: bool = False
    followed_by: bool = False
    blocking: bool = False
    profile_image_url_https: str = ''
    verified: bool = False

    @classmethod
    def from_data(cls, client: Client, data: dict) -> CommunityMember:
        legacy = data['legacy']
        return cls(
            _client=client,
            id=data['rest_id'],
            community_role=data['community_role'],
            super_following=data['super_following'],
            super_follow_eligible=data['super_follow_eligible'],
            super_followed_by=data['super_followed_by'],
            smart_blocking=data['smart_blocking'],
            is_blue_verified=data['is_blue_verified'],
            screen_name=legacy['screen_name'],
            name=legacy['name'],
            follow_request_sent=legacy['follow_request_sent'],
            protected=legacy['protected'],
            following=legacy['following'],
            followed_by=legacy['followed_by'],
            blocking=legacy['blocking'],
            profile_image_url_https=legacy['profile_image_url_https'],
            verified=legacy['verified'],
        )

    def __eq__(self, other: object) -> bool:
        return isinstance(other, CommunityMember) and self.id == other.id

    def __repr__(self) -> str:
        return f'<CommunityMember id="{self.id}">'


@dataclass(eq=False, repr=False)
class Community:
    """
    Attributes
    ----------
    id : :class:`str`
        The ID of the community.
    name : :class:`str`
        The name of the community.
    member_count : :class:`int`
        The count of members in the community.
    is_nsfw : :class:`bool`
        Indicates if the community is NSFW.
    members_facepile_results : list[:class:`str`]
        The profile image URLs of members.
    banner : :class:`dict`
        The banner information of the community.
    is_member : :class:`bool`
        Indicates if the user is a member of the community.
    role : :class:`str`
        The role of the user in the community.
    description : :class:`str`
        The description of the community.
    creator : :class:`User` | :class:`CommunityCreator` | None
        The creator of the community.
    admin : :class:`User` | None
        The admin of the community.
    join_policy : :class:`str`
        The join policy of the community.
    created_at : :class:`int`
        The timestamp of the community's creation.
    invites_policy : :class:`str`
        The invites policy of the community.
    is_pinned : :class:`bool`
        Indicates if the community is pinned.
    rules : list[:class:`CommunityRule`]
        The rules of the community.
    primary_community_topic : :class:`str` | None
        The primary topic of the community (e.g. 'Software').
    custom_banner : :class:`dict`
        The custom banner information of the community.
    """
    _client: Client = field(repr=False, compare=False)
    id: str = ''
    name: str = ''
    member_count: int = 0
    is_nsfw: bool = False
    members_facepile_results: list[str] = field(default_factory=list)
    banner: dict = field(default_factory=dict)
    custom_banner: dict = field(default_factory=dict)
    is_member: bool | None = None
    role: str | None = None
    description: str | None = None
    creator: User | CommunityCreator | None = None
    admin: User | None = None
    join_policy: str | None = None
    created_at: int | None = None
    invites_policy: str | None = None
    is_pinned: bool | None = None
    rules: list[CommunityRule] | None = None
    primary_community_topic: str | None = None

    @classmethod
    def from_data(cls, client: Client, data: dict) -> Community:
        members_facepile = []
        for i in data.get('members_facepile_results', []):
            result = i.get('result', {})
            legacy = result.get('legacy', {})
            url = legacy.get('profile_image_url_https')
            if url:
                members_facepile.append(url)

        banner_media = data.get('default_banner_media', {})
        banner = banner_media.get('media_info', {})

        creator = None
        if 'creator_results' in data:
            creator_data = data['creator_results'].get('result', {})
            if 'rest_id' in creator_data:
                creator = User.from_data(client, creator_data)
            elif 'id' in creator_data and 'legacy' in creator_data:
                creator = CommunityCreator(
                    b64_to_str(creator_data['id']).removeprefix('User:'),
                    creator_data['legacy']['screen_name'],
                    creator_data['legacy']['verified'],
                )

        admin = None
        admin_results = data.get('admin_results', {})
        if 'result' in admin_results:
            admin = User.from_data(client, admin_results['result'])

        rules = None
        if 'rules' in data:
            rules = [
                CommunityRule(i['rest_id'], i['name']) for i in data['rules']
            ]

        custom_banner_media = data.get('custom_banner_media', {})
        custom_banner = custom_banner_media.get('media_info', {})

        topic_data = data.get('primary_community_topic', {})
        primary_topic = topic_data.get('topic_name') if topic_data else None

        return cls(
            _client=client,
            id=data.get('rest_id', ''),
            name=data.get('name', ''),
            member_count=data.get('member_count', 0),
            is_nsfw=data.get('is_nsfw', False),
            members_facepile_results=members_facepile,
            banner=banner,
            custom_banner=custom_banner,
            is_member=data.get('is_member'),
            role=data.get('role'),
            description=data.get('description'),
            creator=creator,
            admin=admin,
            join_policy=data.get('join_policy'),
            created_at=data.get('created_at'),
            invites_policy=data.get('invites_policy'),
            is_pinned=data.get('is_pinned'),
            rules=rules,
            primary_community_topic=primary_topic,
        )

    async def get_tweets(
        self,
        tweet_type: Literal['Top', 'Latest', 'Media'],
        count: int = 40,
        cursor: str | None = None
    ) -> Result[Tweet]:
        """Retrieves tweets from the community."""
        return await self._client.get_community_tweets(
            self.id, tweet_type, count, cursor
        )

    async def join(self) -> Community:
        """Join the community."""
        return await self._client.join_community(self.id)

    async def leave(self) -> Community:
        """Leave the community."""
        return await self._client.leave_community(self.id)

    async def request_to_join(self, answer: str | None = None) -> Community:
        """Request to join the community."""
        return await self._client.request_to_join_community(self.id, answer)

    async def get_members(
        self, count: int = 20, cursor: str | None = None
    ) -> Result[CommunityMember]:
        """Retrieves members of the community."""
        return await self._client.get_community_members(
            self.id, count, cursor
        )

    async def get_moderators(
        self, count: int = 20, cursor: str | None = None
    ) -> Result[CommunityMember]:
        """Retrieves moderators of the community."""
        return await self._client.get_community_moderators(
            self.id, count, cursor
        )

    async def search_tweet(
        self, query: str, count: int = 20, cursor: str | None = None
    ) -> Result[Tweet]:
        """Searches tweets in the community."""
        return await self._client.search_community_tweet(
            self.id, query, count, cursor
        )

    async def update(self) -> None:
        new = await self._client.get_community(self.id)
        self.__dict__.update(new.__dict__)

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Community) and self.id == other.id

    def __repr__(self) -> str:
        return f'<Community id="{self.id}">'

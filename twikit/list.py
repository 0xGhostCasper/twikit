from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import TYPE_CHECKING, Literal

from .user import User
from .utils import timestamp_to_datetime

if TYPE_CHECKING:
    from httpx import Response

    from .client.client import Client
    from .tweet import Tweet
    from .utils import Result


@dataclass(eq=False, repr=False)
class List:
    """
    Class representing a Twitter List.

    Attributes
    ----------
    id : :class:`str`
        The unique identifier of the List.
    created_at : :class:`int`
        The timestamp when the List was created.
    default_banner : :class:`dict`
        Information about the default banner of the List.
    banner : :class:`dict`
        Information about the banner of the List.
    description : :class:`str`
        The description of the List.
    following : :class:`bool`
        Indicates if the authenticated user is following the List.
    is_member : :class:`bool`
        Indicates if the authenticated user is a member of the List.
    member_count : :class:`int`
        The number of members in the List.
    mode : {'Private', 'Public'}
        The mode of the List, either 'Private' or 'Public'.
    muting : :class:`bool`
        Indicates if the authenticated user is muting the List.
    name : :class:`str`
        The name of the List.
    pinning : :class:`bool`
        Indicates if the List is pinned.
    subscriber_count : :class:`int`
        The number of subscribers to the List.
    facepile_urls : list[:class:`str`]
        Profile image URLs of list members.
    followers_context : :class:`str` | None
        Follower context string (e.g. '2.4K followers including @user').
    members_context : :class:`str` | None
        Member context string (e.g. '87 members').
    owner : :class:`User` | None
        The user who owns the list.
    """
    _client: Client = field(repr=False, compare=False)
    id: str = ''
    created_at: int = 0
    default_banner: dict = field(default_factory=dict)
    banner: dict = field(default_factory=dict)
    description: str = ''
    following: bool = False
    is_member: bool = False
    member_count: int = 0
    mode: Literal['Private', 'Public'] = 'Public'
    muting: bool = False
    name: str = ''
    pinning: bool = False
    subscriber_count: int = 0
    facepile_urls: list[str] = field(default_factory=list)
    followers_context: str | None = None
    members_context: str | None = None
    owner: User | None = None

    @classmethod
    def from_data(cls, client: Client, data: dict) -> List:
        default_banner_media = data.get('default_banner_media', {})
        default_banner = default_banner_media.get('media_info', {})
        if 'custom_banner_media' in data:
            banner = data['custom_banner_media'].get('media_info', default_banner)
        else:
            banner = default_banner

        owner = None
        user_results = data.get('user_results', {})
        if 'result' in user_results:
            owner = User.from_data(client, user_results['result'])

        return cls(
            _client=client,
            id=data.get('id_str', ''),
            created_at=data.get('created_at', 0),
            default_banner=default_banner,
            banner=banner,
            description=data.get('description', ''),
            following=data.get('following', False),
            is_member=data.get('is_member', False),
            member_count=data.get('member_count', 0),
            mode=data.get('mode', 'Public'),
            muting=data.get('muting', False),
            name=data.get('name', ''),
            pinning=data.get('pinning', False),
            subscriber_count=data.get('subscriber_count', 0),
            facepile_urls=data.get('facepile_urls', []) or [],
            followers_context=data.get('followers_context'),
            members_context=data.get('members_context'),
            owner=owner,
        )

    @property
    def created_at_datetime(self) -> datetime:
        return timestamp_to_datetime(self.created_at)

    async def edit_banner(self, media_id: str) -> Response:
        """Edit the banner image of the list."""
        return await self._client.edit_list_banner(self.id, media_id)

    async def delete_banner(self) -> Response:
        """Deletes the list banner."""
        return await self._client.delete_list_banner(self.id)

    async def edit(
        self,
        name: str | None = None,
        description: str | None = None,
        is_private: bool | None = None
    ) -> List:
        """Edits list information."""
        return await self._client.edit_list(
            self.id, name, description, is_private
        )

    async def add_member(self, user_id: str) -> Response:
        """Adds a member to the list."""
        return await self._client.add_list_member(self.id, user_id)

    async def remove_member(self, user_id: str) -> Response:
        """Removes a member from the list."""
        return await self._client.remove_list_member(self.id, user_id)

    async def get_tweets(
        self, count: int = 20, cursor: str | None = None
    ) -> Result[Tweet]:
        """Retrieves tweets from the list."""
        return await self._client.get_list_tweets(self.id, count, cursor)

    async def get_members(
        self, count: int = 20, cursor: str | None = None
    ) -> Result[User]:
        """Retrieves members of the list."""
        return await self._client.get_list_members(self.id, count, cursor)

    async def get_subscribers(
        self, count: int = 20, cursor: str | None = None
    ) -> Result[User]:
        """Retrieves subscribers of the list."""
        return await self._client.get_list_subscribers(self.id, count, cursor)

    async def update(self) -> None:
        new = await self._client.get_list(self.id)
        self.__dict__.update(new.__dict__)

    def __eq__(self, other: object) -> bool:
        return isinstance(other, List) and self.id == other.id

    def __repr__(self) -> str:
        return f'<List id="{self.id}">'

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from .message import Message
from .user import User
from .utils import build_user_data

if TYPE_CHECKING:
    from httpx import Response

    from .client.client import Client
    from .utils import Result


@dataclass(eq=False, repr=False)
class Group:
    """
    Represents a group.

    Attributes
    ----------
    id : :class:`str`
        The ID of the group.
    name : :class:`str` | None
        The name of the group.
    members : list[:class:`User`]
        Members of the group.
    """
    _client: Client = field(repr=False, compare=False)
    id: str = ''
    name: str | None = None
    members: list[User] = field(default_factory=list)

    @classmethod
    def from_data(cls, client: Client, group_id: str, data: dict) -> Group:
        conversation_timeline = data["conversation_timeline"]
        name = (
            conversation_timeline["conversations"][group_id]["name"]
            if len(conversation_timeline["conversations"].keys()) > 0
            else None
        )
        members_data = conversation_timeline["users"].values()
        members = [
            User.from_data(client, build_user_data(i)) for i in members_data
        ]
        return cls(
            _client=client,
            id=group_id,
            name=name,
            members=members,
        )

    async def get_history(
        self, max_id: str | None = None
    ) -> Result[GroupMessage]:
        """Retrieves the DM conversation history in the group."""
        return await self._client.get_group_dm_history(self.id, max_id)

    async def add_members(self, user_ids: list[str]) -> Response:
        """Adds members to the group."""
        return await self._client.add_members_to_group(self.id, user_ids)

    async def change_name(self, name: str) -> Response:
        """Changes group name."""
        return await self._client.change_group_name(self.id, name)

    async def send_message(
        self,
        text: str,
        media_id: str | None = None,
        reply_to: str | None = None
    ) -> GroupMessage:
        """Sends a message to the group."""
        return await self._client.send_dm_to_group(
            self.id, text, media_id, reply_to
        )

    async def update(self) -> None:
        new = await self._client.get_group(self.id)
        self.__dict__.update(new.__dict__)

    def __repr__(self) -> str:
        return f'<Group id="{self.id}">'


@dataclass(eq=False, repr=False)
class GroupMessage(Message):
    """
    Represents a group direct message.

    Attributes
    ----------
    group_id : :class:`str`
        The ID of the group.
    """
    group_id: str = ''

    @classmethod
    def from_data(
        cls, client: Client, data: dict, sender_id: str, group_id: str
    ) -> GroupMessage:
        return cls(
            _client=client,
            id=data['id'],
            time=data['time'],
            text=data['text'],
            attachment=data.get('attachment'),
            sender_id=sender_id,
            recipient_id=None,
            group_id=group_id,
        )

    async def group(self) -> Group:
        """Gets the group to which the message was sent."""
        return await self._client.get_group(self.group_id)

    async def reply(
        self, text: str, media_id: str | None = None
    ) -> GroupMessage:
        """Replies to the message."""
        return await self._client.send_dm_to_group(
            self.group_id, text, media_id, self.id
        )

    async def add_reaction(self, emoji: str) -> Response:
        """Adds a reaction to the message."""
        return await self._client.add_reaction_to_message(
            self.id, self.group_id, emoji
        )

    async def remove_reaction(self, emoji: str) -> Response:
        """Removes a reaction from the message."""
        return await self._client.remove_reaction_from_message(
            self.id, self.group_id, emoji
        )

    def __repr__(self) -> str:
        return f'<GroupMessage id="{self.id}">'

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from httpx import Response

    from .client.client import Client


@dataclass(eq=False, repr=False)
class Message:
    """
    Represents a direct message.

    Attributes
    ----------
    id : :class:`str`
        The ID of the message.
    time : :class:`str`
        The timestamp of the message.
    text : :class:`str`
        The text content of the message.
    attachment : :class:`dict`
        Attachment Information.
    sender_id : :class:`str`
        The ID of the sender.
    recipient_id : :class:`str` | None
        The ID of the recipient.
    """
    _client: Client = field(repr=False, compare=False)
    id: str = ''
    time: str = ''
    text: str = ''
    attachment: dict | None = None
    sender_id: str = ''
    recipient_id: str | None = None

    @classmethod
    def from_data(
        cls, client: Client, data: dict, sender_id: str, recipient_id: str
    ) -> Message:
        return cls(
            _client=client,
            id=data['id'],
            time=data['time'],
            text=data['text'],
            attachment=data.get('attachment'),
            sender_id=sender_id,
            recipient_id=recipient_id,
        )

    async def reply(self, text: str, media_id: str | None = None) -> Message:
        """Replies to the message.

        Parameters
        ----------
        text : :class:`str`
            The text content of the direct message.
        media_id : :class:`str`, default=None
            The media ID associated with any media content
            to be included in the message.
            Media ID can be received by using the :func:`.upload_media` method.

        Returns
        -------
        :class:`Message`
            `Message` object containing information about the message sent.

        See Also
        --------
        Client.send_dm
        """
        user_id = await self._client.user_id()
        send_to = (
            self.recipient_id
            if user_id == self.sender_id else
            self.sender_id
        )
        return await self._client.send_dm(send_to, text, media_id, self.id)

    async def add_reaction(self, emoji: str) -> Response:
        """
        Adds a reaction to the message.

        Parameters
        ----------
        emoji : :class:`str`
            The emoji to be added as a reaction.

        Returns
        -------
        :class:`httpx.Response`
            Response returned from twitter api.
        """
        user_id = await self._client.user_id()
        partner_id = (
            self.recipient_id
            if user_id == self.sender_id else
            self.sender_id
        )
        conversation_id = f'{partner_id}-{user_id}'
        return await self._client.add_reaction_to_message(
            self.id, conversation_id, emoji
        )

    async def remove_reaction(self, emoji: str) -> Response:
        """
        Removes a reaction from the message.

        Parameters
        ----------
        emoji : :class:`str`
            The emoji to be removed.

        Returns
        -------
        :class:`httpx.Response`
            Response returned from twitter api.
        """
        user_id = await self._client.user_id()
        partner_id = (
            self.recipient_id
            if user_id == self.sender_id else
            self.sender_id
        )
        conversation_id = f'{partner_id}-{user_id}'
        return await self._client.remove_reaction_from_message(
            self.id, conversation_id, emoji
        )

    async def delete(self) -> Response:
        """
        Deletes the message.

        Returns
        -------
        :class:`httpx.Response`
            Response returned from twitter api.

        See Also
        --------
        Client.delete_dm
        """
        return await self._client.delete_dm(self.id)

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Message) and self.id == other.id

    def __repr__(self) -> str:
        return f'<Message id="{self.id}">'

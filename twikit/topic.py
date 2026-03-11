from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .client.client import Client


class Topic:
    """
    Represents a Twitter Topic.

    Attributes
    ----------
    id : :class:`str`
        The ID of the topic.
    name : :class:`str`
        The display name of the topic.
    description : :class:`str`
        A description of the topic.
    not_interested : :class:`bool`
        Whether the user marked this topic as not interested.
    following : :class:`bool`
        Whether the user follows this topic.
    """

    def __init__(self, client: Client, data: dict) -> None:
        self._client = client

        self.id: str = data.get('id', data.get('rest_id', ''))
        self.name: str = data.get('name', '')
        self.description: str = data.get('description', '')
        self.not_interested: bool = data.get('not_interested', False)
        self.following: bool = data.get('following', False)

    def __repr__(self) -> str:
        return f'<Topic id="{self.id}" name="{self.name}">'

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Topic) and self.id == other.id

    def __ne__(self, other: object) -> bool:
        return not self == other

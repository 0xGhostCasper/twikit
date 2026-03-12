from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .client.client import Client


@dataclass(eq=False, repr=False)
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
    _client: Client = field(repr=False, compare=False)
    id: str = ''
    name: str = ''
    description: str = ''
    not_interested: bool = False
    following: bool = False

    @classmethod
    def from_data(cls, client: Client, data: dict) -> Topic:
        return cls(
            _client=client,
            id=data.get('id', data.get('rest_id', '')),
            name=data.get('name', ''),
            description=data.get('description', ''),
            not_interested=data.get('not_interested', False),
            following=data.get('following', False),
        )

    def __repr__(self) -> str:
        return f'<Topic id="{self.id}" name="{self.name}">'

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Topic) and self.id == other.id

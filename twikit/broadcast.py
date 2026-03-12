from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .client.client import Client


@dataclass(eq=False, repr=False)
class Broadcast:
    """
    Represents a Twitter Broadcast (live video).

    Attributes
    ----------
    id : :class:`str`
        The broadcast ID.
    title : :class:`str`
        The title of the broadcast.
    state : :class:`str`
        The broadcast state (e.g., 'RUNNING', 'ENDED').
    media_key : :class:`str`
        The media key of the broadcast.
    created_at : :class:`int`
        The creation timestamp.
    started_at : :class:`int`
        When the broadcast started.
    ended_at : :class:`int` | None
        When the broadcast ended, if applicable.
    total_participants : :class:`int`
        The total number of participants.
    total_replay_watched : :class:`int`
        The total number of replay views.
    image_url : :class:`str` | None
        The thumbnail/image URL.
    """
    _client: Client = field(repr=False, compare=False)
    id: str = ''
    title: str = ''
    state: str = ''
    media_key: str = ''
    created_at: int = 0
    started_at: int = 0
    ended_at: int | None = None
    total_participants: int = 0
    total_replay_watched: int = 0
    image_url: str | None = None

    @classmethod
    def from_data(cls, client: Client, data: dict) -> Broadcast:
        return cls(
            _client=client,
            id=data.get('id', ''),
            title=data.get('title', ''),
            state=data.get('state', ''),
            media_key=data.get('media_key', ''),
            created_at=data.get('created_at_ms', 0),
            started_at=data.get('start', 0),
            ended_at=data.get('end'),
            total_participants=data.get('total_participants', 0),
            total_replay_watched=data.get('total_replay_watched', 0),
            image_url=data.get('image_url'),
        )

    def __repr__(self) -> str:
        return f'<Broadcast id="{self.id}" title="{self.title}">'

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Broadcast) and self.id == other.id

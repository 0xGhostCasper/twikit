from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .client.client import Client


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

    def __init__(self, client: Client, data: dict) -> None:
        self._client = client

        self.id: str = data.get('id', '')
        self.title: str = data.get('title', '')
        self.state: str = data.get('state', '')
        self.media_key: str = data.get('media_key', '')
        self.created_at: int = data.get('created_at_ms', 0)
        self.started_at: int = data.get('start', 0)
        self.ended_at: int | None = data.get('end')
        self.total_participants: int = data.get('total_participants', 0)
        self.total_replay_watched: int = data.get('total_replay_watched', 0)
        self.image_url: str | None = data.get('image_url')

    def __repr__(self) -> str:
        return f'<Broadcast id="{self.id}" title="{self.title}">'

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Broadcast) and self.id == other.id

    def __ne__(self, other: object) -> bool:
        return not self == other

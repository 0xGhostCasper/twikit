from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .client.client import Client


class AudioSpace:
    """
    Represents a Twitter Space.

    Attributes
    ----------
    id : :class:`str`
        The ID of the space.
    title : :class:`str`
        The title of the space.
    state : :class:`str`
        The state of the space (e.g., 'Running', 'Ended').
    created_at : :class:`int`
        The timestamp when the space was created.
    started_at : :class:`int`
        The timestamp when the space started.
    ended_at : :class:`int` | None
        The timestamp when the space ended, if applicable.
    is_locked : :class:`bool`
        Whether the space is locked.
    total_replay_watched : :class:`int`
        The total number of replay views.
    total_live_listeners : :class:`int`
        The total number of live listeners.
    creator_user_id : :class:`str` | None
        The user ID of the space creator.
    """

    def __init__(self, client: Client, data: dict) -> None:
        self._client = client

        metadata = data.get('metadata', data)
        self.id: str = metadata.get('rest_id', '')
        self.title: str = metadata.get('title', '')
        self.state: str = metadata.get('state', '')
        self.created_at: int = metadata.get('created_at', 0)
        self.started_at: int = metadata.get('started_at', 0)
        self.ended_at: int | None = metadata.get('ended_at')
        self.is_locked: bool = metadata.get('is_locked', False)
        self.total_replay_watched: int = metadata.get('total_replay_watched', 0)
        self.total_live_listeners: int = metadata.get('total_live_listeners', 0)

        creator_results = metadata.get('creator_results', {})
        creator_result = creator_results.get('result', {})
        self.creator_user_id: str | None = creator_result.get('rest_id')

    def __repr__(self) -> str:
        return f'<AudioSpace id="{self.id}" title="{self.title}">'

    def __eq__(self, other: object) -> bool:
        return isinstance(other, AudioSpace) and self.id == other.id

    def __ne__(self, other: object) -> bool:
        return not self == other

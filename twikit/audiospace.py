from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .client.client import Client


@dataclass(eq=False, repr=False)
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
    _client: Client = field(repr=False, compare=False)
    id: str = ''
    title: str = ''
    state: str = ''
    created_at: int = 0
    started_at: int = 0
    ended_at: int | None = None
    is_locked: bool = False
    total_replay_watched: int = 0
    total_live_listeners: int = 0
    creator_user_id: str | None = None

    @classmethod
    def from_data(cls, client: Client, data: dict) -> AudioSpace:
        metadata = data.get('metadata', data)
        creator_results = metadata.get('creator_results', {})
        creator_result = creator_results.get('result', {})

        return cls(
            _client=client,
            id=metadata.get('rest_id', ''),
            title=metadata.get('title', ''),
            state=metadata.get('state', ''),
            created_at=metadata.get('created_at', 0),
            started_at=metadata.get('started_at', 0),
            ended_at=metadata.get('ended_at'),
            is_locked=metadata.get('is_locked', False),
            total_replay_watched=metadata.get('total_replay_watched', 0),
            total_live_listeners=metadata.get('total_live_listeners', 0),
            creator_user_id=creator_result.get('rest_id'),
        )

    def __repr__(self) -> str:
        return f'<AudioSpace id="{self.id}" title="{self.title}">'

    def __eq__(self, other: object) -> bool:
        return isinstance(other, AudioSpace) and self.id == other.id

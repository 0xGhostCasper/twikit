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
    ended_at : :class:`str` | None
        The timestamp when the space ended (string from API).
    scheduled_start : :class:`int` | None
        The scheduled start timestamp.
    updated_at : :class:`int` | None
        The timestamp when the space was last updated.
    is_locked : :class:`bool`
        Whether the space is locked.
    is_space_available_for_replay : :class:`bool`
        Whether the space is available for replay.
    is_space_available_for_clipping : :class:`bool`
        Whether the space is available for clipping.
    total_replay_watched : :class:`int`
        The total number of replay views.
    total_live_listeners : :class:`int`
        The total number of live listeners.
    media_key : :class:`str` | None
        The media key of the space.
    content_type : :class:`str` | None
        The content type (e.g., 'visual_audio').
    creator_user_id : :class:`str` | None
        The user ID of the space creator.
    creator_username : :class:`str` | None
        The screen name of the space creator.
    creator_name : :class:`str` | None
        The display name of the space creator.
    admin_count : :class:`int`
        The number of admins.
    speaker_count : :class:`int`
        The number of speakers.
    listener_count : :class:`int`
        The number of listeners.
    """
    _client: Client = field(repr=False, compare=False)
    id: str = ''
    title: str = ''
    state: str = ''
    created_at: int = 0
    started_at: int = 0
    ended_at: str | None = None
    scheduled_start: int | None = None
    updated_at: int | None = None
    is_locked: bool = False
    is_space_available_for_replay: bool = False
    is_space_available_for_clipping: bool = False
    total_replay_watched: int = 0
    total_live_listeners: int = 0
    media_key: str | None = None
    content_type: str | None = None
    creator_user_id: str | None = None
    creator_username: str | None = None
    creator_name: str | None = None
    admin_count: int = 0
    speaker_count: int = 0
    listener_count: int = 0

    @classmethod
    def from_data(cls, client: Client, data: dict) -> AudioSpace:
        metadata = data.get('metadata', data)
        creator_results = metadata.get('creator_results', {})
        creator_result = creator_results.get('result', {})
        creator_legacy = creator_result.get('legacy', {})
        creator_core = creator_result.get('core', {})

        participants = data.get('participants', {})

        return cls(
            _client=client,
            id=metadata.get('rest_id', ''),
            title=metadata.get('title', ''),
            state=metadata.get('state', ''),
            created_at=metadata.get('created_at', 0),
            started_at=metadata.get('started_at', 0),
            ended_at=metadata.get('ended_at'),
            scheduled_start=metadata.get('scheduled_start'),
            updated_at=metadata.get('updated_at'),
            is_locked=metadata.get('is_locked', False),
            is_space_available_for_replay=metadata.get('is_space_available_for_replay', False),
            is_space_available_for_clipping=metadata.get('is_space_available_for_clipping', False),
            total_replay_watched=metadata.get('total_replay_watched', 0),
            total_live_listeners=metadata.get('total_live_listeners', 0),
            media_key=metadata.get('media_key'),
            content_type=metadata.get('content_type'),
            creator_user_id=creator_result.get('rest_id'),
            creator_username=creator_core.get('screen_name') or creator_legacy.get('screen_name'),
            creator_name=creator_core.get('name') or creator_legacy.get('name'),
            admin_count=len(participants.get('admins', [])),
            speaker_count=len(participants.get('speakers', [])),
            listener_count=len(participants.get('listeners', [])),
        )

    def __repr__(self) -> str:
        return f'<AudioSpace id="{self.id}" title="{self.title}">'

    def __eq__(self, other: object) -> bool:
        return isinstance(other, AudioSpace) and self.id == other.id

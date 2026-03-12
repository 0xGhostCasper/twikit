from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .client.client import Client
    from .tweet import Tweet
    from .user import User


@dataclass(eq=False, repr=False)
class Notification:
    """
    Attributes
    ----------
    id : :class:`str`
        The unique identifier of the notification.
    timestamp_ms : :class:`int`
        The timestamp of the notification in milliseconds.
    icon : :class:`dict`
        Dictionary containing icon data for the notification.
    message : :class:`str`
        The message text of the notification.
    tweet : :class:`.Tweet`
        The tweet associated with the notification.
    from_user : :class:`.User`
        The user who triggered the notification.
    """
    _client: Client = field(repr=False, compare=False)
    id: str = ''
    timestamp_ms: int = 0
    icon: dict = field(default_factory=dict)
    message: str = ''
    tweet: Tweet | None = None
    from_user: User | None = None

    @classmethod
    def from_data(
        cls, client: Client, data: dict, tweet: Tweet, from_user: User
    ) -> Notification:
        return cls(
            _client=client,
            id=data['id'],
            timestamp_ms=int(data['timestampMs']),
            icon=data['icon'],
            message=data['message']['text'],
            tweet=tweet,
            from_user=from_user,
        )

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Notification) and self.id == other.id

    def __repr__(self) -> str:
        return f'<Notification id="{self.id}">'

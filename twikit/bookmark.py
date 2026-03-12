from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from httpx import Response

    from .client.client import Client
    from .tweet import Tweet
    from .utils import Result


@dataclass(eq=False, repr=False)
class BookmarkFolder:
    """
    Attributes
    ----------
    id : :class:`str`
        The ID of the folder.
    name : :class:`str`
        The name of the folder
    media : :class:`dict`
        Icon image data.
    """
    _client: Client = field(repr=False, compare=False)
    id: str = ''
    name: str = ''
    media: dict = field(default_factory=dict)

    @classmethod
    def from_data(cls, client: Client, data: dict) -> BookmarkFolder:
        return cls(
            _client=client,
            id=data['id'],
            name=data['name'],
            media=data['media'],
        )

    async def get_tweets(self, cursor: str | None = None) -> Result[Tweet]:
        """Retrieves tweets from the folder."""
        return await self._client.get_bookmarks(
            cursor=cursor, folder_id=self.id
        )

    async def edit(self, name: str) -> BookmarkFolder:
        """Edits the folder."""
        return await self._client.edit_bookmark_folder(self.id, name)

    async def delete(self) -> Response:
        """Deletes the folder."""
        return await self._client.delete_bookmark_folder(self.id)

    async def add(self, tweet_id: str) -> Response:
        """Adds a tweet to the folder."""
        return await self._client.bookmark_tweet(tweet_id, self.id)

    def __eq__(self, other: object) -> bool:
        return isinstance(other, BookmarkFolder) and self.id == other.id

    def __repr__(self) -> str:
        return f'<BookmarkFolder id="{self.id}">'

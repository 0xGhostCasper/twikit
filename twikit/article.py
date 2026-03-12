from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .client.client import Client


@dataclass(eq=False, repr=False)
class Article:
    """
    Represents a Twitter Article (long-form content).

    Attributes
    ----------
    id : :class:`str`
        The ID of the article.
    title : :class:`str`
        The title of the article.
    preview_text : :class:`str`
        A preview/snippet of the article content.
    cover_media_url : :class:`str` | None
        The URL of the article's cover media.
    author_user_id : :class:`str` | None
        The user ID of the article author.
    created_at : :class:`str`
        The creation timestamp.
    state : :class:`str`
        The article state (e.g., 'Published').
    content_blocks : list[:class:`dict`]
        The content blocks of the article.
    """
    _client: Client = field(repr=False, compare=False)
    id: str = ''
    title: str = ''
    preview_text: str = ''
    cover_media_url: str | None = None
    author_user_id: str | None = None
    created_at: str = ''
    state: str = ''
    content_blocks: list[dict] = field(default_factory=list)

    @classmethod
    def from_data(cls, client: Client, data: dict) -> Article:
        cover_media = data.get('cover_media', {})
        media_info = cover_media.get('media_info', {})

        author = data.get('author_results', {}).get('result', {})

        return cls(
            _client=client,
            id=data.get('rest_id', data.get('id', '')),
            title=data.get('title', ''),
            preview_text=data.get('preview_text', ''),
            cover_media_url=media_info.get('original_img_url'),
            author_user_id=author.get('rest_id'),
            created_at=data.get('created_at', ''),
            state=data.get('state', ''),
            content_blocks=data.get('content', {}).get('blocks', []),
        )

    def __repr__(self) -> str:
        return f'<Article id="{self.id}" title="{self.title}">'

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Article) and self.id == other.id

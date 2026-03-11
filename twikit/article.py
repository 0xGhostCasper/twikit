from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .client.client import Client


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
    """

    def __init__(self, client: Client, data: dict) -> None:
        self._client = client

        self.id: str = data.get('rest_id', data.get('id', ''))
        self.title: str = data.get('title', '')
        self.preview_text: str = data.get('preview_text', '')

        cover_media = data.get('cover_media', {})
        media_info = cover_media.get('media_info', {})
        original = media_info.get('original_img_url')
        self.cover_media_url: str | None = original

        author = data.get('author_results', {}).get('result', {})
        self.author_user_id: str | None = author.get('rest_id')

        self.created_at: str = data.get('created_at', '')
        self.state: str = data.get('state', '')
        self.content_blocks: list[dict] = data.get('content', {}).get('blocks', [])

    def __repr__(self) -> str:
        return f'<Article id="{self.id}" title="{self.title}">'

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Article) and self.id == other.id

    def __ne__(self, other: object) -> bool:
        return not self == other

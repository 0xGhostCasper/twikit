from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime
from typing import TYPE_CHECKING

from .geo import Place
from .media import MEDIA_TYPE, _media_from_data
from .user import User
from .utils import find_dict, timestamp_to_datetime

if TYPE_CHECKING:
    from httpx import Response

    from .client.client import Client
    from .utils import Result


@dataclass(eq=False, repr=False)
class Tweet:
    """
    Attributes
    ----------
    id : :class:`str`
        The unique identifier of the tweet.
    user: :class:`User`
        Author of the tweet.
    replies: Result[:class:`Tweet`] | None
        Replies to the tweet.
    reply_to: list[:class:`Tweet`] | None
        A list of Tweet objects representing the tweets to which to reply.
    related_tweets : list[:class:`Tweet`] | None
        Related tweets.
    thread : list[:class:`Tweet`] | None
        Tweet thread.
    """
    _client: Client = field(repr=False, compare=False)
    _data: dict = field(repr=False, compare=False, default_factory=dict)
    _legacy: dict = field(repr=False, compare=False, default_factory=dict)
    user: User | None = None
    replies: Result[Tweet] | None = None
    reply_to: list[Tweet] | None = None
    related_tweets: list[Tweet] | None = None
    thread: list[Tweet] | None = None

    @classmethod
    def from_data(cls, client: Client, data: dict, user: User = None) -> Tweet:
        return cls(
            _client=client,
            _data=data,
            _legacy=data['legacy'],
            user=user,
        )

    @property
    def id(self) -> str:
        return self._data['rest_id']

    @property
    def created_at(self) -> str:
        return self._legacy['created_at']

    @property
    def text(self) -> str:
        return self._legacy['full_text']

    @property
    def lang(self) -> str:
        return self._legacy['lang']

    @property
    def source(self) -> str | None:
        """The client application used to post the tweet (e.g. 'Twitter for iPhone')."""
        return self._data.get('source')

    @property
    def conversation_id(self) -> str | None:
        """The conversation/thread ID this tweet belongs to."""
        return self._legacy.get('conversation_id_str')

    @property
    def in_reply_to(self) -> str | None:
        return self._legacy.get('in_reply_to_status_id_str')

    @property
    def in_reply_to_screen_name(self) -> str | None:
        """The screen name of the user being replied to."""
        return self._legacy.get('in_reply_to_screen_name')

    @property
    def in_reply_to_user_id(self) -> str | None:
        """The user ID of the user being replied to."""
        return self._legacy.get('in_reply_to_user_id_str')

    @property
    def display_text_range(self) -> list[int] | None:
        """The display text range [start, end]."""
        return self._legacy.get('display_text_range')

    @property
    def retweeted(self) -> bool:
        """Whether the authenticated user has retweeted this tweet."""
        return self._legacy.get('retweeted', False)

    @property
    def is_quote_status(self) -> bool:
        return self._legacy['is_quote_status']

    @property
    def possibly_sensitive(self) -> bool:
        return self._legacy.get('possibly_sensitive')

    @property
    def possibly_sensitive_editable(self) -> bool:
        return self._legacy.get('possibly_sensitive_editable')

    @property
    def quote_count(self) -> int:
        return self._legacy.get('quote_count')

    @property
    def reply_count(self) -> int:
        return self._legacy['reply_count']

    @property
    def favorite_count(self) -> int:
        return self._legacy['favorite_count']

    @property
    def favorited(self) -> bool:
        return self._legacy['favorited']

    @property
    def retweet_count(self) -> int:
        return self._legacy['retweet_count']

    @property
    def _place_data(self):
        return self._legacy.get('place')

    @property
    def bookmark_count(self) -> int:
        return self._legacy.get('bookmark_count')

    @property
    def bookmarked(self) -> bool:
        return self._legacy.get('bookmarked')

    @property
    def edit_tweet_ids(self) -> list[int]:
        return self._data['edit_control'].get('edit_tweet_ids', [])

    @property
    def editable_until_msecs(self) -> int:
        return self._data['edit_control'].get('editable_until_msecs')

    @property
    def is_translatable(self) -> bool:
        return self._data.get('is_translatable')

    @property
    def is_edit_eligible(self) -> bool:
        return self._data['edit_control'].get('is_edit_eligible')

    @property
    def edits_remaining(self) -> int:
        return self._data['edit_control'].get('edits_remaining')

    @property
    def view_count(self) -> int | None:
        return self._data.get('views', {}).get('count')

    @property
    def view_count_state(self) -> str | None:
        return self._data.get('views', {}).get('state')

    @property
    def has_community_notes(self) -> bool:
        return self._data.get('has_birdwatch_notes')

    @property
    def quote(self) -> Tweet | None:
        if self._data.get('quoted_status_result'):
            quoted_tweet = self._data['quoted_status_result']
            return tweet_from_data(self._client, quoted_tweet)

    @property
    def retweeted_tweet(self) -> Tweet | None:
        if self._legacy.get('retweeted_status_result'):
            retweeted_tweet = self._legacy['retweeted_status_result']
            return tweet_from_data(self._client, retweeted_tweet)

    @property
    def _note_tweet_results(self) -> dict | None:
        if 'note_tweet' in self._data and 'note_tweet_results' in self._data['note_tweet']:
            return self._data['note_tweet']['note_tweet_results']

    @property
    def full_text(self) -> str:
        note_tweet_results = self._note_tweet_results
        if note_tweet_results:
            return note_tweet_results['result']['text']
        return self.text

    @property
    def hashtags(self) -> list[str]:
        note_tweet_results = self._note_tweet_results
        if note_tweet_results:
            entity_set = note_tweet_results['result']['entity_set']
            hashtags = entity_set.get('hashtags', [])
        else:
            hashtags = self._legacy['entities'].get('hashtags', [])
        return [i['text'] for i in hashtags]

    @property
    def urls(self) -> list[str]:
        note_tweet_results = self._note_tweet_results
        if note_tweet_results:
            entity_set = note_tweet_results['result']['entity_set']
            return entity_set.get('urls')
        return self._legacy['entities'].get('urls')

    @property
    def community_note(self) -> dict | None:
        community_note_data = self._data.get('birdwatch_pivot')
        if community_note_data and 'note' in community_note_data:
            return {
                'id': community_note_data['note']['rest_id'],
                'text': community_note_data['subtitle']['text']
            }

    @property
    def _binding_values(self) -> dict | None:
        if (
            'card' in self._data and
            'legacy' in self._data['card'] and
            'binding_values' in self._data['card']['legacy']
        ):
            card_data = self._data['card']['legacy']['binding_values']
            if isinstance(card_data, list):
                return {
                    i.get('key'): i.get('value')
                    for i in card_data
                }

    @property
    def has_card(self) -> bool:
        return 'card' in self._data

    @property
    def thumbnail_title(self) -> str | None:
        binding_values = self._binding_values
        if (
            binding_values and
            'title' in binding_values and
            'string_value' in binding_values['title']
        ):
            return binding_values['title']['string_value']

    @property
    def thumbnail_url(self) -> str | None:
        binding_values = self._binding_values
        if (
            binding_values and
            'thumbnail_image_original' in binding_values and
            'image_value' in binding_values['thumbnail_image_original'] and
            'url' in binding_values['thumbnail_image_original']['image_value']
        ):
            return binding_values['thumbnail_image_original']['image_value']['url']

    @property
    def created_at_datetime(self) -> datetime:
        return timestamp_to_datetime(self.created_at)

    @property
    def poll(self) -> Poll:
        if (
            'card' in self._data and
            'legacy' in self._data['card'] and
            'name' in self._data['card']['legacy'] and
            self._data['card']['legacy']['name'].startswith('poll')
        ):
            return Poll.from_data(self._client, self._data['card'], self)

    @property
    def place(self) -> Place:
        if self._place_data:
            return Place.from_data(self._client, self._place_data)

    @property
    def media(self) -> list[MEDIA_TYPE]:
        media_data = self._legacy['entities'].get('media', [])
        m = []
        for entry in media_data:
            media_obj = _media_from_data(self._client, entry)
            if not media_obj:
                continue
            m.append(media_obj)
        return m

    async def delete(self) -> Response:
        """Deletes the tweet."""
        return await self._client.delete_tweet(self.id)

    async def favorite(self) -> Response:
        """Favorites the tweet."""
        return await self._client.favorite_tweet(self.id)

    async def unfavorite(self) -> Response:
        """Unfavorites the tweet."""
        return await self._client.unfavorite_tweet(self.id)

    async def retweet(self) -> Response:
        """Retweets the tweet."""
        return await self._client.retweet(self.id)

    async def delete_retweet(self) -> Response:
        """Deletes the retweet."""
        return await self._client.delete_retweet(self.id)

    async def bookmark(self) -> Response:
        """Adds the tweet to bookmarks."""
        return await self._client.bookmark_tweet(self.id)

    async def delete_bookmark(self) -> Response:
        """Removes the tweet from bookmarks."""
        return await self._client.delete_bookmark(self.id)

    async def reply(
        self,
        text: str = '',
        media_ids: list[str] | None = None,
        **kwargs
    ) -> Tweet:
        """Replies to the tweet."""
        return await self._client.create_tweet(
            text, media_ids, reply_to=self.id, **kwargs
        )

    async def get_retweeters(
        self, count: str = 40, cursor: str | None = None
    ) -> Result[User]:
        """Retrieve users who retweeted the tweet."""
        return await self._client.get_retweeters(self.id, count, cursor)

    async def get_favoriters(
        self, count: str = 40, cursor: str | None = None
    ) -> Result[User]:
        """Retrieve users who favorited the tweet."""
        return await self._client.get_favoriters(self.id, count, cursor)

    async def get_similar_tweets(self) -> list[Tweet]:
        """Retrieves tweets similar to the tweet (Twitter premium only)."""
        return await self._client.get_similar_tweets(self.id)

    async def get_quotes(
        self, count: int = 20, cursor: str | None = None
    ) -> Result[Tweet]:
        """Retrieve tweets that quote this tweet."""
        return await self._client.get_tweet_quotes(self.id, count, cursor)

    async def update(self) -> None:
        new = await self._client.get_tweet_by_id(self.id)
        self.__dict__.update(new.__dict__)

    def __repr__(self) -> str:
        return f'<Tweet id="{self.id}">'

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Tweet) and self.id == other.id


def tweet_from_data(client: Client, data: dict) -> Tweet:
    ':meta private:'
    tweet_data_ = find_dict(data, 'result', True)
    if not tweet_data_:
        return None
    tweet_data = tweet_data_[0]

    if tweet_data.get('__typename') == 'TweetTombstone':
        return None
    if 'tweet' in tweet_data:
        tweet_data = tweet_data['tweet']
    if 'core' not in tweet_data:
        return None
    user_results = tweet_data['core'].get('user_results')
    if not user_results or 'result' not in user_results:
        return None
    if 'legacy' not in tweet_data:
        return None

    user_data = tweet_data['core']['user_results']['result']
    return Tweet.from_data(client, tweet_data, User.from_data(client, user_data))


@dataclass(eq=False, repr=False)
class ScheduledTweet:
    _client: Client = field(repr=False, compare=False)
    id: str = ''
    execute_at: int = 0
    state: str = ''
    type: str = ''
    text: str = ''
    media: list = field(default_factory=list)

    @classmethod
    def from_data(cls, client: Client, data: dict) -> ScheduledTweet:
        return cls(
            _client=client,
            id=data['rest_id'],
            execute_at=data['scheduling_info']['execute_at'],
            state=data['scheduling_info']['state'],
            type=data['tweet_create_request']['type'],
            text=data['tweet_create_request']['status'],
            media=[i['media_info'] for i in data.get('media_entities', [])],
        )

    async def delete(self) -> Response:
        """Delete the scheduled tweet."""
        return await self._client.delete_scheduled_tweet(self.id)

    def __repr__(self) -> str:
        return f'<ScheduledTweet id="{self.id}">'


@dataclass(eq=False, repr=False)
class TweetTombstone:
    _client: Client = field(repr=False, compare=False)
    id: str = ''
    text: str = ''

    @classmethod
    def from_data(cls, client: Client, tweet_id: str, data: dict) -> TweetTombstone:
        return cls(
            _client=client,
            id=tweet_id,
            text=data['text']['text'],
        )

    def __repr__(self) -> str:
        return f'<TweetTombstone id="{self.id}">'

    def __eq__(self, other: object) -> bool:
        return isinstance(other, TweetTombstone) and self.id == other.id


@dataclass(eq=False, repr=False)
class Poll:
    """Represents a poll associated with a tweet."""
    _client: Client = field(repr=False, compare=False)
    tweet: Tweet | None = None
    id: str = ''
    name: str = ''
    choices: list[dict] = field(default_factory=list)
    duration_minutes: int = 0
    end_datetime_utc: str = ''
    last_updated_datetime_utc: str = ''
    counts_are_final: bool = False
    selected_choice: str | None = None

    @classmethod
    def from_data(
        cls, client: Client, data: dict, tweet: Tweet | None = None
    ) -> Poll:
        legacy = data['legacy']
        binding_values = legacy['binding_values']

        if isinstance(legacy['binding_values'], list):
            binding_values = {
                i.get('key'): i.get('value')
                for i in legacy['binding_values']
            }

        poll_name = legacy['name']
        choices_number = int(re.findall(
            r'poll(\d)choice_text_only', poll_name
        )[0])
        choices = []
        for i in range(1, choices_number + 1):
            choice_label = binding_values[f'choice{i}_label']
            choice_count = binding_values.get(f'choice{i}_count', {})
            choices.append({
                'number': str(i),
                'label': choice_label['string_value'],
                'count': choice_count.get('string_value', '0')
            })

        selected = None
        if 'selected_choice' in binding_values:
            selected = binding_values['selected_choice']['string_value']

        return cls(
            _client=client,
            tweet=tweet,
            id=data['rest_id'],
            name=poll_name,
            choices=choices,
            duration_minutes=int(binding_values['duration_minutes']['string_value']),
            end_datetime_utc=binding_values['end_datetime_utc']['string_value'],
            last_updated_datetime_utc=binding_values['last_updated_datetime_utc']['string_value'],
            counts_are_final=binding_values['counts_are_final']['boolean_value'],
            selected_choice=selected,
        )

    async def vote(self, selected_choice: str) -> Poll:
        """Vote on the poll with the specified selected choice."""
        return await self._client.vote(
            selected_choice, self.id, self.tweet.id, self.name
        )

    def __repr__(self) -> str:
        return f'<Poll id="{self.id}">'

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Poll) and self.id == other.id


@dataclass(eq=False, repr=False)
class CommunityNote:
    """Represents a community note."""
    _client: Client = field(repr=False, compare=False)
    id: str = ''
    text: str = ''
    misleading_tags: list[str] | None = None
    trustworthy_sources: bool | None = None
    helpful_tags: list[str] | None = None
    created_at: int | None = None
    can_appeal: bool | None = None
    appeal_status: str | None = None
    is_media_note: bool | None = None
    media_note_matches: str | None = None
    birdwatch_profile: dict | None = None
    tweet_id: str = ''

    @classmethod
    def from_data(cls, client: Client, data: dict) -> CommunityNote:
        data_v1 = data['data_v1']
        return cls(
            _client=client,
            id=data['rest_id'],
            text=data_v1['summary']['text'],
            misleading_tags=data_v1.get('misleading_tags'),
            trustworthy_sources=data_v1.get('trustworthy_sources'),
            helpful_tags=data.get('helpful_tags'),
            created_at=data.get('created_at'),
            can_appeal=data.get('can_appeal'),
            appeal_status=data.get('appeal_status'),
            is_media_note=data.get('is_media_note'),
            media_note_matches=data.get('media_note_matches'),
            birdwatch_profile=data.get('birdwatch_profile'),
            tweet_id=data['tweet_results']['result']['rest_id'],
        )

    async def update(self) -> None:
        new = await self._client.get_community_note(self.id)
        self.__dict__.update(new.__dict__)

    def __repr__(self) -> str:
        return f'<CommunityNote id="{self.id}">'

    def __eq__(self, other: object) -> bool:
        return isinstance(other, CommunityNote) and self.id == other.id

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import TYPE_CHECKING, Literal

from .utils import timestamp_to_datetime

if TYPE_CHECKING:
    from httpx import Response

    from .client.client import Client
    from .message import Message
    from .tweet import Tweet
    from .utils import Result


@dataclass(eq=False, repr=False)
class AccountAbout:
    """
    Represents data returned from Twitter's "About this account" panel.

    Attributes
    ----------
    id : :class:`str` | None
        User rest id.
    screen_name : :class:`str` | None
        The username of the account.
    name : :class:`str` | None
        The display name of the account.
    account_based_in : :class:`str` | None
        Region Twitter believes the account is based in.
    location_accurate : :class:`bool` | None
        Whether the location is considered accurate.
    affiliate_username : :class:`str` | None
        Linked affiliate username, if present.
    source : :class:`str` | None
        How the account source was determined.
    username_changes : :class:`int` | None
        Number of username changes Twitter recorded.
    username_last_changed_at : :class:`int` | None
        Timestamp in milliseconds of the last username change.
    is_identity_verified : :class:`bool` | None
        Whether the account has identity verification.
    verified_since_msec : :class:`int` | None
        Timestamp in milliseconds since verification.
    """
    id: str | None = None
    rest_id: str | None = None
    screen_name: str | None = None
    name: str | None = None
    account_based_in: str | None = None
    location_accurate: bool | None = None
    affiliate_username: str | None = None
    source: str | None = None
    username_changes: int | None = None
    username_last_changed_at: int | None = None
    is_identity_verified: bool | None = None
    verified_since_msec: int | None = None

    @classmethod
    def from_data(cls, data: dict) -> AccountAbout:
        about = data.get('about_profile') or {}
        core = data.get('core') or {}
        verification = data.get('verification_info') or {}
        reason = verification.get('reason') or {}
        username_changes = about.get('username_changes') or {}

        rest_id = data.get('rest_id')
        return cls(
            id=rest_id,
            rest_id=rest_id,
            screen_name=core.get('screen_name'),
            name=core.get('name'),
            account_based_in=about.get('account_based_in'),
            location_accurate=about.get('location_accurate'),
            affiliate_username=about.get('affiliate_username'),
            source=about.get('source'),
            username_changes=_to_int(username_changes.get('count')),
            username_last_changed_at=_to_int(
                username_changes.get('last_changed_at_msec')
            ),
            is_identity_verified=verification.get('is_identity_verified'),
            verified_since_msec=_to_int(reason.get('verified_since_msec')),
        )

    def __repr__(self) -> str:
        return f'<AccountAbout id="{self.id}" screen_name="{self.screen_name}">'


def _to_int(value) -> int | None:
    if value is None:
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


@dataclass(eq=False, repr=False)
class User:
    """
    Attributes
    ----------
    id : :class:`str`
        The unique identifier of the user.
    created_at : :class:`str`
        The date and time when the user account was created.
    name : :class:`str`
        The user's name.
    screen_name : :class:`str`
        The user's screen name.
    profile_image_url : :class:`str`
        The URL of the user's profile image (HTTPS version).
    profile_banner_url : :class:`str`
        The URL of the user's profile banner.
    url : :class:`str`
        The user's URL.
    location : :class:`str`
        The user's location information.
    description : :class:`str`
        The user's profile description.
    description_urls : :class:`list`
        URLs found in the user's profile description.
    urls : :class:`list`
        URLs associated with the user.
    pinned_tweet_ids : :class:`str`
        The IDs of tweets that the user has pinned to their profile.
    is_blue_verified : :class:`bool`
        Indicates if the user is verified with a blue checkmark.
    verified : :class:`bool`
        Indicates if the user is verified.
    possibly_sensitive : :class:`bool`
        Indicates if the user's content may be sensitive.
    can_dm : :class:`bool`
        Indicates whether the user can receive direct messages.
    can_media_tag : :class:`bool`
        Indicates whether the user can be tagged in media.
    want_retweets : :class:`bool`
        Indicates if the user wants retweets.
    default_profile : :class:`bool`
        Indicates if the user has the default profile.
    default_profile_image : :class:`bool`
        Indicates if the user has the default profile image.
    has_custom_timelines : :class:`bool`
        Indicates if the user has custom timelines.
    followers_count : :class:`int`
        The count of followers.
    fast_followers_count : :class:`int`
        The count of fast followers.
    normal_followers_count : :class:`int`
        The count of normal followers.
    following_count : :class:`int`
        The count of users the user is following.
    favourites_count : :class:`int`
        The count of favorites or likes.
    listed_count : :class:`int`
        The count of lists the user is a member of.
    media_count : :class:`int`
        The count of media items associated with the user.
    statuses_count : :class:`int`
        The count of tweets.
    is_translator : :class:`bool`
        Indicates if the user is a translator.
    translator_type : :class:`str`
        The type of translator.
    withheld_in_countries : list[:class:`str`]
        Countries where the user's content is withheld.
    protected : :class:`bool`
        Indicates if the user's tweets are protected.
    profile_image_shape : :class:`str`
        The shape of the profile image ('Circle' or 'Square').
    creator_subscriptions_count : :class:`int`
        The count of creator subscriptions.
    professional : :class:`dict` | None
        Professional account info (category, professional_type).
    highlights_info : :class:`dict` | None
        Highlights info (can_highlight_tweets, highlighted_tweets).
    affiliates_highlighted_label : :class:`dict` | None
        Affiliate badge information.
    verification_info : :class:`dict` | None
        Detailed verification information.
    super_follow_eligible : :class:`bool`
        Whether the user is eligible for super follows.
    super_following : :class:`bool`
        Whether you are super following this user.
    super_followed_by : :class:`bool`
        Whether this user super follows you.
    follow_request_sent : :class:`bool`
        Whether a follow request has been sent.
    notifications : :class:`bool`
        Whether notifications are enabled for this user.
    profile_interstitial_type : :class:`str`
        The type of profile interstitial.
    following : :class:`bool`
        Whether you are following this user.
    followed_by : :class:`bool`
        Whether this user follows you.
    blocking : :class:`bool`
        Whether you are blocking this user.
    blocked_by : :class:`bool`
        Whether this user blocks you.
    muting : :class:`bool`
        Whether you are muting this user.
    """
    _client: Client = field(repr=False, compare=False)
    id: str = ''
    created_at: str = ''
    name: str = ''
    screen_name: str = ''
    profile_image_url: str = ''
    profile_banner_url: str | None = None
    url: str | None = None
    location: str = ''
    description: str = ''
    description_urls: list = field(default_factory=list)
    urls: list | None = None
    pinned_tweet_ids: list[str] = field(default_factory=list)
    is_blue_verified: bool = False
    verified: bool = False
    possibly_sensitive: bool = False
    can_dm: bool = False
    can_media_tag: bool = False
    want_retweets: bool = False
    default_profile: bool = False
    default_profile_image: bool = False
    has_custom_timelines: bool = False
    followers_count: int = 0
    fast_followers_count: int = 0
    normal_followers_count: int = 0
    following_count: int = 0
    favourites_count: int = 0
    listed_count: int = 0
    media_count: int = 0
    statuses_count: int = 0
    is_translator: bool = False
    translator_type: str = ''
    withheld_in_countries: list[str] = field(default_factory=list)
    protected: bool = False
    profile_image_shape: str = ''
    creator_subscriptions_count: int = 0
    professional: dict | None = None
    highlights_info: dict | None = None
    affiliates_highlighted_label: dict | None = None
    verification_info: dict | None = None
    super_follow_eligible: bool = False
    super_following: bool = False
    super_followed_by: bool = False
    follow_request_sent: bool = False
    notifications: bool = False
    profile_interstitial_type: str = ''
    following: bool = False
    followed_by: bool = False
    blocking: bool = False
    blocked_by: bool = False
    muting: bool = False

    @classmethod
    def from_data(cls, client: Client, data: dict) -> User:
        legacy = data.get('legacy', {})
        core = data.get('core', {})
        avatar = data.get('avatar', {})
        location_data = data.get('location', {})
        dm_perms = data.get('dm_permissions', {})
        verification = data.get('verification', {})
        privacy = data.get('privacy', {})
        relationship = data.get('relationship_perspectives', {})

        return cls(
            _client=client,
            id=data.get('rest_id', ''),
            created_at=legacy.get('created_at') or core.get('created_at', ''),
            name=legacy.get('name') or core.get('name', ''),
            screen_name=legacy.get('screen_name') or core.get('screen_name', ''),
            profile_image_url=(
                legacy.get('profile_image_url_https')
                or avatar.get('image_url', '')
            ),
            profile_banner_url=legacy.get('profile_banner_url'),
            url=legacy.get('url'),
            location=(
                legacy.get('location')
                if 'location' in legacy
                else location_data.get('location', '')
            ),
            description=legacy.get('description', ''),
            description_urls=legacy.get('entities', {}).get('description', {}).get('urls', []),
            urls=legacy.get('entities', {}).get('url', {}).get('urls'),
            pinned_tweet_ids=legacy.get('pinned_tweet_ids_str', []),
            is_blue_verified=data.get('is_blue_verified', False),
            verified=(
                legacy.get('verified')
                if 'verified' in legacy
                else verification.get('verified', False)
            ),
            possibly_sensitive=legacy.get('possibly_sensitive', False),
            can_dm=(
                legacy.get('can_dm')
                if 'can_dm' in legacy
                else dm_perms.get('can_dm', False)
            ),
            can_media_tag=legacy.get('can_media_tag', False),
            want_retweets=legacy.get('want_retweets', False),
            default_profile=legacy.get('default_profile', False),
            default_profile_image=legacy.get('default_profile_image', False),
            has_custom_timelines=legacy.get('has_custom_timelines', False),
            followers_count=legacy.get('followers_count', 0),
            fast_followers_count=legacy.get('fast_followers_count', 0),
            normal_followers_count=legacy.get('normal_followers_count', 0),
            following_count=legacy.get('friends_count', 0),
            favourites_count=legacy.get('favourites_count', 0),
            listed_count=legacy.get('listed_count', 0),
            media_count=legacy.get('media_count', 0),
            statuses_count=legacy.get('statuses_count', 0),
            is_translator=legacy.get('is_translator', False),
            translator_type=legacy.get('translator_type', ''),
            withheld_in_countries=legacy.get('withheld_in_countries', []),
            protected=(
                legacy.get('protected')
                if 'protected' in legacy
                else privacy.get('protected', False)
            ),
            profile_image_shape=data.get('profile_image_shape', ''),
            creator_subscriptions_count=data.get('creator_subscriptions_count', 0),
            professional=data.get('professional'),
            highlights_info=data.get('highlights_info'),
            affiliates_highlighted_label=data.get('affiliates_highlighted_label'),
            verification_info=data.get('verification_info'),
            super_follow_eligible=data.get('super_follow_eligible', False),
            super_following=data.get('super_following', False),
            super_followed_by=data.get('super_followed_by', False),
            follow_request_sent=(
                legacy.get('follow_request_sent')
                if 'follow_request_sent' in legacy
                else data.get('follow_request_sent', False)
            ),
            notifications=legacy.get('notifications', False),
            profile_interstitial_type=legacy.get('profile_interstitial_type', ''),
            following=relationship.get('following', False),
            followed_by=relationship.get('followed_by', False),
            blocking=relationship.get('blocking', False),
            blocked_by=relationship.get('blocked_by', False),
            muting=relationship.get('muting', False),
        )

    @property
    def created_at_datetime(self) -> datetime:
        return timestamp_to_datetime(self.created_at)

    async def get_tweets(
        self,
        tweet_type: Literal['Tweets', 'Replies', 'Media', 'Likes'],
        count: int = 40,
    ) -> Result[Tweet]:
        """
        Retrieves the user's tweets.

        Parameters
        ----------
        tweet_type : {'Tweets', 'Replies', 'Media', 'Likes'}
            The type of tweets to retrieve.
        count : :class:`int`, default=40
            The number of tweets to retrieve.

        Returns
        -------
        Result[:class:`Tweet`]
            A Result object containing a list of `Tweet` objects.
        """
        return await self._client.get_user_tweets(self.id, tweet_type, count)

    async def get_about(self) -> AccountAbout:
        """Retrieves the "About this account" information for the user."""
        return await self._client.get_user_about(self.screen_name)

    async def follow(self) -> Response:
        """Follows the user."""
        return await self._client.follow_user(self.id)

    async def unfollow(self) -> Response:
        """Unfollows the user."""
        return await self._client.unfollow_user(self.id)

    async def block(self) -> Response:
        """Blocks the user."""
        return await self._client.block_user(self.id)

    async def unblock(self) -> Response:
        """Unblocks the user."""
        return await self._client.unblock_user(self.id)

    async def mute(self) -> Response:
        """Mutes the user."""
        return await self._client.mute_user(self.id)

    async def unmute(self) -> Response:
        """Unmutes the user."""
        return await self._client.unmute_user(self.id)

    async def get_followers(self, count: int = 20) -> Result[User]:
        """Retrieves a list of followers for the user."""
        return await self._client.get_user_followers(self.id, count)

    async def get_verified_followers(self, count: int = 20) -> Result[User]:
        """Retrieves a list of verified followers for the user."""
        return await self._client.get_user_verified_followers(self.id, count)

    async def get_followers_you_know(self, count: int = 20) -> Result[User]:
        """Retrieves a list of followers whom the user might know."""
        return await self._client.get_user_followers_you_know(self.id, count)

    async def get_following(self, count: int = 20) -> Result[User]:
        """Retrieves a list of users whom the user is following."""
        return await self._client.get_user_following(self.id, count)

    async def get_subscriptions(self, count: int = 20) -> Result[User]:
        """Retrieves a list of users whom the user is subscribed to."""
        return await self._client.get_user_subscriptions(self.id, count)

    async def get_latest_followers(
        self, count: int | None = None, cursor: str | None = None
    ) -> Result[User]:
        """Retrieves the latest followers. Max count: 200."""
        return await self._client.get_latest_followers(
            self.id, count=count, cursor=cursor
        )

    async def get_latest_friends(
        self, count: int | None = None, cursor: str | None = None
    ) -> Result[User]:
        """Retrieves the latest friends (following users). Max count: 200."""
        return await self._client.get_latest_friends(
            self.id, count=count, cursor=cursor
        )

    async def send_dm(
        self, text: str, media_id: str = None, reply_to=None
    ) -> Message:
        """
        Send a direct message to the user.

        Parameters
        ----------
        text : :class:`str`
            The text content of the direct message.
        media_id : :class:`str`, default=None
            The media ID associated with any media content
            to be included in the message.
        reply_to : :class:`str`, default=None
            Message ID to reply to.

        Returns
        -------
        :class:`Message`
            `Message` object containing information about the message sent.
        """
        return await self._client.send_dm(self.id, text, media_id, reply_to)

    async def get_dm_history(self, max_id: str = None) -> Result[Message]:
        """Retrieves the DM conversation history with the user."""
        return await self._client.get_dm_history(self.id, max_id)

    async def get_highlights_tweets(
        self, count: int = 20, cursor: str | None = None
    ) -> Result[Tweet]:
        """Retrieves highlighted tweets from the user's timeline."""
        return await self._client.get_user_highlights_tweets(self.id, count, cursor)

    async def update(self) -> None:
        new = await self._client.get_user_by_id(self.id)
        self.__dict__.update(new.__dict__)

    def __repr__(self) -> str:
        return f'<User id="{self.id}">'

    def __eq__(self, other: object) -> bool:
        return isinstance(other, User) and self.id == other.id

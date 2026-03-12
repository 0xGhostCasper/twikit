"""Integration tests for tweet-related read-only endpoints."""

import pytest

from twikit.client.client import Client
from twikit.errors import NotFound, TooManyRequests
from twikit.user import User
from twikit.tweet import Tweet
from twikit.utils import Result

from .constants import ELON_USER_ID, ELON_TWEET_ID


class TestTweetDetail:
    @pytest.mark.asyncio
    async def test_returns_tweet(self, client: Client):
        tweet = await client.get_tweet_by_id(ELON_TWEET_ID)
        assert isinstance(tweet, Tweet)
        assert tweet.id == ELON_TWEET_ID

    @pytest.mark.asyncio
    async def test_tweet_has_text(self, client: Client):
        tweet = await client.get_tweet_by_id(ELON_TWEET_ID)
        assert tweet.text is not None
        assert len(tweet.text) > 0

    @pytest.mark.asyncio
    async def test_fields_populated(self, client: Client):
        """Verify key Tweet fields are populated with real data."""
        tweet = await client.get_tweet_by_id(ELON_TWEET_ID)
        # Identity
        assert tweet.id != ''
        assert tweet.created_at != ''
        assert tweet.text != ''
        assert tweet.full_text != ''
        assert tweet.lang != ''
        # Author
        assert isinstance(tweet.user, User)
        assert tweet.user.id != ''
        assert tweet.user.screen_name != ''
        # Counters — should be ints, not None
        assert isinstance(tweet.reply_count, int)
        assert isinstance(tweet.retweet_count, int)
        assert isinstance(tweet.favorite_count, int)
        assert isinstance(tweet.quote_count, int)
        assert isinstance(tweet.bookmark_count, int)
        # Booleans
        assert isinstance(tweet.favorited, bool)
        assert isinstance(tweet.retweeted, bool)
        assert isinstance(tweet.bookmarked, bool)
        assert isinstance(tweet.is_quote_status, bool)
        assert isinstance(tweet.is_translatable, bool)
        # New fields
        assert tweet.source is not None and tweet.source != ''
        assert tweet.conversation_id is not None and tweet.conversation_id != ''
        # View count (should be present on any public tweet)
        assert tweet.view_count is not None or tweet.view_count_state is not None


class TestTweetsByIds:
    @pytest.mark.asyncio
    async def test_returns_tweets(self, client: Client):
        tweets = await client.get_tweets_by_ids([ELON_TWEET_ID])
        assert isinstance(tweets, list)
        assert len(tweets) >= 1


class TestTweetEditHistory:
    @pytest.mark.asyncio
    async def test_returns_list(self, client: Client):
        history = await client.get_tweet_edit_history(ELON_TWEET_ID)
        assert isinstance(history, list)
        # Even unedited tweets should return at least the original version


class TestUserTweets:
    @pytest.mark.asyncio
    async def test_tweets(self, client: Client):
        tweets = await client.get_user_tweets(ELON_USER_ID, "Tweets", count=5)
        assert isinstance(tweets, Result)
        assert len(tweets) > 0
        assert all(isinstance(t, Tweet) for t in tweets)

    @pytest.mark.asyncio
    async def test_replies(self, client: Client):
        try:
            tweets = await client.get_user_tweets(ELON_USER_ID, "Replies", count=5)
        except NotFound:
            pytest.skip("UserTweetsAndReplies returned transient 404")
        assert isinstance(tweets, Result)
        assert len(tweets) > 0

    @pytest.mark.asyncio
    async def test_media(self, client: Client):
        tweets = await client.get_user_tweets(ELON_USER_ID, "Media", count=5)
        assert isinstance(tweets, Result)
        assert len(tweets) > 0

    @pytest.mark.asyncio
    async def test_likes(self, client: Client):
        tweets = await client.get_user_tweets(ELON_USER_ID, "Likes", count=5)
        assert isinstance(tweets, Result)
        # Likes may be hidden, just check it returns a Result


class TestUserHighlightsTweets:
    @pytest.mark.asyncio
    async def test_returns_result(self, client: Client):
        tweets = await client.get_user_highlights_tweets(ELON_USER_ID, count=5)
        assert isinstance(tweets, Result)


class TestUserArticles:
    @pytest.mark.asyncio
    async def test_returns_result(self, client: Client):
        tweets = await client.get_user_articles(ELON_USER_ID, count=5)
        assert isinstance(tweets, Result)


class TestSearchTweet:
    @pytest.mark.asyncio
    async def test_top(self, client: Client):
        try:
            tweets = await client.search_tweet("python programming", "Top", count=5)
        except (TooManyRequests, NotFound):
            pytest.skip("Rate limited or transient 404")
        assert isinstance(tweets, Result)
        assert len(tweets) > 0
        assert all(isinstance(t, Tweet) for t in tweets)

    @pytest.mark.asyncio
    async def test_latest(self, client: Client):
        try:
            tweets = await client.search_tweet("python", "Latest", count=5)
        except (TooManyRequests, NotFound):
            pytest.skip("Rate limited or transient 404")
        assert isinstance(tweets, Result)
        assert len(tweets) > 0


class TestSimilarTweets:
    @pytest.mark.asyncio
    async def test_returns_list(self, client: Client):
        tweets = await client.get_similar_tweets(ELON_TWEET_ID)
        assert isinstance(tweets, list)
        # May be empty if premium-only, but should not error


class TestRetweeters:
    @pytest.mark.asyncio
    async def test_returns_users(self, client: Client):
        users = await client.get_retweeters(ELON_TWEET_ID, count=5)
        assert isinstance(users, Result)
        assert len(users) > 0
        assert all(isinstance(u, User) for u in users)


class TestFavoriters:
    @pytest.mark.asyncio
    async def test_returns_users(self, client: Client):
        users = await client.get_favoriters(ELON_TWEET_ID, count=5)
        assert isinstance(users, Result)
        # Favoriters may be restricted; just verify the Result type
        if len(users) > 0:
            assert all(isinstance(u, User) for u in users)

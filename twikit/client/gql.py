from __future__ import annotations

from typing import TYPE_CHECKING

from ..constants import (
    ABOUT_ACCOUNT_FEATURES,
    ARTICLE_FEATURES,
    AUDIO_SPACE_FEATURES,
    BIRDWATCH_NOTES_FEATURES,
    BIRDWATCH_PUBLIC_DATA_FEATURES,
    BOOKMARK_FOLDER_TIMELINE_FEATURES,
    COMMUNITY_NOTE_FEATURES,
    COMMUNITY_TWEETS_FEATURES,
    DOMAIN,
    FEATURES,
    JOIN_COMMUNITY_FEATURES,
    LIST_FEATURES,
    NOTE_TWEET_FEATURES,
    SIMILAR_POSTS_FEATURES,
    TIMELINE_FEATURES,
    TWEET_RESULT_BY_REST_ID_FEATURES,
    TWEET_RESULTS_BY_REST_IDS_FEATURES,
    USER_FEATURES,
    USER_HIGHLIGHTS_TWEETS_FEATURES
)
from ..utils import flatten_params, get_query_id

if TYPE_CHECKING:
    from ..guest.client import GuestClient
    from .client import Client

    ClientType = Client | GuestClient


class Endpoint:
    @staticmethod
    def url(path):
        return f'https://{DOMAIN}/i/api/graphql/{path}'

    SEARCH_TIMELINE = url('OFvapAUD5xrCWn9xcD0A6A/SearchTimeline')
    SIMILAR_POSTS = url('pJaa5NFs5SrwntuB739Ghg/SimilarPosts')
    CREATE_NOTE_TWEET = url('4e-YHiuiNDaITMxa29cerw/CreateNoteTweet')
    CREATE_TWEET = url('RXKQMYyEqEjGgWpcSP6LBw/CreateTweet')
    CREATE_SCHEDULED_TWEET = url('LCVzRQGxOaGnOnYH01NQXg/CreateScheduledTweet')
    DELETE_TWEET = url('nxpZCY2K-I6QoFHAHeojFQ/DeleteTweet')
    USER_BY_SCREEN_NAME = url('pLsOiyHJ1eFwPJlNmLp4Bg/UserByScreenName')
    USER_BY_REST_ID = url('FJ17ptkJuQAZGWilcySi5w/UserByRestId')
    USERS_BY_REST_IDS = url('8OKmcyotfczJb44QTTu5tQ/UsersByRestIds')
    USERS_BY_SCREEN_NAMES = url('Ats5GnHiQxT-Nnzw09raMw/UsersByScreenNames')
    ABOUT_ACCOUNT = url('zs_jFPFT78rBpXv9Z3U2YQ/AboutAccountQuery')
    TWEET_DETAIL = url('1eAGnXrtvTBUePpQfTXZzA/TweetDetail')
    TWEET_RESULT_BY_REST_ID = url('tcA4FFMIjGSDv48Cu_FS5Q/TweetResultByRestId')
    TWEET_EDIT_HISTORY = url('Ziq1ud3_9eS5sGVPr-0C2g/TweetEditHistory')
    FETCH_SCHEDULED_TWEETS = url('cmwoO7AWw5zCpd8TaPFQHg/FetchScheduledTweets')
    DELETE_SCHEDULED_TWEET = url('CTOVqej0JBXAZSwkp1US0g/DeleteScheduledTweet')
    RETWEETERS = url('u0enVmmny6cjmIbco9yrUQ/Retweeters')
    FAVORITERS = url('Fw6QQz0BKGh7TzDtM0wIZQ/Favoriters')
    FETCH_COMMUNITY_NOTE = url('iP6eDL64fDmYURNVi14Hhw/BirdwatchFetchOneNote')
    USER_TWEETS = url('5M8UuGym7_VyIEggQIyjxQ/UserTweets')
    USER_TWEETS_AND_REPLIES = url('C3YpYjTsQZznJIdyy2JKuQ/UserTweetsAndReplies')
    USER_MEDIA = url('mWo2yKjZEaqK7_vKox_67Q/UserMedia')
    USER_LIKES = url('dv5-II7_Bup_PHish7p6fw/Likes')
    USER_HIGHLIGHTS_TWEETS = url('_2SslPATDKMdL4SKoB1mGA/UserHighlightsTweets')
    USER_ARTICLES_TWEETS = url('40vO56ZJWVfYSnaNQEDaug/UserArticlesTweets')
    HOME_TIMELINE = url('gXtpuBkna6SRLFFKaT2OTg/HomeTimeline')
    HOME_LATEST_TIMELINE = url('JVzDMxTXbT9bRXSpUR16CQ/HomeLatestTimeline')
    FAVORITE_TWEET = url('lI07N6Otwv1PhnEgXILM7A/FavoriteTweet')
    UNFAVORITE_TWEET = url('ZYKSe-w7KEslx3JhSIk5LA/UnfavoriteTweet')
    CREATE_RETWEET = url('mbRO74GrOvSfRcJnlMapnQ/CreateRetweet')
    DELETE_RETWEET = url('ZyZigVsNiFO6v1dEks1eWg/DeleteRetweet')
    CREATE_BOOKMARK = url('aoDbu3RHznuiSkQ9aNM67Q/CreateBookmark')
    BOOKMARK_TO_FOLDER = url('4KHZvvNbHNf07bsgnL9gWA/bookmarkTweetToFolder')
    DELETE_BOOKMARK = url('Wlmlj2-xzyS1GN3a6cj-mQ/DeleteBookmark')
    BOOKMARKS = url('bujk3QTuew1W0yZzP3zDNA/Bookmarks')
    BOOKMARK_FOLDER_TIMELINE = url('DzN2eA2NhBdW6XRbxnSyNg/BookmarkFolderTimeline')
    BOOKMARKS_ALL_DELETE = url('skiACZKC1GDYli-M8RzEPQ/BookmarksAllDelete')
    BOOKMARK_FOLDERS_SLICE = url('i78YDd0Tza-dV4SYs58kRg/BookmarkFoldersSlice')
    EDIT_BOOKMARK_FOLDER = url('a6kPp1cS1Dgbsjhapz1PNw/EditBookmarkFolder')
    DELETE_BOOKMARK_FOLDER = url('2UTTsO-6zs93XqlEUZPsSg/DeleteBookmarkFolder')
    CREATE_BOOKMARK_FOLDER = url('6Xxqpq8TM_CREYiuof_h5w/createBookmarkFolder')
    FOLLOWERS = url('8sIMO3RbSCdvk2QzxcPpIg/Followers')
    BLUE_VERIFIED_FOLLOWERS = url('ZH16zF8R8YAJAAfIGbef9A/BlueVerifiedFollowers')
    FOLLOWERS_YOU_KNOW = url('fBi9FJP1haBdGoZuVfZVzQ/FollowersYouKnow')
    FOLLOWING = url('lEJDj0bTio9-s0hSukCD9Q/Following')
    USER_CREATOR_SUBSCRIPTIONS = url('3bO__PTHgSxzcKGi2PBiNQ/UserCreatorSubscriptions')
    USER_DM_REACTION_MUTATION_ADD_MUTATION = url('VyDyV9pC2oZEj6g52hgnhA/useDMReactionMutationAddMutation')
    USER_DM_REACTION_MUTATION_REMOVE_MUTATION = url('bV_Nim3RYHsaJwMkTXJ6ew/useDMReactionMutationRemoveMutation')
    DM_MESSAGE_DELETE_MUTATION = url('BJ6DtxA2llfjnRoRjaiIiw/DMMessageDeleteMutation')
    ADD_PARTICIPANTS_MUTATION = url('oBwyQ0_xVbAQ8FAyG0pCRA/AddParticipantsMutation')
    CREATE_LIST = url('QXil-VE8uEJPfUKFiO36Bg/CreateList')
    EDIT_LIST_BANNER = url('buH0utnb8bSZUo8RSWRI8Q/EditListBanner')
    DELETE_LIST_BANNER = url('-oOeYNihEO1SUYJrdIC0wA/DeleteListBanner')
    UPDATE_LIST = url('qE2QVWL84jqa6CmH-m-D3w/UpdateList')
    LIST_ADD_MEMBER = url('nAi8BAjn1xQOyCH0hWZpPA/ListAddMember')
    LIST_REMOVE_MEMBER = url('pGMiwtWRMx08r4XCYxai4Q/ListRemoveMember')
    LIST_MANAGEMENT_PACE_TIMELINE = url('3HVC3dmZ7C-zFXkps66_8g/ListsManagementPageTimeline')
    LIST_BY_REST_ID = url('bSE1lqLBnovM86uu4p4Iqg/ListByRestId')
    LIST_LATEST_TWEETS_TIMELINE = url('gNXkRRRV67cSRJkmpgGPnA/ListLatestTweetsTimeline')
    LIST_MEMBERS = url('fqecRWCF4EcSAOs5yXh7Ig/ListMembers')
    LIST_SUBSCRIBERS = url('iQIPCAepWJ4v9kgfmNiPnQ/ListSubscribers')
    SEARCH_COMMUNITY = url('daVUkhfHn7-Z8llpYVKJSw/CommunitiesSearchQuery')
    COMMUNITY_QUERY = url('lUBKrilodgg9Nikaw3cIiA/CommunityQuery')
    COMMUNITY_MEDIA_TIMELINE = url('wD2wnGtnd3Fz0z_wIT1S3Q/CommunityMediaTimeline')
    COMMUNITY_TWEETS_TIMELINE = url('gE30Mj3l6o4l8ks4BZ1fqA/CommunityTweetsTimeline')
    COMMUNITIES_MAIN_PAGE_TIMELINE = url('7dpsrKDlRGRIYNTP8URNEQ/CommunitiesMainPageTimeline')
    JOIN_COMMUNITY = url('ksbhXZQU1A6YPvuWSRnCTQ/JoinCommunity')
    LEAVE_COMMUNITY = url('-uBu9jQ1bQz5xAatKuRU5g/LeaveCommunity')
    REQUEST_TO_JOIN_COMMUNITY = url('1G8LYzgrA5X1RXst5ccSmw/RequestToJoinCommunity')
    MEMBERS_SLICE_TIMELINE_QUERY = url('KDAssJ5lafCy-asH4wm1dw/membersSliceTimeline_Query')
    MODERATORS_SLICE_TIMELINE_QUERY = url('9KI_r8e-tgp3--N5SZYVjg/moderatorsSliceTimeline_Query')
    COMMUNITY_TWEET_SEARCH_MODULE_QUERY = url('5341rmzzvdjqfmPKfoHUBw/CommunityTweetSearchModuleQuery')
    TWEET_RESULTS_BY_REST_IDS = url('M441-7OPnT7o_TzVwteU3Q/TweetResultsByRestIds')
    AUDIO_SPACE_BY_ID = url('84Nq0w42k2OT9eD69mUUhg/AudioSpaceById')
    AUDIO_SPACE_SEARCH = url('NTq79TuSz6fHj8lQaferJw/AudioSpaceSearch')
    TREND_HISTORY = url('LftLG10fy08uXU-gVzBuog/TrendHistory')
    TREND_RELEVANT_USERS = url('ciyWJk807WubnL17fdpYOw/TrendRelevantUsers')
    TOPIC_BY_REST_ID = url('4OUZZOonV2h60I0wdlQb_w/TopicByRestId')
    TOPIC_LANDING_PAGE = url('S7VFVaSgxtfDtkRh0B1PfA/TopicLandingPage')
    ARTICLE_RESULT_BY_REST_ID = url('i1GUp3zg_bzMUQdEuT3XPg/ArticleEntityResultByRestId')
    BROADCAST_QUERY = url('gIcysSvC6v8JF9-OlCRXUA/BroadcastQuery')
    BIRDWATCH_FETCH_NOTES = url('C7r8eSyiH-iziuuCqQrzMA/BirdwatchFetchNotes')
    BIRDWATCH_FETCH_SOURCE_LINK_SLICE = url('qqJ7slrA6HP_mUwYLykuVg/BirdwatchFetchSourceLinkSlice')
    BIRDWATCH_FETCH_GLOBAL_TIMELINE = url('EQ9zXLXMB5lCQJWaXpvARw/BirdwatchFetchGlobalTimeline')
    BIRDWATCH_FETCH_PUBLIC_DATA = url('T4Qdev0aBeS9tK9v4TkgQg/BirdwatchFetchPublicData')
    LIST_RANKED_TWEETS_TIMELINE = url('fOxHc7rBx_w5u3Ady0xNPg/ListRankedTweetsTimeline')
    LIST_SEARCH_TIMELINE = url('ipVCKPHN6XYQYYyglh7crg/ListSearchTimeline')
    COMMUNITIES_EXPLORE_TIMELINE = url('fwSasLCjsp5uhRAy22C0rw/CommunitiesExploreTimeline')
    COMMUNITY_HASHTAGS_TIMELINE = url('XoelkPhkr6E0gDwz94TGDQ/CommunityHashtagsTimeline')
    GENERIC_TIMELINE_BY_ID = url('fZ345bHV4wktguCL33ghHQ/GenericTimelineById')


class GQLClient:
    def __init__(self, base: ClientType) -> None:
        self.base = base

    async def gql_get(
        self,
        url: str,
        variables: dict,
        features: dict | None = None,
        headers: dict | None = None,
        extra_params: dict | None = None,
        **kwargs
    ):
        params = {'variables': variables}
        if features is not None:
            params['features'] = features
        if extra_params is not None:
            params |= extra_params
        if headers is None:
            headers = self.base._base_headers
        return await self.base.get(url, params=flatten_params(params), headers=headers, **kwargs)

    async def gql_post(
        self,
        url: str,
        variables: dict,
        features: dict | None = None,
        headers: dict | None = None,
        extra_data: dict | None = None,
        **kwargs
    ):
        data = {'variables': variables, 'queryId': get_query_id(url)}
        if features is not None:
            data['features'] = features
        if extra_data is not None:
            data |= extra_data
        if headers is None:
            headers = self.base._base_headers
        return await self.base.post(url, json=data, headers=headers, **kwargs)

    async def search_timeline(
        self,
        query: str,
        product: str,
        count: int,
        cursor: str | None
    ):
        variables = {
            'rawQuery': query,
            'count': count,
            'querySource': 'typed_query',
            'product': product,
            'includePromotedContent': False
        }
        if cursor is not None:
            variables['cursor'] = cursor
        params = {
            'fieldToggles': {'withArticleRichContentState': False}
        }
        return await self.gql_get(
            Endpoint.SEARCH_TIMELINE, variables, FEATURES, extra_params=params
        )

    async def similar_posts(self, tweet_id: str):
        variables = {'tweet_id': tweet_id}
        return await self.gql_get(
            Endpoint.SIMILAR_POSTS,
            variables,
            SIMILAR_POSTS_FEATURES
        )

    async def create_tweet(
        self, is_note_tweet, text, media_entities,
        poll_uri, reply_to, attachment_url,
        community_id, share_with_followers,
        richtext_options, edit_tweet_id, limit_mode
    ):
        variables = {
            'tweet_text': text,
            'dark_request': False,
            'media': {
                'media_entities': media_entities,
                'possibly_sensitive': False
            },
            'semantic_annotation_ids': [],
        }

        if poll_uri is not None:
            variables['card_uri'] = poll_uri

        if reply_to is not None:
            variables['reply'] = {
                'in_reply_to_tweet_id': reply_to,
                'exclude_reply_user_ids': []
            }

        if limit_mode is not None:
            variables['conversation_control'] = {'mode': limit_mode}

        if attachment_url is not None:
            variables['attachment_url'] = attachment_url

        if community_id is not None:
            variables['semantic_annotation_ids'] = [{
                'entity_id': community_id,
                'group_id': '8',
                'domain_id': '31'
            }]
            variables['broadcast'] = share_with_followers

        if richtext_options is not None:
            is_note_tweet = True
            variables['richtext_options'] = {
                'richtext_tags': richtext_options
            }
        if edit_tweet_id is not None:
            variables['edit_options'] = {
                'previous_tweet_id': edit_tweet_id
            }

        if is_note_tweet:
            endpoint = Endpoint.CREATE_NOTE_TWEET
            features = NOTE_TWEET_FEATURES
        else:
            endpoint = Endpoint.CREATE_TWEET
            features = FEATURES
        return await self.gql_post(endpoint, variables, features)

    async def create_scheduled_tweet(self, scheduled_at, text, media_ids) -> str:
        variables = {
            'post_tweet_request': {
            'auto_populate_reply_metadata': False,
            'status': text,
            'exclude_reply_user_ids': [],
            'media_ids': media_ids
            },
            'execute_at': scheduled_at
        }
        return await self.gql_post(Endpoint.CREATE_SCHEDULED_TWEET, variables)

    async def delete_tweet(self, tweet_id):
        variables = {
            'tweet_id': tweet_id,
            'dark_request': False
        }
        return await self.gql_post(Endpoint.DELETE_TWEET, variables)

    async def user_by_screen_name(self, screen_name):
        variables = {
            'screen_name': screen_name,
            'withSafetyModeUserFields': False
        }
        params = {
            'fieldToggles': {'withAuxiliaryUserLabels': False}
        }
        return await self.gql_get(Endpoint.USER_BY_SCREEN_NAME, variables, USER_FEATURES, extra_params=params)

    async def user_by_rest_id(self, user_id):
        variables = {
            'userId': user_id,
            'withSafetyModeUserFields': True
        }
        return await self.gql_get(Endpoint.USER_BY_REST_ID, variables, USER_FEATURES)

    async def about_account(self, screen_name):
        variables = {
            'screenName': screen_name
        }
        return await self.gql_get(Endpoint.ABOUT_ACCOUNT, variables, ABOUT_ACCOUNT_FEATURES)

    async def tweet_detail(self, tweet_id, cursor):
        variables = {
            'focalTweetId': tweet_id,
            'with_rux_injections': False,
            'includePromotedContent': True,
            'withCommunity': True,
            'withQuickPromoteEligibilityTweetFields': True,
            'withBirdwatchNotes': True,
            'withVoice': True,
            'withV2Timeline': True
        }
        if cursor is not None:
            variables['cursor'] = cursor
        params = {
            'fieldToggles': {'withAuxiliaryUserLabels': False}
        }
        return await self.gql_get(Endpoint.TWEET_DETAIL, variables, FEATURES, extra_params=params)

    async def fetch_scheduled_tweets(self):
        variables = {'ascending': True}
        return await self.gql_get(Endpoint.FETCH_SCHEDULED_TWEETS, variables)

    async def delete_scheduled_tweet(self, tweet_id):
        variables = {'scheduled_tweet_id': tweet_id}
        return await self.gql_post(Endpoint.DELETE_SCHEDULED_TWEET, variables)

    async def tweet_engagements(self, tweet_id, count, cursor, endpoint):
        variables = {
            'tweetId': tweet_id,
            'count': count,
            'includePromotedContent': True
        }
        if cursor is not None:
            variables['cursor'] = cursor
        return await self.gql_get(endpoint, variables, FEATURES)

    async def retweeters(self, tweet_id, count, cursor):
        return await self.tweet_engagements(tweet_id, count, cursor, Endpoint.RETWEETERS)

    async def favoriters(self, tweet_id, count, cursor):
        return await self.tweet_engagements(tweet_id, count, cursor, Endpoint.FAVORITERS)

    async def bird_watch_one_note(self, note_id):
        variables = {'note_id': note_id}
        return await self.gql_get(Endpoint.FETCH_COMMUNITY_NOTE, variables, COMMUNITY_NOTE_FEATURES)

    async def _get_user_tweets(self, user_id, count, cursor, endpoint):
        variables = {
            'userId': user_id,
            'count': count,
            'includePromotedContent': True,
            'withQuickPromoteEligibilityTweetFields': True,
            'withVoice': True,
            'withV2Timeline': True
        }
        if cursor is not None:
            variables['cursor'] = cursor
        return await self.gql_get(endpoint, variables, FEATURES)

    async def user_tweets(self, user_id, count, cursor):
        return await self._get_user_tweets(user_id, count, cursor, Endpoint.USER_TWEETS)

    async def user_tweets_and_replies(self, user_id, count, cursor):
        return await self._get_user_tweets(user_id, count, cursor, Endpoint.USER_TWEETS_AND_REPLIES)

    async def user_media(self, user_id, count, cursor):
        return await self._get_user_tweets(user_id, count, cursor, Endpoint.USER_MEDIA)

    async def user_likes(self, user_id, count, cursor):
        return await self._get_user_tweets(user_id, count, cursor, Endpoint.USER_LIKES)

    async def user_highlights_tweets(self, user_id, count, cursor):
        variables = {
            'userId': user_id,
            'count': count,
            'includePromotedContent': True,
            'withVoice': True
        }
        if cursor is not None:
            variables['cursor'] = cursor
        return await self.gql_get(
            Endpoint.USER_HIGHLIGHTS_TWEETS,
            variables,
            USER_HIGHLIGHTS_TWEETS_FEATURES,
            self.base._base_headers
        )

    async def home_timeline(self, count, seen_tweet_ids, cursor):
        variables = {
            'count': count,
            'includePromotedContent': True,
            'latestControlAvailable': True,
            'requestContext': 'launch',
            'withCommunity': True,
            'seenTweetIds': seen_tweet_ids or []
        }
        if cursor is not None:
            variables['cursor'] = cursor
        return await self.gql_post(Endpoint.HOME_TIMELINE, variables, FEATURES)

    async def home_latest_timeline(self, count, seen_tweet_ids, cursor):
        variables = {
            'count': count,
            'includePromotedContent': True,
            'latestControlAvailable': True,
            'requestContext': 'launch',
            'withCommunity': True,
            'seenTweetIds': seen_tweet_ids or []
        }
        if cursor is not None:
            variables['cursor'] = cursor
        return await self.gql_post(Endpoint.HOME_LATEST_TIMELINE, variables, FEATURES)

    async def favorite_tweet(self, tweet_id):
        variables = {'tweet_id': tweet_id}
        return await self.gql_post(Endpoint.FAVORITE_TWEET, variables)

    async def unfavorite_tweet(self, tweet_id):
        variables = {'tweet_id': tweet_id}
        return await self.gql_post(Endpoint.UNFAVORITE_TWEET, variables)

    async def retweet(self, tweet_id):
        variables = {'tweet_id': tweet_id, 'dark_request': False}
        return await self.gql_post(Endpoint.CREATE_RETWEET, variables)

    async def delete_retweet(self, tweet_id):
        variables = {'source_tweet_id': tweet_id,'dark_request': False}
        return await self.gql_post(Endpoint.DELETE_RETWEET, variables)

    async def create_bookmark(self, tweet_id):
        variables = {'tweet_id': tweet_id}
        return await self.gql_post(Endpoint.CREATE_BOOKMARK, variables)

    async def bookmark_tweet_to_folder(self, tweet_id, folder_id):
        variables = {
            'tweet_id': tweet_id,
            'bookmark_collection_id': folder_id
        }
        return await self.gql_post(Endpoint.BOOKMARK_TO_FOLDER, variables)

    async def delete_bookmark(self, tweet_id):
        variables = {'tweet_id': tweet_id}
        return await self.gql_post(Endpoint.DELETE_BOOKMARK, variables)

    async def bookmarks(self, count, cursor):
        variables = {
            'count': count,
            'includePromotedContent': True
        }
        features = FEATURES | {
            'graphql_timeline_v2_bookmark_timeline': True
        }
        if cursor is not None:
            variables['cursor'] = cursor
        params = flatten_params({
            'variables': variables,
            'features': features
        })
        return await self.base.get(
            Endpoint.BOOKMARKS,
            params=params,
            headers=self.base._base_headers
        )

    async def bookmark_folder_timeline(self, count, cursor, folder_id):
        variables = {
            'count': count,
            'includePromotedContent': True,
            'bookmark_collection_id': folder_id
        }
        variables['bookmark_collection_id'] = folder_id
        if cursor is not None:
            variables['cursor'] = cursor
        return await self.gql_get(Endpoint.BOOKMARK_FOLDER_TIMELINE, variables, BOOKMARK_FOLDER_TIMELINE_FEATURES)

    async def delete_all_bookmarks(self):
        return await self.gql_post(Endpoint.BOOKMARKS_ALL_DELETE, {})

    async def bookmark_folders_slice(self, cursor):
        variables = {}
        if cursor is not None:
            variables['cursor'] = cursor
        variables = {'variables': variables}
        return await self.gql_get(Endpoint.BOOKMARK_FOLDERS_SLICE, variables)

    async def edit_bookmark_folder(self, folder_id, name):
        variables = {
            'bookmark_collection_id': folder_id,
            'name': name
        }
        return await self.gql_post(Endpoint.EDIT_BOOKMARK_FOLDER, variables)

    async def delete_bookmark_folder(self, folder_id):
        variables = {'bookmark_collection_id': folder_id}
        return await self.gql_post(Endpoint.DELETE_BOOKMARK_FOLDER, variables)

    async def create_bookmark_folder(self, name):
        variables = {'name': name}
        return await self.gql_post(Endpoint.CREATE_BOOKMARK_FOLDER, variables)

    async def _friendships(self, user_id, count, endpoint, cursor):
        variables = {
            'userId': user_id,
            'count': count,
            'includePromotedContent': False
        }
        if cursor is not None:
            variables['cursor'] = cursor
        return await self.gql_get(endpoint, variables, FEATURES)

    async def followers(self, user_id, count, cursor):
        return await self._friendships(user_id, count, Endpoint.FOLLOWERS, cursor)

    async def blue_verified_followers(self, user_id, count, cursor):
        return await self._friendships(user_id, count, Endpoint.BLUE_VERIFIED_FOLLOWERS, cursor)

    async def followers_you_know(self, user_id, count, cursor):
        return await self._friendships(user_id, count, Endpoint.FOLLOWERS_YOU_KNOW, cursor)

    async def following(self, user_id, count, cursor):
        return await self._friendships(user_id, count, Endpoint.FOLLOWING, cursor)

    async def user_creator_subscriptions(self, user_id, count, cursor):
        return await self._friendships(user_id, count, Endpoint.USER_CREATOR_SUBSCRIPTIONS, cursor)

    async def user_dm_reaction_mutation_add_mutation(self, message_id, conversation_id, emoji):
        variables = {
            'messageId': message_id,
            'conversationId': conversation_id,
            'reactionTypes': ['Emoji'],
            'emojiReactions': [emoji]
        }
        return await self.gql_post(Endpoint.USER_DM_REACTION_MUTATION_ADD_MUTATION, variables)

    async def user_dm_reaction_mutation_remove_mutation(self, message_id, conversation_id, emoji):
        variables = {
            'conversationId': conversation_id,
            'messageId': message_id,
            'reactionTypes': ['Emoji'],
            'emojiReactions': [emoji]
        }
        return await self.gql_post(Endpoint.USER_DM_REACTION_MUTATION_REMOVE_MUTATION, variables)

    async def dm_message_delete_mutation(self, message_id):
        variables = {'messageId': message_id}
        return await self.gql_post(Endpoint.DM_MESSAGE_DELETE_MUTATION, variables)

    async def add_participants_mutation(self, group_id, user_ids):
        variables = {
            'addedParticipants': user_ids,
            'conversationId': group_id
        }
        return await self.gql_post(Endpoint.ADD_PARTICIPANTS_MUTATION, variables)

    async def create_list(self, name, description, is_private):
        variables = {
            'isPrivate': is_private,
            'name': name,
            'description': description
        }
        return await self.gql_post(Endpoint.CREATE_LIST, variables, LIST_FEATURES)

    async def edit_list_banner(self, list_id, media_id):
        variables = {
            'listId': list_id,
            'mediaId': media_id
        }
        return await self.gql_post(Endpoint.EDIT_LIST_BANNER, variables, LIST_FEATURES)

    async def delete_list_banner(self, list_id):
        variables = {'listId': list_id}
        return await self.gql_post(Endpoint.DELETE_LIST_BANNER, variables, LIST_FEATURES)

    async def update_list(self, list_id, name, description, is_private):
        variables = {'listId': list_id}
        if name is not None:
            variables['name'] = name
        if description is not None:
            variables['description'] = description
        if is_private is not None:
            variables['isPrivate'] = is_private
        return await self.gql_post(Endpoint.UPDATE_LIST, variables, LIST_FEATURES)

    async def list_add_member(self, list_id, user_id):
        variables = {
            'listId': list_id,
            'userId': user_id
        }
        return await self.gql_post(Endpoint.LIST_ADD_MEMBER, variables, LIST_FEATURES)

    async def list_remove_member(self, list_id, user_id):
        variables = {
            'listId': list_id,
            'userId': user_id
        }
        return await self.gql_post(Endpoint.LIST_REMOVE_MEMBER, variables, LIST_FEATURES)

    async def list_management_pace_timeline(self, count, cursor):
        variables = {'count': count}
        if cursor is not None:
            variables['cursor'] = cursor
        return await self.gql_get(Endpoint.LIST_MANAGEMENT_PACE_TIMELINE, variables, FEATURES)

    async def list_by_rest_id(self, list_id):
        variables = {'listId': list_id}
        return await self.gql_get(Endpoint.LIST_BY_REST_ID, variables, LIST_FEATURES)

    async def list_latest_tweets_timeline(self, list_id, count, cursor):
        variables = {'listId': list_id, 'count': count}
        if cursor is not None:
            variables['cursor'] = cursor
        return await self.gql_get(Endpoint.LIST_LATEST_TWEETS_TIMELINE, variables, FEATURES)

    async def _list_users(self, endpoint, list_id, count, cursor):
        variables = {'listId': list_id, 'count': count}
        if cursor is not None:
            variables['cursor'] = cursor
        return await self.gql_get(endpoint, variables, FEATURES)

    async def list_members(self, list_id, count, cursor):
        return await self._list_users(Endpoint.LIST_MEMBERS, list_id, count, cursor)

    async def list_subscribers(self, list_id, count, cursor):
        return await self._list_users(Endpoint.LIST_SUBSCRIBERS, list_id, count, cursor)

    async def search_community(self, query, cursor):
        variables = {'query': query}
        if cursor is not None:
            variables['cursor'] = cursor
        return await self.gql_get(Endpoint.SEARCH_COMMUNITY, variables)

    async def community_query(self, community_id):
        variables = {'communityId': community_id}
        features = {
            'c9s_list_members_action_api_enabled': False,
            'c9s_superc9s_indication_enabled': False
        }
        return await self.gql_get(Endpoint.COMMUNITY_QUERY, variables, features)

    async def community_media_timeline(self, community_id, count, cursor):
        variables = {
            'communityId': community_id,
            'count': count,
            'withCommunity': True
        }
        if cursor is not None:
            variables['cursor'] = cursor
        return await self.gql_get(Endpoint.COMMUNITY_MEDIA_TIMELINE, variables, COMMUNITY_TWEETS_FEATURES)

    async def community_tweets_timeline(self, community_id, ranking_mode, count, cursor):
        variables = {
            'communityId': community_id,
            'count': count,
            'withCommunity': True,
            'rankingMode': ranking_mode
        }
        if cursor is not None:
            variables['cursor'] = cursor
        return await self.gql_get(Endpoint.COMMUNITY_TWEETS_TIMELINE, variables, COMMUNITY_TWEETS_FEATURES)

    async def communities_main_page_timeline(self, count, cursor):
        variables = {
            'count': count,
            'withCommunity': True
        }
        if cursor is not None:
            variables['cursor'] = cursor
        return await self.gql_get(Endpoint.COMMUNITIES_MAIN_PAGE_TIMELINE, variables, COMMUNITY_TWEETS_FEATURES)

    async def join_community(self, community_id):
        variables = {'communityId': community_id}
        return await self.gql_post(Endpoint.JOIN_COMMUNITY, variables, JOIN_COMMUNITY_FEATURES)

    async def leave_community(self, community_id):
        variables = {'communityId': community_id}
        return await self.gql_post(Endpoint.LEAVE_COMMUNITY, variables, JOIN_COMMUNITY_FEATURES)

    async def request_to_join_community(self, community_id, answer):
        variables = {
            'communityId': community_id,
            'answer': '' if answer is None else answer
        }
        return await self.gql_post(Endpoint.REQUEST_TO_JOIN_COMMUNITY, variables, JOIN_COMMUNITY_FEATURES)

    async def _get_community_users(self, endpoint, community_id, count, cursor):
        variables = {'communityId': community_id, 'count': count}
        features = {'responsive_web_graphql_timeline_navigation_enabled': True}
        if cursor is not None:
            variables['cursor'] = cursor
        return await self.gql_get(endpoint, variables, features)

    async def members_slice_timeline_query(self, community_id, count, cursor):
        return await self._get_community_users(Endpoint.MEMBERS_SLICE_TIMELINE_QUERY, community_id, count, cursor)

    async def moderators_slice_timeline_query(self, community_id, count, cursor):
        return await self._get_community_users(Endpoint.MODERATORS_SLICE_TIMELINE_QUERY, community_id, count, cursor)

    async def community_tweet_search_module_query(self, community_id, query, count, cursor):
        variables = {
            'count': count,
            'query': query,
            'communityId': community_id,
            'includePromotedContent': False,
            'withBirdwatchNotes': True,
            'withVoice': False,
            'isListMemberTargetUserId': '0',
            'withCommunity': False,
            'withSafetyModeUserFields': True
        }
        if cursor is not None:
            variables['cursor'] = cursor
        return await self.gql_get(Endpoint.COMMUNITY_TWEET_SEARCH_MODULE_QUERY, variables, COMMUNITY_TWEETS_FEATURES)

    async def tweet_results_by_rest_ids(self, tweet_ids):
        variables = {
            'tweetIds': tweet_ids,
            'includePromotedContent': True,
            'withBirdwatchNotes': True,
            'withVoice': True,
            'withCommunity': True
        }
        return await self.gql_get(Endpoint.TWEET_RESULTS_BY_REST_IDS, variables, TWEET_RESULTS_BY_REST_IDS_FEATURES)

    async def users_by_rest_ids(self, user_ids):
        variables = {
            'userIds': user_ids
        }
        return await self.gql_get(Endpoint.USERS_BY_REST_IDS, variables, USER_FEATURES)

    async def users_by_screen_names(self, screen_names):
        variables = {
            'screen_names': screen_names
        }
        return await self.gql_get(Endpoint.USERS_BY_SCREEN_NAMES, variables, USER_FEATURES)

    async def user_articles_tweets(self, user_id, count, cursor):
        variables = {
            'userId': user_id,
            'count': count,
            'includePromotedContent': False,
            'withVoice': True
        }
        if cursor is not None:
            variables['cursor'] = cursor
        return await self.gql_get(Endpoint.USER_ARTICLES_TWEETS, variables, FEATURES)

    async def tweet_edit_history(self, tweet_id):
        variables = {
            'tweetId': tweet_id,
            'withQuickPromoteEligibilityTweetFields': True
        }
        return await self.gql_get(Endpoint.TWEET_EDIT_HISTORY, variables, FEATURES)

    async def audio_space_by_id(self, space_id):
        variables = {
            'id': space_id,
            'isMetatagsQuery': False,
            'withReplays': True,
            'withListeners': True
        }
        return await self.gql_get(Endpoint.AUDIO_SPACE_BY_ID, variables, AUDIO_SPACE_FEATURES)

    async def audio_space_search(self, query, count, cursor):
        variables = {
            'query': query,
            'count': count
        }
        if cursor is not None:
            variables['cursor'] = cursor
        return await self.gql_get(Endpoint.AUDIO_SPACE_SEARCH, variables)

    async def trend_history(self, trend_id):
        variables = {
            'trendId': trend_id
        }
        return await self.gql_get(Endpoint.TREND_HISTORY, variables)

    async def trend_relevant_users(self, trend_id):
        variables = {
            'trendId': trend_id
        }
        return await self.gql_get(Endpoint.TREND_RELEVANT_USERS, variables, USER_FEATURES)

    async def topic_by_rest_id(self, topic_id):
        variables = {
            'topicId': topic_id
        }
        return await self.gql_get(Endpoint.TOPIC_BY_REST_ID, variables)

    async def topic_landing_page(self, topic_id, count, cursor):
        variables = {
            'topicId': topic_id,
            'count': count,
            'withCommunity': True
        }
        if cursor is not None:
            variables['cursor'] = cursor
        return await self.gql_get(Endpoint.TOPIC_LANDING_PAGE, variables, TIMELINE_FEATURES)

    async def article_result_by_rest_id(self, article_id):
        variables = {
            'articleId': article_id
        }
        return await self.gql_get(Endpoint.ARTICLE_RESULT_BY_REST_ID, variables, ARTICLE_FEATURES)

    async def broadcast_query(self, broadcast_id):
        variables = {
            'id': broadcast_id
        }
        return await self.gql_get(Endpoint.BROADCAST_QUERY, variables, TIMELINE_FEATURES)

    async def birdwatch_fetch_notes(self, tweet_id):
        variables = {
            'tweetId': tweet_id
        }
        return await self.gql_get(Endpoint.BIRDWATCH_FETCH_NOTES, variables, BIRDWATCH_NOTES_FEATURES)

    async def birdwatch_fetch_source_link_slice(self, url, count, cursor):
        variables = {
            'url': url,
            'count': count
        }
        if cursor is not None:
            variables['cursor'] = cursor
        return await self.gql_get(Endpoint.BIRDWATCH_FETCH_SOURCE_LINK_SLICE, variables, TIMELINE_FEATURES)

    async def birdwatch_fetch_global_timeline(self, count, cursor):
        variables = {
            'count': count
        }
        if cursor is not None:
            variables['cursor'] = cursor
        return await self.gql_get(Endpoint.BIRDWATCH_FETCH_GLOBAL_TIMELINE, variables, TIMELINE_FEATURES)

    async def birdwatch_fetch_public_data(self):
        variables = {}
        return await self.gql_get(Endpoint.BIRDWATCH_FETCH_PUBLIC_DATA, variables, BIRDWATCH_PUBLIC_DATA_FEATURES)

    async def list_ranked_tweets_timeline(self, list_id, count, cursor):
        variables = {
            'listId': list_id,
            'count': count
        }
        if cursor is not None:
            variables['cursor'] = cursor
        return await self.gql_get(Endpoint.LIST_RANKED_TWEETS_TIMELINE, variables, TIMELINE_FEATURES)

    async def list_search_timeline(self, list_id, query, count, cursor):
        variables = {
            'listId': list_id,
            'rawQuery': query,
            'count': count
        }
        if cursor is not None:
            variables['cursor'] = cursor
        return await self.gql_get(Endpoint.LIST_SEARCH_TIMELINE, variables, TIMELINE_FEATURES)

    async def communities_explore_timeline(self, count, cursor):
        variables = {
            'count': count
        }
        if cursor is not None:
            variables['cursor'] = cursor
        return await self.gql_get(Endpoint.COMMUNITIES_EXPLORE_TIMELINE, variables, TIMELINE_FEATURES)

    async def community_hashtags_timeline(self, community_id, hashtags, count, cursor):
        variables = {
            'communityId': community_id,
            'hashtags': hashtags,
            'count': count,
            'withCommunity': True
        }
        if cursor is not None:
            variables['cursor'] = cursor
        return await self.gql_get(Endpoint.COMMUNITY_HASHTAGS_TIMELINE, variables, TIMELINE_FEATURES)

    async def generic_timeline_by_id(self, timeline_id, count, cursor):
        variables = {
            'timelineId': timeline_id,
            'count': count
        }
        if cursor is not None:
            variables['cursor'] = cursor
        return await self.gql_get(Endpoint.GENERIC_TIMELINE_BY_ID, variables, TIMELINE_FEATURES)

    ####################
    # For guest client
    ####################

    async def tweet_result_by_rest_id(self, tweet_id):
        variables = {
            'tweetId': tweet_id,
            'withCommunity': False,
            'includePromotedContent': False,
            'withVoice': False
        }
        params = {
            'fieldToggles': {
                'withArticleRichContentState': True,
                'withArticlePlainText': False,
                'withGrokAnalyze': False
            }
        }
        return await self.gql_get(
            Endpoint.TWEET_RESULT_BY_REST_ID, variables, TWEET_RESULT_BY_REST_ID_FEATURES, extra_params=params
        )

"""User.from_data reads both X user shapes: with ``legacy`` and without it.

Both payloads are UserByScreenName(elonmusk) results captured on 2026-10-07 with
one account: the first with twikit's static queryId/features, the second with
the web app's live ones (no ``legacy`` block; fields moved to per-topic blocks).
"""

from twikit.user import User

LEGACY_SHAPE = {
    "rest_id": "44196397",
    "is_blue_verified": True,
    "core": {"created_at": "Tue Jun 02 20:12:29 +0000 2009", "name": "Elon Musk", "screen_name": "elonmusk"},
    "avatar": {"image_url": "https://pbs.twimg.com/profile_images/2103567689515954176/aR-Kjpp4_normal.jpg"},
    "location": {"location": ""},
    "privacy": {"protected": False},
    "verification": {"verified": False},
    "dm_permissions": {"can_dm": False},
    "media_permissions": {"can_media_tag": False},
    "profile_bio": {"description": "https://t.co/ZdBx5WABYx"},
    "relationship_perspectives": {"blocked_by": False, "blocking": False, "followed_by": False, "following": True, "muting": False},
    "legacy": {
        "default_profile": False,
        "default_profile_image": False,
        "description": "https://t.co/ZdBx5WABYx",
        "entities": {"description": {"urls": [{"display_url": "Terafab.AI", "expanded_url": "http://Terafab.AI", "indices": [0, 23], "url": "https://t.co/ZdBx5WABYx"}]}},
        "fast_followers_count": 0,
        "favourites_count": 250962,
        "follow_request_sent": False,
        "followers_count": 241700433,
        "friends_count": 1415,
        "has_custom_timelines": True,
        "is_translator": False,
        "listed_count": 170826,
        "media_count": 4729,
        "normal_followers_count": 241700433,
        "notifications": False,
        "pinned_tweet_ids_str": ["2107724314451878104"],
        "possibly_sensitive": False,
        "profile_banner_url": "https://pbs.twimg.com/profile_banners/44196397/1774145451",
        "profile_interstitial_type": "",
        "statuses_count": 109571,
        "translator_type": "none",
        "url": "",
        "want_retweets": True,
    },
}

NEW_SHAPE = {
    "rest_id": "44196397",
    "is_blue_verified": True,
    "possibly_sensitive": False,
    "core": {"created_at": "Tue Jun 02 20:12:29 +0000 2009", "name": "Elon Musk", "screen_name": "elonmusk"},
    "avatar": {"image_url": "https://pbs.twimg.com/profile_images/2103567689515954176/aR-Kjpp4_normal.jpg"},
    "banner": {"image_url": "https://pbs.twimg.com/profile_banners/44196397/1774145451"},
    "location": {"location": ""},
    "privacy": {"protected": False},
    "verification": {"verified": False},
    "media_permissions": {"can_media_tag": False},
    "action_counts": {"favorites_count": 250962},
    "notifications_settings": {"notifications_enabled": False},
    "pinned_items": {"tweet_ids_str": ["2107724314451878104"]},
    "profile_bio": {
        "description": "https://t.co/ZdBx5WABYx",
        "entities": {"description": {"urls": [{"display_url": "Terafab.AI", "expanded_url": "http://Terafab.AI", "indices": [0, 23], "url": "https://t.co/ZdBx5WABYx"}]}},
    },
    "profile_metadata": {"profile_interstitial_type": ""},
    "profile_translation": {"translator_type": "none"},
    "relationship_counts": {"followers": 241700433, "following": 1415},
    "relationship_perspectives": {"blocked_by": False, "blocking": False, "followed_by": False, "following": True, "live_following": False, "muting": False},
    "tweet_counts": {"media_tweets": 4729, "tweets": 109571},
    "website": {"url": ""},
}

SHARED_FIELDS = (
    "id", "created_at", "name", "screen_name", "profile_image_url", "profile_banner_url",
    "url", "location", "description", "description_urls", "pinned_tweet_ids",
    "is_blue_verified", "verified", "possibly_sensitive", "can_media_tag",
    "followers_count", "normal_followers_count", "following_count", "favourites_count",
    "media_count", "statuses_count", "translator_type", "protected",
    "notifications", "profile_interstitial_type", "following",
)


def test_new_shape_has_counts_and_profile():
    user = User.from_data(None, NEW_SHAPE)
    assert user.followers_count == 241700433
    assert user.following_count == 1415
    assert user.statuses_count == 109571
    assert user.media_count == 4729
    assert user.favourites_count == 250962
    assert user.description == "https://t.co/ZdBx5WABYx"
    assert user.description_urls[0]["expanded_url"] == "http://Terafab.AI"
    assert user.profile_banner_url.endswith("/1774145451")
    assert user.pinned_tweet_ids == ["2107724314451878104"]


def test_both_shapes_parse_the_same():
    old = User.from_data(None, LEGACY_SHAPE)
    new = User.from_data(None, NEW_SHAPE)
    for field in SHARED_FIELDS:
        assert getattr(old, field) == getattr(new, field), field

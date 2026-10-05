"""Timeline conversation modules must yield EVERY tweet in the thread.

X groups a reply thread into one module entry (``list-conversation-*`` on list
timelines, ``home-conversation-*`` on the home timeline) holding the tweets in
``content.items[].item``. ``get_list_tweets`` skipped anything not starting with
``tweet`` and ``get_latest_timeline`` only read ``content.itemContent``, so the
thread's tweets were silently dropped (upstream d60/twikit PRs #340 / #337).
"""

from unittest.mock import AsyncMock

from twikit.client.client import Client


def _tweet(tweet_id: str) -> dict:
    return {
        "itemContent": {
            "itemType": "TimelineTweet",
            "tweet_results": {
                "result": {
                    "__typename": "Tweet",
                    "rest_id": tweet_id,
                    "core": {
                        "user_results": {
                            "result": {
                                "__typename": "User",
                                "rest_id": "42",
                                "legacy": {"screen_name": "someone", "name": "Someone", "created_at": "Mon Jan 01 00:00:00 +0000 2024"},
                            }
                        }
                    },
                    "legacy": {
                        "id_str": tweet_id,
                        "full_text": f"tweet {tweet_id}",
                        "created_at": "Mon Jan 01 00:00:00 +0000 2024",
                        "lang": "en",
                    },
                }
            },
        }
    }


def _module(entry_id: str, *tweet_ids: str) -> dict:
    return {
        "entryId": entry_id,
        "content": {
            "entryType": "TimelineTimelineModule",
            "items": [{"entryId": f"{entry_id}-tweet-{t}", "item": _tweet(t)} for t in tweet_ids],
        },
    }


def _response(entries: list) -> dict:
    return {"data": {"timeline": {"instructions": [{"type": "TimelineAddEntries", "entries": entries}]}}}


ENTRIES = [
    {"entryId": "tweet-1", "content": {"entryType": "TimelineTimelineItem", **_tweet("1")}},
    None,  # placeholder for the conversation module (per-timeline prefix)
    {"entryId": "promoted-tweet-9", "content": {"entryType": "TimelineTimelineItem", **_tweet("9")}},
    {"entryId": "cursor-bottom-1", "content": {"entryType": "TimelineTimelineCursor", "value": "CUR", "cursorType": "Bottom"}},
]


def _client() -> Client:
    client = Client.__new__(Client)  # no network/session needed
    client.gql = AsyncMock()
    return client


async def test_list_tweets_unpacks_list_conversation_module():
    client = _client()
    entries = list(ENTRIES)
    entries[1] = _module("list-conversation-5", "2", "1", "3")  # "1" repeats the standalone tweet
    client.gql.list_latest_tweets_timeline.return_value = (_response(entries), None)

    result = await client.get_list_tweets("123")

    # thread tweets kept, duplicate dropped, promoted entry still excluded, order preserved
    assert [t.id for t in result] == ["1", "2", "3"]


async def test_latest_timeline_unpacks_home_conversation_module():
    client = _client()
    entries = list(ENTRIES)
    entries[1] = _module("home-conversation-5", "2", "3")
    client.gql.home_latest_timeline.return_value = (_response(entries), None)

    result = await client.get_latest_timeline()

    assert [t.id for t in result][:3] == ["1", "2", "3"]

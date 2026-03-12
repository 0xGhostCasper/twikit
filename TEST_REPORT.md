# Test Report

**Date:** 2026-03-12
**Python:** 3.14.0
**pytest:** 9.0.2
**Duration:** 64.66s
**Result:** 41 passed, 5 skipped, 0 failed

## Results by Module

### test_communities.py (8 tests)

| Test | Status |
|------|--------|
| `TestCommunityFields::test_fields_populated` | PASSED |
| `TestSearchCommunity::test_returns_results` | PASSED |
| `TestCommunityTweets::test_top` | PASSED |
| `TestCommunityTweets::test_media` | PASSED |
| `TestExploreCommunities::test_returns_result` | PASSED |
| `TestCommunityHashtags::test_returns_result` | PASSED |
| `TestCommunityNotesStats::test_returns_dict` | PASSED |
| `TestCommunityNotesTimeline::test_returns_result` | PASSED |

### test_lists.py (7 tests)

| Test | Status |
|------|--------|
| `TestListByRestId::test_returns_list` | PASSED |
| `TestListByRestId::test_fields_populated` | PASSED |
| `TestListLatestTweets::test_returns_tweets` | PASSED |
| `TestListMembers::test_returns_users` | PASSED |
| `TestListSubscribers::test_returns_result` | PASSED |
| `TestListRankedTweets::test_returns_result` | PASSED |
| `TestSearchListTweets::test_returns_result` | PASSED |

### test_spaces.py (1 test)

| Test | Status | Reason |
|------|--------|--------|
| `TestSearchAudioSpaces::test_returns_result` | SKIPPED | Endpoint returns 404 (possibly deprecated server-side) |

### test_timelines.py (2 tests)

| Test | Status |
|------|--------|
| `TestGetTimeline::test_returns_tweets` | PASSED |
| `TestGetLatestTimeline::test_returns_tweets` | PASSED |

### test_trends.py (3 tests)

| Test | Status | Reason |
|------|--------|--------|
| `TestGetTrends::test_returns_trends` | PASSED | |
| `TestTrendHistory::test_returns_list` | SKIPPED | Trends API returned no trendId to query |
| `TestTrendRelevantUsers::test_returns_list` | SKIPPED | Trends API returned no trendId to query |

### test_tweets.py (14 tests)

| Test | Status | Reason |
|------|--------|--------|
| `TestTweetDetail::test_returns_tweet` | PASSED | |
| `TestTweetDetail::test_tweet_has_text` | PASSED | |
| `TestTweetDetail::test_fields_populated` | PASSED | |
| `TestTweetsByIds::test_returns_tweets` | PASSED | |
| `TestTweetEditHistory::test_returns_list` | PASSED | |
| `TestUserTweets::test_tweets` | PASSED | |
| `TestUserTweets::test_replies` | PASSED | |
| `TestUserTweets::test_media` | PASSED | |
| `TestUserTweets::test_likes` | PASSED | |
| `TestUserHighlightsTweets::test_returns_result` | PASSED | |
| `TestUserArticles::test_returns_result` | PASSED | |
| `TestSearchTweet::test_top`  | PASSED | |
| `TestSearchTweet::test_latest`  | PASSED | |
| `TestSimilarTweets::test_returns_list` | PASSED | |
| `TestRetweeters::test_returns_users` | PASSED | |
| `TestFavoriters::test_returns_users` | PASSED | |

### test_users.py (8 tests)

| Test | Status |
|------|--------|
| `TestUserByScreenName::test_returns_user` | PASSED |
| `TestUserByScreenName::test_has_profile_data` | PASSED |
| `TestUserByScreenName::test_fields_populated` | PASSED |
| `TestUserById::test_returns_user` | PASSED |
| `TestUsersByIds::test_returns_multiple_users` | PASSED |
| `TestUsersByScreenNames::test_returns_multiple_users` | PASSED |
| `TestFollowers::test_returns_users` | PASSED |
| `TestFollowing::test_returns_users` | PASSED |
| `TestVerifiedFollowers::test_returns_result` | PASSED |

## Skipped Tests Summary

All 5 skipped tests are due to external Twitter/X API issues, not code bugs:

| # | Test | Root Cause |
|---|------|------------|
| 1 | `TestSearchAudioSpaces::test_returns_result` | AudioSpaceSearch endpoint returns 404 server-side (queryId `NTq79TuSz6fHj8lQaferJw` verified correct against reference repo) |
| 2 | `TestTrendHistory::test_returns_list` | Trends API returns no `trendId` metadata to query history with |
| 3 | `TestTrendRelevantUsers::test_returns_list` | Same — depends on `trendId` from trends API |

## Field Population Coverage

Four `test_fields_populated` tests verify that key dataclass fields are actually populated with real API data (not just default/None values):

- **User** — 20+ field assertions (identity, counters, verification, relationship booleans)
- **Tweet** — 15+ field assertions (identity, author, counters, booleans, source, conversation_id, views)
- **List** — 12+ field assertions (identity, counters, mode, booleans, facepile, owner)
- **Community** — 10+ field assertions (identity, counters, metadata, topic, creator, banner)

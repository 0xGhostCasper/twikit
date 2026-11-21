"""GraphQL queries X serves only over POST.

2026-11-21 ~04:00-04:45 UTC: X began answering GET UsersByRestIds,
UsersByScreenNames and ListLatestTweetsTimeline (and SearchTimeline) with an
empty-body 404 from its edge for every pooled account. The same session and IP
got 200 with data for UsersByScreenNames sent as POST {variables, queryId,
features}. These tests need no account: the client's transport is faked.
"""

import pytest

from twikit.client import gql
from twikit.client.gql import Endpoint, GQLClient
from twikit.errors import NotFound, ServerError

EMPTY_404 = 'status: 404, message: ""'
OK = {"data": {"user": {"result": {"rest_id": "1"}}}}


class FakeBase:
    """Records each request; answers GET and POST with the given outcomes in turn."""

    _base_headers = {"authorization": "Bearer x"}

    def __init__(self, get=(), post=()):
        self._get, self._post = list(get), list(post)
        self.calls = []

    async def _answer(self, outcomes):
        outcome = outcomes.pop(0)
        if isinstance(outcome, Exception):
            raise outcome
        return outcome, None

    async def get(self, url, params=None, headers=None, **kwargs):
        self.calls.append(("GET", url.rsplit("/", 1)[-1], params))
        return await self._answer(self._get)

    async def post(self, url, json=None, headers=None, **kwargs):
        self.calls.append(("POST", url.rsplit("/", 1)[-1], json))
        return await self._answer(self._post)


@pytest.fixture(autouse=True)
def _fresh_learned():
    gql._learned_post_only.clear()
    yield
    gql._learned_post_only.clear()


@pytest.mark.parametrize(
    "call, name, variables",
    [
        (lambda c: c.users_by_screen_names(["XDevelopers"]), "UsersByScreenNames", {"screen_names": ["XDevelopers"]}),
        (lambda c: c.users_by_rest_ids(["2244994945"]), "UsersByRestIds", {"userIds": ["2244994945"]}),
        (lambda c: c.list_latest_tweets_timeline("123", 20, None), "ListLatestTweetsTimeline", {"listId": "123", "count": 20}),
    ],
)
async def test_post_only_operations_go_straight_to_post(call, name, variables):
    base = FakeBase(post=[OK])
    await call(GQLClient(base))
    assert len(base.calls) == 1
    method, op, body = base.calls[0]
    assert (method, op) == ("POST", name)
    # The web client's POST body: JSON objects, not the GET's JSON-encoded strings.
    assert body["variables"] == variables
    assert body["queryId"]
    assert isinstance(body["features"], dict)


async def test_empty_404_on_get_is_retried_as_post_and_learned():
    base = FakeBase(get=[NotFound(EMPTY_404)], post=[OK, OK])
    client = GQLClient(base)
    result, _ = await client.gql_get(Endpoint.USER_TWEETS, {"userId": "1"}, {"f": True})
    assert result == OK
    assert [(m, op) for m, op, _ in base.calls] == [("GET", "UserTweets"), ("POST", "UserTweets")]

    await client.gql_get(Endpoint.USER_TWEETS, {"userId": "1"}, {"f": True})
    assert base.calls[-1][0] == "POST"  # no second GET once learned
    assert len(base.calls) == 3


async def test_extra_params_become_body_fields_on_post():
    base = FakeBase(get=[NotFound(EMPTY_404)], post=[OK])
    await GQLClient(base).gql_get(
        Endpoint.USER_TWEETS, {"userId": "1"}, None, extra_params={"fieldToggles": {"withArticlePlainText": False}}
    )
    body = base.calls[-1][2]
    assert body["fieldToggles"] == {"withArticlePlainText": False}
    assert "features" not in body


async def test_search_timeline_empty_404_is_not_retried():
    """Its empty 404 is also "no results"; its POST errored for the same sessions."""
    base = FakeBase(get=[NotFound(EMPTY_404)])
    with pytest.raises(NotFound):
        await GQLClient(base).search_timeline("from:x", "Latest", 20, None)
    assert [m for m, _, _ in base.calls] == ["GET"]


async def test_404_with_a_body_is_not_retried():
    base = FakeBase(get=[NotFound('status: 404, message: "{\\"errors\\":[{\\"code\\":34}]}"')])
    with pytest.raises(NotFound):
        await GQLClient(base).gql_get(Endpoint.USER_TWEETS, {"userId": "1"})
    assert len(base.calls) == 1


async def test_failed_post_reraises_the_original_404_and_learns_nothing():
    base = FakeBase(get=[NotFound(EMPTY_404), NotFound(EMPTY_404)], post=[ServerError("status: 500")])
    client = GQLClient(base)
    with pytest.raises(NotFound):
        await client.gql_get(Endpoint.USER_TWEETS, {"userId": "1"})
    assert "UserTweets" not in gql._learned_post_only


async def test_post_answer_with_errors_is_returned_but_not_learned():
    bad = {"data": {}, "errors": [{"message": "Internal server error"}]}
    base = FakeBase(get=[NotFound(EMPTY_404)], post=[bad])
    result, _ = await GQLClient(base).gql_get(Endpoint.USER_TWEETS, {"userId": "1"})
    assert result == bad
    assert "UserTweets" not in gql._learned_post_only


async def test_other_queries_still_go_get():
    base = FakeBase(get=[OK])
    await GQLClient(base).gql_get(Endpoint.USER_TWEETS, {"userId": "1"}, {"f": True})
    method, _, params = base.calls[0]
    assert method == "GET"
    assert params["variables"] == '{"userId": "1"}'

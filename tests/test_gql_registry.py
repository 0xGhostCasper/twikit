"""GQL registry: read live queryIds/features from X's bundle, fall back safely."""

import json

from twikit.client.gql_registry import (
    SCRIPT_BASE,
    GQLRegistry,
    chunk_urls,
    parse_feature_values,
    parse_operations,
)

SEARCH_OP = (
    'queryId:"liveSearch",operationName:"SearchTimeline",operationType:"query",'
    'metadata:{featureSwitches:["flag_a","flag_b"],fieldToggles:["toggle_x"]}'
)
LIST_OP = (
    'queryId:"liveList",operationName:"ListLatestTweetsTimeline",operationType:"query",'
    'metadata:{featureSwitches:[],fieldToggles:[]}'
)
STATE = {"featureSwitch": {
    "defaultConfig": {"flag_a": {"value": True}, "flag_b": {"value": False}},
    "user": {"config": {"flag_b": {"value": True}}},
}}
HOME = (
    f'<script src="{SCRIPT_BASE}main.abc1234a.js"></script>'
    f'<script>window.__INITIAL_STATE__={json.dumps(STATE)};</script>'
    '<script>a={1:"bundle.Search",2:"i18n/en",3:"shared~bundle.Lists"}'
    '[e]||e)+"."+{1:"1111111",2:"2222222",3:"3333333"}[e]</script>'
)
STATIC_URL = "https://x.com/i/api/graphql/staleSearch/SearchTimeline"


def test_parse_operations():
    ops = parse_operations("x={" + SEARCH_OP + "}")
    op = ops["SearchTimeline"]
    assert op.query_id == "liveSearch"
    assert op.feature_switches == ("flag_a", "flag_b")
    assert op.field_toggles == ("toggle_x",)


def test_feature_values_prefer_user_config():
    assert parse_feature_values(HOME) == {"flag_a": True, "flag_b": True}


def test_chunk_urls_skip_non_carrier_chunks():
    urls = chunk_urls(HOME)
    assert urls[0] == f"{SCRIPT_BASE}main.abc1234a.js"
    assert f"{SCRIPT_BASE}bundle.Search.1111111a.js" in urls
    assert f"{SCRIPT_BASE}shared~bundle.Lists.3333333a.js" in urls
    assert not any("i18n" in u for u in urls)


def _registry_with_ops() -> GQLRegistry:
    reg = GQLRegistry()
    reg.enabled = True
    reg.operations = parse_operations(SEARCH_OP + LIST_OP)
    reg.feature_values = {"flag_a": True}
    return reg


def test_resolve_rewrites_query_id_and_features():
    url, features = _registry_with_ops().resolve(STATIC_URL, {"flag_b": True, "old_flag": True})
    assert url == "https://x.com/i/api/graphql/liveSearch/SearchTimeline"
    # browser's list; live value first, then static default, then False
    assert features == {"flag_a": True, "flag_b": True}


def test_resolve_keeps_static_values_when_unknown_or_disabled():
    reg = _registry_with_ops()
    other = "https://x.com/i/api/graphql/abc/UserByScreenName"
    assert reg.resolve(other, {"f": True}) == (other, {"f": True})
    reg.enabled = False
    assert reg.resolve(STATIC_URL, {"f": True}) == (STATIC_URL, {"f": True})


def test_resolve_keeps_static_features_when_op_has_none():
    url, features = _registry_with_ops().resolve(
        "https://x.com/i/api/graphql/stale/ListLatestTweetsTimeline", {"f": True}
    )
    assert url.endswith("/liveList/ListLatestTweetsTimeline")
    assert features == {"f": True}


async def test_refresh_fetches_carriers_and_caches_by_filename():
    bodies = {
        f"{SCRIPT_BASE}main.abc1234a.js": SEARCH_OP,
        f"{SCRIPT_BASE}bundle.Search.1111111a.js": "",
        f"{SCRIPT_BASE}shared~bundle.Lists.3333333a.js": LIST_OP,
    }
    fetched = []

    async def fetch(url):
        fetched.append(url)
        return bodies[url]

    reg = GQLRegistry()
    reg.enabled = True
    await reg._refresh(HOME, fetch)
    assert set(reg.operations) == {"SearchTimeline", "ListLatestTweetsTimeline"}
    assert reg.feature_values["flag_b"] is True

    fetched.clear()
    await reg._refresh(HOME, fetch)
    assert fetched == []  # unchanged chunk filenames are not downloaded again


async def test_failed_refresh_keeps_previous_state():
    reg = _registry_with_ops()
    before = dict(reg.operations)

    async def fetch(url):
        raise RuntimeError("cdn down")

    await reg._refresh(HOME, fetch)
    assert reg.operations == before


async def test_maybe_refresh_runs_once_in_background_then_waits_for_interval():
    calls = []

    async def fetch(url):
        calls.append(url)
        return SEARCH_OP if "main." in url else ""

    reg = GQLRegistry()
    reg.enabled = True
    reg.maybe_refresh(HOME, fetch)
    reg.maybe_refresh(HOME, fetch)  # in flight: no second task
    await reg._task
    assert "SearchTimeline" in reg.operations
    n = len(calls)
    reg.maybe_refresh(HOME, fetch)  # fresh: skipped until the interval passes
    assert reg._task.done() and len(calls) == n


def test_maybe_refresh_noop_when_disabled():
    reg = GQLRegistry()
    reg.enabled = False
    reg.maybe_refresh(HOME)
    assert reg._task is None

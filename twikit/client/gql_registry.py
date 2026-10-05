"""Live GraphQL operation registry: queryIds and feature switches read from X's web bundle.

X rotates each GraphQL operation's ``queryId`` with every frontend release and
keeps the old hash alive only for a while, so a hard-coded id works until the
day it 404s. On 2026-10-05, 61 of the 80 operations this library uses had
already drifted from the ids in ``gql.Endpoint``.

The web app declares every operation it can send as::

    queryId:"<id>",operationName:"<Name>",operationType:"query",
    metadata:{featureSwitches:[...],fieldToggles:[...]}

spread over ``main`` and the lazily loaded ``bundle.* / shared~* / loader.* /
ondemand.*`` chunks; the values of those feature switches live in the logged-in
page's ``window.__INITIAL_STATE__.featureSwitch`` config. The registry reads
both, so a request can send exactly what the browser would. Anything it cannot
resolve falls back to the caller's static values, and a refresh failure never
reaches a request.

One registry is shared per process (``REGISTRY``): a pool of clients refreshes
it once, and chunk files are cached by their content-hashed filename so a
refresh only downloads what X actually changed.
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import re
import time
from dataclasses import dataclass
from typing import Any, Awaitable, Callable

import httpx

logger = logging.getLogger(__name__)

SCRIPT_BASE = "https://abs.twimg.com/responsive-web/client-web/"
# Chunk families that carry operation definitions; i18n/emoji/c2pa never do.
CARRIER_PREFIXES = ("bundle.", "shared~", "loader.", "ondemand.")

OPERATION_RE = re.compile(
    r'queryId:"(?P<qid>[\w-]+)",operationName:"(?P<name>\w+)",operationType:"(?P<type>\w+)",'
    r'metadata:\{featureSwitches:\[(?P<fs>[^\]]*)\],fieldToggles:\[(?P<ft>[^\]]*)\]'
)
MAIN_JS_RE = re.compile(re.escape(SCRIPT_BASE) + r"main\.[0-9a-f]+a?\.js")
CHUNK_PAIR_RE = re.compile(r'[,{](\d+):"([^"]+)"')
CHUNK_HASH_RE = re.compile(r"[0-9a-f]{7,20}")
INITIAL_STATE_RE = re.compile(r"window\.__INITIAL_STATE__\s*=\s*(\{.*?\});", re.S)
QUOTED_RE = re.compile(r'"(\w+)"')

REFRESH_INTERVAL_S = float(os.environ.get("TWIKIT_GQL_REGISTRY_REFRESH_S", "21600"))
FETCH_CONCURRENCY = 16


async def fetch_public(url: str) -> str:
    """Download a public bundle straight from the CDN.

    Deliberately not through an account's session: these are static assets with
    no account linkage, and the first full fetch is tens of MB that should not
    be spent on metered residential bandwidth.
    """
    async with httpx.AsyncClient(timeout=30, follow_redirects=True) as http:
        response = await http.get(url)
        response.raise_for_status()
        return response.text


@dataclass(frozen=True)
class Operation:
    query_id: str
    operation_type: str
    feature_switches: tuple[str, ...]
    field_toggles: tuple[str, ...]


def parse_operations(js: str) -> dict[str, Operation]:
    """Every operation declared in one bundle, keyed by operation name."""
    return {
        m["name"]: Operation(
            query_id=m["qid"],
            operation_type=m["type"],
            feature_switches=tuple(QUOTED_RE.findall(m["fs"])),
            field_toggles=tuple(QUOTED_RE.findall(m["ft"])),
        )
        for m in OPERATION_RE.finditer(js)
    }


def parse_feature_values(home_html: str) -> dict[str, Any]:
    """Feature-switch values the logged-in page was served (user config over defaults)."""
    m = INITIAL_STATE_RE.search(home_html)
    if not m:
        return {}
    try:
        switches = json.loads(m.group(1)).get("featureSwitch", {})
    except ValueError:
        return {}
    config = {**switches.get("defaultConfig", {}), **switches.get("user", {}).get("config", {})}
    return {name: entry["value"] for name, entry in config.items() if isinstance(entry, dict) and "value" in entry}


def chunk_urls(home_html: str) -> list[str]:
    """``main`` plus every carrier chunk the page's webpack runtime can load."""
    pairs = CHUNK_PAIR_RE.findall(home_html)
    hashes = {i: v for i, v in pairs if CHUNK_HASH_RE.fullmatch(v)}
    names = {i: v for i, v in pairs if i in hashes and not CHUNK_HASH_RE.fullmatch(v)}
    urls = list(dict.fromkeys(MAIN_JS_RE.findall(home_html)))
    urls += [
        f"{SCRIPT_BASE}{name}.{hashes[i]}a.js"
        for i, name in names.items()
        if name.startswith(CARRIER_PREFIXES)
    ]
    return urls


class GQLRegistry:
    """Process-wide view of X's current GraphQL operations."""

    def __init__(self) -> None:
        self.enabled = os.environ.get("TWIKIT_GQL_REGISTRY", "1") != "0"
        self.operations: dict[str, Operation] = {}
        self.feature_values: dict[str, Any] = {}
        self.refreshed_at = 0.0
        self._chunk_ops: dict[str, dict[str, Operation]] = {}
        self._lock = asyncio.Lock()
        self._task: asyncio.Task | None = None

    def query_id(self, name: str, default: str) -> str:
        op = self.operations.get(name) if self.enabled else None
        return op.query_id if op else default

    def features(self, name: str, default: dict | None) -> dict | None:
        """The feature set the browser sends for ``name``; ``default`` if unknown.

        Values come from X's live config, then the static ``default``, then False.
        """
        op = self.operations.get(name) if self.enabled else None
        if default is None or op is None or not op.feature_switches:
            return default
        return {
            f: self.feature_values.get(f, default.get(f, False))
            for f in op.feature_switches
        }

    def resolve(self, url: str, features: dict | None) -> tuple[str, dict | None]:
        """Rewrite a ``.../graphql/<queryId>/<Name>`` URL and its features to the live ones."""
        prefix, _, tail = url.rpartition("/graphql/")
        if not prefix or "/" not in tail:
            return url, features
        static_id, name = tail.split("/", 1)
        live_id = self.query_id(name, static_id)
        if live_id != static_id:
            url = f"{prefix}/graphql/{live_id}/{name}"
        return url, self.features(name, features)

    def maybe_refresh(self, home_html: str, fetch: Callable[[str], Awaitable[str]] = fetch_public) -> None:
        """Start a background refresh if due; never blocks or raises into the caller."""
        if not self.enabled or not home_html:
            return
        if self._task is not None and not self._task.done():
            return
        if time.monotonic() - self.refreshed_at < REFRESH_INTERVAL_S and self.operations:
            return
        self._task = asyncio.create_task(self._refresh(home_html, fetch))

    async def _refresh(self, home_html: str, fetch: Callable[[str], Awaitable[str]]) -> None:
        async with self._lock:
            try:
                urls = chunk_urls(home_html)
                missing = [u for u in urls if u not in self._chunk_ops]
                limit = asyncio.Semaphore(FETCH_CONCURRENCY)

                async def fetch_one(u: str) -> str:
                    async with limit:
                        return await fetch(u)

                bodies = await asyncio.gather(*(fetch_one(u) for u in missing), return_exceptions=True)
                for url, body in zip(missing, bodies):
                    if isinstance(body, str):
                        self._chunk_ops[url] = parse_operations(body)
                operations: dict[str, Operation] = {}
                for url in urls:  # main first, so it wins a duplicate name
                    for name, op in self._chunk_ops.get(url, {}).items():
                        operations.setdefault(name, op)
                self._chunk_ops = {u: ops for u, ops in self._chunk_ops.items() if u in urls}
                if not operations:
                    logger.warning("GQL registry refresh found no operations; keeping previous state")
                    return
                self.operations = operations
                self.feature_values = parse_feature_values(home_html) or self.feature_values
                self.refreshed_at = time.monotonic()
                logger.info(
                    "GQL registry refreshed: %d operations from %d chunks (%d fetched)",
                    len(operations), len(urls), len(missing),
                )
            except Exception:  # a refresh must never break a request
                logger.exception("GQL registry refresh failed; keeping previous state")


REGISTRY = GQLRegistry()

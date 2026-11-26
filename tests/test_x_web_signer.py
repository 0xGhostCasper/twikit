"""The x-web build: x.com -> 307 /home, a signer chunk found through the entry bundle,
and wrapper ids next to the animation frames.

Since 2026-11-24 x serves a growing share of logged-in accounts its new x-web app.
For them ``GET https://x.com`` answers ``307 Location: /home`` and /home carries
the verification meta and the four loading-x-anim frames but no ondemand.s map.
The signer is the chunk ``entry-client-*.js -> <shared chunk> -> import(./X.js)``
loads; it has the same (a[N], 16) indices as ondemand.s, with this build's values
(11-26: [22, 40, 18, 0] against [23, 8, 28, 35] on the classic build). The shapes
below are cut from that day's bundles.
"""

import asyncio

import bs4
import pytest

from twikit.errors import AccountStateError
from twikit.x_client_transaction import utils
from twikit.x_client_transaction.transaction import (
    ClientTransaction,
    find_x_web_signer,
    signing_source,
    x_web_signer_candidates,
)

ENTRY = "https://abs.twimg.com/x-web/x-web/entry-client-D3IPuBng.js"
SHARED = "https://abs.twimg.com/x-web/x-web/assets/Bx6p0tyz.js"
SIGNER = "https://abs.twimg.com/x-web/x-web/assets/Bo_7AybE.js"

# The second path of each frame is 16 "C" rows of 11 numbers: 3+3 colours, a
# rotation and 4 cubic-bezier controls, as on x's page.
_ROWS = "C".join(f" {r * 9 % 256} 60 200 30 90 150 {r * 13 % 256} 40 80 160 220 " for r in range(16))
FRAME = (
    '<svg viewBox="0 0 24 24" id="loading-x-anim-{n}" aria-hidden="true"><g>'
    '<path d="M1 1"></path>'
    '<path d="M 10 30 C' + _ROWS + '"></path>'
    "</g></svg>"
)
X_WEB_HOME = (
    "<html><head>"
    '<meta name="twitter-site-verification" content="AAECAwQFBgcICQoLDA0ODxAREhMUFRYXGBkaGxwdHh8gISIjJCUmJygpKissLS4v"/>'
    '<style id="loading-x-anim-css">.x{}</style>'
    f'<script type="module" src="{ENTRY}"></script>'
    "</head><body>"
    '<div id="loading-x-anim-svgs">' + "".join(FRAME.format(n=n) for n in range(4)) + "</div>"
    "</body></html>"
)
CLASSIC_HOME = '<html><script>{,20113:"ondemand.s"},{,20113:"6f9eb54770ab2d0b"}</script></html>'

ENTRY_JS = (
    'const __vite__mapDeps=(i,m=__vite__mapDeps,d=(m.f||(m.f=["assets/CIOxRz11.js"])))=>i.map(i=>d[i]);'
    'import{n as e}from"./assets/y8ipOul8.js";import{Ed as $s}from"./assets/Bx6p0tyz.js";'
    "getClientTransactionId:(e,t)=>$s(e,t,py)"
)
SHARED_JS = (
    "x=A(()=>import(`./By2Tz0x0.js`).then(e=>({default:e.GpcOptOut})),__vite__mapDeps([1]));"
    "function Ms(){return Ls??=A(()=>import(`./Bo_7AybE.js`).then(e=>e.default()),__vite__mapDeps([0])),Ls}"
    "async function Ns(e,t,n){let r=await Ms();return await r(t,n)}"
    "function sye(e){return async function(t,n){let r=await Ns(t);let i=new Headers(t.headers);"
    "return i.set(`x-client-transaction-id`,r),n({...t,headers:i})}}"
)
SIGNER_JS = "function t(e,r){e-=228}x=(a[22],16),y=(b[40],16),z=(c[18],16),w=(d[0],16);export{o as default};"


class _Resp:
    def __init__(self, status=200, text="", headers=None):
        self.status_code = status
        self.text = text
        self.content = text.encode()
        self.headers = headers or {}


class _Session:
    def __init__(self, routes):
        self.routes = routes
        self.calls = []

    async def request(self, method, url, headers=None, data=None):
        self.calls.append(url)
        route = self.routes.get(url)
        if route is None:
            return _Resp(404, "")
        return route


def _x_web_routes(home_status=307):
    routes = {
        "https://x.com/home": _Resp(200, X_WEB_HOME),
        ENTRY: _Resp(200, ENTRY_JS),
        "https://abs.twimg.com/x-web/x-web/assets/y8ipOul8.js": _Resp(200, "export const n=1;"),
        SHARED: _Resp(200, SHARED_JS),
        SIGNER: _Resp(200, SIGNER_JS),
    }
    if home_status == 307:
        routes["https://x.com"] = _Resp(307, "", {"location": "/home"})
    else:
        routes["https://x.com"] = _Resp(200, X_WEB_HOME)
    return routes


# --- the /home redirect ------------------------------------------------------------


@pytest.mark.parametrize(
    "location, expected",
    [
        ("/home", "https://x.com/home"),
        ("https://x.com/home", "https://x.com/home"),
        ("/home?lang=en", "https://x.com/home?lang=en"),
        ("/i/flow/login", None),
        ("/account/access", None),
        ("https://evil.example/home", None),
    ],
)
def test_only_a_same_origin_home_redirect_is_followed(location, expected):
    assert utils.home_redirect_target(_Resp(307, "", {"location": location})) == expected


def test_a_200_is_not_a_redirect():
    assert utils.home_redirect_target(_Resp(200, "<html/>")) is None


def test_migration_follows_the_home_redirect():
    session = _Session(_x_web_routes())
    page = asyncio.run(utils.handle_x_migration(session, {}))
    assert page.select_one("[name='twitter-site-verification']") is not None
    assert session.calls[:2] == ["https://x.com", "https://x.com/home"]


def test_a_login_redirect_is_still_an_account_state():
    session = _Session({"https://x.com": _Resp(307, "", {"location": "/i/flow/login"})})
    with pytest.raises(AccountStateError):
        asyncio.run(utils.handle_x_migration(session, {}))


# --- the signer chunk --------------------------------------------------------------


def test_signer_candidates_put_the_tid_loader_first():
    assert x_web_signer_candidates(SHARED_JS)[0] == "./Bo_7AybE.js"


def test_find_x_web_signer_walks_entry_shared_signer():
    session = _Session(_x_web_routes())
    url, js = asyncio.run(find_x_web_signer(session, {}, X_WEB_HOME))
    assert url == SIGNER
    assert js == SIGNER_JS


def test_get_indices_on_an_x_web_page():
    session = _Session(_x_web_routes())
    soup = bs4.BeautifulSoup(X_WEB_HOME, "lxml")
    row, key_bytes = asyncio.run(ClientTransaction().get_indices(soup, session, {}))
    assert (row, list(key_bytes)) == (22, [40, 18, 0])


def test_no_signer_found_still_raises():
    routes = _x_web_routes()
    routes[SIGNER] = _Resp(200, "export{o as default};")
    soup = bs4.BeautifulSoup(X_WEB_HOME, "lxml")
    with pytest.raises(Exception, match="KEY_BYTE"):
        asyncio.run(ClientTransaction().get_indices(soup, _Session(routes), {}))


def test_signing_source_names_the_build():
    assert signing_source(CLASSIC_HOME) == "6f9eb54770ab2d0b"
    assert signing_source(X_WEB_HOME) == ENTRY
    assert signing_source("<html/>") is None


# --- the frames ----------------------------------------------------------------------


def test_frames_skip_the_wrappers():
    soup = bs4.BeautifulSoup(X_WEB_HOME, "lxml")
    frames = ClientTransaction().get_frames(soup)
    assert [f.get("id") for f in frames] == [f"loading-x-anim-{n}" for n in range(4)]


def test_full_init_on_an_x_web_account():
    ct = ClientTransaction()
    asyncio.run(ct.init(_Session(_x_web_routes()), {}))
    assert (ct.DEFAULT_ROW_INDEX, list(ct.DEFAULT_KEY_BYTES_INDICES)) == (22, [40, 18, 0])
    assert ct.animation_key
    assert ct.generate_transaction_id(method="GET", path="/i/api/graphql/x/SearchTimeline")

import re
import bs4
import math
import time
import random
import base64
import hashlib
from typing import Union, List
from functools import reduce
from urllib.parse import urljoin
from .cubic_curve import Cubic
from .interpolate import interpolate
from .rotation import convert_rotation_to_matrix
from .utils import float_to_hex, is_odd, base64_encode, handle_x_migration

# The signing chunk is ondemand.s on the logged-in build and sign.o on the
# x-web build the logged-out shell serves (twscrape#379); accept both, and use
# the matched chunk name in the CDN URL.
ON_DEMAND_FILE_REGEX = re.compile(
    r""",(\d+):["'](ondemand\.s|sign\.o)["']""",
    flags=(re.VERBOSE | re.MULTILINE),
)
ON_DEMAND_HASH_PATTERN = r',{}:["\']([0-9a-f]+)["\']'
INDICES_REGEX = re.compile(
    r"""(\(\w{1,2}\[(\d{1,2})\],\s*16\))+""", flags=(re.VERBOSE | re.MULTILINE)
)
# Fallback when the minifier stops using 1-2 char names or 1-2 digit indices
# (upstream d60/twikit PR #432). Only consulted if the strict form finds nothing.
LOOSE_INDICES_REGEX = re.compile(r"\[(\d+)\],\s*16\)")


def parse_key_byte_indices(ondemand_js: str) -> list[int]:
    """KEY_BYTE indices from the ondemand.s bundle: strict pattern first, loose fallback."""
    indices = [m.group(2) for m in INDICES_REGEX.finditer(ondemand_js)]
    if not indices:
        indices = [m.group(1) for m in LOOSE_INDICES_REGEX.finditer(ondemand_js)]
    return [int(i) for i in indices]


# x-web (the Vite build x serves a growing share of logged-in accounts since
# 2026-11-24) names no signing chunk in its page. The page loads
# entry-client-<hash>.js; one of the chunks that one imports sets
# x-client-transaction-id from a lazily imported chunk (11-26: `import(`./Bo_7AybE.js`)
# .then(e=>e.default())`). That chunk is the old ondemand.s signer under a content
# hash name: the same (a[N], 16) indices, different per build.
X_WEB_ENTRY_REGEX = re.compile(
    r"https://abs\.twimg\.com/x-web/x-web/entry-client-[A-Za-z0-9_-]+\.js"
)
_STATIC_IMPORT_REGEX = re.compile(r"""(?:\bfrom|\bimport)\s*["'`](\./[A-Za-z0-9_./-]+\.js)["'`]""")
_LAZY_IMPORT_REGEX = re.compile(r"""\bimport\(\s*["'`](\./[A-Za-z0-9_./-]+\.js)["'`]\s*\)""")
_DEFAULT_LAZY_IMPORT_REGEX = re.compile(
    r"""\bimport\(\s*["'`](\./[A-Za-z0-9_./-]+\.js)["'`]\s*\)\.then\(\s*(\w+)\s*=>\s*\2\.default\(\)\s*\)"""
)
_TID_HEADER = "x-client-transaction-id"
_FRAME_ID_REGEX = re.compile(r"loading-x-anim-\d+")
# How far before the header name the signer's lazy import sits (11-26: ~650 chars).
_TID_WINDOW = 2000
# Most chunks fetched to find the signer: entry imports, then signer candidates.
X_WEB_MAX_ENTRY_IMPORTS = 8
X_WEB_MAX_SIGNER_CANDIDATES = 4


def x_web_entry_url(page: str) -> Union[str, None]:
    """The x-web entry-client URL a home page loads, or None on the classic build."""
    match = X_WEB_ENTRY_REGEX.search(page)
    return match.group(0) if match else None


def signing_source(page: str) -> Union[str, None]:
    """What identifies a home page's KEY_BYTE indices without fetching anything.

    The classic build's ``ondemand.s``/``sign.o`` chunk hash, or the x-web entry
    URL (it changes with every x-web release). Pages with the same source sign
    with the same indices, so callers can cache them under it.
    """
    chunk = ON_DEMAND_FILE_REGEX.search(page)
    if chunk:
        file_hash = re.search(ON_DEMAND_HASH_PATTERN.format(chunk.group(1)), page)
        if file_hash:
            return file_hash.group(1)
    return x_web_entry_url(page)


def _unique(items):
    seen = set()
    out = []
    for item in items:
        if item not in seen:
            seen.add(item)
            out.append(item)
    return out


def x_web_signer_candidates(chunk_js: str) -> list[str]:
    """Relative URLs of the chunks a tid-setting chunk may load the signer from.

    A lazy import that both sits just before an ``x-client-transaction-id``
    reference and has the signer's loader shape (``import(...).then(e=>e.default())``)
    comes first, then the other lazy imports near the header (closest first), then
    the other loader-shaped ones.
    """
    near = []
    for match in re.finditer(re.escape(_TID_HEADER), chunk_js):
        window = chunk_js[max(0, match.start() - _TID_WINDOW):match.start()]
        near.extend(reversed(_LAZY_IMPORT_REGEX.findall(window)[-3:]))
    defaults = [m.group(1) for m in _DEFAULT_LAZY_IMPORT_REGEX.finditer(chunk_js)]
    both = [c for c in near if c in defaults]
    return _unique(both + near + defaults)


async def find_x_web_signer(session, headers, page: str):
    """``(url, js)`` of an x-web page's signing chunk, or None if it is not found.

    Walks entry-client -> its static imports -> the one that sets
    x-client-transaction-id -> its signer candidates, and returns the first
    candidate whose code carries the strict (a[N], 16) indices.
    """
    entry = x_web_entry_url(page)
    if entry is None:
        return None
    entry_js = (await session.request(method="GET", url=entry, headers=headers)).text
    for rel in _unique(_STATIC_IMPORT_REGEX.findall(entry_js))[:X_WEB_MAX_ENTRY_IMPORTS]:
        chunk_url = urljoin(entry, rel)
        chunk_js = (await session.request(method="GET", url=chunk_url, headers=headers)).text
        if _TID_HEADER not in chunk_js:
            continue
        for cand in x_web_signer_candidates(chunk_js)[:X_WEB_MAX_SIGNER_CANDIDATES]:
            signer_url = urljoin(chunk_url, cand)
            signer_js = (await session.request(method="GET", url=signer_url, headers=headers)).text
            if INDICES_REGEX.search(signer_js):
                return signer_url, signer_js
    return None


class ClientTransaction:
    ADDITIONAL_RANDOM_NUMBER = 3
    DEFAULT_KEYWORD = "obfiowerehiring"
    DEFAULT_ROW_INDEX = None
    DEFAULT_KEY_BYTES_INDICES = None

    def __init__(self):
        self.home_page_response = None
        self.key = None
        self.key_bytes = None
        self.animation_key = None

    async def init(self, session, headers):
        home_page_response = await handle_x_migration(session, headers)

        self.home_page_response = self.validate_response(home_page_response)
        # A 200 page that carries neither the verification meta nor any signing
        # chunk is the logged-out x-web shell: the session is dead/suspended, and
        # no amount of pool refreshing will mint a key from it.
        _shell = str(self.home_page_response)
        if (
            not self.home_page_response.select_one("[name='twitter-site-verification']")
            and not ON_DEMAND_FILE_REGEX.search(_shell)
        ):
            from twikit.errors import AccountStateError

            raise AccountStateError(
                "home not a logged-in app shell (no verification meta / signing "
                "chunk: suspended/locked/logged-out account)"
            )
        # Skip the expensive JS file fetch if indices were pre-populated
        # (e.g. by a shared bootstrap). The indices are session-independent
        # but the key/animation_key are derived from the session-specific
        # home page and must always be computed fresh.
        if self.DEFAULT_ROW_INDEX is None or self.DEFAULT_KEY_BYTES_INDICES is None:
            self.DEFAULT_ROW_INDEX, self.DEFAULT_KEY_BYTES_INDICES = await self.get_indices(
                self.home_page_response, session, headers
            )
        self.key = self.get_key(response=self.home_page_response)
        self.key_bytes = self.get_key_bytes(key=self.key)
        self.animation_key = self.get_animation_key(
            key_bytes=self.key_bytes, response=self.home_page_response
        )

    async def get_indices(self, home_page_response, session, headers):
        key_byte_indices = []
        response = self.validate_response(home_page_response) or self.home_page_response
        response_str = str(response)

        on_demand_file = ON_DEMAND_FILE_REGEX.search(response_str)
        if on_demand_file:
            on_demand_file_index, chunk_name = on_demand_file.group(1), on_demand_file.group(2)
            hash_regex = re.compile(ON_DEMAND_HASH_PATTERN.format(on_demand_file_index))
            hash_match = hash_regex.search(response_str)
            if hash_match:
                filename = hash_match.group(1)
                on_demand_file_url = f"https://abs.twimg.com/responsive-web/client-web/{chunk_name}.{filename}a.js"
                on_demand_file_response = await session.request(
                    method="GET", url=on_demand_file_url, headers=headers
                )
                key_byte_indices = parse_key_byte_indices(str(on_demand_file_response.text))
        elif x_web_entry_url(response_str):
            signer = await find_x_web_signer(session, headers, response_str)
            if signer is not None:
                key_byte_indices = parse_key_byte_indices(signer[1])
        if not key_byte_indices:
            raise Exception("Couldn't get KEY_BYTE indices")
        return key_byte_indices[0], key_byte_indices[1:]

    def validate_response(self, response: bs4.BeautifulSoup):
        if not isinstance(response, bs4.BeautifulSoup):
            raise Exception("invalid response")
        return response

    def get_key(self, response=None):
        response = self.validate_response(response) or self.home_page_response
        # <meta name="twitter-site-verification" content="mentU...+1yPz..../IcNS+......./RaF...R+b"/>
        element = response.select_one("[name='twitter-site-verification']")
        if not element:
            raise Exception("Couldn't get key from the page source")
        return element.get("content")

    def get_key_bytes(self, key: str):
        return list(base64.b64decode(bytes(key, "utf-8")))

    def get_frames(self, response=None):
        # loading-x-anim-0...loading-x-anim-3. The x-web page also carries
        # loading-x-anim-svgs (the frames' wrapper) and loading-x-anim-css, so
        # take the numbered frames only.
        response = self.validate_response(response) or self.home_page_response
        return [
            frame
            for frame in response.select("[id^='loading-x-anim-']")
            if _FRAME_ID_REGEX.fullmatch(frame.get("id", ""))
        ]

    def get_2d_array(
        self, key_bytes: List[Union[float, int]], response, frames: bs4.ResultSet = None
    ):
        if not frames:
            frames = self.get_frames(response)
        # return list(list(frames[key[5] % 4].children)[0].children)[1].get("d")[9:].split("C")
        return [
            [int(x) for x in re.sub(r"[^\d]+", " ", item).strip().split()]
            for item in list(list(frames[key_bytes[5] % 4].children)[0].children)[1]
            .get("d")[9:]
            .split("C")
        ]

    def solve(self, value, min_val, max_val, rounding: bool):
        result = value * (max_val - min_val) / 255 + min_val
        return math.floor(result) if rounding else round(result, 2)

    def animate(self, frames, target_time):
        # from_color = f"#{''.join(['{:x}'.format(digit) for digit in frames[:3]])}"
        # to_color = f"#{''.join(['{:x}'.format(digit) for digit in frames[3:6]])}"
        # from_rotation = "rotate(0deg)"
        # to_rotation = f"rotate({solve(frames[6], 60, 360, True)}deg)"
        # easing_values = [solve(value, -1 if count % 2 else 0, 1, False)
        #                  for count, value in enumerate(frames[7:])]
        # easing = f"cubic-bezier({','.join([str(value) for value in easing_values])})"
        # current_time = round(target_time / 10) * 10

        from_color = [float(item) for item in [*frames[:3], 1]]
        to_color = [float(item) for item in [*frames[3:6], 1]]
        from_rotation = [0.0]
        to_rotation = [self.solve(float(frames[6]), 60.0, 360.0, True)]
        frames = frames[7:]
        curves = [
            self.solve(float(item), is_odd(counter), 1.0, False)
            for counter, item in enumerate(frames)
        ]
        cubic = Cubic(curves)
        val = cubic.get_value(target_time)
        color = interpolate(from_color, to_color, val)
        color = [value if value > 0 else 0 for value in color]
        rotation = interpolate(from_rotation, to_rotation, val)
        matrix = convert_rotation_to_matrix(rotation[0])
        # str_arr = [format(int(round(color[i])), '02x') for i in range(len(color) - 1)]
        # str_arr = [format(int(round(color[i])), 'x') for i in range(len(color) - 1)]
        str_arr = [format(round(value), "x") for value in color[:-1]]
        for value in matrix:
            rounded = round(value, 2)
            if rounded < 0:
                rounded = -rounded
            hex_value = float_to_hex(rounded)
            str_arr.append(
                f"0{hex_value}".lower()
                if hex_value.startswith(".")
                else hex_value if hex_value else "0"
            )
        str_arr.extend(["0", "0"])
        animation_key = re.sub(r"[.-]", "", "".join(str_arr))
        return animation_key

    def get_animation_key(self, key_bytes, response):
        total_time = 4096
        # row_index, frame_time = [key_bytes[2] % 16, key_bytes[12] % 16 * (key_bytes[14] % 16) * (key_bytes[7] % 16)]
        # row_index, frame_time = [key_bytes[2] % 16, key_bytes[2] % 16 * (key_bytes[42] % 16) * (key_bytes[45] % 16)]

        row_index = key_bytes[self.DEFAULT_ROW_INDEX] % 16
        frame_time = reduce(
            lambda num1, num2: num1 * num2,
            [key_bytes[index] % 16 for index in self.DEFAULT_KEY_BYTES_INDICES],
        )
        arr = self.get_2d_array(key_bytes, response)
        frame_row = arr[row_index]

        target_time = float(frame_time) / total_time
        animation_key = self.animate(frame_row, target_time)
        return animation_key

    def generate_transaction_id(
        self,
        method: str,
        path: str,
        response=None,
        key=None,
        animation_key=None,
        time_now=None,
    ):
        time_now = time_now or math.floor(
            (time.time() * 1000 - 1682924400 * 1000) / 1000
        )
        time_now_bytes = [(time_now >> (i * 8)) & 0xFF for i in range(4)]
        key = key or self.key or self.get_key(response)
        key_bytes = self.get_key_bytes(key)
        animation_key = (
            animation_key
            or self.animation_key
            or self.get_animation_key(key_bytes, response)
        )
        # hash_val = hashlib.sha256(f"{method}!{path}!{time_now}bird{animation_key}".encode()).digest()
        hash_val = hashlib.sha256(
            f"{method}!{path}!{time_now}{self.DEFAULT_KEYWORD}{animation_key}".encode()
        ).digest()
        # hash_bytes = [int(hash_val[i]) for i in range(len(hash_val))]
        hash_bytes = list(hash_val)
        random_num = random.randint(0, 255)
        bytes_arr = [
            *key_bytes,
            *time_now_bytes,
            *hash_bytes[:16],
            self.ADDITIONAL_RANDOM_NUMBER,
        ]
        out = bytearray([random_num, *[item ^ random_num for item in bytes_arr]])
        return base64_encode(out).strip("=")

import re
import bs4
import base64
from typing import Union
from urllib.parse import urljoin, urlparse

_REDIRECT_STATUSES = (301, 302, 303, 307, 308)


def home_redirect_target(response) -> Union[str, None]:
    """The x.com/home URL a redirect points at, or None.

    Since 2026-11-24 x answers ``GET https://x.com`` with ``307 Location: /home`` for
    the logged-in accounts it serves its new x-web build, and /home is the full app
    shell. Only that same-origin hop is followed; any other redirect (login flow,
    /account/access, logout) stays an account state.
    """
    if getattr(response, "status_code", 200) not in _REDIRECT_STATUSES:
        return None
    headers = getattr(response, "headers", None) or {}
    location = headers.get("location") or headers.get("Location")
    if not location:
        return None
    target = urljoin("https://x.com/", location)
    parsed = urlparse(target)
    if parsed.scheme != "https" or parsed.netloc not in ("x.com", "www.x.com"):
        return None
    if parsed.path.rstrip("/") != "/home":
        return None
    return target


def _raise_if_not_app_shell(response, first: bool) -> None:
    """A home page that is not the logged-in app shell can never yield signing
    inputs. 403/404 (and a redirect anywhere but x.com/home, which httpx does not
    follow here) mean x is treating the session as suspended/locked/logged-out — an
    account state, not a parse problem — so raise AccountStateError instead of
    letting the parse fail with a bogus KEY_BYTE error that pool-thrashes. Other
    statuses keep their old crash-late behaviour (429 HTML is an edge rate limit, not
    a verdict)."""
    from twikit.errors import AccountStateError

    status = getattr(response, "status_code", 200)
    if status in (301, 302, 303, 307, 308, 403, 404):
        raise AccountStateError(
            f"home not a logged-in app shell (status {status}: "
            "suspended/locked/logged-out account)"
        )


async def handle_x_migration(session, headers):
    home_page = None
    migration_redirection_regex = re.compile(
        r"""(http(?:s)?://(?:www\.)?(twitter|x){1}\.com(/x)?/migrate([/?])?tok=[a-zA-Z0-9%\-_]+)+""", re.VERBOSE)
    response = await session.request(method="GET", url="https://x.com", headers=headers)
    home = home_redirect_target(response)
    if home is not None:
        response = await session.request(method="GET", url=home, headers=headers)
    _raise_if_not_app_shell(response, first=True)
    home_page = bs4.BeautifulSoup(response.content, 'lxml')
    migration_url = home_page.select_one("meta[http-equiv='refresh']")
    migration_redirection_url = re.search(migration_redirection_regex, str(
        migration_url)) or re.search(migration_redirection_regex, str(response.content))
    if migration_redirection_url:
        response = await session.request(method="GET", url=migration_redirection_url.group(0), headers=headers)
        _raise_if_not_app_shell(response, first=False)
        home_page = bs4.BeautifulSoup(response.content, 'lxml')
    migration_form = home_page.select_one("form[name='f']") or home_page.select_one(f"form[action='https://x.com/x/migrate']")
    if migration_form:
        url = migration_form.attrs.get("action", "https://x.com/x/migrate") + "/?mx=2"
        method = migration_form.attrs.get("method", "POST")
        request_payload = {input_field.get("name"): input_field.get("value") for input_field in migration_form.select("input")}
        response = await session.request(method=method, url=url, data=request_payload, headers=headers)
        _raise_if_not_app_shell(response, first=False)
        home_page = bs4.BeautifulSoup(response.content, 'lxml')
    return home_page


def float_to_hex(x):
    result = []
    quotient = int(x)
    fraction = x - quotient

    while quotient > 0:
        quotient = int(x / 16)
        remainder = int(x - (float(quotient) * 16))

        if remainder > 9:
            result.insert(0, chr(remainder + 55))
        else:
            result.insert(0, str(remainder))

        x = float(quotient)

    if fraction == 0:
        return ''.join(result)

    result.append('.')

    while fraction > 0:
        fraction *= 16
        integer = int(fraction)
        fraction -= float(integer)

        if integer > 9:
            result.append(chr(integer + 55))
        else:
            result.append(str(integer))

    return ''.join(result)


def is_odd(num: Union[int, float]):
    if num % 2:
        return -1.0
    return 0.0


def base64_encode(string):
    string = string.encode() if isinstance(string, str) else string
    return base64.b64encode(string).decode()


def base64_decode(input):
    try:
        data = base64.b64decode(input)
        return data.decode()
    except Exception:
        # return bytes(input, "utf-8")
        return list(bytes(input, "utf-8"))


if __name__ == "__main__":
    pass

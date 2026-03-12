from __future__ import annotations

from dataclasses import dataclass, field
from typing import TypedDict, TYPE_CHECKING

if TYPE_CHECKING:
    from .client.client import Client


@dataclass(eq=False, repr=False)
class Trend:
    """
    Attributes
    ----------
    name : :class:`str`
        The name of the trending topic.
    tweets_count : :class:`int`
        The count of tweets associated with the trend.
    domain_context : :class:`str`
        The context or domain associated with the trend.
    grouped_trends : :class:`list`[:class:`str`]
        A list of trend names grouped under the main trend.
    """
    _client: Client = field(repr=False, compare=False)
    name: str = ''
    tweets_count: int | None = None
    domain_context: str | None = None
    grouped_trends: list[str] = field(default_factory=list)

    @classmethod
    def from_data(cls, client: Client, data: dict) -> Trend:
        metadata: dict = data['trendMetadata']
        return cls(
            _client=client,
            name=data['name'],
            tweets_count=metadata.get('metaDescription'),
            domain_context=metadata.get('domainContext'),
            grouped_trends=[
                trend['name'] for trend in data.get('groupedTrends', [])
            ],
        )

    def __repr__(self) -> str:
        return f'<Trend name="{self.name}">'


class PlaceTrends(TypedDict):
    trends: list[PlaceTrend]
    as_of: str
    created_at: str
    locations: dict


@dataclass(eq=False, repr=False)
class PlaceTrend:
    """
    Attributes
    ----------
    name : :class:`str`
        The name of the trend.
    url : :class:`str`
        The URL to view the trend.
    query : :class:`str`
        The search query corresponding to the trend.
    tweet_volume : :class:`int`
        The volume of tweets associated with the trend.
    """
    _client: Client = field(repr=False, compare=False)
    name: str = ''
    url: str = ''
    promoted_content: None = None
    query: str = ''
    tweet_volume: int = 0

    @classmethod
    def from_data(cls, client: Client, data: dict) -> PlaceTrend:
        return cls(
            _client=client,
            name=data['name'],
            url=data['url'],
            promoted_content=data['promoted_content'],
            query=data['query'],
            tweet_volume=data['tweet_volume'],
        )

    def __repr__(self) -> str:
        return f'<PlaceTrend name="{self.name}">'


@dataclass(eq=False, repr=False)
class Location:
    _client: Client = field(repr=False, compare=False)
    woeid: int = 0
    country: str = ''
    country_code: str = ''
    name: str = ''
    parentid: int = 0
    placeType: dict = field(default_factory=dict)
    url: str = ''

    @classmethod
    def from_data(cls, client: Client, data: dict) -> Location:
        return cls(
            _client=client,
            woeid=data['woeid'],
            country=data['country'],
            country_code=data['countryCode'],
            name=data['name'],
            parentid=data['parentid'],
            placeType=data['placeType'],
            url=data['url'],
        )

    async def get_trends(self) -> PlaceTrends:
        return await self._client.get_place_trends(self.woeid)

    def __repr__(self) -> str:
        return f'<Location name="{self.name}" woeid={self.woeid}>'

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Location) and self.woeid == other.woeid

from __future__ import annotations

import warnings
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from .errors import TwitterException

if TYPE_CHECKING:
    from .client.client import Client


@dataclass(eq=False, repr=False)
class Place:
    """
    Attributes
    ----------
    id : :class:`str`
        The ID of the place.
    name : :class:`str`
        The name of the place.
    full_name : :class:`str`
        The full name of the place.
    country : :class:`str`
        The country where the place is located.
    country_code : :class:`str`
        The ISO 3166-1 alpha-2 country code of the place.
    url : :class:`str`
        The URL providing more information about the place.
    place_type : :class:`str`
        The type of place.
    attributes : :class:`dict`
    bounding_box : :class:`dict`
        The bounding box that defines the geographical area of the place.
    centroid : list[:class:`float`] | None
        The geographical center of the place, represented by latitude and
        longitude.
    contained_within : list[:class:`.Place`]
        A list of places that contain this place.
    """
    _client: Client = field(repr=False, compare=False)
    id: str = ''
    name: str = ''
    full_name: str = ''
    country: str = ''
    country_code: str = ''
    url: str = ''
    place_type: str = ''
    attributes: dict | None = None
    bounding_box: dict = field(default_factory=dict)
    centroid: list[float] | None = None
    contained_within: list[Place] = field(default_factory=list)

    @classmethod
    def from_data(cls, client: Client, data: dict) -> Place:
        return cls(
            _client=client,
            id=data['id'],
            name=data['name'],
            full_name=data['full_name'],
            country=data['country'],
            country_code=data['country_code'],
            url=data['url'],
            place_type=data['place_type'],
            attributes=data.get('attributes'),
            bounding_box=data['bounding_box'],
            centroid=data.get('centroid'),
            contained_within=[
                Place.from_data(client, place)
                for place in data.get('contained_within', [])
            ],
        )

    async def update(self) -> None:
        new = self._client.get_place(self.id)
        await self.__dict__.update(new.__dict__)

    def __repr__(self) -> str:
        return f'<Place id="{self.id}" name="{self.name}">'

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Place) and self.id == other.id


def _places_from_response(client: Client, response: dict) -> list[Place]:
    if 'errors' in response:
        e = response['errors'][0]
        # No data available for the given coordinate.
        if e['code'] == 6:
            warnings.warn(e['message'])
        else:
            raise TwitterException(e['message'])

    places = response['result']['places'] if 'result' in response else []
    return [Place.from_data(client, place) for place in places]

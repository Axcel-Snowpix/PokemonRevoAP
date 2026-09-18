from __future__ import annotations

from typing import TYPE_CHECKING, Optional, NamedTuple

from BaseClasses import Location

from . import items

if TYPE_CHECKING:
    from .world import PBRWorld


class PBRLocationData(NamedTuple):
    """
    This class represents the data for a location in Pokémon Battle Revolution.

    :param group: The group the location is in.
    :param code: The unique code identifier for the location.
    :param region: The name of the region where the location resides.
    :param value: A special value used for checking the location.
    """

    group: str
    code: Optional[int]
    region: str
    value: Optional[int] = None


class PBRLocation(Location):
    game = "Pokémon Battle Revolution"


LOCATION_TABLE: dict[str, PBRLocationData] = {
    "Gateway Colosseum - Clear Check #1":     PBRLocationData("Colosseum Clears", 1,    "Gateway Colosseum",     0x124F0),
    "Gateway Colosseum - Clear Check #2":     PBRLocationData("Colosseum Clears", 2,    "Gateway Colosseum",     0x124F0),
    "Main Street Colosseum - Clear Check #1": PBRLocationData("Colosseum Clears", 3,    "Main Street Colosseum", 0x124F7),
    "Main Street Colosseum - Clear Check #2": PBRLocationData("Colosseum Clears", 4,    "Main Street Colosseum", 0x124F7),
    "Waterfall Colosseum - Clear Check #1":   PBRLocationData("Colosseum Clears", 5,    "Waterfall Colosseum",   0x124F6),
    "Waterfall Colosseum - Clear Check #2":   PBRLocationData("Colosseum Clears", 6,    "Waterfall Colosseum",   0x124F6),
    "Neon Colosseum - Clear Check #1":        PBRLocationData("Colosseum Clears", 7,    "Neon Colosseum",        0x124F5),
    "Neon Colosseum - Clear Check #2":        PBRLocationData("Colosseum Clears", 8,    "Neon Colosseum",        0x124F5),
    "Crystal Colosseum - Clear Check #1":     PBRLocationData("Colosseum Clears", 9,    "Crystal Colosseum",     0x124F4),
    "Crystal Colosseum - Clear Check #2":     PBRLocationData("Colosseum Clears", 10,   "Crystal Colosseum",     0x124F4),
    "Sunny Park Colosseum - Clear Check #1":  PBRLocationData("Colosseum Clears", 11,   "Sunny Park Colosseum",  0x124FB),
    "Sunny Park Colosseum - Clear Check #2":  PBRLocationData("Colosseum Clears", 12,   "Sunny Park Colosseum",  0x124FB),
    "Magma Colosseum - Clear Check #1":       PBRLocationData("Colosseum Clears", 13,   "Magma Colosseum",       0x124FA),
    "Magma Colosseum - Clear Check #2":       PBRLocationData("Colosseum Clears", 14,   "Magma Colosseum",       0x124FA),
    "Courtyard Colosseum - Clear Check #1":   PBRLocationData("Colosseum Clears", 15,   "Courtyard Colosseum",   0x124F9),
    "Courtyard Colosseum - Clear Check #2":   PBRLocationData("Colosseum Clears", 16,   "Courtyard Colosseum",   0x124F9),
    "Sunset Colosseum - Clear Check #1":      PBRLocationData("Colosseum Clears", 17,   "Sunset Colosseum",      0x124F8),
    "Sunset Colosseum - Clear Check #2":      PBRLocationData("Colosseum Clears", 18,   "Sunset Colosseum",      0x124F8),
    "Stargazer Colosseum - Clear":            PBRLocationData("Colosseum Clears", None, "Stargazer Colosseum",   0x124FF),

    "Gateway Colosseum - Borrow Cyndy's Rental Pass":   PBRLocationData("Rental Pass Checks", 19, "Gateway Colosseum", 0),
    "Gateway Colosseum - Borrow Nate's Rental Pass":    PBRLocationData("Rental Pass Checks", 20, "Gateway Colosseum", 1),
    "Gateway Colosseum - Borrow Tommy's Rental Pass":   PBRLocationData("Rental Pass Checks", 21, "Gateway Colosseum", 2),
    "Gateway Colosseum - Borrow Daisy's Rental Pass":   PBRLocationData("Rental Pass Checks", 22, "Gateway Colosseum", 3),
    "Gateway Colosseum - Borrow Joel's Rental Pass":    PBRLocationData("Rental Pass Checks", 23, "Gateway Colosseum", 4),
    "Gateway Colosseum - Borrow Natalie's Rental Pass": PBRLocationData("Rental Pass Checks", 24, "Gateway Colosseum", 5),
}


def get_location_names_with_ids(location_names: list[str]) -> dict[str, int | None]:
    return {location_name: LOCATION_TABLE[location_name].code for location_name in location_names}


def create_all_locations(world: PBRWorld) -> None:
    for location, data in LOCATION_TABLE.items():
        if data.code == None:
            region = world.get_region(data.region)
            region.add_event(
                location, "Victory", location_type=PBRLocation, item_type=items.PBRItem
            )
        elif data.group != "Rental Pass Checks" or world.options.randomize_rental_passes:
            region = world.get_region(data.region)
            region.add_locations({location: data.code}, PBRLocation)

location_name_groups = {
    "Gateway Colosseum": set(),
    "Main Street Colosseum": set(),
    "Waterfall Colosseum": set(),
    "Neon Colosseum": set(),
    "Crystal Colosseum": set(),
    "Sunny Park Colosseum": set(),
    "Magma Colosseum": set(),
    "Courtyard Colosseum": set(),
    "Sunset Colosseum": set(),
    "Stargazer Colosseum": set(),
    "Rental Pass Checks": set(),
}
for item, data in LOCATION_TABLE.items():
    if data.group in location_name_groups:
        location_name_groups[data.group].add(item)
    elif data.region in location_name_groups:
        location_name_groups[data.region].add(item)
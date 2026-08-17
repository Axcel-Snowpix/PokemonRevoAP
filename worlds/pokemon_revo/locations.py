from __future__ import annotations

from typing import TYPE_CHECKING, Optional, NamedTuple

from BaseClasses import ItemClassification, Location

from . import items

if TYPE_CHECKING:
    from .world import PBRWorld


class PBRLocationData(NamedTuple):
    """
    This class represents the data for a location in Pokémon Battle Revolution.

    :param group: The group the location is in.
    :param code: The unique code identifier for the location.
    :param region: The name of the region where the location resides.
    :param offset: The offset used to find the location in memory.
    """

    group: str
    code: Optional[int]
    region: str
    offset: Optional[int] = None


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

    "Gateway Colosseum - Obtain Cyndy's Rental Pass":   PBRLocationData("Rental Pass Checks", 19, "Gateway Colosseum", 0x23A39),
    "Gateway Colosseum - Obtain Nate's Rental Pass":    PBRLocationData("Rental Pass Checks", 20, "Gateway Colosseum", 0x24125),
    "Gateway Colosseum - Obtain Tommy's Rental Pass":   PBRLocationData("Rental Pass Checks", 21, "Gateway Colosseum", 0x24811),
    "Gateway Colosseum - Obtain Daisy's Rental Pass":   PBRLocationData("Rental Pass Checks", 22, "Gateway Colosseum", 0x24EFD),
    "Gateway Colosseum - Obtain Joel's Rental Pass":    PBRLocationData("Rental Pass Checks", 23, "Gateway Colosseum", 0x255E9),
    "Gateway Colosseum - Obtain Natalie's Rental Pass": PBRLocationData("Rental Pass Checks", 24, "Gateway Colosseum", 0x25CD5),
}


def get_location_names_with_ids(location_names: list[str]) -> dict[str, int | None]:
    return {location_name: LOCATION_TABLE[location_name].code for location_name in location_names}


def create_all_locations(world: PBRWorld) -> None:
    create_locations(world)


def create_locations(world: PBRWorld) -> None:
    for location in LOCATION_TABLE:
        if LOCATION_TABLE[location].code == None:
            region = world.get_region(LOCATION_TABLE[location].region)
            region.add_event(
                location, "Victory", location_type=PBRLocation, item_type=items.PBRItem
            )
        elif LOCATION_TABLE[location].group == "Rental Pass Checks":
            if world.options.randomize_rental_passes:
                region = world.get_region(LOCATION_TABLE[location].region)
                region.add_locations({location: LOCATION_TABLE[location].code}, PBRLocation)
        else:
            region = world.get_region(LOCATION_TABLE[location].region)
            region.add_locations({location: LOCATION_TABLE[location].code}, PBRLocation)
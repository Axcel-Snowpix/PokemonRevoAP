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
    "Gateway Colosseum - Clear Check #1":     PBRLocationData("Colosseum Clears", 1,    "Gateway Colosseum",     0x12870),
    "Gateway Colosseum - Clear Check #2":     PBRLocationData("Colosseum Clears", 2,    "Gateway Colosseum",     0x12870),
    "Main Street Colosseum - Clear Check #1": PBRLocationData("Colosseum Clears", 3,    "Main Street Colosseum", 0x12877),
    "Main Street Colosseum - Clear Check #2": PBRLocationData("Colosseum Clears", 4,    "Main Street Colosseum", 0x12877),
    "Waterfall Colosseum - Clear Check #1":   PBRLocationData("Colosseum Clears", 5,    "Waterfall Colosseum",   0x12876),
    "Waterfall Colosseum - Clear Check #2":   PBRLocationData("Colosseum Clears", 6,    "Waterfall Colosseum",   0x12876),
    "Neon Colosseum - Clear Check #1":        PBRLocationData("Colosseum Clears", 7,    "Neon Colosseum",        0x12875),
    "Neon Colosseum - Clear Check #2":        PBRLocationData("Colosseum Clears", 8,    "Neon Colosseum",        0x12875),
    "Crystal Colosseum - Clear Check #1":     PBRLocationData("Colosseum Clears", 9,    "Crystal Colosseum",     0x12874),
    "Crystal Colosseum - Clear Check #2":     PBRLocationData("Colosseum Clears", 10,   "Crystal Colosseum",     0x12874),
    "Sunny Park Colosseum - Clear Check #1":  PBRLocationData("Colosseum Clears", 11,   "Sunny Park Colosseum",  0x1287B),
    "Sunny Park Colosseum - Clear Check #2":  PBRLocationData("Colosseum Clears", 12,   "Sunny Park Colosseum",  0x1287B),
    "Magma Colosseum - Clear Check #1":       PBRLocationData("Colosseum Clears", 13,   "Magma Colosseum",       0x1287A),
    "Magma Colosseum - Clear Check #2":       PBRLocationData("Colosseum Clears", 14,   "Magma Colosseum",       0x1287A),
    "Courtyard Colosseum - Clear Check #1":   PBRLocationData("Colosseum Clears", 15,   "Courtyard Colosseum",   0x12879),
    "Courtyard Colosseum - Clear Check #2":   PBRLocationData("Colosseum Clears", 16,   "Courtyard Colosseum",   0x12879),
    "Sunset Colosseum - Clear Check #1":      PBRLocationData("Colosseum Clears", 17,   "Sunset Colosseum",      0x12878),
    "Sunset Colosseum - Clear Check #2":      PBRLocationData("Colosseum Clears", 18,   "Sunset Colosseum",      0x12878),
    "Stargazer Colosseum - Clear":            PBRLocationData("Colosseum Clears", None, "Stargazer Colosseum",   0x1287F),

    "Gateway Colosseum - Obtain Cyndy's Rental Pass":   PBRLocationData("Rental Pass Checks", 19, "Gateway Colosseum", 0x23DB9),
    "Gateway Colosseum - Obtain Nate's Rental Pass":    PBRLocationData("Rental Pass Checks", 20, "Gateway Colosseum", 0x244A5),
    "Gateway Colosseum - Obtain Tommy's Rental Pass":   PBRLocationData("Rental Pass Checks", 21, "Gateway Colosseum", 0x24B91),
    "Gateway Colosseum - Obtain Daisy's Rental Pass":   PBRLocationData("Rental Pass Checks", 22, "Gateway Colosseum", 0x2527D),
    "Gateway Colosseum - Obtain Joel's Rental Pass":    PBRLocationData("Rental Pass Checks", 23, "Gateway Colosseum", 0x25969),
    "Gateway Colosseum - Obtain Natalie's Rental Pass": PBRLocationData("Rental Pass Checks", 24, "Gateway Colosseum", 0x26055),
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
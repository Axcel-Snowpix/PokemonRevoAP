from __future__ import annotations

from typing import TYPE_CHECKING, Optional, NamedTuple

from BaseClasses import Location

from Utils import logging

from . import items

if TYPE_CHECKING:
    from .world import PBRWorld


class PBRLocationData(NamedTuple):
    """
    This class represents the data for a location in Pokémon Battle Revolution.

    :param group: The group the location is in.
    :param code: The unique code identifier for the location.
    :param region: The name of the region where the location resides.
    :param offset: The offset of the location's place in memory.
    :param bit: The bit to check for if the location has been gotten.
    """

    group: str
    code: Optional[int]
    region: str
    offset: Optional[int] = None
    bit: Optional[int] = None


class PBRLocation(Location):
    game = "Pokémon Battle Revolution"


LOCATION_TABLE: dict[str, PBRLocationData] = {
    "Gateway Colosseum - Clear Check #1": PBRLocationData("Colosseum Clears", 1, "Gateway Colosseum", 0x124F0),
    "Gateway Colosseum - Clear Check #2": PBRLocationData("Colosseum Clears", 2, "Gateway Colosseum", 0x124F0),
    "Main Street Colosseum - Clear Check #1": PBRLocationData("Colosseum Clears", 3, "Main Street Colosseum", 0x124F7),
    "Main Street Colosseum - Clear Check #2": PBRLocationData("Colosseum Clears", 4, "Main Street Colosseum", 0x124F7),
    "Waterfall Colosseum - Clear Check #1": PBRLocationData("Colosseum Clears", 5, "Waterfall Colosseum", 0x124F6),
    "Waterfall Colosseum - Clear Check #2": PBRLocationData("Colosseum Clears", 6, "Waterfall Colosseum", 0x124F6),
    "Neon Colosseum - Clear Check #1": PBRLocationData("Colosseum Clears", 7, "Neon Colosseum", 0x124F5),
    "Neon Colosseum - Clear Check #2": PBRLocationData("Colosseum Clears", 8, "Neon Colosseum", 0x124F5),
    "Crystal Colosseum - Clear Check #1": PBRLocationData("Colosseum Clears", 9, "Crystal Colosseum", 0x124F4),
    "Crystal Colosseum - Clear Check #2": PBRLocationData("Colosseum Clears", 10, "Crystal Colosseum", 0x124F4),
    "Sunny Park Colosseum - Clear Check #1": PBRLocationData("Colosseum Clears", 11, "Sunny Park Colosseum", 0x124FB),
    "Sunny Park Colosseum - Clear Check #2": PBRLocationData("Colosseum Clears", 12, "Sunny Park Colosseum", 0x124FB),
    "Magma Colosseum - Clear Check #1": PBRLocationData("Colosseum Clears", 13, "Magma Colosseum", 0x124FA),
    "Magma Colosseum - Clear Check #2": PBRLocationData("Colosseum Clears", 14, "Magma Colosseum", 0x124FA),
    "Courtyard Colosseum - Clear Check #1": PBRLocationData("Colosseum Clears", 15, "Courtyard Colosseum", 0x124F9),
    "Courtyard Colosseum - Clear Check #2": PBRLocationData("Colosseum Clears", 16, "Courtyard Colosseum", 0x124F9),
    "Sunset Colosseum - Clear Check #1": PBRLocationData("Colosseum Clears", 17, "Sunset Colosseum", 0x124F8),
    "Sunset Colosseum - Clear Check #2": PBRLocationData("Colosseum Clears", 18, "Sunset Colosseum", 0x124F8),
    "Stargazer Colosseum - Clear Check #1": PBRLocationData("Colosseum Clears", 19, "Stargazer Colosseum", 0x124FF),
    "Stargazer Colosseum - Clear Check #2": PBRLocationData("Colosseum Clears", 20, "Stargazer Colosseum", 0x124FF),

    "Stargazer Colosseum - Goal": PBRLocationData("Colosseum Clears", None, "Stargazer Colosseum", 0x124FF),

    "Gateway Colosseum - Borrow Cyndy's Rental Pass": PBRLocationData("Rental Pass Checks", 21, "Gateway Colosseum", 0x69021, 0),
    "Gateway Colosseum - Borrow Nate's Rental Pass": PBRLocationData("Rental Pass Checks", 22, "Gateway Colosseum", 0x69021, 1),
    "Gateway Colosseum - Borrow Tommy's Rental Pass": PBRLocationData("Rental Pass Checks", 23, "Gateway Colosseum", 0x69021, 2),
    "Gateway Colosseum - Borrow Daisy's Rental Pass": PBRLocationData("Rental Pass Checks", 24, "Gateway Colosseum", 0x69021, 3),
    "Gateway Colosseum - Borrow Joel's Rental Pass": PBRLocationData("Rental Pass Checks", 25, "Gateway Colosseum", 0x69021, 4),
    "Gateway Colosseum - Borrow Natalie's Rental Pass": PBRLocationData("Rental Pass Checks", 26, "Gateway Colosseum", 0x69021, 5),

    "Gateway Colosseum - Win Battle #1": PBRLocationData("Battlesanity", 27, "Gateway Colosseum", 0x69023, 0),
    "Gateway Colosseum - Win Battle #2": PBRLocationData("Battlesanity", 28, "Gateway Colosseum", 0x69023, 1),
    "Gateway Colosseum - Win Battle #3": PBRLocationData("Battlesanity", 29, "Gateway Colosseum", 0x69023, 2),
    "Gateway Colosseum - Win Battle #4": PBRLocationData("Battlesanity", 30, "Gateway Colosseum", 0x69023, 3),
    "Gateway Colosseum - Win Battle #5": PBRLocationData("Battlesanity", 31, "Gateway Colosseum", 0x69023, 4),
    "Gateway Colosseum - Win Battle #6": PBRLocationData("Battlesanity", 32, "Gateway Colosseum", 0x69023, 5),
    "Main Street Colosseum - Win Battle #1": PBRLocationData("Battlesanity", 33, "Main Street Colosseum", 0x69024, 0),
    "Main Street Colosseum - Win Battle #2": PBRLocationData("Battlesanity", 34, "Main Street Colosseum", 0x69024, 1),
    "Main Street Colosseum - Win Battle #3": PBRLocationData("Battlesanity", 35, "Main Street Colosseum", 0x69024, 2),
    "Main Street Colosseum - Win Battle #4": PBRLocationData("Battlesanity", 36, "Main Street Colosseum", 0x69024, 3),
    "Main Street Colosseum - Win Battle #5": PBRLocationData("Battlesanity", 37, "Main Street Colosseum", 0x69024, 4),
    "Main Street Colosseum - Win Battle #6": PBRLocationData("Battlesanity", 38, "Main Street Colosseum", 0x69024, 5),
    "Waterfall Colosseum - Win Battle #1": PBRLocationData("Battlesanity", 39, "Waterfall Colosseum", 0x69025, 0),
    "Waterfall Colosseum - Win Battle #2": PBRLocationData("Battlesanity", 40, "Waterfall Colosseum", 0x69025, 1),
    "Waterfall Colosseum - Win Battle #3": PBRLocationData("Battlesanity", 41, "Waterfall Colosseum", 0x69025, 2),
    "Waterfall Colosseum - Win Battle #4": PBRLocationData("Battlesanity", 42, "Waterfall Colosseum", 0x69025, 3),
    "Waterfall Colosseum - Win Battle #5": PBRLocationData("Battlesanity", 43, "Waterfall Colosseum", 0x69025, 4),
    "Waterfall Colosseum - Win Battle #6": PBRLocationData("Battlesanity", 44, "Waterfall Colosseum", 0x69025, 5),
    "Neon Colosseum - Win Battle #1": PBRLocationData("Battlesanity", 45, "Neon Colosseum", 0x69026, 0),
    "Neon Colosseum - Win Battle #2": PBRLocationData("Battlesanity", 46, "Neon Colosseum", 0x69026, 1),
    "Neon Colosseum - Win Battle #3": PBRLocationData("Battlesanity", 47, "Neon Colosseum", 0x69026, 2),
    "Neon Colosseum - Win Battle #4": PBRLocationData("Battlesanity", 48, "Neon Colosseum", 0x69026, 3),
    "Neon Colosseum - Win Battle #5": PBRLocationData("Battlesanity", 49, "Neon Colosseum", 0x69026, 4),
    "Neon Colosseum - Win Battle #6": PBRLocationData("Battlesanity", 50, "Neon Colosseum", 0x69026, 5),
    "Crystal Colosseum - Win Battle #1": PBRLocationData("Battlesanity", 51, "Crystal Colosseum", 0x69027, 0),
    "Crystal Colosseum - Win Battle #2": PBRLocationData("Battlesanity", 52, "Crystal Colosseum", 0x69027, 1),
    "Crystal Colosseum - Win Battle #3": PBRLocationData("Battlesanity", 53, "Crystal Colosseum", 0x69027, 2),
    "Crystal Colosseum - Win Battle #4": PBRLocationData("Battlesanity", 54, "Crystal Colosseum", 0x69027, 3),
    "Sunny Park Colosseum - Win Battle #1": PBRLocationData("Battlesanity", 55, "Sunny Park Colosseum", 0x69028, 0),
    "Sunny Park Colosseum - Win Battle #2": PBRLocationData("Battlesanity", 56, "Sunny Park Colosseum", 0x69028, 1),
    "Sunny Park Colosseum - Win Battle #3": PBRLocationData("Battlesanity", 57, "Sunny Park Colosseum", 0x69028, 2),
    "Sunny Park Colosseum - Win Battle #4": PBRLocationData("Battlesanity", 58, "Sunny Park Colosseum", 0x69028, 3),
    "Sunny Park Colosseum - Win Battle #5": PBRLocationData("Battlesanity", 59, "Sunny Park Colosseum", 0x69028, 4),
    "Sunny Park Colosseum - Win Battle #6": PBRLocationData("Battlesanity", 60, "Sunny Park Colosseum", 0x69028, 5),
    "Magma Colosseum - Win Battle #1": PBRLocationData("Battlesanity", 61, "Magma Colosseum", 0x69029, 0),
    "Magma Colosseum - Win Battle #2": PBRLocationData("Battlesanity", 62, "Magma Colosseum", 0x69029, 1),
    "Magma Colosseum - Win Battle #3": PBRLocationData("Battlesanity", 63, "Magma Colosseum", 0x69029, 2),
    "Magma Colosseum - Win Battle #4": PBRLocationData("Battlesanity", 64, "Magma Colosseum", 0x69029, 3),
    "Magma Colosseum - Win Battle #5": PBRLocationData("Battlesanity", 65, "Magma Colosseum", 0x69029, 4),
    "Courtyard Colosseum - Win Battle #1": PBRLocationData("Battlesanity", 66, "Courtyard Colosseum", 0x6902A, 0),
    "Courtyard Colosseum - Win Battle #2": PBRLocationData("Battlesanity", 67, "Courtyard Colosseum", 0x6902A, 1),
    "Courtyard Colosseum - Win Battle #3": PBRLocationData("Battlesanity", 68, "Courtyard Colosseum", 0x6902A, 2),
    "Courtyard Colosseum - Win Battle #4": PBRLocationData("Battlesanity", 69, "Courtyard Colosseum", 0x6902A, 3),
    "Courtyard Colosseum - Win Battle #5": PBRLocationData("Battlesanity", 70, "Courtyard Colosseum", 0x6902A, 4),
    "Courtyard Colosseum - Win Battle #6": PBRLocationData("Battlesanity", 71, "Courtyard Colosseum", 0x6902A, 5),
    "Sunset Colosseum - Win Battle #1": PBRLocationData("Battlesanity", 72, "Sunset Colosseum", 0x6902B, 0),
    "Sunset Colosseum - Win Battle #2": PBRLocationData("Battlesanity", 73, "Sunset Colosseum", 0x6902B, 1),
    "Sunset Colosseum - Win Battle #3": PBRLocationData("Battlesanity", 74, "Sunset Colosseum", 0x6902B, 2),
    "Stargazer Colosseum - Win Battle #1": PBRLocationData("Battlesanity", 75, "Stargazer Colosseum", 0x6902C, 0),
    "Stargazer Colosseum - Win Battle #2": PBRLocationData("Battlesanity", 76, "Stargazer Colosseum", 0x6902C, 1),
    "Stargazer Colosseum - Win Battle #3": PBRLocationData("Battlesanity", 77, "Stargazer Colosseum", 0x6902C, 2),
    "Stargazer Colosseum - Win Battle #4": PBRLocationData("Battlesanity", 78, "Stargazer Colosseum", 0x6902C, 3),
    "Stargazer Colosseum - Win Battle #5": PBRLocationData("Battlesanity", 79, "Stargazer Colosseum", 0x6902C, 4),
    "Stargazer Colosseum - Win Battle #6": PBRLocationData("Battlesanity", 80, "Stargazer Colosseum", 0x6902C, 5),
}


def get_location_names_with_ids(location_names: list[str]) -> dict[str, int | None]:
    return {location_name: LOCATION_TABLE[location_name].code for location_name in location_names}


def create_all_locations(world: PBRWorld) -> None:
    for location, data in LOCATION_TABLE.items():
        remove = False
        if data.code == None:
            region = world.get_region(data.region)
            region.add_event(
                location, "Victory", location_type=PBRLocation, item_type=items.PBRItem
            )
        else:
            if data.group == "Rental Pass Checks" and not world.options.randomize_rental_passes:
                remove = True
            if data.group == "Battlesanity" and not world.options.battlesanity:
                remove = True
            if data.region == "Stargazer Colosseum" and world.options.remove_goal_locations:
                remove = True

            if not remove:
                region = world.get_region(data.region)
                region.add_locations({location: data.code}, PBRLocation)

location_name_groups = {
    "Colosseum Clears": set(),
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
    if data.region in location_name_groups:
        location_name_groups[data.region].add(item)
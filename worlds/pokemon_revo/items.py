from __future__ import annotations

from typing import TYPE_CHECKING, NamedTuple, Optional

from BaseClasses import Item, ItemClassification

if TYPE_CHECKING:
    from .world import PBRWorld

class PBRItemData(NamedTuple):
    """
    This class represents the data for an item in Pokémon Battle Revolution.

    :param group: The group the item is in (e.g. "Colosseum Set 1", "Rental Passes").
    :param classification: The item's classification (progression, useful, filler).
    :param code: The unique code identifier for the item.
    :param value: A special value used for giving the item to the player.
    :param bit: The bit index used to check if a Colosseum has already been obtained.
    """

    group: str
    classification: ItemClassification
    code: int
    value: Optional[int]
    bit: Optional[int]


class PBRItem(Item):
    game = "Pokémon Battle Revolution"


ITEM_TABLE: dict[str, PBRItemData] = {
    "Gateway Colosseum":     PBRItemData("Colosseum Set 1", ItemClassification.progression, 1,  0x10, 4),
    "Main Street Colosseum": PBRItemData("Colosseum Set 1", ItemClassification.progression, 2,  0x20, 5),
    "Waterfall Colosseum":   PBRItemData("Colosseum Set 1", ItemClassification.progression, 3,  0x40, 6),
    "Neon Colosseum":        PBRItemData("Colosseum Set 1", ItemClassification.progression, 4,  0x80, 7),
    "Crystal Colosseum":     PBRItemData("Colosseum Set 2", ItemClassification.progression, 5,  0x01, 0),
    "Sunny Park Colosseum":  PBRItemData("Colosseum Set 2", ItemClassification.progression, 6,  0x02, 1),
    "Magma Colosseum":       PBRItemData("Colosseum Set 2", ItemClassification.progression, 7,  0x04, 2),
    "Courtyard Colosseum":   PBRItemData("Colosseum Set 2", ItemClassification.progression, 8,  0x08, 3),
    "Sunset Colosseum":      PBRItemData("Colosseum Set 2", ItemClassification.progression, 9,  0x10, 4),
   #"Stargazer Colosseum":   PBRItemData("Colosseum Set 2", ItemClassification.progression, 10, 0x20, 5),

    "Pokétopia Badge": PBRItemData("Macguffin", ItemClassification.progression_deprioritized, 10, None, None),

    "Cyndy's Rental Pass":   PBRItemData("Rental Passes", ItemClassification.useful, 11, 0x23DB9, None),
    "Nate's Rental Pass":    PBRItemData("Rental Passes", ItemClassification.useful, 12, 0x244A5, None),
    "Tommy's Rental Pass":   PBRItemData("Rental Passes", ItemClassification.useful, 13, 0x24B91, None),
    "Daisy's Rental Pass":   PBRItemData("Rental Passes", ItemClassification.useful, 14, 0x2527D, None),
    "Joel's Rental Pass":    PBRItemData("Rental Passes", ItemClassification.useful, 15, 0x25969, None),
    "Natalie's Rental Pass": PBRItemData("Rental Passes", ItemClassification.useful, 16, 0x26055, None),

    "100 Poké Coupons": PBRItemData("Poké Coupons", ItemClassification.filler, 17, 0x64,  None),
    "200 Poké Coupons": PBRItemData("Poké Coupons", ItemClassification.filler, 18, 0xC8,  None),
    "300 Poké Coupons": PBRItemData("Poké Coupons", ItemClassification.filler, 19, 0x12C, None),
}


LOOKUP_ID_TO_NAME: dict[int, str] = {
    data.code: item for item, data in ITEM_TABLE.items() if data.code is not None
}


def get_random_filler_item_name(world: PBRWorld) -> str:
    match world.random.randint(0,2):
        case 0:
            filler_item = "100 Poké Coupons"
        case 1:
            filler_item = "200 Poké Coupons"
        case 2:
            filler_item = "300 Poké Coupons"
    return filler_item


def create_item_with_correct_classification(world: PBRWorld, name: str) -> PBRItem:
    return PBRItem(name, ITEM_TABLE[name].classification, ITEM_TABLE[name].code, world.player)


def create_all_items(world: PBRWorld) -> None:
    itempool: list[Item] = []
    if world.options.total_badge_amount < world.options.required_badge_amount:
        world.options.total_badge_amount = world.options.required_badge_amount
    if world.options.starting_colosseum_amount != -1:
        if len(world.options.starting_colosseum_pool.value) < world.options.starting_colosseum_amount:
            colosseum_list = [
                "Gateway Colosseum",
                "Main Street Colosseum",
                "Waterfall Colosseum",
                "Neon Colosseum",
                "Crystal Colosseum",
                "Sunny Park Colosseum",
                "Magma Colosseum",
                "Courtyard Colosseum",
                "Sunset Colosseum",
            ]
            for colosseum in world.options.starting_colosseum_pool:
                colosseum_list.remove(colosseum)
            while True:
                random_colosseum = world.random.randrange(0,len(colosseum_list))
                world.options.starting_colosseum_pool.value.add(colosseum_list[random_colosseum])
                if len(world.options.starting_colosseum_pool.value) >= world.options.starting_colosseum_amount:
                    break
        starting_colosseums = []
        pool = list(world.options.starting_colosseum_pool.value)
        for _ in range(0,world.options.starting_colosseum_amount):
            new_colosseum = world.random.randrange(0,len(pool))
            starting_colosseums.append(pool[new_colosseum])
            pool.pop(new_colosseum)
    else:
        starting_colosseums = ["Gateway Colosseum", "Main Street Colosseum"]

    for item in ITEM_TABLE:
        if "Colosseum" in ITEM_TABLE[item].group:
            if item in starting_colosseums:
                world.push_precollected(world.create_item(item))
            else:
                itempool.append(world.create_item(item))
        elif ITEM_TABLE[item].group == "Rental Passes":
            if world.options.randomize_rental_passes:
                starter_pass_check = item.lower().removesuffix("'s rental pass")
                if not world.options.starting_rental_pass == starter_pass_check:
                    itempool.append(world.create_item(item))
                else:
                    world.push_precollected(world.create_item(item))
        elif ITEM_TABLE[item].group == "Macguffin":
            if world.options.goal_unlock_method == "badge_hunt" or world.options.goal_unlock_method == "both":
                for _ in range(0,world.options.total_badge_amount):
                    itempool.append(world.create_item(item))

    number_of_items = len(itempool)
    number_of_unfilled_locations = len(world.multiworld.get_unfilled_locations(world.player))
    needed_number_of_filler_items = number_of_unfilled_locations - number_of_items
    itempool += [world.create_filler() for _ in range(needed_number_of_filler_items)]

    world.multiworld.itempool += itempool

item_name_groups = {
    "Colosseums": set(),
    "Rental Passes": set(),
    "Poké Coupons": set(),
}
for item in ITEM_TABLE:
    if "Colosseum" in ITEM_TABLE[item].group:
        item_name_groups["Colosseums"].add(item)
    elif ITEM_TABLE[item].group in item_name_groups:
        item_name_groups[ITEM_TABLE[item].group].add(item)
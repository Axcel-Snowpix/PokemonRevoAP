from __future__ import annotations

from typing import TYPE_CHECKING, NamedTuple, Optional

from Utils import logging

from BaseClasses import Item, ItemClassification

from .data.pokemon_data import id_to_mon

if TYPE_CHECKING:
    from .world import PBRWorld

class PBRItemData(NamedTuple):
    """
    This class represents the data for an item in Pokémon Battle Revolution.

    :param group: The group the item is in (e.g. "Colosseums", "Rental Passes").
    :param classification: The item's classification (progression, useful, filler).
    :param code: The unique code identifier for the item.
    :param values: Special values used for giving the item to the player.
    """

    group: str
    classification: ItemClassification
    code: int
    values: Optional[list] = None


class PBRItem(Item):
    game = "Pokémon Battle Revolution"


ITEM_TABLE: dict[str, PBRItemData] = {
    "Gateway Colosseum":     PBRItemData("Colosseums", ItemClassification.progression, 1,  [4]),
    "Main Street Colosseum": PBRItemData("Colosseums", ItemClassification.progression, 2,  [5]),
    "Waterfall Colosseum":   PBRItemData("Colosseums", ItemClassification.progression, 3,  [6]),
    "Neon Colosseum":        PBRItemData("Colosseums", ItemClassification.progression, 4,  [7]),
    "Crystal Colosseum":     PBRItemData("Colosseums", ItemClassification.progression, 5,  [8]),
    "Sunny Park Colosseum":  PBRItemData("Colosseums", ItemClassification.progression, 6,  [9]),
    "Magma Colosseum":       PBRItemData("Colosseums", ItemClassification.progression, 7,  [10]),
    "Courtyard Colosseum":   PBRItemData("Colosseums", ItemClassification.progression, 8,  [11]),
    "Sunset Colosseum":      PBRItemData("Colosseums", ItemClassification.progression, 9,  [12]),
   #"Stargazer Colosseum":   PBRItemData("Colosseums", ItemClassification.progression, 10, [13]),

    "Pokétopia Badge": PBRItemData("Macguffin", ItemClassification.progression_skip_balancing, 10),

    "Cyndy's Rental Pass":   PBRItemData("Rental Passes", ItemClassification.progression_deprioritized, 11, [0x23A39, 0]),
    "Nate's Rental Pass":    PBRItemData("Rental Passes", ItemClassification.progression_deprioritized, 12, [0x24125, 1]),
    "Tommy's Rental Pass":   PBRItemData("Rental Passes", ItemClassification.progression_deprioritized, 13, [0x24811, 2]),
    "Daisy's Rental Pass":   PBRItemData("Rental Passes", ItemClassification.progression_deprioritized, 14, [0x24EFD, 3]),
    "Joel's Rental Pass":    PBRItemData("Rental Passes", ItemClassification.progression_deprioritized, 15, [0x255E9, 4]),
    "Natalie's Rental Pass": PBRItemData("Rental Passes", ItemClassification.progression_deprioritized, 16, [0x25CD5, 5]),

    "100 Poké Coupons": PBRItemData("Poké Coupons", ItemClassification.filler, 17, [0x64]),
    "200 Poké Coupons": PBRItemData("Poké Coupons", ItemClassification.filler, 18, [0xC8]),
    "300 Poké Coupons": PBRItemData("Poké Coupons", ItemClassification.filler, 19, [0x12C]),
    "500 Poké Coupons": PBRItemData("Poké Coupons", ItemClassification.filler, 20, [0x1F4]),
    "1000 Poké Coupons": PBRItemData("Poké Coupons", ItemClassification.filler, 21, [0x3E8]),

    "Potion": PBRItemData("Heals", ItemClassification.filler, 22, [0x14]),
    "Super Potion": PBRItemData("Heals", ItemClassification.filler, 23, [0x32]),
    "Hyper Potion": PBRItemData("Heals", ItemClassification.filler, 24, [0xC8]),

    "X Attack": PBRItemData("Stat Changes", ItemClassification.filler, 25, [0x1, 0x1]),
    "X Defense": PBRItemData("Stat Changes", ItemClassification.filler, 26, [0x2, 0x1]),
    "X Speed": PBRItemData("Stat Changes", ItemClassification.filler, 27, [0x3, 0x1]),
    "X Sp. Atk": PBRItemData("Stat Changes", ItemClassification.filler, 28, [0x4, 0x1]),
    "X Sp. Def": PBRItemData("Stat Changes", ItemClassification.filler, 29, [0x5, 0x1]),
    "X Accuracy": PBRItemData("Stat Changes", ItemClassification.filler, 30, [0x6, 0x1]),
    "X Evasion": PBRItemData("Stat Changes", ItemClassification.filler, 31, [0x7, 0x1]),

    "+1 Perfect Point": PBRItemData("Perfect Points", ItemClassification.filler, 32, [0x1]),

    "Poison Trap": PBRItemData("Status Conditions", ItemClassification.trap, 33, [3]),
    "Burn Trap": PBRItemData("Status Conditions", ItemClassification.trap, 34, [4]),
    "Freeze Trap": PBRItemData("Status Conditions", ItemClassification.trap, 35, [5]),
    "Paralysis Trap": PBRItemData("Status Conditions", ItemClassification.trap, 36, [6]),
    "Toxic Trap": PBRItemData("Status Conditions", ItemClassification.trap, 37, [7]),
    "Sleep Trap": PBRItemData("Status Conditions", ItemClassification.trap, 38),

    "Attack Drop Trap": PBRItemData("Stat Changes", ItemClassification.trap, 39, [0x1, -0x1]),
    "Defense Drop Trap": PBRItemData("Stat Changes", ItemClassification.trap, 40, [0x2, -0x1]),
    "Speed Drop Trap": PBRItemData("Stat Changes", ItemClassification.trap, 41, [0x3, -0x1]),
    "Sp. Atk Drop Trap": PBRItemData("Stat Changes", ItemClassification.trap, 42, [0x4, -0x1]),
    "Sp. Def Drop Trap": PBRItemData("Stat Changes", ItemClassification.trap, 43, [0x5, -0x1]),
    "Accuracy Drop Trap": PBRItemData("Stat Changes", ItemClassification.trap, 44, [0x6, -0x1]),
    "Evasion Drop Trap": PBRItemData("Stat Changes", ItemClassification.trap, 45, [0x7, -0x1]),

    "Metronome Trap": PBRItemData("Move Changes", ItemClassification.trap, 46, [0x76, 0xA]),

    **{pkmn: PBRItemData("Pokémon", ItemClassification.useful, 47 + i) for i, pkmn in enumerate(id_to_mon.values())}
}


LOOKUP_ID_TO_NAME: dict[int, str] = {
    data.code: item for item, data in ITEM_TABLE.items() if data.code is not None
}


def get_random_filler_item_name(world: PBRWorld, itempool) -> str:
    increased_weight_items = [
        "100 Poké Coupons", "200 Poké Coupons", "300 Poké Coupons",
        "Poison Trap", "Burn Trap", "Paralysis Trap"
    ]
    if world.random.randint(0,99) >= world.options.trap_percentage_chance:
        item_groups = ["Pokémon", "Poké Coupons", "Heals", "Stat Changes", "Perfect Points"]
        item_weights = [
            world.options.pokemon_weight, world.options.poke_coupon_weight,
            world.options.healing_item_weight, world.options.stat_boost_weight,
            world.options.perfect_point_weight,
        ]
        trap = False
    else:
        item_groups = ["Status Conditions", "Stat Changes", "Move Changes"]
        item_weights = [
            world.options.status_condition_trap_weight, world.options.stat_drop_trap_weight,
            world.options.metronome_trap_weight,
        ]
        trap = True
    item_group_pool = []
    for i in range(len(item_groups)):
        for _ in range(item_weights[i]):
            item_group_pool.append(item_groups[i])
    if len(item_group_pool) <= 0:
        item_group_pool = item_groups
    include_duplicate_mons = False
    if item_group_pool.count("Pokémon") > 0:
        has_other_filler = False
        for i in range(0,len(item_weights)):
            if item_weights[i] > 0 and i != 0:
                has_other_filler = True
        for pkmn in id_to_mon:
            if pkmn not in itempool:
                pkmn_available = True
                break
        if not pkmn_available:
            if has_other_filler:
                for _ in range(0,item_group_pool.count("Pokémon")):
                    item_group_pool.remove("Pokémon")
            else:
                include_duplicate_mons = True
    group = item_group_pool[world.random.randrange(0,len(item_group_pool))]
    item_list = []
    for item, data in ITEM_TABLE.items():
        if (
            data.group == group 
            and ((
                trap and data.classification == ItemClassification.trap
            ) or (
                not trap and data.classification != ItemClassification.trap
            )
            )
            and (
                world.options.allow_accuracy_drop_trap
                or item != "Accuracy Drop Trap"
            )
            and (
                world.create_item(item) not in itempool
                or include_duplicate_mons
                or group != "Pokémon"
            )
        ):
            item_list.append(item)
            if item in increased_weight_items:
                item_list.append(item)
    return item_list[world.random.randrange(0,len(item_list))]


def create_item_with_correct_classification(world: PBRWorld, name: str) -> PBRItem:
    return PBRItem(name, ITEM_TABLE[name].classification, ITEM_TABLE[name].code, world.player)


def create_all_items(world: PBRWorld) -> None:
    itempool: list[Item] = []

    colosseum_pool_warning = f"""
WARNING: {world.player_name} does not have enough Colosseums in the Starting Colosseum Pool.
Random Colosseums will be added to the pool until there is enough."""

    low_total_badges_warning = f"""
WARNING: {world.player_name}'s Required Badge Amount is lower than their Total Badge Amount.
The total amount of badges will be raised to match the number of required badges."""

    starting_colosseums = []
    colo_pool = world.options.starting_colosseum_pool.value
    if world.options.starting_colosseum_amount != -1:
        if len(colo_pool) < world.options.starting_colosseum_amount:
            logging.warning(colosseum_pool_warning)
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
            for colosseum in colo_pool:
                colosseum_list.remove(colosseum)
            while len(colo_pool) < world.options.starting_colosseum_amount:
                random_colosseum = world.random.randrange(0,len(colosseum_list))
                colo_pool.add(colosseum_list[random_colosseum])
        for _ in range(0,world.options.starting_colosseum_amount):
            colo_pool = sorted(colo_pool)
            new_colosseum = world.random.randrange(0,len(colo_pool))
            starting_colosseums.append(colo_pool[new_colosseum])
            colo_pool.pop(new_colosseum)
    else:
        starting_colosseums = ["Gateway Colosseum", "Main Street Colosseum"]

    is_ut = getattr(world.multiworld, "generation_is_fake", False)

    for item, data in ITEM_TABLE.items():
        if data.group == "Colosseums":
            if item in starting_colosseums and not is_ut:
                world.push_precollected(world.create_item(item))
            else:
                itempool.append(world.create_item(item))
        elif data.group == "Rental Passes" and world.options.randomize_rental_passes:
            starter_pass_check = item.lower().removesuffix("'s rental pass")
            if world.options.starting_rental_pass == starter_pass_check and not is_ut:
                world.push_precollected(world.create_item(item))
            else:
                itempool.append(world.create_item(item))
        elif data.group == "Macguffin" and world.options.goal_unlock_method != "colosseum_clears":
            if world.options.total_badge_amount < world.options.required_badge_amount:
                logging.warning(low_total_badges_warning)
                world.options.total_badge_amount.value = world.options.required_badge_amount.value
            for _ in range(world.options.total_badge_amount):
                itempool.append(world.create_item(item))

    number_of_items = len(itempool)
    number_of_unfilled_locations = len(world.multiworld.get_unfilled_locations(world.player))

    if number_of_items > number_of_unfilled_locations:
        excess_items = number_of_items - number_of_unfilled_locations
        for _ in range(excess_items):
            itempool.remove(world.create_item("Pokétopia Badge"))
        new_number_of_badges = len([item for item in itempool if item == world.create_item("Pokétopia Badge")])

        excess_total_badges_warning = f"""
WARNING: {world.player_name}'s Total Badge Amount is higher than the number of available locations.
The total number of badges will be decreased to {new_number_of_badges}."""

        excess_required_badges_warning = f"""
WARNING: {world.player_name}'s Required Badge Amount is higher than the number of available locations.
The number of required badges will be decreased to {new_number_of_badges}."""
    
        if world.options.total_badge_amount > new_number_of_badges:
            logging.warning(excess_total_badges_warning)
            world.options.total_badge_amount.value = new_number_of_badges
        if world.options.required_badge_amount > new_number_of_badges:
            logging.warning(excess_required_badges_warning)
            world.options.required_badge_amount.value = new_number_of_badges

    needed_number_of_filler_items = number_of_unfilled_locations - number_of_items
    for _ in range(needed_number_of_filler_items):
        itempool.append(world.create_item(get_random_filler_item_name(world, itempool)))

    world.multiworld.itempool += itempool

item_name_groups = {
    "Colosseums": set(),
    "Rental Passes": set(),
    "Poké Coupons": set(),
    "Heals": set(),
    "Stat Changes": set(),
    "Status Conditions": set(),
    "Pokémon": set(),
}
for item, data in ITEM_TABLE.items():
    if data.group in item_name_groups:
        item_name_groups[data.group].add(item)
from collections.abc import Mapping
from typing import Any, ClassVar, Optional

from worlds.AutoWorld import World
from Options import Option

from . import items, locations, regions, rules, web_world
from . import options as pbr_options  # rename due to a name conflict with World.options
from .items import ITEM_TABLE, item_name_groups
from .locations import LOCATION_TABLE

class PBRWorld(World):
    """
    Pokémon Battle Revolution is the series' first game on the Wii. Battle through 10 different Colosseums
    on your way to the rank of Pokétopia Master, all in the series' famous turn-based battles!
    """

    game = "Pokémon Battle Revolution"

    web = web_world.PBRWebWorld()

    ut_can_gen_without_yaml = True

    options_dataclass = pbr_options.PBROptions
    options: pbr_options.PBROptions

    location_name_to_id: ClassVar[dict[str, int]] = {
        name: data.code for name, data in LOCATION_TABLE.items() if data.code is not None
    }
    item_name_to_id: ClassVar[dict[str, int]] = {
        name: data.code for name, data in ITEM_TABLE.items() if data.code is not None
    }

    item_name_groups: ClassVar[dict[str, set[str]]] = item_name_groups

    origin_region_name = "Menu"

    @staticmethod
    def interpret_slot_data(slot_data: dict[str, Any]) -> dict[str, Any]:
        # Trigger a regen in UT
        return slot_data

    def generate_early(self) -> None:
        re_gen_passthrough = getattr(self.multiworld, "re_gen_passthrough", {})
        if re_gen_passthrough and self.game in re_gen_passthrough:
            # Get the passed through slot data from the real generation
            slot_data: dict[str, Any] = re_gen_passthrough[self.game]
            
            # Set all your options here instead of getting them from the yaml
            for key, value in slot_data.items():
                opt: Optional[Option] = getattr(self.options, key, None)
                if opt is not None:
                    # You can also set .value directly but that won't work if you have OptionSets
                    setattr(self.options, key, opt.from_any(value))

    def create_regions(self) -> None:
        regions.create_and_connect_regions(self)
        locations.create_all_locations(self)

    def set_rules(self) -> None:
        rules.set_all_rules(self)

    def create_items(self) -> None:
        items.create_all_items(self)

    def create_item(self, name: str) -> items.PBRItem:
        return items.create_item_with_correct_classification(self, name)

    def get_filler_item_name(self) -> str:
        return items.get_random_filler_item_name(self)

    def fill_slot_data(self) -> Mapping[str, Any]:
        slot_data = self.options.as_dict(
            "goal_unlock_method",
            "required_badge_amount",
            "colosseum_clear_count",
            "randomize_rental_passes", 
        )
        return slot_data
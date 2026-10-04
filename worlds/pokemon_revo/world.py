import os
from collections.abc import Mapping
from typing import Any, ClassVar, Optional

import json

from worlds.AutoWorld import World
import settings
from Options import Option

from . import items, locations, regions, rules, web_world
from . import options as pbr_options  # rename due to a name conflict with World.options
from .items import ITEM_TABLE, item_name_groups
from .locations import LOCATION_TABLE, location_name_groups
from .rom import PBRPatch
from ..Files import APPlayerContainer

class PBRSettings(settings.Group):
    class PBRRomFile(settings.UserFilePath):
        description = "Pokémon Battle Revolution USA ROM File"
        copy_to = "Pokemon Battle Revolution (USA).iso"
        md5s = [PBRPatch.hash]

    rom_file: PBRRomFile = PBRRomFile(PBRRomFile.copy_to)

class PBRWorld(World):
    """
    Pokémon Battle Revolution is the series' first game on the Wii. Battle through 10 different Colosseums
    on your way to the rank of Pokétopia Master, all in the mainline games' famous turn-based battles!
    """

    game = "Pokémon Battle Revolution"

    web = web_world.PBRWebWorld()

    settings_key = "pokemon_battle_revolution_settings"
    settings: ClassVar[PBRSettings]

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
    location_name_groups: ClassVar[dict[str, set[str]]] = location_name_groups

    origin_region_name = "Menu"

    @staticmethod
    def interpret_slot_data(slot_data: dict[str, Any]) -> dict[str, Any]:
        # Trigger a regen in UT
        return slot_data

    def generate_early(self) -> None:
        re_gen_passthrough = getattr(self.multiworld, "re_gen_passthrough", {})
        if re_gen_passthrough and self.game in re_gen_passthrough:
            slot_data: dict[str, Any] = re_gen_passthrough[self.game]
            
            for key, value in slot_data.items():
                opt: Optional[Option] = getattr(self.options, key, None)
                if opt is not None:
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

    def generate_output(self, output_directory: str) -> None:
        patch = PBRPatch(player=self.player, player_name=self.player_name)

        options_file = self.options.as_dict("randomize_rental_passes")
        patch.write_file("options.json", json.dumps(options_file).encode('utf-8'))

        out_file_name = self.multiworld.get_out_file_name_base(self.player)
        patch.write(os.path.join(output_directory, f"{out_file_name}{patch.patch_file_ending}"))

    def fill_slot_data(self) -> Mapping[str, Any]:
        slot_data = self.options.as_dict(
            "goal_unlock_method",
            "required_badge_amount",
            "colosseum_clear_count",
            "randomize_rental_passes", 
        )
        return slot_data

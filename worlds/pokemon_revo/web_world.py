from BaseClasses import Tutorial
from worlds.AutoWorld import WebWorld

from .options import option_groups

class PBRWebWorld(WebWorld):
    game = "Pokémon Battle Revolution"
    theme = "partyTime"
    setup_en = Tutorial(
        "Multiworld Setup Guide",
        "A guide to playing Pokémon Battle Revolution with Archipelago.",
        "English",
        "setup_en.md",
        "setup/en",
        ["Axcel Snowpix"],
    )
    tutorials = [setup_en]
    option_groups = option_groups
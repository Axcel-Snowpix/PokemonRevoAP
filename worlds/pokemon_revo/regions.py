from __future__ import annotations

from typing import TYPE_CHECKING

from BaseClasses import Entrance, Region
from rule_builder.rules import Has, HasAll, Rule

if TYPE_CHECKING:
    from .world import PBRWorld

def create_and_connect_regions(world: PBRWorld) -> None:
    create_all_regions(world)
    connect_regions(world)


def create_all_regions(world: PBRWorld) -> None:
    menu = Region("Menu", world.player, world.multiworld)
    gateway_colosseum = Region("Gateway Colosseum", world.player, world.multiworld)
    main_street_colosseum = Region("Main Street Colosseum", world.player, world.multiworld)
    waterfall_colosseum = Region("Waterfall Colosseum", world.player, world.multiworld)
    neon_colosseum = Region("Neon Colosseum", world.player, world.multiworld)
    crystal_colosseum = Region("Crystal Colosseum", world.player, world.multiworld)
    sunny_park_colosseum = Region("Sunny Park Colosseum", world.player, world.multiworld)
    magma_colosseum = Region("Magma Colosseum", world.player, world.multiworld)
    courtyard_colosseum = Region("Courtyard Colosseum", world.player, world.multiworld)
    sunset_colosseum = Region("Sunset Colosseum", world.player, world.multiworld)
    stargazer_colosseum = Region("Stargazer Colosseum", world.player, world.multiworld)

    regions = [menu, gateway_colosseum, main_street_colosseum, waterfall_colosseum, neon_colosseum, crystal_colosseum,
               sunny_park_colosseum, magma_colosseum, courtyard_colosseum, sunset_colosseum, stargazer_colosseum]

    world.multiworld.regions += regions


def connect_regions(world: PBRWorld) -> None:
    menu = world.get_region("Menu")
    gateway_colosseum = world.get_region("Gateway Colosseum")
    main_street_colosseum = world.get_region("Main Street Colosseum")
    waterfall_colosseum = world.get_region("Waterfall Colosseum")
    neon_colosseum = world.get_region("Neon Colosseum")
    crystal_colosseum = world.get_region("Crystal Colosseum")
    sunny_park_colosseum = world.get_region("Sunny Park Colosseum")
    magma_colosseum = world.get_region("Magma Colosseum")
    courtyard_colosseum = world.get_region("Courtyard Colosseum")
    sunset_colosseum = world.get_region("Sunset Colosseum")
    stargazer_colosseum = world.get_region("Stargazer Colosseum")

    menu.connect(gateway_colosseum, "Menu to Gateway Colosseum", Has("Gateway Colosseum"))
    menu.connect(main_street_colosseum, "Menu to Main Street Colosseum", Has("Main Street Colosseum"))
    menu.connect(waterfall_colosseum, "Menu to Waterfall Colosseum", Has("Waterfall Colosseum"))
    menu.connect(neon_colosseum, "Menu to Neon Colosseum", Has("Neon Colosseum"))
    menu.connect(crystal_colosseum, "Menu to Crystal Colosseum", Has("Crystal Colosseum"))
    menu.connect(sunny_park_colosseum, "Menu to Sunny Park Colosseum", Has("Sunny Park Colosseum"))
    menu.connect(magma_colosseum, "Menu to Magma Colosseum", Has("Magma Colosseum"))
    menu.connect(courtyard_colosseum, "Menu to Courtyard Colosseum", Has("Courtyard Colosseum"))
    menu.connect(sunset_colosseum, "Menu to Sunset Colosseum", Has("Sunset Colosseum"))
    menu.connect(stargazer_colosseum, "Menu to Stargazer Colosseum")
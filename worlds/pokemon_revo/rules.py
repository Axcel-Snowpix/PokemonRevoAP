from __future__ import annotations

from typing import TYPE_CHECKING

from rule_builder.options import OptionFilter
from rule_builder.rules import Has, HasAll, Rule, HasFromList

if TYPE_CHECKING:
    from .world import PBRWorld
    

def set_all_rules(world: PBRWorld) -> None:
    set_all_location_rules(world)
    set_completion_condition(world)


def set_all_location_rules(world: PBRWorld) -> None:
    if world.options.randomize_rental_passes:
        tommy_pass_location = world.get_location("Gateway Colosseum - Obtain Tommy's Rental Pass")
        world.set_rule(tommy_pass_location, Has("Waterfall Colosseum"))

        daisy_pass_location = world.get_location("Gateway Colosseum - Obtain Daisy's Rental Pass")
        world.set_rule(daisy_pass_location, Has("Waterfall Colosseum"))

        joel_pass_location = world.get_location("Gateway Colosseum - Obtain Joel's Rental Pass")
        world.set_rule(joel_pass_location, Has("Sunny Park Colosseum"))

        natalie_pass_location = world.get_location("Gateway Colosseum - Obtain Natalie's Rental Pass")
        world.set_rule(natalie_pass_location, Has("Sunny Park Colosseum"))


def set_completion_condition(world: PBRWorld) -> None:
    stargazer_colosseum = world.get_entrance("Menu to Stargazer Colosseum")
    stargazer_rule = Rule
    if world.options.goal_unlock_method != "colosseum_clears":
        stargazer_rule = Has("Pokétopia Badge", count=world.options.required_badge_amount.value)
    if world.options.goal_unlock_method != "badge_hunt":
        stargazer_rule = stargazer_rule & HasFromList("Gateway Colosseum", "Main Street Colosseum",
                                                      "Waterfall Colosseum", "Neon Colosseum",
                                                      "Crystal Colosseum", "Sunny Park Colosseum",
                                                      "Magma Colosseum", "Courtyard Colosseum",
                                                      "Sunset Colosseum",
                                                      count=world.options.colosseum_clear_count.value)
    world.set_rule(stargazer_colosseum, stargazer_rule)
    world.set_completion_rule(Has("Victory"))
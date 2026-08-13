from dataclasses import dataclass

from Options import Choice, OptionGroup, PerGameCommonOptions, Range, Toggle, DefaultOnToggle, NamedRange, OptionSet

class GoalUnlockMethod(Choice):
    """
    Determines how Stargazer Colosseum (your goal) will be unlocked.

    Badge Hunt: Stargazer Colosseum will be unlocked once you get a certain number of Pokétopia Badges (macguffin item).
    Colosseum Clears: Stargazer Colosseum will be unlocked once you beat a certain number of Colosseums.
    """
    display_name = "Goal Unlock Method"
    option_badge_hunt = 0
    option_colosseum_clears = 1
    default = 0

class RequiredBadgeAmount(Range):
    """
    The number of Pokétopia Badges required to unlock Stargazer Colosseum.
    This option only matters if Goal Unlock Method is set to Badge Hunt.
    """
    display_name = "Required Badge Amount"
    range_start = 3
    range_end = 10
    default = 5

class TotalBadgeAmount(Range):
    """
    The total number of Pokétopia Badges in the item pool.
    If this option is set to a lower number than Required Badge Amount, then it will be increased to match.
    This option only matters if Goal Unlock Method is set to Badge Hunt.
    """
    display_name = "Total Badge Amount"
    range_start = 4
    range_end = 10
    default = 8

class ColosseumClearCount(Range):
    """
    The number of Colosseums needed to be cleared to unlock Stargazer Colosseum.
    This option only matters if Goal Unlock Method is set to Colosseum Clears.
    """
    display_name = "Colosseum Clear Count"
    range_start = 4
    range_end = 9
    default = 5

class StartingColosseumAmount(NamedRange):
    """
    The number of random Colosseums you will start with.
    Set to Vanilla to begin with the vanilla starter Colosseums (Gateway and Main Street Colosseums).
    """
    display_name = "Starting Colosseum Amount"
    range_start = 1
    range_end = 3
    special_range_names = {"vanilla": -1}
    default = 2

class StartingColosseumPool(OptionSet):
    """
    The Colosseums that can be chosen for you to start with.
    If the number of Colosseums set in this option is lower than the Starting Colosseum Amount,
    then random ones will be added to the pool until the number matches.
    """
    display_name = "Starting Colosseum Pool"
    valid_keys = [
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
    default = valid_keys.copy()

class RandomizeRentalPasses(DefaultOnToggle):
    """
    Whether Rental Passes should be added to the item pool.
    Getting new Rental Passes from Gateway Colosseum will give you checks.
    """
    display_name = "Randomize Rental Passes"

class StartingRentalPass(Choice):
    """
    The Rental Pass that you will start with.
    This option only matters if Randomize Rental Passes is turned on.
    """
    display_name = "Starting Rental Pass"
    option_cyndy = 0
    option_nate = 1
    option_tommy = 2
    option_daisy = 3
    option_joel = 4
    option_natalie = 5
    default = "random"

@dataclass
class PBROptions(PerGameCommonOptions):
    goal_unlock_method: GoalUnlockMethod
    required_badge_amount: RequiredBadgeAmount
    total_badge_amount: TotalBadgeAmount
    colosseum_clear_count: ColosseumClearCount
    starting_colosseum_amount: StartingColosseumAmount
    starting_colosseum_pool: StartingColosseumPool
    randomize_rental_passes: RandomizeRentalPasses
    starting_rental_pass: StartingRentalPass

option_groups = [
    OptionGroup(
        "Goal Options",
        [GoalUnlockMethod, RequiredBadgeAmount, TotalBadgeAmount, ColosseumClearCount],
    ),
    OptionGroup(
        "Gameplay Options",
        [StartingColosseumAmount, StartingColosseumPool, RandomizeRentalPasses, StartingRentalPass],
    ),
]
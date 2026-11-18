from dataclasses import dataclass
import logging
from typing import Any

from worlds.AutoWorld import World

from .data.gen4_pokemon_structure import Gen4Pokemon, decode_text
from .data.pokemon_data import pokemon_data, ability_to_id, item_to_id, move_to_id, move_data, category_to_id, level_up_moves, id_to_mon, type_to_id, tm_learnsets

weather_setting_moves: set[int] = {move_to_id['Sunny Day'], move_to_id['Sandstorm'], move_to_id['Rain Dance'], move_to_id['Hail']}
harsh_sunlight_moves: set[int] = {move_to_id['SolarBeam'], move_to_id['Weather Ball'], move_to_id['Moonlight'], move_to_id['Synthesis'], move_to_id['Morning Sun']}
rain_moves: set[int] = {move_to_id['Thunder'], move_to_id['Weather Ball']}
sandstorm_moves: set[int] = {move_to_id['Weather Ball']}
hail_moves: set[int] = {move_to_id['Weather Ball'], move_to_id['Blizzard']}
weather_moves: set[int] = weather_setting_moves | weather_setting_moves | harsh_sunlight_moves | rain_moves | sandstorm_moves | hail_moves
two_turn_moves: set[int] = {move_to_id['Bounce'], move_to_id['Dig'], move_to_id['Dive'], move_to_id['Fly'], move_to_id['Shadow Force'], move_to_id['Skull Bash'], move_to_id['Sky Attack'], move_to_id['SolarBeam']}
protect_moves: set[int] = {move_to_id['Protect'], move_to_id['Detect']}
recharge_moves: set[int] = {move_to_id['Giga Impact'], move_to_id['Rock Wrecker'], move_to_id['Hyper Beam'], move_to_id['Blast Burn'], move_to_id['Hydro Cannon'], move_to_id['Frenzy Plant'], move_to_id['Roar of Time']}

def pid_to_nature(pid: int) -> int:
    return (pid % 100) % 25

def nature_to_increased_stat(nature: int) -> str:
    if nature / 5 == nature % 5:
        return 'none'
    match (nature / 5):
        case 0:
            return "attack"
        case 1:
            return "defense"
        case 2:
            return "speed"
        case 3:
            return "sp attack"
        case 4:
            return "sp defense"
        case _:
            return "none"


def nature_to_decreased_stat(nature: int) -> str:
    if nature / 5 == nature % 5:
        return 'none'
    match nature % 5:
        case 0:
            return "attack"
        case 1:
            return "defense"
        case 2:
            return "speed"
        case 3:
            return "sp attack"
        case 4:
            return "sp defense"
        case _:
            return "none"

def pid_to_ability_for_species(pid: int, species: int) -> int:
    if species not in pokemon_data:
        ability_to_id['None'] # this could also just be 0
    
    species_data = pokemon_data[species]
    ability_1: int = species_data["ability1"]
    ability_2: int = species_data["ability2"]
    if ability_2 == 'None' or pid & 0b1 == 0b0:
        return ability_1
    else:
        return ability_2

def pid_to_gender_for_species(pid: int, species: int) -> int:
    if species not in pokemon_data:
        ability_to_id['None'] # this could also just be 0
        
    species_data = pokemon_data[species]
    gender_ratio: int = species_data["gender"]
    if gender_ratio == 0:
        return 0b00 # always male
    if gender_ratio == 254:
        return 0b01 # always female
    if gender_ratio == 255:
        return 0b10 # genderless
    
    if pid & 0xFF < gender_ratio:
        return 0b01 # rolled female
    else:
        return 0b00 # rolled male
    
def generate_normal_random_pokemon(world: World, lvl: int) -> list[dict[str, Any]]:
    # TODO: Remove moves listed in the yaml that the user wont want selected. ie: Splash, Memento
    generated_pokemon: list[dict[str, Any]] = []
    for species in pokemon_data.keys():
        if id_to_mon[species] == "-----":
            break
        lvl_moves: set[int] = set({move for lvl_learned, move in list(level_up_moves[species]) if lvl_learned < lvl})
        tm_moves: set[int] = tm_learnsets[species]
        generate_pokemon_inner(world, species, lvl_moves, tm_moves, set())
    return generated_pokemon

def generate_chaotic_random_pokemon(world: World):
    # TODO: Remove moves listed in the yaml that the user wont want selected. ie: Splash, Memento
    generated_pokemon: list[dict[str, Any]] = []
    for species in pokemon_data.keys():
        if id_to_mon[species] != "-----":
            break
        
        generated_pokemon.append(generate_pokemon_inner(world, species, set(move_data.keys()), set(move_data.keys()), set()))
    return generated_pokemon

def generate_pokemon_inner(world: World, species: int, lvl_moves: set[int], tm_moves: set[int], items: set[int]) -> dict[str, Any]:
    # Generate the PID and IVs (needs to be saved).
    pid: int = world.random.randint(0, 0xFFFFFFFF)
    ivs: int = world.random.randint(0, 0xFFFFFFFF)
    
    # Grab the ability, gender, and nature to check for moves/items/etc. This does
    # not need to be saved since it can be recalculated from the pid and species.
    gender: int = pid_to_gender_for_species(pid, species)
    ability: int = pid_to_ability_for_species(pid, species)
    nature: int = pid_to_nature(pid)
    
    # Check for valid moves for the species.
    species_data = pokemon_data[species]
    selected_moves: list[int] = []
    selectable_moves = lvl_moves | tm_moves
    # TODO: Remove extremely redundant moves from all_moves some situations include but are not
    # limited to:
    # Weather Setting Ability + Weather Setting Move
    # Shedinja + Recoil Moves
    # Vital Spirit/Insomnia + Rest
    # Genderless + Attract
    num_selectable_moves = len(selectable_moves)
    
    if num_selectable_moves == 0:
        # If a Pokemon has 0 moves available (because of yaml settings or bugs), PANIC.
        selected_moves.extend(generate_panic_moveset(world, species, 50))
    elif num_selectable_moves <= 4:
        # If a Pokemon has less than 4 moves available to it, just select those moves.
        selected_moves.extend(selectable_moves)
        if num_selectable_moves < 4:
            # Pad out the moveset until we get 4 moves.
            selected_moves.extend([move_to_id['-']] * (4 - num_selectable_moves))
            
    # TODO: Insert chance of certain sets with usable strategies to be generated so that they appear
    # within 'reasonable' frequency.
    # Weather Set (ie: Rain Dance + Damage Water Move)
    # Helping Hand or Helping Hand/Protect
    # FEAR Strategies
    # Charge + Electric Attack
    # Rest + Snore
    # Defense Curl + Rollout / Ice Ball
    # Endure + Flail
    # Fake Out + Last Resort
    # etc.
    
    # If none of the special cases above are true, use one of the following generalized methods to
    # generate a Pokemon.
    species_type_1 = species_data["type1"]
    species_type_2 = species_data["type2"]
    selectable_move_subsets: list[set] = [set(), set(), set(), set()]
    if len(selected_moves) == 0:
        generation_type_chance: float = world.random.random()
        if generation_type_chance < 0.2:
            # 20% Select STAB + secondary STAB or coverage + 1 lvl status + 1 TM status
            # Decide type to prioritize.
            if world.random.random() < 0.5:
                primary_stab_type: int = species_type_1
                secondary_stab_type: int = species_type_2
            else:
                primary_stab_type: int = species_type_2
                secondary_stab_type: int = species_type_1
            # Select the first stab move.
            if species_data["atk"] == species_data["sp_atk"]:
                selectable_move_subsets[0] = {k for k, v in move_data.items() if k in selectable_moves and v["type"] == primary_stab_type and 70 <= v["power"] and k not in two_turn_moves | recharge_moves}
            elif species_data["atk"] > species_data["sp_atk"]:
                selectable_move_subsets[0] = {k for k, v in move_data.items() if k in selectable_moves and v["type"] == primary_stab_type and 70 <= v["power"] and v["category"]  == category_to_id["Physical"] and k not in two_turn_moves | recharge_moves}
            else: # elif species_data['atk'] < species_data['sp_atk']:
                selectable_move_subsets[0] = {k for k, v in move_data.items() if k in selectable_moves and v["type"] == primary_stab_type and 70 <= v["power"] and v["category"]  == category_to_id["Special"] and k not in two_turn_moves | recharge_moves}
            # Either select a secondary stab move (if applicable) or a coverage move.
            if primary_stab_type == secondary_stab_type or world.random.random() < 0.5:
                selectable_move_subsets[1] = {k for k, v in move_data.items() if k in selectable_moves and v["type"] != primary_stab_type and 90 >= v["power"] and 40 <= v["power"] and k not in two_turn_moves | recharge_moves}
            else:
                selectable_move_subsets[1] = {k for k, v in move_data.items() if k in selectable_moves and v["type"] == secondary_stab_type and 80 >= v["power"] and 40 <= v["power"] and k not in recharge_moves}
            # Select the level and tm status moves.
            selectable_move_subsets[2] = {k for k, v in move_data.items() if k in lvl_moves and v["category"] == category_to_id["Status"] and k not in protect_moves | weather_setting_moves}
            selectable_move_subsets[3] = {k for k, v in move_data.items() if k in tm_moves and v["category"] == category_to_id["Status"] and k not in protect_moves | weather_setting_moves}
        elif generation_type_chance < 0.4:
            # 20% Select STAB + secondary STAB or coverage + coverage + lvl or tm status
            # Decide type to prioritize.
            if world.random.random() < 0.5:
                primary_stab_type: int = species_type_1
                secondary_stab_type: int = species_type_2
            else:
                primary_stab_type: int = species_type_2
                secondary_stab_type: int = species_type_1
            # Select the first stab move.
            if species_data["atk"] == species_data["sp_atk"]:
                selectable_move_subsets[0] = {k for k, v in move_data.items() if k in selectable_moves and v["type"] == primary_stab_type and 60 <= v["power"] and k not in two_turn_moves | recharge_moves}
            elif species_data["atk"] > species_data["sp_atk"]:
                selectable_move_subsets[0] = {k for k, v in move_data.items() if k in selectable_moves and v["type"] == primary_stab_type and 60 <= v["power"] and v["category"]  == category_to_id["Physical"] and k not in two_turn_moves | recharge_moves}
            else: # elif species_data['atk'] < species_data['sp_atk']:
                selectable_move_subsets[0] = {k for k, v in move_data.items() if k in selectable_moves and v["type"] == primary_stab_type and 60 <= v["power"] and v["category"] == category_to_id["Special"] and k not in two_turn_moves | recharge_moves}
            # Either select a secondary stab move (if applicable) or a coverage move.
            if primary_stab_type == secondary_stab_type or world.random.random() < 0.5:
                selectable_move_subsets[1] = {k for k, v in move_data.items() if k in selectable_moves and v["type"] != primary_stab_type and 80 >= v["power"] and 40 <= v["power"] and k not in recharge_moves}
            else:
                selectable_move_subsets[1] = {k for k, v in move_data.items() if k in selectable_moves and v["type"] == secondary_stab_type and 60 >= v["power"] and 40 <= v["power"] and k not in two_turn_moves | recharge_moves}
            # Select a random damage move.
            selectable_move_subsets[2] = {k for k, v in move_data.items() if k in selectable_moves and v["type"] != primary_stab_type and v["type"] != secondary_stab_type and 80 >= v["power"] and k not in two_turn_moves | recharge_moves}
            selectable_move_subsets[3] = {k for k, v in move_data.items() if k in lvl_moves and v["category"] == category_to_id["Status"] and k not in protect_moves | weather_setting_moves}
        elif generation_type_chance < 0.5:
            # 10% Select 1 level damage move (higher power) + 1 level damage move (lower power) + random tm (higher power) + random tm (lower power)
            selectable_move_subsets[0] = {k for k, v in move_data.items() if k in lvl_moves and 70 <= v["power"]}
            selectable_move_subsets[1] = {k for k, v in move_data.items() if k in lvl_moves and 70 > v["power"] and k not in recharge_moves}
            selectable_move_subsets[2] = {k for k, v in move_data.items() if k in tm_moves and 70 <= v["power"] and k not in recharge_moves}
            selectable_move_subsets[3] = {k for k, v in move_data.items() if k in tm_moves and 70 > v["power"] and k not in recharge_moves}
        elif generation_type_chance < 0.6:
            # 10% Select 2 random lvl damage move + 1 random tm move (not equal to stab) + random lvl status
            selectable_move_subsets[0] = {k for k, v in move_data.items() if k in lvl_moves and 80 <= v["power"] and v["category"] != category_to_id["Status"]}
            selectable_move_subsets[1] = {k for k, v in move_data.items() if k in lvl_moves and 40 <= v["power"] and v["category"] != category_to_id["Status"]}
            selectable_move_subsets[2] = {k for k, v in move_data.items() if k in tm_moves and 60 <= v["power"] and v["category"] != category_to_id["Status"]}
            selectable_move_subsets[3] = {k for k, v in move_data.items() if k in lvl_moves and v["category"] == category_to_id["Status"] and k not in protect_moves | weather_setting_moves}
        elif generation_type_chance < 0.7:
            # 10% X Damage Moves Descending In Power* + (4 - X) Moves Ascending in PP.
            num_damage_moves: int = world.random.choice(list({0, 1, 1, 2, 2, 2, 2, 2, 3, 3, 3, 3, 4}))
            damage_power_cap: int = 150
            for i in range(num_damage_moves - 1):
                if world.random.random() < 0.8:
                    selectable_move_subsets[i] = {k for k, v in move_data.items() if k in lvl_moves and damage_power_cap >= v["power"] >= (damage_power_cap / 2) and v["category"] != category_to_id["Status"] and k not in two_turn_moves}
                else:
                    selectable_move_subsets[i] = {k for k, v in move_data.items() if k in tm_moves and damage_power_cap >= v["power"] >= (damage_power_cap / 2) and v["category"] != category_to_id["Status"] and k not in two_turn_moves}
                damage_power_cap = int(damage_power_cap * 0.75)
            pp_cap: int = 5
            for i in range(4 - num_damage_moves):
                if world.random.random() < 0.6:
                    selectable_move_subsets[num_damage_moves + i] = {k for k, v in move_data.items() if k in lvl_moves and pp_cap >= v["pp"] and v["category"] == category_to_id["Status"] and k not in protect_moves}
                else:
                    selectable_move_subsets[num_damage_moves + i] = {k for k, v in move_data.items() if k in tm_moves and pp_cap >= v["pp"] and v["category"] == category_to_id["Status"] and k not in weather_moves | protect_moves}
                pp_cap = pp_cap * 2
        elif generation_type_chance < 0.76:
            # 6% Forced Protect + 1 medium BP stab move + 1 high bp non-STAB move + low PP status move
            if species_data["atk"] == species_data["sp_atk"]:
                selectable_move_subsets[0] = {k for k, v in move_data.items() if k in selectable_moves and (v["type"] == species_type_1 or v["type"] == species_type_2) and 80 <= v["power"] <= 100 and k not in two_turn_moves | recharge_moves}
                selectable_move_subsets[1] = {k for k, v in move_data.items() if k in selectable_moves and (v["type"] != species_type_1 or v["type"] != species_type_2) and 60 <= v["power"] <= 80 and k not in two_turn_moves | recharge_moves}
            elif species_data["atk"] > species_data["sp_atk"]:
                selectable_move_subsets[0] = {k for k, v in move_data.items() if k in selectable_moves and (v["type"] == species_type_1 or v["type"] == species_type_2) and 80 <= v["power"] <= 100 and v["category"]  == category_to_id["Physical"] and k not in two_turn_moves | recharge_moves}
                selectable_move_subsets[1] = {k for k, v in move_data.items() if k in selectable_moves and (v["type"] != species_type_1 or v["type"] != species_type_2) and 60 <= v["power"] <= 80 and v["category"]  == category_to_id["Physical"] and k not in two_turn_moves | recharge_moves}
            else: # elif species_data['atk'] < species_data['sp_atk']:
                selectable_move_subsets[0] = {k for k, v in move_data.items() if k in selectable_moves and (v["type"] == species_type_1 or v["type"] == species_type_2) and 80 <= v["power"] <= 100 and v["category"] == category_to_id["Special"] and k not in two_turn_moves | recharge_moves}
                selectable_move_subsets[1] = {k for k, v in move_data.items() if k in selectable_moves and (v["type"] != species_type_1 or v["type"] != species_type_2) and 60 <= v["power"] <= 80 and v["category"]  == category_to_id["Special"] and k not in two_turn_moves | recharge_moves}
            selectable_move_subsets[2] = {k for k, v in move_data.items() if k in lvl_moves and 10 >= v["pp"] and v["category"] == category_to_id["Status"]}
            selectable_move_subsets[3] = protect_moves & selectable_moves
        elif generation_type_chance < 0.82:
            # 6 % Forced Two-Turn Move + 1 stab + 1 coverage or status + 1 status
            selectable_move_subsets[0] = two_turn_moves & selectable_moves
            if species_data["atk"] == species_data["sp_atk"]:
                selectable_move_subsets[1] = {k for k, v in move_data.items() if k in selectable_moves and (v["type"] == species_type_1 or v["type"] == species_type_2) and 70 <= v["power"] and k not in two_turn_moves | recharge_moves}
            elif species_data["atk"] > species_data["sp_atk"]:
                selectable_move_subsets[1] = {k for k, v in move_data.items() if k in selectable_moves and (v["type"] == species_type_1 or v["type"] == species_type_2) and 70 <= v["power"] and v["category"]  == category_to_id["Physical"] and k not in two_turn_moves | recharge_moves}
            else: # elif species_data['atk'] < species_data['sp_atk']:
                selectable_move_subsets[1] = {k for k, v in move_data.items() if k in selectable_moves and (v["type"] == species_type_1 or v["type"] == species_type_2) and 70 <= v["power"] and v["category"]  == category_to_id["Special"] and k not in two_turn_moves | recharge_moves}
            selectable_move_subsets[2] = {k for k, v in move_data.items() if k in selectable_moves and(v["type"] != species_type_1 or v["type"] != species_type_2) and 90 >= v["power"] and 40 <= v["power"] and k not in two_turn_moves | recharge_moves}
            if world.random.random() < 0.6:
                selectable_move_subsets[3] = {k for k, v in move_data.items() if k in lvl_moves and 30 >= v["pp"] and v["category"] == category_to_id["Status"] and k not in protect_moves}
            else:
                selectable_move_subsets[3] = {k for k, v in move_data.items() if k in tm_moves and 30 >= v["pp"] and v["category"] == category_to_id["Status"] and k not in weather_moves | protect_moves}
        elif generation_type_chance < 0.88:
            # 6% High BP Move + 3 Random Status
            if species_data["atk"] == species_data["sp_atk"]:
                selectable_move_subsets[0] = {k for k, v in move_data.items() if k in selectable_moves and (v["type"] == species_type_1 or v["type"] == species_type_2) and 80 <= v["power"] <= 100 and k not in two_turn_moves | recharge_moves}
            elif species_data["atk"] > species_data["sp_atk"]:
                selectable_move_subsets[0] = {k for k, v in move_data.items() if k in selectable_moves and (v["type"] == species_type_1 or v["type"] == species_type_2) and 80 <= v["power"] <= 100 and v["category"]  == category_to_id["Physical"] and k not in two_turn_moves | recharge_moves}
            else: # elif species_data['atk'] < species_data['sp_atk']:
                selectable_move_subsets[0] = {k for k, v in move_data.items() if k in selectable_moves and (v["type"] == species_type_1 or v["type"] == species_type_2) and 80 <= v["power"] <= 100 and v["category"] == category_to_id["Special"] and k not in two_turn_moves | recharge_moves}
            selectable_move_subsets[1] = {k for k, v in move_data.items() if k in selectable_moves and 10 >= v["pp"] and v["category"] == category_to_id["Status"] and k not in protect_moves | weather_moves}
            selectable_move_subsets[2] = {k for k, v in move_data.items() if k in selectable_moves and 20 >= v["pp"] and v["category"] == category_to_id["Status"] and k not in protect_moves | weather_moves}
            selectable_move_subsets[3] = {k for k, v in move_data.items() if k in selectable_moves and 30 >= v["pp"] and v["category"] == category_to_id["Status"] and k not in protect_moves | weather_moves}
        elif generation_type_chance < 0.91:
            # 3% Quadruple status (why.)
            num_lvl_status_moves: int = world.random.choice(list({0, 1, 1, 2, 2, 2, 2, 2, 3, 3, 3, 3, 4}))
            for i in range(num_lvl_status_moves):
                selectable_move_subsets[i] = {k for k, v in move_data.items() if k in lvl_moves and v["category"] == category_to_id["Status"] and k not in protect_moves}
            for i in range(4 - num_lvl_status_moves):
                selectable_move_subsets[num_lvl_status_moves + i] = {k for k, v in move_data.items() if k in tm_moves and v["category"] == category_to_id["Status"] and k not in weather_moves}
        elif generation_type_chance < 0.94:
            # 3% Force recharge move + 1 lvl damage + 1 tm damage + 1 status
            selectable_move_subsets[0] = recharge_moves & selectable_moves
            selectable_move_subsets[1] = {k for k, v in move_data.items() if k in lvl_moves and 0 < v["power"] and k not in two_turn_moves | recharge_moves}
            selectable_move_subsets[2] = {k for k, v in move_data.items() if k in tm_moves and 0 < v["power"] and k not in two_turn_moves | recharge_moves}
            selectable_move_subsets[3] = {k for k, v in move_data.items() if k in selectable_moves and v["category"] == category_to_id["Status"] and k not in protect_moves | weather_moves}
        else:
            # 6% Entirely random
            selectable_move_subsets[0] = selectable_moves
            selectable_move_subsets[1] = selectable_moves
            selectable_move_subsets[2] = selectable_moves
            selectable_move_subsets[3] = selectable_moves
        selected_moves = generate_normal_moveset(world, selectable_move_subsets[0], selectable_move_subsets[1], selectable_move_subsets[2], selectable_move_subsets[3])

    # If for some reason the number of moves generated above is less than 4 for whatever reason,
    # fill it out with a random of assortment of moves. Also, if for some reason more than
    # four moves are added to the moveset force it down to 4 moves. Note: Ideally, never add more
    # than 4 moves.
    if len(selected_moves) < 4:
        unselected_moves: set = selectable_moves - set(selected_moves)
        # selected_moves.extend([move_to_id['-']] * (4 - len(selected_moves)))
        selected_moves.extend(world.random.sample(list(unselected_moves), 4 - len(selected_moves)))
    elif len(selected_moves) != 4:
        selected_moves = selected_moves[4:]
    
    logger = logging.getLogger()
    logger.info('%s Set: %s\n', id_to_mon[species], str([move_data[item]["name"] for item in selected_moves]))
    
    # TODO: item logic
    selected_item = item_to_id['None']
    
    # Add the minimal Pokemon Data to the AP World.
    minimal_pokemon_data: dict[str, Any] = {
        "pid": pid,
        "ivs": ivs,
        "moves": selected_moves,
        "item": selected_item,
    }
    return minimal_pokemon_data

# Generate a moveset for when a monster has 0 selectable moves because of yaml settings.
# ie: Removing Harden from allowed moves will mean that Kakuna/Metapod has 0 valid moves which is an
# illegal moveset. Build a new one from scratch.
def generate_panic_moveset(world: World, species: int, lvl: int) -> list[int]:
    generated_moveset: list[int] = []
    if world.random.random() < 0.2:
        # Your folly has been noted... explosively.
        generated_moveset.append(move_to_id['Explosion'])
        generated_moveset.extend([move_to_id['-']] * 3)
    else:
        panic_learnset: list[int] = [move for lvl_learned, move in list(level_up_moves[species]) if lvl_learned < max(lvl, 1)]
        if len(panic_learnset) == 0:
            # This should never run. If it is, there may be a mistake in the level_up_moves table.
            generated_moveset.append(move_to_id['Explosion'])
            generated_moveset.extend([move_to_id['-']] * 3)
        if len(panic_learnset) < 4:
            # If there aren't many moves in the original moveset (like for Kakuna), just add those.
            generated_moveset.extend(world.random.sample(list(panic_learnset), len(panic_learnset)))
            generated_moveset.extend([move_to_id["-"]] * (4 - len(panic_learnset)))
        else:
            # Randomly roll moves available if greater than 4.
            generated_moveset.extend(world.random.sample(list(panic_learnset), 4))
    return generated_moveset

def generate_normal_moveset(world: World, move_0_options: set[int], move_1_options: set[int], move_2_options: set[int], move_3_options: set[int]) -> list[int]:
    generated_moveset: list[int] = []
    if len(move_0_options) > 0:
        generated_moveset.append(world.random.choice(list(move_0_options)))
    move_1_options.discard(set(generated_moveset))
    if len(move_1_options) > 0:
        generated_moveset.append(world.random.choice(list(move_1_options)))
    move_2_options.discard(set(generated_moveset))
    if len(move_2_options) > 0:
        generated_moveset.append(world.random.choice(list(move_2_options)))
    move_3_options.discard(set(generated_moveset))
    if len(move_3_options) > 0:
        generated_moveset.append(world.random.choice(list(move_3_options)))
    return generated_moveset


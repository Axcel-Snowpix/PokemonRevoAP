from dataclasses import dataclass
import logging
from typing import Any

from worlds.AutoWorld import World

from .data.gen4_pokemon_structure import Gen4Pokemon, decode_text
from .data.pokemon_data import pokemon_data, ability_to_id, item_to_id, id_to_item, move_to_id, move_data, category_to_id, level_up_moves, id_to_mon, mon_to_id, type_to_id, type_to_plate, tm_learnsets, hp_type_table, bit_to_gender, gender_to_bit, id_to_ability, id_to_nature, berry_to_natural_gift_type 

weather_setting_moves: set[int] = {move_to_id['Sunny Day'], move_to_id['Sandstorm'], move_to_id['Rain Dance'], move_to_id['Hail']}
harsh_sunlight_moves: set[int] = {move_to_id['SolarBeam'], move_to_id['Weather Ball'], move_to_id['Moonlight'], move_to_id['Synthesis'], move_to_id['Morning Sun']}
rain_moves: set[int] = {move_to_id['Thunder'], move_to_id['Weather Ball']}
sandstorm_moves: set[int] = {move_to_id['Weather Ball']}
hail_moves: set[int] = {move_to_id['Weather Ball'], move_to_id['Blizzard']}
weather_moves: set[int] = weather_setting_moves | harsh_sunlight_moves | rain_moves | sandstorm_moves | hail_moves
two_turn_moves: set[int] = {move_to_id['Bounce'], move_to_id['Dig'], move_to_id['Dive'], move_to_id['Fly'], move_to_id['Shadow Force'], move_to_id['Skull Bash'], move_to_id['Sky Attack'], move_to_id['SolarBeam']}
protect_moves: set[int] = {move_to_id['Protect'], move_to_id['Detect']}
recharge_moves: set[int] = {move_to_id['Giga Impact'], move_to_id['Rock Wrecker'], move_to_id['Hyper Beam'], move_to_id['Blast Burn'], move_to_id['Hydro Cannon'], move_to_id['Frenzy Plant'], move_to_id['Roar of Time']}
recoil_moves: set[int] = {move_to_id["Brave Bird"], move_to_id["Double-Edge"], move_to_id["Flare Blitz"], move_to_id["Head Smash"], move_to_id["Submission"], move_to_id["Take Down"], move_to_id["Volt Tackle"], move_to_id["Wood Hammer"]}
self_damaging_moves: set[int] = set({move_to_id["Curse"], move_to_id["Belly Drum"], move_to_id["Pain Split"]}) | recoil_moves
hazard_moves: set[int] = {move_to_id['Spikes'], move_to_id['Stealth Rock'], move_to_id['Toxic Spikes']}
explosive_moves: set[int] = {move_to_id["Explosion"], move_to_id["Selfdestruct"]}
ohko_moves: set[int] = {move_to_id["Fissure"], move_to_id["Guillotine"], move_to_id["Horn Drill"], move_to_id["Sheer Cold"]}
multhit_moves: set[int] = {move_to_id["Bone Rush"], move_to_id["Rock Blast"], move_to_id["Spike Cannon"], move_to_id["Comet Punch"], move_to_id["Fury Swipes"], move_to_id["Arm Thrust"], move_to_id["Barrage"], move_to_id["DoubleSlap"], move_to_id["Fury Attack"], move_to_id["Pin Missile"], move_to_id["Bullet Seed"], move_to_id["Icicle Spear"]}
gender_based_moves: set[int] = {move_to_id["Attract"], move_to_id["Captivate"]}
self_healing_moves: set[int] = {move_to_id["Aqua Ring"], move_to_id["Ingrain"], move_to_id["Heal Order"], move_to_id["Milk Drink"], move_to_id["Moonlight"], move_to_id["Morning Sun"], move_to_id["Recover"], move_to_id["Rest"], move_to_id["Roost"], move_to_id["Slack Off"], move_to_id["Softboiled"], move_to_id["Synthesis"], move_to_id["Pain Split"]}
item_stealing_moves: set[int] = {move_to_id["Thief"], move_to_id["Covet"]}
item_swapping_moves: set[int] = {move_to_id["Trick"], move_to_id["Switcheroo"]}
self_sleep_moves: set[int] = {move_to_id["Snore"], move_to_id["Sleep Talk"]}
target_sleep_moves: set[int] = {move_to_id["Dream Eater"], move_to_id["Nightmare"]}
stockpile_moves: set[int] = {move_to_id["Stockpile"], move_to_id["Swallow"], move_to_id["Spit Up"]}
self_confusion_moves: set[int] = {move_to_id["Outrage"], move_to_id["Petal Dance"], move_to_id["Thrash"]}
status_healing_moves: set[int] = {move_to_id["Refresh"], move_to_id["Heal Bell"], move_to_id["Aromatherapy"]}

niche_damage_moves: set[int] = two_turn_moves | recharge_moves | explosive_moves | self_sleep_moves | target_sleep_moves | ohko_moves | set({move_to_id["Spit Up"]})
niche_status_moves: set[int] = {move_to_id["Nightmare"], move_to_id["Swallow"], move_to_id["Imprison"], move_to_id["Sketch"], move_to_id["Splash"]}

status_berry_items: set[int] = {item_to_id["Cheri Berry"], item_to_id["Chesto Berry"], item_to_id["Pecha Berry"], item_to_id["Rawst Berry"], item_to_id["Aspear Berry"], item_to_id["Persim Berry"], item_to_id["Lum Berry"]}
healing_percent_items: set[int] = {item_to_id["Sitrus Berry"], item_to_id["Figy Berry"], item_to_id["Wiki Berry"], item_to_id["Mago Berry"], item_to_id["Aguav Berry"], item_to_id["Iapapa Berry"]}

weather_setting_abilities: set[int] = {ability_to_id["Drought"], ability_to_id["Drizzle"], ability_to_id["Sand Stream"], ability_to_id["Snow Warning"]}
weather_removing_abilities: set[int] = {ability_to_id["Cloud Nine"], ability_to_id["Air Lock"]}
sleep_preventing_abilities: set[int] = {ability_to_id["Insomnia"], ability_to_id["Vital Spirit"]}
status_countering_abilities: set[int] = {ability_to_id["Shed Skin"], ability_to_id["Hydration"], ability_to_id["Natural Cure"], ability_to_id["Leaf Guard"]}

# Non-exhaustive list, but rather a 'useful' list.
general_fling_items: set[int] = {item_to_id["Flame Orb"], item_to_id["King's Rock"], item_to_id["Light Ball"], item_to_id["Mental Herb"], item_to_id["Poison Barb"], item_to_id["Razor Fang"], item_to_id["Toxic Orb"], item_to_id["Hard Stone"], item_to_id["Iron Ball"]}

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
        return ability_to_id['None'] # this could also just be 0
    
    species_data = pokemon_data[species]
    ability_1: int = species_data["ability1"]
    ability_2: int = species_data["ability2"]
    if ability_2 == ability_to_id['None'] or pid & 0b1 == 0b0:
        return ability_1
    else:
        return ability_2

def pid_to_gender_for_species(pid: int, species: int) -> int:
    if species not in pokemon_data:
        return 0b00
        
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

def get_stat(stat: str, base_stat: int, lvl: int, iv: int, ev: int, nature: int):
    if stat == "hp":
        if base_stat == 1:
            return 1
        else:
            return int(((2 * base_stat + iv + (ev // 4)) * lvl // 100) + lvl + 10)
    else:
        if nature_to_increased_stat(nature) == stat:
            nat_mod = 1.1
        elif nature_to_decreased_stat(nature) == stat:
            nat_mod = 0.9
        else:
            nat_mod = 1
        return int((((2 * base_stat + iv + (ev // 4)) * lvl // 100) + 5) * nat_mod)
    
def generate_normal_random_pokemon(world: World, lvl: int) -> list[dict[str, Any]]:
    # TODO: Remove moves listed in the yaml that the user wont want selected. ie: Splash, Memento
    generated_pokemon: list[dict[str, Any]] = []
    for species in pokemon_data.keys():
        if id_to_mon[species] == "Deoxys-Attack":
            break
        else:
            # Wormadam form needs to be decided here so that the moveset can be set accordingly.
            if species == mon_to_id["Wormadam-Plant"]:
                form = world.random.randint(0,2)
                if form > 0:
                    species = 498 + form
            lvl_moves: set[int] = set({move for lvl_learned, move in list(level_up_moves[species]) if lvl_learned < lvl})
            tm_moves: set[int] = tm_learnsets[species]
            generated_pokemon.append(generate_pokemon_inner(world, species, lvl_moves, tm_moves, set(), lvl))
    return generated_pokemon

def generate_chaotic_random_pokemon(world: World, lvl):
    # TODO: Remove moves listed in the yaml that the user wont want selected. ie: Splash, Memento
    generated_pokemon: list[dict[str, Any]] = []
    for species in pokemon_data.keys():
        if id_to_mon[species] == "Deoxys-Attack":
            break
        else:
            # Wormadam form needs to be decided here so that the moveset can be set accordingly.
            if species == mon_to_id["Wormadam-Plant"]:
                form = world.random.randint(0,2)
                if form > 0:
                    species = 498 + form
            generated_pokemon.append(generate_pokemon_inner(world, species, set(move_data.keys()), set(move_data.keys()), set(), lvl))
    return generated_pokemon

def generate_pokemon_inner(world: World, species: int, lvl_moves: set[int], tm_moves: set[int], items: set[int], lvl: int) -> dict[str, Any]:
    logger = logging.getLogger()

    species_data = pokemon_data[species]

    # Generate Pokémon's Form, if it has more than 1.
    if species == mon_to_id["Unown"]:
        form = world.random.randint(0, 27)
    elif species == mon_to_id["Deoxys-Normal"]:
        form = world.random.randint(0,3)
        if form > 0:
            species = 495 + form
            species_data = pokemon_data[species]
    elif species == mon_to_id["Burmy"]:
        form = world.random.randint(0,2)
    elif species in [mon_to_id["Wormadam-Sandy"], mon_to_id["Wormadam-Trash"]]:
        form = species - 498
    elif species in [mon_to_id["Shellos"], mon_to_id["Gastrodon"]]:
        form = world.random.randint(0,1)
    elif species == mon_to_id["Arceus"]:
        form_list = list(type_to_id.values())
        form_list.remove(type_to_id["???"])
        form = world.random.sample(form_list, 1)[0]
        species_data["type1"] = form
        species_data["type2"] = form
    else:
        form = 0

    logger.info(f"Species: {id_to_mon[species]}")
    logger.info(f"Form: {form}")
    
    # Generate the PID, IVs and Friendship (needs to be saved).
    pid: int = world.random.randint(0, 0xFFFFFFFF)
    ivs: int = world.random.randint(0, 0x3FFFFFFF) << 2
    friendship: int = world.random.randint(0, 0xFF)

    logger.info(f"PID: {pid}")
    logger.info(f"IVs: {ivs >> 27 & 31}/{ivs >> 22 & 31}/{ivs >> 17 & 31}/{ivs >> 12 & 31}/{ivs >> 7 & 31}/{ivs >> 2 & 31}")
    logger.info(f"Friendship: {friendship}")
    
    # Grab the ability, gender, and nature to check for moves/items/etc. This does
    # not need to be saved since it can be recalculated from the pid and species.
    gender: int = pid_to_gender_for_species(pid, species)
    ability: int = pid_to_ability_for_species(pid, species)
    nature: int = pid_to_nature(pid)

    logger.info(f"Gender: {bit_to_gender[gender]}")
    logger.info(f"Ability: {id_to_ability[ability]}")
    logger.info(f"Nature: {id_to_nature[nature]}")

    # Generate Pokéball (needs to be saved).
    pokeball = world.random.randint(0x1,0x10)
    logger.info(f"Pokéball: {pokeball}")

    # Calculate Attack and Special Attack stats.
    atk = get_stat("attack", species_data["atk"], lvl, ivs >> 22 & 31, 0, nature)
    if ability in [ability_to_id["Huge Power"], ability_to_id["Pure Power"]]:
        atk = atk * 2
    elif ability in [ability_to_id["Guts"], ability_to_id["Hustle"]]:
        atk = int(atk * 1.5)
    logger.info(f"Attack Stat: {atk}")
    sp_atk = get_stat("sp attack", species_data["sp_atk"], lvl, ivs >> 7 & 31, 0, nature)
    logger.info(f"Special Attack Stat: {sp_atk}")

    # Copy move data.
    move_data_mod = {**{k: v for k, v in move_data.items() if k in (lvl_moves | tm_moves)}}
    moves_list = list(move_data_mod.keys())
    # Apply Technician Power Boost
    if ability_to_id["Technician"] == ability:
        for k, v in move_data_mod.items():
            power = v['power']
            if power <= 60:
                move_data_mod[k]['power'] = int(power * 1.5)
    # Set Return and Frustration's Base Powers.
    if move_to_id["Return"] in moves_list:
        return_bp = int(max(friendship // 2.5, 1))
        move_data_mod[move_to_id["Return"]]['power'] = return_bp
        logger.info(f"Return Power: {return_bp}")
    if move_to_id["Frustration"] in moves_list:
        frustration_bp = int(max((255 - friendship) // 2.5, 1))
        move_data_mod[move_to_id["Frustration"]]['power'] = frustration_bp
        logger.info(f"Frustration Power: {frustration_bp}")
    # Set Hidden Power data.
    if move_to_id["Hidden Power"] in moves_list:
        if ability != ability_to_id['Normalize']:
            # Set Hidden Power Type.
            hp_type = ((ivs & 1)+(ivs >> 5 & 1)*2+(ivs >> 10 & 1)*4+(ivs >> 15 & 1)*8+(ivs >> 20 & 1)*16+(ivs >> 25 & 1)*32) * 15 // 63
            move_data_mod[move_to_id["Hidden Power"]]['type'] = type_to_id[hp_type_table[hp_type]]
            logger.info(f"HP Type: {hp_type_table[hp_type]}")
        # Set Hidden Power base power.
        hp_power = (((ivs >> 1 & 1)+(ivs >> 6 & 1)*2+(ivs >> 11 & 1)*4+(ivs >> 16 & 1)*8+(ivs >> 21 & 1)*16+(ivs >> 26 & 1)*32) * 40 // 63) + 30
        move_data_mod[move_to_id["Hidden Power"]]['power'] = hp_power
        logger.info(f"HP Power: {hp_power}")
    # Set Weather Ball Type and power.
    if ability in weather_setting_moves and move_to_id["Weather Ball"] in moves_list:
        move_data_mod[move_to_id["Weather Ball"]]["power"] = 100
        if ability == ability_to_id["Drought"]:
            move_data_mod[move_to_id["Weather Ball"]]["type"] = type_to_id["Fire"]
        elif ability == ability_to_id["Drizzle"]:
            move_data_mod[move_to_id["Weather Ball"]]["type"] = type_to_id["Water"]
        elif ability == ability_to_id["Sand Stream"]:
            move_data_mod[move_to_id["Weather Ball"]]["type"] = type_to_id["Rock"]
        else: # elif ability == ability_to_id["Snow Warning"]
            move_data_mod[move_to_id["Weather Ball"]]["type"] = type_to_id["Ice"]
    # Set all Moves to Normal Type if ability is Normalize.
    if ability == ability_to_id['Normalize']:
        for id in list(move_data_mod.keys()):
            move_data_mod[id]['type'] = type_to_id['Normal']
        logger.info("Set all moves to Normal Type.")
    # Recalculate BP for fixed multi-hit Moves
    if move_to_id["Bonemerang"] in moves_list:
        bonemerang_one_hit_bp = move_data_mod[move_to_id["Bonemerang"]]['power']
        move_data_mod[move_to_id["Bonemerang"]]['power'] = bonemerang_one_hit_bp * 2
    if move_to_id["Double Hit"] in moves_list:
        double_hit_one_hit_bp = move_data_mod[move_to_id["Double Hit"]]['power']
        move_data_mod[move_to_id["Double Hit"]]['power'] = double_hit_one_hit_bp * 2
    # Calculate BP for random multi-hit Moves
    average_number_multi_hits = 3
    if ability_to_id["Skill Link"] == ability:
        average_number_multi_hits = 5
    else:
        average_number_multi_hits = 3
    for k, v in move_data_mod.items():
        if k in multhit_moves:
            power = v['power']
            move_data_mod[k]['power'] = int(power * average_number_multi_hits)
    # Force BP variable moves to average.
    if move_to_id["Magnitude"] in moves_list:
        move_data_mod[move_to_id["Magnitude"]]['power'] = 70
    if move_to_id["Present"] in moves_list:
        move_data_mod[move_to_id["Present"]]['power'] = 52
    if move_to_id["Trump Card"] in moves_list:
        move_data_mod[move_to_id["Trump Card"]]['power'] = 60
    if move_to_id["Wring Out"] in moves_list:
        move_data_mod[move_to_id["Wring Out"]]['power'] = 60
    if move_to_id["Crush Grip"] in moves_list:
        move_data_mod[move_to_id["Crush Grip"]]['power'] = 60
    if move_to_id["Water Spout"] in moves_list:
        move_data_mod[move_to_id["Water Spout"]]['power'] = 75
    if move_to_id["Eruption"] in moves_list:
        move_data_mod[move_to_id["Eruption"]]['power'] = 75
    if move_to_id["Reversal"] in moves_list:
        move_data_mod[move_to_id["Reversal"]]['power'] = 80
    if move_to_id["Punishment"] in moves_list: # 60 + 20 Per Increasced Stage of Target
        move_data_mod[move_to_id["Punishment"]]['power'] = 60
    # TODO: Deal damaging moves with fixed damage so that they aren't picked for things like Guts
    # (either by artificially making them status moves, double checking when needed, etc).
    
    # Check for valid moves for the species.
    selected_moves: list[int] = []
    selectable_moves = lvl_moves | tm_moves
    
    is_shedinja: bool = species_data["hp"] == 1
    # Remove extremely redundant moves from selectable_moves
    if ability in weather_setting_abilities or ability in weather_removing_abilities:
        selectable_moves -= weather_setting_moves
    if is_shedinja:
        selectable_moves -= self_damaging_moves
        selectable_moves -= self_healing_moves
        selectable_moves -= set({move_to_id["Bide"]})
    if gender == gender_to_bit["Genderless"]:
        selectable_moves -= gender_based_moves
    if ability in sleep_preventing_abilities:
        selectable_moves -= set({move_to_id["Rest"]})
    elif ability == ability_to_id["Scrappy"]:
        selectable_moves -= set({move_to_id["Foresight"], move_to_id["Odor Sleuth"]})
    elif ability == ability_to_id["Truant"]:
        selectable_moves -= two_turn_moves
    elif ability == ability_to_id["Damp"]:
        selectable_moves -= explosive_moves
    elif ability == ability_to_id["Klutz"]:
        # Note: Technically, Bug Bite and Pluck will remove and 'consume' the berry from the opponent; however, the user
        # does not gain its effect. They both also still do damage.
        selectable_moves -= set({move_to_id["Recycle"], move_to_id["Natural Gift"]}) #, move_to_id["Bug Bite"], move_to_id["Pluck"]})
    elif ability == ability_to_id["Dry Skin"]:
        selectable_moves -= set({move_to_id["Sunny Day"]})
    elif ability == ability_to_id["Shell Armor"]:
        selectable_moves -= set({move_to_id["Safeguard"]})

    num_selectable_moves = len(selectable_moves)
    
    if num_selectable_moves == 0:
        # If a Pokemon has 0 moves available (because of yaml settings or bugs), PANIC.
        logger.info("Generation Type: PANIC")
        selected_moves.extend(generate_panic_moveset(world, species, 50))
    elif num_selectable_moves <= 4:
        logger.info("Generation Type: All selectable moves (<= 4 moves available)")
        # If a Pokemon has less than 4 moves available to it, just select those moves.
        selected_moves.extend(selectable_moves)
        if num_selectable_moves < 4:
            # Pad out the moveset until we get 4 moves.
            selected_moves.extend([move_to_id['-']] * (4 - num_selectable_moves))
    
    selected_item = item_to_id["None"]
    # TODO: Insert chance of certain sets with usable strategies to be generated so that they appear
    # within 'reasonable' frequency.
    # Weather Set (ie: Rain Dance + Damage Water Move)
    # Helping Hand or Helping Hand/Protect
    # FEAR Strategies
    # Charge + Electric Attack
    # Rest + Snore/Sleep Talk
    # Defense Curl + Rollout / Ice Ball
    # Endure + Flail
    # Fake Out + Last Resort
    # Stockpile + Spit Up/Swallow
    # Weather
    # Setup + Baton Pass
    # etc.
    
    # If none of the special cases above are true, use one of the following generalized methods to
    # generate a Pokemon.
    # TODO: Remove status moves that have 0 use from being picked on set ie: Swords Dance on Sp. Attacker
    species_type_1 = species_data["type1"]
    species_type_2 = species_data["type2"]
    selectable_move_subsets: list[set] = [set(), set(), set(), set()]
    if len(selected_moves) == 0:
        generation_type_chance: float = world.random.random()
        if generation_type_chance < 0.2:
            logger.info("Generation Type: 20% Select STAB + secondary STAB or coverage + 1 lvl status + 1 TM status")
            # 20% Select STAB + secondary STAB or coverage + 1 lvl status + 1 TM status
            # Decide type to prioritize.
            if world.random.random() < 0.5:
                primary_stab_type: int = species_type_1
                secondary_stab_type: int = species_type_2
            else:
                primary_stab_type: int = species_type_2
                secondary_stab_type: int = species_type_1
            # Select the first stab move.
            if atk == sp_atk or (id_to_ability[ability] == "Slow Start" and int(atk // 2) < sp_atk and atk > sp_atk):
                categories = [category_to_id["Physical"], category_to_id["Special"]]
            elif atk > sp_atk:
                categories = [category_to_id["Physical"]]
            else: # elif atk < sp_atk:
                categories = [category_to_id["Special"]]
            swapped_types = False
            while True:
                min_power = 70
                while True:
                    selectable_move_subsets[0] = {k for k, v in move_data_mod.items() if k in selectable_moves and v["type"] == primary_stab_type and min_power <= v["power"] and v["category"] in categories and k not in niche_damage_moves}
                    if len(selectable_move_subsets[0]) > 0 or min_power <= 0:
                        break
                    elif min_power <= 40:
                        min_power = 0
                    else:
                        min_power -= 10
                if len(selectable_move_subsets[0]) == 0 and primary_stab_type != secondary_stab_type and not swapped_types:
                    swap_type_1 = primary_stab_type
                    swap_type_2 = secondary_stab_type
                    primary_stab_type = swap_type_2
                    secondary_stab_type = swap_type_1
                    swapped_types = True
                else:
                    break
            # Either select a secondary stab move (if applicable) or a coverage move.
            if primary_stab_type == secondary_stab_type or world.random.random() < 0.35:
                selectable_move_subsets[1] = {k for k, v in move_data_mod.items() if k in selectable_moves and v["type"] != primary_stab_type and 95 >= v["power"] and 40 <= v["power"] and k not in niche_damage_moves}
                if len(selectable_move_subsets[1]) == 0:
                    selectable_move_subsets[1] = {k for k, v in move_data_mod.items() if k in selectable_moves and v["type"] != primary_stab_type and 95 >= v["power"] and k not in niche_damage_moves}
            else:
                selectable_move_subsets[1] = {k for k, v in move_data_mod.items() if k in selectable_moves and v["type"] == secondary_stab_type and 80 >= v["power"] and 40 <= v["power"] and k not in (niche_damage_moves - two_turn_moves)}
                if len(selectable_move_subsets[1]) == 0:
                    selectable_move_subsets[1] = {k for k, v in move_data_mod.items() if k in selectable_moves and v["type"] == secondary_stab_type and 80 >= v["power"] and k not in recharge_moves}
            # Select the level and tm status moves.
            selectable_move_subsets[2] = {k for k, v in move_data_mod.items() if k in lvl_moves and v["category"] == category_to_id["Status"] and k not in protect_moves | weather_setting_moves | niche_status_moves}
            selectable_move_subsets[3] = {k for k, v in move_data_mod.items() if k in tm_moves and v["category"] == category_to_id["Status"] and k not in protect_moves | weather_setting_moves | niche_status_moves}
        elif generation_type_chance < 0.4:
            logger.info("Generation Type: 20% Select STAB + secondary STAB or coverage + coverage + lvl or tm status")
            # 20% Select STAB + secondary STAB or coverage + coverage + lvl or tm status
            # Decide type to prioritize.
            if world.random.random() < 0.5:
                primary_stab_type: int = species_type_1
                secondary_stab_type: int = species_type_2
            else:
                primary_stab_type: int = species_type_2
                secondary_stab_type: int = species_type_1
            # Select the first stab move.
            if atk == sp_atk:
                categories = [category_to_id["Physical"], category_to_id["Special"]]
            elif atk > sp_atk:
                categories = [category_to_id["Physical"]]
            else: # elif atk < sp_atk:
                categories = [category_to_id["Special"]]
            swapped_types = False
            while True:
                min_power = 60
                while True:
                    selectable_move_subsets[0] = {k for k, v in move_data_mod.items() if k in selectable_moves and v["type"] == primary_stab_type and 60 <= v["power"] and v["category"] in categories and k not in niche_damage_moves}
                    if len(selectable_move_subsets[0]) > 0 or min_power <= 0:
                        break
                    elif min_power <= 40:
                        min_power = 0
                    else:
                        min_power -= 10
                if len(selectable_move_subsets[0]) == 0 and primary_stab_type != secondary_stab_type and not swapped_types:
                    swap_type_1 = primary_stab_type
                    swap_type_2 = secondary_stab_type
                    primary_stab_type = swap_type_2
                    secondary_stab_type = swap_type_1
                    swapped_types = True
                else:
                    break
            # Either select a secondary stab move (if applicable) or a coverage move.
            if primary_stab_type == secondary_stab_type or world.random.random() < 0.2:
                selectable_move_subsets[1] = {k for k, v in move_data_mod.items() if k in selectable_moves and v["type"] != primary_stab_type and 80 >= v["power"] and 40 <= v["power"] and k not in niche_damage_moves}
                if len(selectable_move_subsets[1]) == 0:
                    selectable_move_subsets[1] = {k for k, v in move_data_mod.items() if k in selectable_moves and v["type"] != primary_stab_type and 80 >= v["power"]}
            else:
                selectable_move_subsets[1] = {k for k, v in move_data_mod.items() if k in selectable_moves and v["type"] == secondary_stab_type and 60 >= v["power"] and 40 <= v["power"] and k not in niche_damage_moves}
                if len(selectable_move_subsets[1]) == 0:
                    selectable_move_subsets[1] = {k for k, v in move_data_mod.items() if k in selectable_moves and v["type"] == secondary_stab_type and 60 >= v["power"]}
            # Select a random damage move.
            selectable_move_subsets[2] = {k for k, v in move_data_mod.items() if k in selectable_moves and v["type"] != primary_stab_type and v["type"] != secondary_stab_type and 80 >= v["power"] and k not in niche_damage_moves}
            # Select a random level up status move.
            selectable_move_subsets[3] = {k for k, v in move_data_mod.items() if k in lvl_moves and v["category"] == category_to_id["Status"] and k not in protect_moves | weather_setting_moves | niche_status_moves}
        elif generation_type_chance < 0.5:
            # 10% Select 1 level damage move (higher power) + 1 level damage move (lower power) + random tm (higher power) + random tm (lower power)
            logger.info("Generation Type: 10% Select 1 level damage move (higher power) + 1 level damage move (lower power) + random tm (higher power) + random tm (lower power)")
            selectable_move_subsets[0] = {k for k, v in move_data_mod.items() if k in lvl_moves and 70 <= v["power"] and k not in niche_damage_moves}
            selectable_move_subsets[1] = {k for k, v in move_data_mod.items() if k in lvl_moves and 70 > v["power"] and k not in (niche_damage_moves - two_turn_moves - recharge_moves)}
            selectable_move_subsets[2] = {k for k, v in move_data_mod.items() if k in tm_moves and 70 <= v["power"] and k not in (niche_damage_moves - two_turn_moves - recharge_moves)}
            selectable_move_subsets[3] = {k for k, v in move_data_mod.items() if k in tm_moves and 70 > v["power"] and k not in (niche_damage_moves - two_turn_moves - recharge_moves)}
        elif generation_type_chance < 0.6:
            # 10% Select 2 random lvl damage moves + 1 random tm move (not equal to stab) + random lvl status
            logger.info("Generation Type: # 10% Select 2 random lvl damage moves + 1 random tm move (not equal to stab) + random lvl status")
            min_power = 80
            while True:
                selectable_move_subsets[0] = {k for k, v in move_data_mod.items() if k in lvl_moves and min_power <= v["power"] and v["category"] != category_to_id["Status"]}
                if len(selectable_move_subsets[0]) > 0 or min_power <= 0:
                    break
                elif min_power <= 40:
                    min_power = 0
                else:
                    min_power -= 10
            selectable_move_subsets[1] = {k for k, v in move_data_mod.items() if k in lvl_moves and 40 <= v["power"] and v["category"] != category_to_id["Status"]}
            if len(selectable_move_subsets[1]) == 0:
                selectable_move_subsets[1] = {k for k, v in move_data_mod.items() if k in lvl_moves and v["category"] != category_to_id["Status"]}
            min_power = 60
            while True:
                selectable_move_subsets[2] = {k for k, v in move_data_mod.items() if k in tm_moves and min_power <= v["power"] and v["category"] != category_to_id["Status"]}
                if len(selectable_move_subsets[2]) > 0 or min_power <= 0:
                    break
                elif min_power <= 40:
                    min_power = 0
                else:
                    min_power -= 10
            selectable_move_subsets[3] = {k for k, v in move_data_mod.items() if k in lvl_moves and v["category"] == category_to_id["Status"] and k not in protect_moves | weather_setting_moves | niche_status_moves}
        elif generation_type_chance < 0.7:
            # 10% X Damage Moves Descending In Power* + (4 - X) Moves Ascending in PP.
            logger.info("Generation Type: 10% X Damage Moves Descending In Power* + (4 - X) Moves Ascending in PP.")
            num_damage_moves: int = world.random.choice(list({0, 1, 1, 2, 2, 2, 2, 2, 3, 3, 3, 3, 4}))
            damage_power_cap: int = 150
            for i in range(num_damage_moves - 1):
                if world.random.random() < 0.8:
                    selectable_move_subsets[i] = {k for k, v in move_data_mod.items() if k in lvl_moves and damage_power_cap >= v["power"] >= (damage_power_cap / 2) and v["category"] != category_to_id["Status"] and k not in (niche_damage_moves - two_turn_moves)}
                else:
                    selectable_move_subsets[i] = {k for k, v in move_data_mod.items() if k in tm_moves and damage_power_cap >= v["power"] >= (damage_power_cap / 2) and v["category"] != category_to_id["Status"] and k not in (niche_damage_moves - two_turn_moves)}
                damage_power_cap = int(damage_power_cap * 0.75)
            pp_cap: int = 5
            for i in range(4 - num_damage_moves):
                if world.random.random() < 0.6:
                    selectable_move_subsets[num_damage_moves + i] = {k for k, v in move_data_mod.items() if k in lvl_moves and pp_cap >= v["pp"] and v["category"] == category_to_id["Status"] and k not in protect_moves | niche_status_moves}
                else:
                    selectable_move_subsets[num_damage_moves + i] = {k for k, v in move_data_mod.items() if k in tm_moves and pp_cap >= v["pp"] and v["category"] == category_to_id["Status"] and k not in weather_moves | protect_moves | niche_status_moves}
                pp_cap = pp_cap * 2
        elif generation_type_chance < 0.76:
            # 6% Forced Protect + 1 medium BP stab move + 1 high bp non-STAB move + low PP status move
            logger.info("Generation Type: 6% Forced Protect + 1 medium BP stab move + 1 high bp non-STAB move + low PP status move")
            if atk == sp_atk:
                categories = [category_to_id["Physical"], category_to_id["Special"]]
            elif atk > sp_atk:
                categories = [category_to_id["Physical"]]
            else: # elif atk < sp_atk:
                categories = [category_to_id["Special"]]
            min_power = 60
            while True:
                selectable_move_subsets[0] = {k for k, v in move_data_mod.items() if k in selectable_moves and (v["type"] == species_type_1 or v["type"] == species_type_2) and min_power <= v["power"] <= 80 and v["category"] in categories and k not in niche_damage_moves}
                if len(selectable_move_subsets[0]) > 0 or min_power <= 0:
                    break
                elif min_power <= 40:
                    min_power = 0
                else:
                    min_power -= 10
            min_power = 80
            while True:
                selectable_move_subsets[1] = {k for k, v in move_data_mod.items() if k in selectable_moves and v["type"] != species_type_1 and v["type"] != species_type_2 and min_power <= v["power"] <= 100 and v["category"] in categories and k not in niche_damage_moves}
                if len(selectable_move_subsets[1]) > 0 or min_power <= 0:
                    break
                elif min_power <= 40:
                    min_power = 0
                else:
                    min_power -= 10
            selectable_move_subsets[2] = {k for k, v in move_data_mod.items() if k in lvl_moves and 10 >= v["pp"] and v["category"] == category_to_id["Status"] and k not in niche_status_moves}
            selectable_move_subsets[3] = protect_moves & selectable_moves
        elif generation_type_chance < 0.82:
            # 6 % Forced Two-Turn Move + 1 stab + 1 coverage + 1 status
            logger.info("Generation Type: 6 % Forced Two-Turn Move + 1 stab + 1 coverage + 1 status")
            selectable_move_subsets[0] = two_turn_moves & selectable_moves
            if atk == sp_atk:
                categories = [category_to_id["Physical"], category_to_id["Special"]]
            elif atk > sp_atk:
                categories = [category_to_id["Physical"]]
            else: # elif atk < sp_atk:
                categories = [category_to_id["Special"]]
            min_power = 70
            while True:
                selectable_move_subsets[1] = {k for k, v in move_data_mod.items() if k in selectable_moves and (v["type"] == species_type_1 or v["type"] == species_type_2) and min_power <= v["power"] and v["category"] in categories and k not in niche_damage_moves}
                if len(selectable_move_subsets[1]) > 0 or min_power <= 0:
                    break
                elif min_power <= 40:
                    min_power = 0
                else:
                    min_power -= 10
            selectable_move_subsets[2] = {k for k, v in move_data_mod.items() if k in selectable_moves and(v["type"] != species_type_1 or v["type"] != species_type_2) and 90 >= v["power"] and 40 <= v["power"] and k not in two_turn_moves | recharge_moves}
            if world.random.random() < 0.6:
                selectable_move_subsets[3] = {k for k, v in move_data_mod.items() if k in lvl_moves and 30 >= v["pp"] and v["category"] == category_to_id["Status"] and k not in protect_moves | niche_status_moves}
            else:
                selectable_move_subsets[3] = {k for k, v in move_data_mod.items() if k in tm_moves and 30 >= v["pp"] and v["category"] == category_to_id["Status"] and k not in weather_moves | protect_moves | niche_status_moves}
        elif generation_type_chance < 0.88:
            # 6% High BP Move + 3 Random Status
            logger.info("Generation Type: 6% High BP Move + 3 Random Status")
            if atk == sp_atk:
                selectable_move_subsets[0] = {k for k, v in move_data_mod.items() if k in selectable_moves and (v["type"] == species_type_1 or v["type"] == species_type_2) and 80 <= v["power"] <= 100 and k not in two_turn_moves | recharge_moves}
            elif atk > sp_atk:
                selectable_move_subsets[0] = {k for k, v in move_data_mod.items() if k in selectable_moves and (v["type"] == species_type_1 or v["type"] == species_type_2) and 80 <= v["power"] <= 100 and v["category"]  == category_to_id["Physical"] and k not in two_turn_moves | recharge_moves}
            else: # elif atk < sp_atk:
                selectable_move_subsets[0] = {k for k, v in move_data_mod.items() if k in selectable_moves and (v["type"] == species_type_1 or v["type"] == species_type_2) and 80 <= v["power"] <= 100 and v["category"] == category_to_id["Special"] and k not in two_turn_moves | recharge_moves}
            selectable_move_subsets[1] = {k for k, v in move_data_mod.items() if k in selectable_moves and 10 >= v["pp"] and v["category"] == category_to_id["Status"] and k not in protect_moves | weather_moves | niche_status_moves}
            selectable_move_subsets[2] = {k for k, v in move_data_mod.items() if k in selectable_moves and 20 >= v["pp"] and v["category"] == category_to_id["Status"] and k not in protect_moves | weather_moves | niche_status_moves}
            selectable_move_subsets[3] = {k for k, v in move_data_mod.items() if k in selectable_moves and 30 >= v["pp"] and v["category"] == category_to_id["Status"] and k not in protect_moves | weather_moves | niche_status_moves}
        elif generation_type_chance < 0.91:
            # 3% Quadruple status (why.)
            logger.info("Generation Type: 3% Quadruple status (why.)")
            num_lvl_status_moves: int = world.random.choice(list({0, 1, 1, 2, 2, 2, 2, 2, 3, 3, 3, 3, 4}))
            for i in range(num_lvl_status_moves):
                selectable_move_subsets[i] = {k for k, v in move_data_mod.items() if k in lvl_moves and v["category"] == category_to_id["Status"] and k not in protect_moves}
            for i in range(4 - num_lvl_status_moves):
                selectable_move_subsets[num_lvl_status_moves + i] = {k for k, v in move_data_mod.items() if k in tm_moves and v["category"] == category_to_id["Status"] and k not in weather_moves | niche_status_moves}
        elif generation_type_chance < 0.94:
            # 3% Force recharge move + 1 lvl damage + 1 tm damage + 1 status
            logger.info("Generation Type: 3% Force recharge move + 1 lvl damage + 1 tm damage + 1 status")
            selectable_move_subsets[0] = recharge_moves & selectable_moves
            selectable_move_subsets[1] = {k for k, v in move_data_mod.items() if k in lvl_moves and 0 < v["power"] and k not in two_turn_moves | recharge_moves}
            selectable_move_subsets[2] = {k for k, v in move_data_mod.items() if k in tm_moves and 0 < v["power"] and k not in two_turn_moves | recharge_moves}
            selectable_move_subsets[3] = {k for k, v in move_data_mod.items() if k in selectable_moves and v["category"] == category_to_id["Status"] and k not in protect_moves | weather_moves | niche_status_moves}
        else:
            # 6% Mostly random.
            logger.info("Generation Type: 6% MOSTLY random")
            selectable_move_subsets[0] = selectable_moves - niche_status_moves - niche_damage_moves
            selectable_move_subsets[1] = selectable_moves - niche_status_moves - niche_damage_moves
            selectable_move_subsets[2] = selectable_moves - niche_status_moves - niche_damage_moves
            selectable_move_subsets[3] = selectable_moves - niche_status_moves - niche_damage_moves
        selected_moves = generate_normal_moveset(world, selectable_move_subsets[0], selectable_move_subsets[1], selectable_move_subsets[2], selectable_move_subsets[3])

    # If for some reason the number of moves generated above is less than 4 for whatever reason,
    # fill it out with a random of assortment of moves. Also, if for some reason more than
    # four moves are added to the moveset force it down to 4 moves. Note: Ideally, never add more
    # than 4 moves.
    if len(selected_moves) < 4:
        logger.info("Not enough moves, pad out the moveset.")
        unselected_moves: set = selectable_moves - set(selected_moves)
        # selected_moves.extend([move_to_id['-']] * (4 - len(selected_moves)))
        selected_moves.extend(world.random.sample(list(unselected_moves), 4 - len(selected_moves)))
    elif len(selected_moves) != 4:
        logger.info("WARNING: More than 4 moves selected, something is wrong. Reducing the moveset")
        selected_moves = selected_moves[4:]
    
    logger.info('Moveset: %s', str([move_data[item]["name"] for item in selected_moves]))

    # Generate EVs.
    total_evs = world.random.randint(0, 510)
    logger.info(f"Total EVs: {total_evs}")
    stats_pool = ["hp", "atk", "def", "spe", "spa", "spd"]
    evs = {"hp": 0, "atk": 0, "def": 0, "spe": 0, "spa": 0, "spd": 0}
    physical = False
    special = False
    for move in selected_moves:
        if move_data[move]["category"] == category_to_id["Physical"]:
            physical = True
        elif move_data[move]["category"] == category_to_id["Special"]:
            special = True
    if not physical:
        stats_pool.remove("atk")
    if not special:
        stats_pool.remove("spa")
    if move_to_id["Trick Room"] in selected_moves:
        stats_pool.remove("spd")
    while total_evs > 0:
        stat_chosen = world.random.sample(stats_pool, 1)[0]
        ev_amount = world.random.randint(1,min(total_evs, 252))
        if evs[stat_chosen] + ev_amount > 252:
            ev_amount = 252 - evs[stat_chosen]
        evs[stat_chosen] += ev_amount
        if evs[stat_chosen] >= 252:
            stats_pool.remove(stat_chosen)
        total_evs -= ev_amount
    logger.info(f"EV Spread: {evs["hp"]}/{evs["atk"]}/{evs["def"]}/{evs["spe"]}/{evs["spa"]}/{evs["spd"]}")
    
    # Check for item stealing move.
    has_item_stealing_move = len(item_stealing_moves & set(selected_moves)) > 0
    # Try to give species exclusive items. Having thief will override the item to None unless the
    # user is Arceus with a form that requires a plate.
    if species == mon_to_id["Arceus"] and form > 0:
        # Arceus-Steel or Arceus-Flying? Arceus-Steel(Arceus-Flying)
        selected_item = type_to_plate[form]
    elif selected_item != item_to_id["None"] or has_item_stealing_move:
        pass
    elif species == mon_to_id["Pikachu"] and (physical or special) and world.random.random() < 0.5:
        selected_item = item_to_id["Light Ball"]
    elif species == mon_to_id["Farfetch'D"] and physical and world.random.random() < 0.5:
        selected_item = item_to_id["Stick"]
    elif species == mon_to_id["Ditto"] and world.random.random() < 0.5:
        if not special or world.random.random() < 0.25:
           selected_item = item_to_id["Metal Powder"]
        else:
           selected_item = item_to_id["Quick Powder"]
    elif (species == mon_to_id["Cubone"] or species == mon_to_id["Marowak"]) and physical and world.random.random() < 0.5:
        selected_item = item_to_id["Thick Club"]
    elif species == mon_to_id["Clamperl"] and world.random.random() < 0.5:
        if not special or world.random.random() < 0.5:
            selected_item = item_to_id["DeepSeaScale"]
        else:
            selected_item = item_to_id["DeepSeaTooth"]
    elif (species == mon_to_id["Latias"] or species == mon_to_id["Latios"]) and world.random.random() < 0.25:
        selected_item = item_to_id["Soul Dew"]
    elif species == mon_to_id["Dialga"] and world.random.random() < 0.25:
        steel_or_dragon_moves = {k for k, v in move_data_mod.items() if k in selected_moves and(v["type"] == type_to_id["Dragon"] or v["type"] == type_to_id["Steel"]) and 0 < v["power"]}
        if len(steel_or_dragon_moves) > 0:
            selected_item = item_to_id["Adamant Orb"]
    elif species == mon_to_id["Palkia"] and world.random.random() < 0.25:
        steel_or_dragon_moves = {k for k, v in move_data_mod.items() if k in selected_moves and(v["type"] == type_to_id["Dragon"] or v["type"] == type_to_id["Water"]) and 0 < v["power"]}
        if len(steel_or_dragon_moves) > 0:
            selected_item = item_to_id["Lustrous Orb"]
    
    # Handle cases where a very specific item should be used.
    if has_item_stealing_move:
        pass
    elif move_to_id["Natural Gift"] in selected_moves:
        current_move_types = set({move_data_mod[move]["type"] for move in selected_moves})
        pickable_berries = {k for k, v in berry_to_natural_gift_type.items() if v not in current_move_types}
        selected_item = world.random.choice(list(pickable_berries))
    elif move_to_id["Fling"] in selected_moves:
        selected_damage_move_types: set[int] = {v['type'] for k, v in move_data_mod.items() if k in selected_moves and k != move_to_id["Fling"] and 0 < v["power"]}
        usable_type_plates: set[int] = {type_to_plate[type] for type in selected_damage_move_types if type in type_to_plate.keys()}
        selectable_fling_items = usable_type_plates | general_fling_items
        selected_item = world.random.choice(list(selectable_fling_items))
    elif move_to_id["Trick"] in selected_moves or move_to_id["Switcheroo"] in selected_moves:
        selected_item = world.random.choice([item_to_id["Full Incense"], item_to_id["Lagging Tail"], item_to_id["Flame Orb"], item_to_id["Iron Ball"], item_to_id["Black Sludge"], item_to_id["Toxic Orb"], item_to_id["Choice Scarf"], item_to_id["Macho Brace"]])
    elif move_to_id["Belly Drum"] in selected_moves and world.random.random() < 0.80:
        selected_item = item_to_id["Sitrus Berry"]
    elif move_to_id["Rest"] in selected_moves and world.random.random() < 0.5:
        selected_item = item_to_id["Chesto Berry"]
    # TODO: Light Clay for Reflect/Light Screen
    # TODO: White Herb for Close Combat/Superpower/Draco Meteor/Psycho Boost/Leaf Storm/Overheat
    elif ability == ability_to_id["Poison Heal"] in selected_moves and world.random.random() < 0.75:
        selected_item = item_to_id["Toxic Orb"]
    elif (len(self_confusion_moves & set(selected_moves)) > 0) and world.random.random() < 0.15:
        selected_item = item_to_id["Persim Berry"]
    elif ability == ability_to_id["Guts"] and physical and world.random.random() < 0.5:
        selected_item = world.random.choice([item_to_id["Flame Orb"], item_to_id["Toxic Orb"]])
    elif ability == ability_to_id["Marvel Scale"] and world.random.random() < 0.2:
        selected_item = item_to_id["Flame Orb"]
    
    selectable_items = set()
    # If no item is previously selected, try to pick one now.
    if selected_item == item_to_id["None"] and not has_item_stealing_move:
        # Because of the number of berries, maybe roll to have Pokemon hold a berry before hand?
        # Or instead give the items weights that will determine how they are used.
        # Status Curing Berries
        if (ability not in status_countering_abilities | set({ability_to_id["Marvel Scale"], ability_to_id["Guts"], ability_to_id["Quick Feet"]})) and (len(set(selected_moves) | status_healing_moves) <= 0):
            if ability not in sleep_preventing_abilities:
                selectable_items.add(item_to_id["Chesto Berry"])
            if ability != ability_to_id["Immunity"]:
                selectable_items.add(item_to_id["Pecha Berry"])
            if ability != ability_to_id["Heatproof"] and ability != ability_to_id["Water Veil"]:
                # Technically Heatproof only halves burn damage.
                selectable_items.add(item_to_id["Rawst Berry"])
            if species_type_1 != type_to_id["Ice"] and species_type_2 != type_to_id["Ice"] and ability != ability_to_id["Magma Armor"] and world.random.random() < 0.15:
                # Freeeze is really uncommon, so often just do not bother adding it.
                selectable_items.add(item_to_id["Aspear Berry"])
            if ability != ability_to_id["Tangled Feet"] and ability != ability_to_id["Own Tempo"]:
                selectable_items.add(item_to_id["Persim Berry"])
            selectable_items.add(item_to_id["Cheri Berry"])
            selectable_items.add(item_to_id["Lum Berry"])
        # TODO: Super-Effective Damage Halving Berries
        
        # TODO: Stat Raising Berries (Reuse EV Logic)
        
        # TODO: Percent Healing Berries (Sitrus Berry, etc) (no Shedinja)
        
        # TODO: Small Chance For Flat Healing Items to Be Added To Pool (Berry Juice, Oran Berry) (Unless Low HP) (no Shedinja)
        
        # TODO: White Herb
        
        # Unburden check to prevent non-consumables with Unburden.
        if ability != ability_to_id["Unburden"]:
            # TODO: Incense Items
            
            # TODO: Type-enhancing Items
            
            # TODO: Plate Items
            
            # TODO: Eviolite Also Add Data
            
            # TODO: Grip Claw
            
            # TODO: Black Sludge, Shell Bell, Leftovers
            
            # TODO: Choice Items, Life Orb
            
            pass
    if selected_item == item_to_id["None"] and (len(selectable_items) > 0):
        selected_item = world.random.choice(list(selectable_items))
    logger.info(f"Held Item: {id_to_item[selected_item]}\n")
    
    # Add the minimal Pokemon Data to the AP World.
    minimal_pokemon_data: dict[str, Any] = {
        "pid": pid,
        "lvl": lvl,
        "form": form,
        "ivs": ivs,
        "friendship": friendship,
        "moves": selected_moves,
        "item": selected_item,
        "hp_ev": evs["hp"],
        "atk_ev": evs["atk"],
        "def_ev": evs["def"],
        "spe_ev": evs["spe"],
        "spa_ev": evs["spa"],
        "spd_ev": evs["spd"],
        "pokeball": pokeball,
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
    move_1_options -= (set(generated_moveset))
    if len(move_1_options) > 0:
        generated_moveset.append(world.random.choice(list(move_1_options)))
    move_2_options -= (set(generated_moveset))
    if len(move_2_options) > 0:
        generated_moveset.append(world.random.choice(list(move_2_options)))
    move_3_options -= (set(generated_moveset))
    if len(move_3_options) > 0:
        generated_moveset.append(world.random.choice(list(move_3_options)))
    return generated_moveset


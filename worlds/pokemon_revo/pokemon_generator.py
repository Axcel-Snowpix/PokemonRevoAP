from worlds.AutoWorld import World
import logging

from .data.gen4_pokemon_structure import Gen4Pokemon, decode_text
from .data.pokemon_data import pokemon_data, ability_to_id, item_to_id, move_to_id, move_data, category_to_id, level_up_moves, id_to_mon

weather_moves: set = {move_to_id['Sunny Day'], move_to_id['Sandstorm'], move_to_id['Rain Dance'], move_to_id['Hail']}
harsh_sunlight_moves: set = {move_to_id['SolarBeam'], move_to_id['Weather Ball'], move_to_id['Moonlight'], move_to_id['Synthesis'], move_to_id['Morning Sun']}
rain_moves: set = {move_to_id['Thunder'], move_to_id['Weather Ball']}
sandstorm_moves: set = {move_to_id['Weather Ball']}
hail_moves: set = {move_to_id['Weather Ball'], move_to_id['Blizzard']}

def pid_to_nature(pid: int) -> int:
    return (pid % 100) % 25

def nature_to_increased_stat(nature: int) -> str:
    if nature / 5 == nature % 5:
        return 'none'
    match (nature / 5):
        case 0:
            return 'attack'
        case 1:
            return 'defense'
        case 2:
            return 'speed'
        case 3:
            return 'sp attack'
        case 4:
            return 'sp defense'
        case _:
            return 'none'


def nature_to_decreased_stat(nature: int) -> str:
    if nature / 5 == nature % 5:
        return 'none'
    match nature % 5:
        case 0:
            return 'attack'
        case 1:
            return 'defense'
        case 2:
            return 'speed'
        case 3:
            return 'sp attack'
        case 4:
            return 'sp defense'
        case _:
            return 'none'

def pid_to_ability_for_species(pid: int, species: int) -> int:
    if species not in pokemon_data:
        ability_to_id['None'] # this could also just be 0
    
    species_data = pokemon_data[species]
    ability_1: int = species_data['ability1']
    ability_2: int = species_data['ability2']
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
    
# TODO: Actually pass lvl_moves and tm_moves for pokemon into generate_random_pokemon_inner.
def generate_normal_random_pokemon(world: World):
    generate_chaotic_random_pokemon(world)

def generate_chaotic_random_pokemon(world: World):
    # TODO: Remove moves listed in the yaml that the user wont want selected. ie: Splash, Memento
    for species in pokemon_data.keys():
        if id_to_mon[species] != '-':
            generate_random_pokemon_inner(world, species, set(move_data.keys()), set(move_data.keys()), [])

def generate_random_pokemon_inner(world: World, species: int, lvl_moves: set[int], tm_moves: set[int], items: list[int]):
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
    all_moves = lvl_moves.union(tm_moves)
    # TODO: Remove extremely redundant moves from all_moves some situations include but are not
    # limited to:
    # Weather Setting Ability + Weather Setting Move
    # Shedinja + Recoil Moves
    # Vital Spirit/Insomnia + Rest
    # Genderless + Attract
    all_moves_len = len(all_moves)
    
    # If a pokemon can only learn 4 or less moves just add all of those moves and call it a day.
    if all_moves_len == 0:
        # PANIC! We can't find any moves. (Most likely because of yaml settings.)
        # 20% Chance For Just Explosion. Otherwise, check the level up learnset and grab whatever
        # we can to salvage the situation.
        if world.random.random() < 0.2:
            # Your folly has been noted... explosively.
            selected_moves.append(move_to_id['Explosion'])
            selected_moves.extend([move_to_id['-']] * 3)
        else:
            # TODO: Filter moves from a certain level or closest to a specified level.
            # panic_learnset: set[tuple[int, int]] = level_up_moves[species]
            panic_learnset: dict[int, int] = dict(level_up_moves[species])
            selected_moves.extend(world.random.sample(list(panic_learnset.values()), 4))
            
    if all_moves_len <= 4:
        selected_moves.extend(all_moves)
        if all_moves_len < 4:
            # If the Pokemon knows less than 4 moves, pad it out to 4 using no move.
            selected_moves.extend([move_to_id['-']] * (4 - all_moves_len))
            
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
    if len(selected_moves) == 0:
        generation_type_chance: float = world.random.random()
        # 30% 1 Stab Damage Move (At Least 60 BP From Higher Stat) From Lvl Or TM + 1 Random Damage + 1 Lvl Status + 1 TM Status
        if generation_type_chance < 0.5:
            if species_data['atk'] == species_data['sp_atk']:
                high_damage_stab_moves: set[int] = set({k: v for k, v in move_data.items() if (v['type'] == species_data['type1'] or v['type'] == species_data['type2']) and 60 <= v['power']}.keys())
            elif species_data['atk'] > species_data['sp_atk']:
                high_damage_stab_moves: set[int] = set({k: v for k, v in move_data.items() if (v['type'] == species_data['type1'] or v['type'] == species_data['type2']) and 60 <= v['power'] and category_to_id['Physical'] == v['category']}.keys())
            else: # elif species_data['atk'] < species_data['sp_atk']:
                high_damage_stab_moves: set[int] = set({k: v for k, v in move_data.items() if (v['type'] == species_data['type1'] or v['type'] == species_data['type2']) and 60 <= v['power'] and category_to_id['Special'] == v['category']}.keys())
            if len(high_damage_stab_moves) > 0:
                picked_high_damage_stab_move: int = world.random.choice(list(high_damage_stab_moves))
                selected_moves.append(picked_high_damage_stab_move)
                all_moves.remove(picked_high_damage_stab_move)
            # TODO: Complete adding a random damage move, 1 lvl status, 1 tm status
            
        # TODO: Complete the other set types after testing the others work.
        # 10% 2 Random Damage Moves From Lvl, 2 Random Damage Moves From TM
        # 10% Highest Stab Move From Lvl, 1 Random Damage TM Move (At Most 60 BP), 1 Lvl Status Move, 1 Status Move TM
        # 10% 1 Stab Damage Move (At Least 60 BP From Higher Stat, If Does Not Exist, TM Move), 1 Random Damage TM Move (At Most 60 BP), 1 Lvl Status Move, Protect
        # 10% 4 Recent Moves From Lvl 50
        # 10% 2 Random Damage Moves From Lvl, 1 Random TM Damage Move, 1 Lvl Status Move
        # 10% 
        # 5% 
        # 5% Purely random moves from tm and learnset.
        else:
            selected_moves.extend(world.random.sample(list(all_moves), 4))

    # If for some reason the number of moves generated above is less than 4 for whatever reason,
    # fill it out with a random of assortment of moves. Also, if for some reason more than
    # four moves are added to the moveset force it down to 4 moves. Note: Ideally, never add more
    # than 4 moves.
    if len(selected_moves) < 4:
        unselected_moves: set = all_moves - set(selected_moves)
        selected_moves.extend(world.random.sample(list(unselected_moves), 4 - len(selected_moves)))
    elif len(selected_moves) != 4:
        selected_moves = selected_moves[:4]
    
    # logger = logging.getLogger()
    # logger.info('%s Set: %s\n', str(species), str(selected_moves))
    
    # TODO: item logic
    selected_item = item_to_id['None']
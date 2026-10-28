import asyncio
import traceback
import json
import time
import random
from pathlib import Path
from typing import TYPE_CHECKING, Any, Optional

import dolphin_memory_engine

import Patch
import Utils
from worlds.AutoWorld import AutoWorldRegister
from CommonClient import get_base_parser, gui_enabled, logger, server_loop

tracker_loaded = False
try:
    from worlds.tracker.TrackerClient import TrackerGameContext as SuperContext
    from worlds.tracker.TrackerClient import TrackerCommandProcessor as SuperCommandProcessor
    tracker_loaded = True
except ModuleNotFoundError:
    from CommonClient import CommonContext as SuperContext
    from CommonClient import ClientCommandProcessor as SuperCommandProcessor

from NetUtils import ClientStatus

if TYPE_CHECKING:
    import kvui

from .items import ITEM_TABLE, LOOKUP_ID_TO_NAME
from .locations import LOCATION_TABLE
from .data.gen4_pokemon_structure import Gen4Pokemon, decode_text

CONNECTION_REFUSED_GAME_STATUS = (
    "Dolphin failed to connect. Please load a randomized ROM for Pokémon Battle Revolution. Trying again in 5 seconds..."
)
CONNECTION_REFUSED_SAVE_STATUS = (
    "Dolphin failed to connect. Please load into a save file made for this Multiworld. Trying again in 5 seconds..."
)
CONNECTION_LOST_STATUS = (
    "Dolphin connection was lost. Please restart your emulator and make sure Pokémon Battle Revolution is running."
)
CONNECTION_CONNECTED_STATUS = "Dolphin connected successfully."
CONNECTION_INITIAL_STATUS = "Dolphin connection has not been initiated."

# This address contains a pointer to the starting address of the save file in memory.
SAVE_FILE_FIND_ADDR = 0x8045DE80

# The offset for the address that contains the currently loaded save profile's index.
SAVE_SLOT_CURRENT = 0x50

# The offset from the start of the save file to the first profile.
SAVE_SLOT_START = 0x380

# The offset from the first save profile to every one past it.
SAVE_SLOT_OFFSET = 0x6FF00

# A custom string in the save file, used to check if it was made with an AP ROM.
AP_SAVE_CHECK = 0x69000

# The Player's slot name, placed in the save file.
# Used to check if the client is reading the correct save for the multiworld
SAVE_SLOT_NAME = 0x69004

# The multiworld's seed, placed in the save file.
# Used to check if the client is reading the correct save for the multiworld
SAVE_SEED = 0x69014

# The expected index for the following item that should be received.
EXPECTED_INDEX_OFFSET = 0x6901E

# The offset containing the player's Pokétopia Badges.
BADGE_COUNT = 0x69020

# Offset for a custom bitfield that tracks your unlocked Rental Passes.
# This is needed so that the game won't remove your unlocked Rental Passes when doing the checks in Gateway.
PASS_UNLOCK_BITFIELD = 0x69022

# Offset for the unlocked Colosseums bitfield.
# Byte 1 is for Gateway, Main Street, Waterfall and Neon Colosseums.
# Byte 2 is for Crystal, Sunny Park, Magma, Courtyard, Sunset and Stargazer Colosseums.
COLOSSEUMS_BITFIELD = 0x12508

# Offset for Player's Poké Coupons.
POKE_COUPONS = 0x124E1

# Offset for Battle Passes
BATTLE_PASS_OFFSET = 0x134D8

# Size of Rental/Battle Passes.
BATTLE_PASS_SIZE = 0x6EC

# Offset for Pokemon on a Battle Pass.
BATTLE_PASS_PKMN_OFFSET = 0x1FC

# Size of Pokemon Struct
PKMM_SIZE = 0x88

# Offset for Player's Copied Pokemon Boxes
PKMN_BOXES_OFFSET = 0x5F8


class PBRCommandProcessor(SuperCommandProcessor):
    """
    Command Processor for Pokémon Battle Revolution client commands.

    This class handles commands specific to Pokémon Battle Revolution.
    """

    def __init__(self, ctx: SuperContext):
        """
        Initialize the command processor with the provided context.

        :param ctx: Context for the client.
        """
        super().__init__(ctx)

    def _cmd_dolphin(self) -> None:
        """
        Display the current Dolphin emulator connection status.
        """
        if isinstance(self.ctx, PBRContext):
            logger.info(f"Dolphin Status: {self.ctx.dolphin_status}")

    def _cmd_death_link(self) -> None:
        """
        Turn Death Link on or off.
        """
        if isinstance(self.ctx, PBRContext):
            if self.ctx.slot is not None:
                if f"DeathLink{self.ctx.death_link_group}" in self.ctx.tags:
                    Utils.async_start(self.ctx.update_death_link(False))
                    logger.info("Death Link disabled.")
                else:
                    Utils.async_start(self.ctx.update_death_link(True))
                    logger.info("Death Link enabled.")
            else:
                logger.info("Please connect to a multiworld first.")

    def _cmd_death_link_mode(self) -> None:
        """
        Change the Death Link Mode between Battle Loss and Pokémon Faint.
        """
        if isinstance(self.ctx, PBRContext):
            if self.ctx.slot is not None:
                if self.ctx.death_link_mode == 0:
                    self.ctx.death_link_mode = 1
                    logger.info("Set Death Link Mode to Pokémon Faint")
                else:
                    self.ctx.death_link_mode = 0
                    logger.info("Set Death Link Mode to Battle Loss")
            else:
                logger.info("Please connect to a multiworld first.")

    def _cmd_death_link_group(self, group: Optional[str]) -> None:
        """
        Change the current Death Link Group.
        """
        if isinstance(self.ctx, PBRContext):
            if self.ctx.slot is not None:
                if group == None:
                    Utils.async_start(self.ctx.update_death_link_group(""))
                    logger.info(f'Set Death Link Group to Empty')
                else:
                    Utils.async_start(self.ctx.update_death_link_group(group))
                    logger.info(f'Set Death Link Group to "{group}"')
            else:
                logger.info("Please connect to a multiworld first.")

    def _cmd_damage_link(self) -> None:
        """
        Turn Damage Link on or off.
        """
        if isinstance(self.ctx, PBRContext):
            if self.ctx.slot is not None:
                if f"SharedDamage{self.ctx.damage_link_group}" in self.ctx.tags:
                    Utils.async_start(self.ctx.update_damage_link(False))
                    logger.info("Damage Link disabled.")
                else:
                    Utils.async_start(self.ctx.update_damage_link(True))
                    logger.info("Damage Link enabled.")
            else:
                logger.info("Please connect to a multiworld first.")

    def _cmd_damage_link_group(self, group: Optional[str]) -> None:
        """
        Change the current Damage Link Group.
        """
        if isinstance(self.ctx, PBRContext):
            if self.ctx.slot is not None:
                if group == None:
                    Utils.async_start(self.ctx.update_damage_link_group(""))
                    logger.info(f'Set Damage Link Group to Empty')
                else:
                    Utils.async_start(self.ctx.update_damage_link_group(group))
                    logger.info(f'Set Damage Link Group to "{group}"')
            else:
                logger.info("Please connect to a multiworld first.")

class PBRContext(SuperContext):
    """
    The context for Pokémon Battle Revolution client.

    This class manages all interactions with the Dolphin emulator and the Archipelago server for Pokémon Battle Revolution.
    """

    command_processor = PBRCommandProcessor
    game: str = "Pokémon Battle Revolution"
    tags = {"AP"}
    items_handling: int = 0b111
    slot_data = dict[str, Any]
    colosseums_cleared: list = []
    has_got_pkmn_dmg_data: bool = False
    dmglink_pkmn_idx: int = 0
    pkmn_hp: list = []

    def __init__(self, server_address: Optional[str], password: Optional[str]) -> None:
        """
        Initialize the PBR context.

        :param server_address: Address of the Archipelago server.
        :param password: Password for server authentication.
        """

        super().__init__(server_address, password)
        self.dolphin_sync_task: Optional[asyncio.Task[None]] = None
        self.dolphin_status: str = CONNECTION_INITIAL_STATUS
        self.awaiting_rom: bool = False
        self.slot_data = {}
        self.has_send_death: bool = False
        self.death_link_mode: int = 0
        self.death_link_group: str = ""
        self.can_send_damagelink: bool = True
        self.damage_link_group: str = ""
        self.last_damage_link: float = time.time()

    async def disconnect(self, allow_autoreconnect: bool = False) -> None:
        """
        Disconnect the client from the server and reset game state variables.

        :param allow_autoreconnect: Allow the client to auto-reconnect to the server. Defaults to `False`.

        """
        self.auth = None
        await super().disconnect(allow_autoreconnect)

    async def server_auth(self, password_requested: bool = False) -> None:
        """
        Authenticate with the Archipelago server.

        :param password_requested: Whether the server requires a password. Defaults to `False`.
        """
        if password_requested and not self.password:
            await super().server_auth(password_requested)
        #if not self.auth:
        #    if self.awaiting_rom:
        #        return
        #    self.awaiting_rom = True
        #    logger.info("Awaiting connection to Dolphin to get player information.")
        #    return
        await self.get_username()
        await self.send_connect()

    def on_package(self, cmd: str, args: dict[str, Any]) -> None:
        """
        Handle incoming packages from the server.

        :param cmd: The command received from the server.
        :param args: The command arguments.
        """
        super().on_package(cmd, args)
        if cmd == "Connected":
            self.slot_data = args["slot_data"]
            Utils.async_start(self.update_death_link_group(self.slot_data["death_link_group"]))
            Utils.async_start(self.update_damage_link_group(self.slot_data["damage_link_group"]))
            Utils.async_start(self.update_death_link(bool(self.slot_data["death_link"])))
            Utils.async_start(self.update_damage_link(bool(self.slot_data["damage_link"])))
            self.death_link_mode = self.slot_data["death_link_mode"]
        elif cmd == "Bounced":
            tags = args.get("tags", [])
            if f"DeathLink{self.death_link_group}" in tags and self.last_death_link != args["data"]["time"]:
                self.on_deathlink(args["data"])
            if f"SharedDamage{self.damage_link_group}" in tags and self.last_damage_link != args["data"]["time"]:
                self.on_damagelink(args["data"])

    def on_deathlink(self, data: dict[str, Any]) -> None:
        """
        Handle a DeathLink event.
    
        :param data: The data associated with the DeathLink event.
        """
        super().on_deathlink(data)
        _give_death(self)

    def on_damagelink(self, data: dict[str, Any]) -> None:
        """
        Handle a DamageLink event.

        :param data: The data associated with the DamageLink event.
        """
        self.last_damage_link = max(data["time"], self.last_damage_link)
        damage = data.get("damage_points", 0)
        text = data.get("cause", "")
        if text:
            logger.info(f"DamageLink: {text}")
        else:
            logger.info(f"DamageLink: Received {damage} damage from {data['source']}")
        _give_damage(self, damage)

    async def send_death(self, death_text: str = ""):
        """Helper function to send a deathlink using death_text as the unique death cause string."""
        if self.server and self.server.socket:
            logger.info("DeathLink: Sending death to your friends...")
            self.last_death_link = time.time()
            await self.send_msgs([{
                "cmd": "Bounce", "tags": [f"DeathLink{self.death_link_group}"],
                "data": {
                    "time": self.last_death_link,
                    "source": self.player_names[self.slot],
                    "cause": death_text
                }
            }])

    async def send_damage(self, damage: int, damage_text: str = ""):
        """Helper function to send a damagelink using damage_text as the unique damage cause string."""
        if self.server and self.server.socket:
            logger.info(f"DamageLink: Sending {damage} damage")
            self.last_damage_link = time.time()
            await self.send_msgs([{
                "cmd": "Bounce", "tags": [f"SharedDamage{self.damage_link_group}"],
                "data": {
                "time": time.time(),
                "uuid": Utils.get_unique_identifier(),
                "source": self.player_names[self.slot],
                "damage_points": damage,
                "cause": damage_text
                },
            }])

    async def update_death_link(self, death_link: bool):
        """Helper function to set Death Link connection tag on/off and update the connection if already connected."""
        old_tags = self.tags.copy()
        if death_link:
            self.tags.add(f"DeathLink{self.death_link_group}")
        else:
            self.tags -= {f"DeathLink{self.death_link_group}"}
        if old_tags != self.tags and self.server and not self.server.socket.closed:
            await self.send_msgs([{"cmd": "ConnectUpdate", "tags": self.tags}])

    async def update_death_link_group(self, group_name: str):
        """Helper function to change the Death Link group, updating the connection tag as needed if already connected."""
        death_link: bool = f"DeathLink{self.death_link_group}" in self.tags
        if death_link:
            self.tags -= {f"DeathLink{self.death_link_group}"}
        self.death_link_group = group_name
        if death_link:
            self.tags.add(f"DeathLink{self.death_link_group}")
            if self.server and not self.server.socket.closed:
                await self.send_msgs([{"cmd": "ConnectUpdate", "tags": self.tags}])

    async def update_damage_link(self, damage_link: bool):
        """Helper function to set Damage Link connection tag on/off and update the connection if already connected."""
        old_tags = self.tags.copy()
        if damage_link:
            self.tags.add(f"SharedDamage{self.damage_link_group}")
        else:
            self.tags -= {f"SharedDamage{self.damage_link_group}"}
        if old_tags != self.tags and self.server and not self.server.socket.closed:
            await self.send_msgs([{"cmd": "ConnectUpdate", "tags": self.tags}])
    
    async def update_damage_link_group(self, group_name: str):
        """Helper function to change the Damage Link group, updating the connection tag as needed if already connected."""
        damage_link: bool = f"SharedDamage{self.damage_link_group}" in self.tags
        if damage_link:
            self.tags -= {f"SharedDamage{self.damage_link_group}"}
        self.damage_link_group = group_name
        if damage_link:
            self.tags.add(f"SharedDamage{self.damage_link_group}")
            if self.server and not self.server.socket.closed:
                await self.send_msgs([{"cmd": "ConnectUpdate", "tags": self.tags}])

    def make_gui(self) -> type["kvui.GameManager"]:
        """
        Initialize the GUI for Pokémon Battle Revolution client.

        :return: The client's GUI.
        """
        ui = super().make_gui()
        ui.base_title = "Archipelago Pokémon Battle Revolution Client"
        return ui


def read_short(console_address: int) -> int:
    """
    Read a 2-byte short from Dolphin memory.

    :param console_address: Address to read from.
    :return: The value read from memory.
    """
    return int.from_bytes(dolphin_memory_engine.read_bytes(console_address, 2), byteorder="big")


def read_word(console_address: int) -> int:
    """
    Read a 4-byte word from Dolphin memory.

    :param console_address: Address to read from.
    :return: The value read from memory.
    """
    return int.from_bytes(dolphin_memory_engine.read_bytes(console_address, 4), byteorder="big")


def write_short(console_address: int, value: int) -> None:
    """
    Write a 2-byte short to Dolphin memory.

    :param console_address: Address to write to.
    :param value: Value to write.
    """
    dolphin_memory_engine.write_bytes(console_address, value.to_bytes(2, byteorder="big"))


def write_word(console_address: int, value: int) -> None:
    """
    Write a 4-byte word to Dolphin memory.

    :param console_address: Address to write to.
    :param value: Value to write.
    """
    dolphin_memory_engine.write_bytes(console_address, value.to_bytes(4, byteorder="big"))


def read_string(console_address: int, strlen: int) -> str:
    """
    Read a string from Dolphin memory.

    :param console_address: Address to start reading from.
    :param strlen: Length of the string to read.
    :return: The string.
    """
    return dolphin_memory_engine.read_bytes(console_address, strlen).split(b"\0", 1)[0].decode()


def _give_death(ctx: PBRContext) -> None:
    """
    Trigger a death in-game.

    :param ctx: The Pokémon Battle Revolution client context
    """
    pointer_addr = read_word(read_word(read_word(0x806288C4) + 0x14) + 0x1c)
    if (
        ctx.slot is not None
        and dolphin_memory_engine.is_hooked()
        and ctx.dolphin_status == CONNECTION_CONNECTED_STATUS
        and check_correct_save(ctx)
        and read_word(0x806288C4) != 0
        and pointer_addr != 0
    ):
        field_data_addr = read_word(pointer_addr + 0x30)
        if ctx.death_link_mode == 0:
            battle_outcome_addr = pointer_addr + 0x23e4
            battle_outcome_value = dolphin_memory_engine.read_byte(battle_outcome_addr)
            ctx.has_send_death = True
            dolphin_memory_engine.write_byte(battle_outcome_addr, (battle_outcome_value & 0xfe) | 0x2)
            write_word(field_data_addr + 0x8, 0x2b)
        else:
            # Check if player is in a Single Battle or Double Battle.
            battle_style = (read_word(read_word(pointer_addr + 0x2c) >> 1)) & 1
            party_data_addr = read_word(pointer_addr + 0x68)
            ctx.has_send_death = True
            if battle_style == 0:
                pkmn_field_idx = 0
            else:
                pkmn_field_idx = random.randint(0,1) * 2
                pkmn_hp = read_word(field_data_addr + 0x2d8c + 0xc0 * pkmn_field_idx)
                if pkmn_hp <= 0 and pkmn_field_idx == 0:
                    pkmn_field_idx = 2
                elif pkmn_hp <= 0 and pkmn_field_idx == 2:
                    pkmn_field_idx = 0
            pkmn_party_idx = dolphin_memory_engine.read_byte(field_data_addr + 0x219c + pkmn_field_idx)
            pkmn_party_hp_addr = party_data_addr + pkmn_party_idx * 0xa4 + 0x8 + 0x8e
            pkmn_offset = 0xc0 * pkmn_field_idx
            # Set Pokémon's HP to 0
            write_word(field_data_addr + 0x2d8c + pkmn_offset, 0x0)
            write_short(pkmn_party_hp_addr, 0x0)
            # Set Pokémon's Moves to Splash (Prevents them from doing anything this turn)
            write_short(field_data_addr + 0x2d4c + pkmn_offset, 0x96)
            write_short(field_data_addr + 0x2d4c + pkmn_offset + 0x2, 0x96)
            write_short(field_data_addr + 0x2d4c + pkmn_offset + 0x4, 0x96)
            write_short(field_data_addr + 0x2d4c + pkmn_offset + 0x6, 0x96)
            # Set Pokémon's Moves' PP to 1 (Prevents them from using Struggle instead of Splash)
            dolphin_memory_engine.write_byte(field_data_addr + 0x2d6c + pkmn_offset, 1)
            dolphin_memory_engine.write_byte(field_data_addr + 0x2d6c + pkmn_offset + 0x1, 1)
            dolphin_memory_engine.write_byte(field_data_addr + 0x2d6c + pkmn_offset + 0x2, 1)
            dolphin_memory_engine.write_byte(field_data_addr + 0x2d6c + pkmn_offset + 0x3, 1)


def _give_damage(ctx: PBRContext, damage: int) -> None:
    """
    Damage the Player's Pokémon

    :param damage: The amount of damage to deal.
    """
    damage = int(damage)
    pointer_addr = read_word(read_word(read_word(0x806288C4) + 0x14) + 0x1c)
    if (
        ctx.slot is not None
        and dolphin_memory_engine.is_hooked()
        and ctx.dolphin_status == CONNECTION_CONNECTED_STATUS
        and check_correct_save(ctx)
        and read_word(0x806288C4) != 0
        and pointer_addr != 0
    ):
        field_data_addr = read_word(pointer_addr + 0x30)
        # Check if player is in a Single Battle or Double Battle.
        battle_style = (read_word(pointer_addr + 0x2c) >> 1) & 1
        party_data_addr = read_word(pointer_addr + 0x68)
        ctx.can_send_damagelink = False
        if battle_style == 0:
            pkmn_field_idx = 0
        else:
            pkmn_field_idx = random.randint(0,1) * 2
            pkmn_hp = read_word(field_data_addr + 0x2d8c + 0xc0 * pkmn_field_idx)
            if pkmn_hp <= 0 and pkmn_field_idx == 0:
                pkmn_field_idx = 2
            elif pkmn_hp <= 0 and pkmn_field_idx == 2:
                pkmn_field_idx = 0
        pkmn_party_idx = dolphin_memory_engine.read_byte(field_data_addr + 0x219c + pkmn_field_idx)
        pkmn_party_hp_addr = party_data_addr + pkmn_party_idx * 0xa4 + 0x8 + 0x8e
        pkmn_offset = 0xc0 * pkmn_field_idx
        # Deal the damage.
        pkmn_hp = read_word(field_data_addr + 0x2d8c + pkmn_offset)
        pkmn_hp = max(pkmn_hp - damage, 0)
        write_word(field_data_addr + 0x2d8c + pkmn_offset, pkmn_hp)
        write_short(pkmn_party_hp_addr, pkmn_hp)
        if pkmn_hp <= 0:
            # Set Pokémon's Moves to Splash if they'll faint (Prevents them from doing anything this turn)
            write_short(field_data_addr + 0x2d4c + pkmn_offset, 0x96)
            write_short(field_data_addr + 0x2d4c + pkmn_offset + 0x2, 0x96)
            write_short(field_data_addr + 0x2d4c + pkmn_offset + 0x4, 0x96)
            write_short(field_data_addr + 0x2d4c + pkmn_offset + 0x6, 0x96)
            # Set Pokémon's Moves' PP to 1 if they'll faint (Prevents them from using Struggle instead of Splash)
            dolphin_memory_engine.write_byte(field_data_addr + 0x2d6c + pkmn_offset, 1)
            dolphin_memory_engine.write_byte(field_data_addr + 0x2d6c + pkmn_offset + 0x1, 1)
            dolphin_memory_engine.write_byte(field_data_addr + 0x2d6c + pkmn_offset + 0x2, 1)
            dolphin_memory_engine.write_byte(field_data_addr + 0x2d6c + pkmn_offset + 0x3, 1)
        if battle_style == 1:
            pkmn_name = dolphin_memory_engine.read_bytes(field_data_addr + pkmn_offset + 0x2d76, 22)
            pkmn_name = decode_text(pkmn_name, 11)
            logger.info(f"{pkmn_name} took the damage!")
        ctx.pkmn_hp[pkmn_party_idx] = pkmn_hp
        ctx.can_send_damagelink = True


def find_save_file_address():
    """
    Finds the starting address of the current profile in memory.
    """
    save_file = read_word(SAVE_FILE_FIND_ADDR)
    return (
        save_file + dolphin_memory_engine.read_byte(save_file + SAVE_SLOT_CURRENT) * SAVE_SLOT_OFFSET + SAVE_SLOT_START
    )


def _give_item(ctx: PBRContext, item_name: str) -> bool:
    """
    Give an item to the player in-game.

    :param ctx: Pokémon Battle Revolution client context.
    :param item_name: Name of the item to give.
    :return: Whether the item was successfully given.
    """
    if not check_correct_save(ctx):
        return False

    save_file_address = find_save_file_address()

    match ITEM_TABLE[item_name].group:
        case "Colosseums":
            colo_flag_value = read_short(save_file_address + COLOSSEUMS_BITFIELD)
            write_short(save_file_address + COLOSSEUMS_BITFIELD, colo_flag_value | ITEM_TABLE[item_name].value)
            return True
        case "Rental Passes":
            rental_pass_value = dolphin_memory_engine.read_byte(save_file_address + ITEM_TABLE[item_name].value)
            dolphin_memory_engine.write_byte(save_file_address + ITEM_TABLE[item_name].value,
                                             rental_pass_value | 0x10)
            unlocked_rental_passes = dolphin_memory_engine.read_byte(save_file_address + PASS_UNLOCK_BITFIELD)
            dolphin_memory_engine.write_byte(save_file_address + PASS_UNLOCK_BITFIELD,
                                             unlocked_rental_passes | (0x1 << ITEM_TABLE[item_name].bit))
            return True
        case "Poké Coupons":
            poke_coupons_value = int.from_bytes(dolphin_memory_engine.read_bytes(save_file_address + POKE_COUPONS, 3))
            if poke_coupons_value + ITEM_TABLE[item_name].value >= 999999:
                dolphin_memory_engine.write_bytes(save_file_address + POKE_COUPONS, 0xF423F.to_bytes(3, byteorder="big"))
            else:
                dolphin_memory_engine.write_bytes(save_file_address + POKE_COUPONS,
                                                 (poke_coupons_value + ITEM_TABLE[item_name].value).to_bytes(3, byteorder="big"))
            return True
        case "Macguffin":
            current_badge_count = dolphin_memory_engine.read_byte(save_file_address + BADGE_COUNT)
            # The player should never need more than 255 badges to goal, so getting past that number is unecessary.
            if current_badge_count < 0xFF:
                current_badge_count += 0x1
                dolphin_memory_engine.write_byte(save_file_address + BADGE_COUNT, current_badge_count)
            return True
    # If unable to place the item in the array, return `False`.
    return False


async def give_items(ctx: PBRContext) -> None:
    """
    Give the player all outstanding items they have yet to receive.

    :param ctx: Pokémon Battle Revolution client context.
    """
    if check_correct_save(ctx):
        save_file_address = find_save_file_address()

        # Read the expected index of the player, which is the index of the next item they're expecting to receive.
        # The expected index starts at 0 for a fresh save file.
        expected_idx = read_short(save_file_address + EXPECTED_INDEX_OFFSET)

        # Check if there are new items.
        received_items = ctx.items_received
        if len(received_items) <= expected_idx:
            # There are no new items.
            return

        # Loop through items to give.
        # Give the player all items at an index greater than or equal to the expected index.
        for idx, item in enumerate(received_items[expected_idx:], start=expected_idx):
            # Attempt to give the item and increment the expected index.
            while not _give_item(ctx, LOOKUP_ID_TO_NAME[item.item]):
                await asyncio.sleep(0.01)

            # Increment the expected index.
            write_short(save_file_address + EXPECTED_INDEX_OFFSET, idx + 1)


async def check_locations(ctx: PBRContext) -> None:
    """
    Iterate through all locations and check whether the player has checked each location.

    Update the server with all newly checked locations since the last update. If the player has completed the goal,
    notify the server.

    :param ctx: Pokémon Battle Revolution client context.
    """
    if check_correct_save(ctx):
        save_file_address = find_save_file_address()

        # Loop through all locations to see if each has been checked.
        for location, data in LOCATION_TABLE.items():
            checked = False
            check_value = dolphin_memory_engine.read_byte(save_file_address + data.offset)
            if data.bit == None:
                if check_value > 0x0:
                    checked = True
            else:
                if bool((check_value >> data.bit) & 1):
                    checked = True

            if checked:
                if data.code == None:
                    if not ctx.finished_game:
                        await ctx.send_msgs([{"cmd": "StatusUpdate", "status": ClientStatus.CLIENT_GOAL}])
                        ctx.finished_game = True
                else:
                    ctx.locations_checked.add(data.code)

        # Send the list of newly-checked locations to the server.
        locations_checked = ctx.locations_checked.difference(ctx.checked_locations)
        if locations_checked:
            await ctx.send_msgs([{"cmd": "LocationChecks", "locations": locations_checked}])


async def check_stargazer_unlock(ctx: PBRContext) -> None:
    """
    Checks if the condition to unlock Stargazer Colosseum has been met.
    """
    if check_correct_save(ctx):
        save_file_address = find_save_file_address()
        colo_flag_value = read_short(save_file_address + COLOSSEUMS_BITFIELD)
        badge_hunt_req = False
        colosseum_clear_req = False

        if not bool((colo_flag_value >> 13) & 1):
            if ctx.slot_data["goal_unlock_method"] != 1:
                current_badge_count = dolphin_memory_engine.read_byte(save_file_address + BADGE_COUNT)
                if current_badge_count >= ctx.slot_data["required_badge_amount"]:
                    badge_hunt_req = True
            else:
                badge_hunt_req = True

            if ctx.slot_data["goal_unlock_method"] != 0:
                for location, data in LOCATION_TABLE.items():
                    if data.group == "Colosseum Clears":
                        colosseum_clears_value = dolphin_memory_engine.read_byte(save_file_address + data.bit)
                        if colosseum_clears_value > 0x0 and data.region not in ctx.colosseums_cleared:
                            ctx.colosseums_cleared.append(data.region)
                if len(ctx.colosseums_cleared) >= ctx.slot_data["colosseum_clear_count"]:
                    colosseum_clear_req = True
            else:
                colosseum_clear_req = True
                
            if badge_hunt_req and colosseum_clear_req:
                write_short(save_file_address + COLOSSEUMS_BITFIELD, colo_flag_value | 0x2000)


async def check_death(ctx: PBRContext) -> None:
    """
    Check for if a Death Link should be sent.
    """
    pointer_addr = read_word(read_word(read_word(0x806288C4) + 0x14) + 0x1c)
    if (
        check_correct_save(ctx)
        and read_word(0x806288C4) != 0
        and pointer_addr != 0
    ):
        field_data_addr = read_word(pointer_addr + 0x30)
        battle_lost = bool(
            (dolphin_memory_engine.read_byte(pointer_addr + 0x23e4) >> 1) & 0x1
        )
        party_data_addr = read_word(pointer_addr + 0x68)
        party_size = read_word(party_data_addr + 0x4)
        pokemon_alive = 0
        for i in range(party_size):
            pokemon_data_addr = party_data_addr + i * 0xa4 + 0x8
            pokemon_hp = read_short(pokemon_data_addr + 0x8e)
            if pokemon_hp > 0x0:
                pokemon_alive += 1
        if battle_lost and pokemon_alive > 0 and not ctx.has_send_death and time.time() >= ctx.last_death_link + 3:
            ctx.has_send_death = True
            await ctx.send_death(ctx.player_names[ctx.slot] + " gave up on the battle!")
        if ctx.death_link_mode == 0:
            if battle_lost and pokemon_alive <= 0 and not ctx.has_send_death and time.time() >= ctx.last_death_link + 3:
                ctx.has_send_death = True
                await ctx.send_death(ctx.player_names[ctx.slot] + " lost the battle!")
            elif not battle_lost and read_word(field_data_addr + 0x8) != 0x2b:
                ctx.has_send_death = False
        else:
            # Check if player is in a Single Battle or Double Battle.
            battle_style = (read_word(pointer_addr + 0x2c) >> 1) & 1
            check_pokemon_1 = True
            check_pokemon_2 = True
            pokemon_1_hp = read_word(field_data_addr + 0x2d8c)
            pokemon_1_name = dolphin_memory_engine.read_bytes(field_data_addr + 0x2d76, 22)
            pokemon_1_name = decode_text(pokemon_1_name, 11)
            if battle_style == 1:
                pokemon_2_hp = read_word(field_data_addr + 0x2d8c + 0x180)
                pokemon_2_name = dolphin_memory_engine.read_bytes(field_data_addr + 0x2d76 + 0x180, 22)
                pokemon_2_name = decode_text(pokemon_2_name, 11)
                # Stop checking a slot's HP if there is no Pokémon there. (Player only has 1 Pokémon left.)
                if pokemon_alive == 1:
                    if pokemon_1_hp <= 0:
                        check_pokemon_1 = False
                    else:
                        check_pokemon_2 = False
                if pokemon_2_hp <= 0 and check_pokemon_2:
                    if not ctx.has_send_death and time.time() >= ctx.last_death_link + 3:
                        ctx.has_send_death = True
                        await ctx.send_death(ctx.player_names[ctx.slot] + f"'s {pokemon_2_name} fainted!")
                elif (
                    (pokemon_1_hp > 0 or not check_pokemon_1)
                    and not battle_lost
                    and read_word(field_data_addr + 0x8) != 0x2b
                ):
                    ctx.has_send_death = False
            if pokemon_1_hp <= 0 and check_pokemon_1:
                if not ctx.has_send_death and time.time() >= ctx.last_death_link + 3:
                    ctx.has_send_death = True
                    await ctx.send_death(ctx.player_names[ctx.slot] + f"'s {pokemon_1_name} fainted!")
            elif battle_style == 0 and not battle_lost and read_word(field_data_addr + 0x8) != 0x2b:
                ctx.has_send_death = False


async def check_damage(ctx: PBRContext) -> None:
    """
    Check for if Damage Links should be sent, and how much damage to send.
    """
    pointer_addr = read_word(read_word(read_word(0x806288C4) + 0x14) + 0x1c)
    if (
        check_correct_save(ctx)
        and read_word(0x806288C4) != 0
        and pointer_addr != 0
    ):
        if ctx.can_send_damagelink and time.time() >= ctx.last_damage_link + 0.5:
            party_data_addr = read_word(pointer_addr + 0x68)
            party_size = read_word(party_data_addr + 0x4)
            if ctx.has_got_pkmn_dmg_data:
                damage = 0
                pokemon_data_addr = party_data_addr + ctx.dmglink_pkmn_idx * 0xa4 + 0x8
                new_pkmn_hp = read_short(pokemon_data_addr + 0x8e)
                damage = max(ctx.pkmn_hp[ctx.dmglink_pkmn_idx] - new_pkmn_hp, 0)
                if damage > 0:
                    pkmn = Gen4Pokemon.create_from_binary(dolphin_memory_engine.read_bytes(pokemon_data_addr, PKMM_SIZE))
                    await ctx.send_damage(damage, f"{ctx.player_names[ctx.slot]}'s {pkmn.nickname} took {damage} damage!")
                ctx.pkmn_hp[ctx.dmglink_pkmn_idx] = new_pkmn_hp
                ctx.dmglink_pkmn_idx += 1
                if ctx.dmglink_pkmn_idx >= party_size:
                    ctx.dmglink_pkmn_idx = 0
            else:
                ctx.has_got_pkmn_dmg_data = True
                for i in range(0,party_size):
                    pokemon_data_addr = party_data_addr + i * 0xa4 + 0x8
                    ctx.pkmn_hp.append(read_short(pokemon_data_addr + 0x8e))
                ctx.dmglink_pkmn_idx = 0
    else:
        ctx.has_got_pkmn_dmg_data = False
        ctx.pkmn_hp.clear()


def check_correct_save(ctx: PBRContext) -> bool:
    """
    Check if the currently loaded save file is the correct one for the current multiworld.

    :return: `True` if it's the correct save, otherwise `False`.
    """
    save_file_address = find_save_file_address()
    if check_ingame():
        save_check = int.from_bytes(dolphin_memory_engine.read_bytes(save_file_address + SAVE_SLOT_NAME, 26), byteorder="big")
        if save_check == 0:
            dolphin_memory_engine.write_bytes(save_file_address + SAVE_SLOT_NAME, ctx.username.encode('utf-8'))
            dolphin_memory_engine.write_bytes(save_file_address + SAVE_SEED, ctx.server_seed_name.encode('utf-8')[0:10])
            return True
        else:
            save_name = read_string(save_file_address + SAVE_SLOT_NAME, 16)
            save_seed = read_string(save_file_address + SAVE_SEED, 10)
            if save_name == ctx.username and save_seed == ctx.server_seed_name[0:10]:
                return True
            logger.info(CONNECTION_REFUSED_SAVE_STATUS)
    # Return False if all other conditions are not met.
    return False


def check_ingame() -> bool:
    """
    Check if the player is currently in-game.

    :return: `True` if the player is in-game, otherwise `False`.
    """
    save_file_address = find_save_file_address()
    return (
        bool((dolphin_memory_engine.read_byte(save_file_address + 0x12565) >> 6) & 1) and
        read_string(save_file_address + AP_SAVE_CHECK, 4) == "APBR"
    )


async def dolphin_sync_task(ctx: PBRContext) -> None:
    """
    The task loop for managing the connection to Dolphin.

    While connected, read the emulator's memory to look for any relevant changes made by the player in the game.

    :param ctx: Pokémon Battle Revolution client context.
    """
    logger.info("Starting Dolphin connector. Use /dolphin for status information.")
    sleep_time = 0.0
    while not ctx.exit_event.is_set():
        if sleep_time > 0.0:
            try:
                # ctx.watcher_event gets set when receiving ReceivedItems or LocationInfo, or when shutting down.
                await asyncio.wait_for(ctx.watcher_event.wait(), sleep_time)
            except asyncio.TimeoutError:
                pass
            sleep_time = 0.0
        ctx.watcher_event.clear()

        try:
            if dolphin_memory_engine.is_hooked() and ctx.dolphin_status == CONNECTION_CONNECTED_STATUS:
                if not check_ingame():
                    sleep_time = 0.1
                    continue
                if ctx.slot is not None:
                    if check_correct_save(ctx):
                        if f"DeathLink{ctx.death_link_group}" in ctx.tags:
                            await check_death(ctx)
                        if f"SharedDamage{ctx.damage_link_group}" in ctx.tags:
                            await check_damage(ctx)
                        await give_items(ctx)
                        await check_locations(ctx)
                        await check_stargazer_unlock(ctx)
                    else:
                        sleep_time = 5
                        continue
                #else:
                #    if not ctx.auth:
                #        ctx.auth = read_string(SLOT_NAME_ADDR, 16)
                #    if ctx.awaiting_rom:
                #        await ctx.server_auth()
                sleep_time = 0.1
            else:
                if ctx.dolphin_status == CONNECTION_CONNECTED_STATUS:
                    logger.info("Connection to Dolphin lost, reconnecting...")
                    ctx.dolphin_status = CONNECTION_LOST_STATUS
                logger.info("Attempting to connect to Dolphin...")
                dolphin_memory_engine.hook()
                if dolphin_memory_engine.is_hooked():
                    if dolphin_memory_engine.read_bytes(0x80000000, 6) != b"RPBE01":
                        logger.info(CONNECTION_REFUSED_GAME_STATUS)
                        ctx.dolphin_status = CONNECTION_REFUSED_GAME_STATUS
                        dolphin_memory_engine.un_hook()
                        sleep_time = 5
                    else:
                        logger.info(CONNECTION_CONNECTED_STATUS)
                        ctx.dolphin_status = CONNECTION_CONNECTED_STATUS
                        ctx.locations_checked = set()
                else:
                    logger.info("Connection to Dolphin failed, attempting again in 5 seconds...")
                    ctx.dolphin_status = CONNECTION_LOST_STATUS
                    await ctx.disconnect()
                    sleep_time = 5
                    continue
        except Exception:
            dolphin_memory_engine.un_hook()
            logger.info("Connection to Dolphin failed, attempting again in 5 seconds...")
            logger.error(traceback.format_exc())
            ctx.dolphin_status = CONNECTION_LOST_STATUS
            await ctx.disconnect()
            sleep_time = 5
            continue

def patch_iso(patch_file: str):
    try:
        Patch.create_rom_file(patch_file)
    except Exception as exc:
        logger.exception(exc)
        Utils.messagebox("Error Patching Game", str(exc), True)

def main(*args: str) -> None:
    """
    Run the main async loop for the Pokémon Battle Revolution client.

    :param *args: Command line arguments passed to the client.
    """
    parser = get_base_parser()
    parser.add_argument("patch_file", default="", type=str, nargs="?", help="Path to an Archipelago patch file")
    parsed_args = parser.parse_args(args)
    
    if parsed_args.patch_file != "":
        patch_iso(parsed_args.patch_file)

    Utils.init_logging("Pokémon Battle Revolution Client")
    
    async def _main(connect: Optional[str], password: Optional[str]) -> None:
        ctx = PBRContext(connect, password)
        ctx.server_task = asyncio.create_task(server_loop(ctx), name="ServerLoop")
        if tracker_loaded:
            ctx.run_generator()
        if gui_enabled:
            ctx.run_gui()
        ctx.run_cli()
        await asyncio.sleep(1)

        worlds_paths = [
            Path(Utils.local_path("worlds")),
            Path(Utils.local_path("custom_worlds")),
            Path(Utils.home_path("worlds")),
            Path(Utils.home_path("custom_worlds")),
        ]
        world_type = AutoWorldRegister.world_types["Pokémon Battle Revolution"]
        world_type_path = Path(world_type.__file__)
        for worlds_path in worlds_paths:
            if world_type_path.is_relative_to(worlds_path):
                world_root = worlds_path / world_type_path.relative_to(worlds_path).parents[0]
                manifest_path = world_root / "archipelago.json"
                break
        with manifest_path.open("r", encoding="utf-8") as file:
            manifest = json.load(file)
        logger.info(f"Pokémon Battle Revolution APWorld Version: {manifest["world_version"]}")

        ctx.dolphin_sync_task = asyncio.create_task(dolphin_sync_task(ctx), name="DolphinSync")

        await ctx.exit_event.wait()
        # Wake the sync task, if it is currently sleeping, so it can start shutting down when it sees that the
        # exit_event is set.
        ctx.watcher_event.set()
        ctx.server_address = None

        await ctx.shutdown()

        if ctx.dolphin_sync_task:
            await ctx.dolphin_sync_task

    import colorama

    colorama.init()
    asyncio.run(_main(parsed_args.connect, parsed_args.password))
    colorama.deinit()

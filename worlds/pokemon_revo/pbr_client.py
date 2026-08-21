import asyncio
import time
import traceback
from typing import TYPE_CHECKING, Any, Optional

import dolphin_memory_engine

import Utils
from CommonClient import ClientCommandProcessor, get_base_parser, gui_enabled, logger, server_loop
tracker_loaded = False
try:
    from worlds.tracker.TrackerClient import TrackerGameContext as SuperContext
    tracker_loaded = True
except ModuleNotFoundError:
    from CommonClient import CommonContext as SuperContext
from NetUtils import ClientStatus

if TYPE_CHECKING:
    import kvui

from .items import ITEM_TABLE, LOOKUP_ID_TO_NAME, PBRItem, PBRItemData
from .locations import LOCATION_TABLE, PBRLocation

CONNECTION_REFUSED_GAME_STATUS = (
    "Dolphin failed to connect. Please load a randomized ROM for Pokémon Battle Revolution. Trying again in 5 seconds..."
)
CONNECTION_REFUSED_SAVE_STATUS = (
    "Dolphin failed to connect. Please load into the save file. Trying again in 5 seconds..."
)
CONNECTION_LOST_STATUS = (
    "Dolphin connection was lost. Please restart your emulator and make sure Pokémon Battle Revolution is running."
)
CONNECTION_CONNECTED_STATUS = "Dolphin connected successfully."
CONNECTION_INITIAL_STATUS = "Dolphin connection has not been initiated."

# This address contains the starting address of the save file in memory.
# Note: It is NOT the actual starting address of the save file.
SAVE_FILE_FIND_ADDR = 0x8045DE80

# The offset for the address that contains the currently loaded save profile's index.
SAVE_SLOT_CURRENT = 0x50

# The offset from the start of the save file to the first profile.
SAVE_SLOT_START = 0x380

# The offset from the first save profile to every one past it.
SAVE_SLOT_OFFSET = 0x6FF00

# The expected index for the following item that should be received.
EXPECTED_INDEX_OFFSET = 0x68531

# The address containing the slot name, used for server authentication.
# TODO: Find a proper address for this, then reimplement automatic server authentication.
# SLOT_NAME_ADDR = 0x80000006

# The offset containing the player's Pokétopia Badges.
BADGE_COUNT = 0x68533

# Offset for the unlocked Colosseums bitfield.
# Byte 1 is for Gateway, Main Street, Waterfall and Neon Colosseums.
# Byte 2 is for Crystal, Sunny Park, Magma, Courtyard, Sunset and Stargazer Colosseums.
COLOSSEUMS_BITFIELD = 0x12508

# Offset for Player's Poké Coupons.
POKE_COUPONS = 0x124E1


class PBRCommandProcessor(ClientCommandProcessor):
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
    colosseums_cleared = []

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
            if "death_link" in args["slot_data"]:
                Utils.async_start(self.update_death_link(bool(args["slot_data"]["death_link"])))
            self.slot_data = args["slot_data"]


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
    Read 4-bytes from Dolphin memory.

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


def read_string(console_address: int, strlen: int) -> str:
    """
    Read a string from Dolphin memory.

    :param console_address: Address to start reading from.
    :param strlen: Length of the string to read.
    :return: The string.
    """
    return dolphin_memory_engine.read_bytes(console_address, strlen).split(b"\0", 1)[0].decode()


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
    if not check_ingame():
        return False

    save_file_address = find_save_file_address()
    colo_flag_value = read_short(save_file_address + COLOSSEUMS_BITFIELD)
    poke_coupons_value = int.from_bytes(dolphin_memory_engine.read_bytes(save_file_address + POKE_COUPONS, 3))

    match ITEM_TABLE[item_name].group:
        case "Colosseums":
            if not bool((colo_flag_value >> ITEM_TABLE[item_name].bit) & 1):
                write_short(save_file_address + COLOSSEUMS_BITFIELD, colo_flag_value + ITEM_TABLE[item_name].value)
            return True
        case "Rental Passes":
            rental_pass_value = dolphin_memory_engine.read_byte(save_file_address + ITEM_TABLE[item_name].value)
            if not bool((rental_pass_value >> 5) & 1):
                dolphin_memory_engine.write_byte(save_file_address + ITEM_TABLE[item_name].value,
                                                rental_pass_value + 0x10)
            return True
        case "Poké Coupons":
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
    if check_ingame():
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
            print(LOOKUP_ID_TO_NAME)
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
    save_file_address = find_save_file_address()

    # Loop through all locations to see if each has been checked.
    for location, data in LOCATION_TABLE.items():
        checked = False
        if data.group == "Colosseum Clears":
            colosseum_clears = dolphin_memory_engine.read_byte(save_file_address + data.offset)
            if colosseum_clears > 0x0:
                checked = True

        if checked:
            if location == "Stargazer Colosseum - Clear":
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
    save_file_address = find_save_file_address()
    colo_flag_value = read_short(save_file_address + COLOSSEUMS_BITFIELD)
    badge_hunt_req = False
    colosseum_clear_req = False

    if not bool((colo_flag_value >> 13) & 1):
        if ctx.slot_data["goal_unlock_method"] != 1:
            current_badge_count = dolphin_memory_engine.read_byte(save_file_address + BADGE_COUNT)
            if current_badge_count >= ctx.slot_data["required_badge_amount"]:
                badge_hunt_req = True
        if ctx.slot_data["goal_unlock_method"] != 0:
            for location, data in LOCATION_TABLE.items():
                if data.group == "Colosseum Clears":
                    colosseum_clears_value = dolphin_memory_engine.read_byte(save_file_address + data.offset)
                    if colosseum_clears_value > 0x0 and data.region not in ctx.colosseums_cleared:
                        ctx.colosseums_cleared.append(data.region)
            if len(ctx.colosseums_cleared) >= ctx.slot_data["colosseum_clear_count"]:
                colosseum_clear_req = True
        if (
            (ctx.slot_data["goal_unlock_method"] == 0 and badge_hunt_req) or
            (ctx.slot_data["goal_unlock_method"] == 1 and colosseum_clear_req) or
            (ctx.slot_data["goal_unlock_method"] == 2 and badge_hunt_req and colosseum_clear_req)
        ):
            write_short(save_file_address + COLOSSEUMS_BITFIELD, colo_flag_value + 0x2000)


def check_ingame() -> bool:
    """
    Check if the player is currently in-game.

    :return: `True` if the player is in-game, otherwise `False`.
    """
    return dolphin_memory_engine.read_byte(read_word(SAVE_FILE_FIND_ADDR)) != 0x0


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
                    await give_items(ctx)
                    await check_locations(ctx)
                    await check_stargazer_unlock(ctx)
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


def main(*args: str) -> None:
    """
    Run the main async loop for the Pokémon Battle Revolution client.

    :param *args: Command line arguments passed to the client.
    """
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

        ctx.dolphin_sync_task = asyncio.create_task(dolphin_sync_task(ctx), name="DolphinSync")

        await ctx.exit_event.wait()
        # Wake the sync task, if it is currently sleeping, so it can start shutting down when it sees that the
        # exit_event is set.
        ctx.watcher_event.set()
        ctx.server_address = None

        await ctx.shutdown()

        if ctx.dolphin_sync_task:
            await ctx.dolphin_sync_task

    parser = get_base_parser()
    parsed_args = parser.parse_args(args)

    import colorama

    colorama.init()
    asyncio.run(_main(parsed_args.connect, parsed_args.password))
    colorama.deinit()

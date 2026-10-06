import os
import zipfile
import bsdiff4
import pkgutil
import shutil
import disc_riider_py
from typing import Dict, Any

from worlds.Files import APAutoPatchInterface
from settings import get_settings


class PBRPatch(APAutoPatchInterface):
    game = "Pokémon Battle Revolution"
    hash = "95a1a518cbec79fa217319e235cf31d7"
    patch_file_ending = ".appbr"
    result_file_ending = ".iso"
    source_data = bytes
    files: Dict[str, bytes]

    @classmethod
    def get_source_data(cls) -> bytes:
        with open(get_settings().pokemon_battle_revolution_settings.rom_file, "rb") as infile:
            base_rom_bytes = bytes(infile.read())

        return base_rom_bytes

    @classmethod
    def get_source_data_with_cache(cls) -> bytes:
        if not hasattr(PBRPatch, "source_data"):
            PBRPatch.source_data = PBRPatch.get_source_data()
        return PBRPatch.source_data

    def patch(self, target):
        self.read()
        options = self.get_file("options.json")
        base_dol_patch = pkgutil.get_data(__name__[:__name__.rfind('.')], "patches/base_dol_patch.bsdiff")
        common_patch = pkgutil.get_data(__name__[:__name__.rfind('.')], "patches/common_fsys_patch.bsdiff")
        iso_path = get_settings().pokemon_battle_revolution_settings.rom_file

        extractor = disc_riider_py.WiiIsoExtractor(iso_path)
        extractor.prepare_extract_section("DATA")

        pbr_temp = target.removesuffix(self.result_file_ending)+"_temp"
        try:
            os.mkdir(pbr_temp)
        except FileExistsError:
            print(f"{pbr_temp} already exists, skipping directory creation.")
        print(f"Extracting ISO at {pbr_temp}...")
        extractor.extract_to(pbr_temp, None)
        print("ISO Extraction Complete.")

        main_dol_path = pbr_temp+"/DATA/sys/main.dol"
        with open(main_dol_path, "rb") as main_dol:
            main_dol_bytes = bytes(main_dol.read())
        print("Adding Base main.dol Patch...")
        patched_dol = bsdiff4.patch(main_dol_bytes, base_dol_patch)
        if '\"randomize_rental_passes\": 1'.encode("utf8") in options:
            pass_patch = pkgutil.get_data(__name__[:__name__.rfind('.')], "patches/rental_pass_rando_patch.bsdiff")
            print("Adding Rental Pass Randomizer Patch...")
            patched_dol = bsdiff4.patch(patched_dol, pass_patch)
        print("Saving Patched main.dol...")
        with open(main_dol_path, "wb") as main_dol:
            main_dol.write(patched_dol)

        common_fsys_path = pbr_temp+"/DATA/files/common.fsys"
        with open(common_fsys_path, "rb") as common_fsys:
            common_fsys_bytes = bytes(common_fsys.read())
        print("Patching common.fsys...")
        patched_common = bsdiff4.patch(common_fsys_bytes, common_patch)
        with open(common_fsys_path, "wb") as common_fsys:
            common_fsys.write(patched_common)

        print("Rebuilding ISO...")
        disc_riider_py.rebuild_from_directory(pbr_temp, target, None)
        print("Rebuilding Complete.")
        shutil.rmtree(pbr_temp)

    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self.files = {}

    def get_manifest(self) -> Dict[str, Any]:
        manifest = super().get_manifest()
        manifest["base_checksum"] = self.hash
        manifest["result_file_ending"] = self.result_file_ending
        return manifest

    def read_contents(self, opened_zipfile: zipfile.ZipFile) -> Dict[str, Any]:
        manifest = super().read_contents(opened_zipfile)
        for file in opened_zipfile.namelist():
            if file not in ["archipelago.json"]:
                self.files[file] = opened_zipfile.read(file)
        return manifest

    def write_contents(self, opened_zipfile: zipfile.ZipFile) -> None:
        super().write_contents(opened_zipfile)
        for file in self.files:
            opened_zipfile.writestr(file, self.files[file],
                                    compress_type=zipfile.ZIP_STORED if file.endswith(".bsdiff4") else None)

    def get_file(self, file: str) -> bytes:
        """ Retrieves a file from the patch container."""
        if file not in self.files:
            self.read()
        return self.files[file]

    def write_file(self, file_name: str, file: bytes) -> None:
        """ Writes a file to the patch container, to be retrieved upon patching. """
        self.files[file_name] = file

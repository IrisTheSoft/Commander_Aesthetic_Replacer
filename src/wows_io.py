import dataclasses as DC
import os as OS
import pathlib as PTH
import shutil as SHU
import subprocess as SPROC
import typing as TP
import xml.etree.ElementTree as ET

import polib as PO


@DC.dataclass
class WowsIo:

    _wows_dir: PTH.Path
    _output_dir: PTH.Path = PTH.Path("output")
    _working_dir: PTH.Path = PTH.Path("working")

    def __post_init__(self):
        print("WoWs IO interface created with the following parameters:")
        print(" ", "WoWs directory:", self._wows_dir)
        print(" ", "Output directory:", self._output_dir)
        print(" ", "Working directory:", self._working_dir)
        self.clean_dir(self._working_dir)
        self.clean_dir(self._output_dir)
        self.unpack(PTH.Path("banks", "OfficialMods", "*", "mod.xml"))
        self.unpack(PTH.Path("gui", "crew_commander", "base", "**"))

    def clean_dir(self, dir: PTH.Path) -> None:
        print(f"Cleaning \"{dir}\" directory.")
        if dir.exists():
            print(f"\"{dir}\" already exists. Deleting it.")
            SHU.rmtree(dir)
        print(f"Creating \"{dir}\" directory.")
        OS.makedirs(dir)

    def unpack(self, pattern: PTH.Path) -> None:
        """Runs wowsunpack.exe"""
        print(f"Unpacking {pattern}.")
        SPROC.run(["wowsunpack.exe", (self._wows_dir/"idx").as_posix(), "-x",
                   "-o", self._working_dir.as_posix(),
                   "-p", "../../../res_packages", # Constant required parameter.
                   "-I", pattern.as_posix()],
                   check=True)

    def list_languages(self) -> TP.List[str]:
        return OS.listdir(self._wows_dir/"res"/"texts")

    def list_voice_overs(self) -> TP.List[str]:
        xpath = ("./AudioModification/ExternalEvent/Container/Path/StateList" +
                 "/State[Name='CrewName']/Value")
        voice_overs = set()
        for file_name in (self._working_dir/"banks"/"OfficialMods").glob("*/mod.xml"):
            voice_overs.update(node.text for node in ET.parse(file_name).findall(xpath))
        return sorted(voice_overs)

    def install_names(self, changes: TP.Dict[str, str], language: str = "en") -> None:
        """Install name mod

        :param changes: Mapping from translation ID's to their new values.
        :param language: Language code.
        """
        if not changes:
            return
        print(f"Installing name mod for language {language}.")

        mo = PO.mofile(self._wows_dir/"res"/"texts"/language/"LC_MESSAGES"/"global.mo")
        for entry in mo:
            if entry.msgid in changes:
                new_value = changes[entry.msgid]
                print(" ", f"{entry.msgstr} -> {new_value}")
                entry.msgstr = new_value
        mod_dir = self._output_dir/"texts"/language/"LC_MESSAGES"
        OS.makedirs(mod_dir)
        mo.save(mod_dir/"global.mo")

    def install_portraits(self, changes: TP.Dict[PTH.Path, PTH.Path]) -> None:
        """Install portrait mod

        :param changes: Mapping from destination file names to their replacements. The \
            replacements are not required to be unique.
        """
        if not changes:
            return
        print(f"Installing portrait mod.")
        mod_dir = self._output_dir/"gui"/"crew_commander"/"base"
        OS.makedirs(mod_dir)
        for destination, source in changes.items():
            print(" ", f"{destination} -> {source}")
            full_destination = PTH.Path(mod_dir, destination)
            if not full_destination.parent.is_dir():
                OS.mkdir(full_destination.parent)
            SHU.copyfile(source, full_destination)

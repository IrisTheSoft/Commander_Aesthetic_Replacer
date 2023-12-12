import copy as CP
import dataclasses as DC
import os as OS
import pathlib as PTH
import shutil as SHU
import subprocess as SPROC
import typing as TP
import xml.etree.ElementTree as ET

import jinja2 as JJ
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
        print("Installing portrait mod.")
        mod_dir = self._output_dir/"gui"/"crew_commander"/"base"
        OS.makedirs(mod_dir)
        for destination, source in changes.items():
            print(" ", f"{destination} -> {source}")
            full_destination = PTH.Path(mod_dir, destination)
            if not full_destination.parent.is_dir():
                OS.mkdir(full_destination.parent)
            SHU.copyfile(source, full_destination)

    def install_voice_overs(self, changes: TP.Dict[str,str], mod_name: str = "My Mod",
                            mod_id: str="wcar") -> None:
        """Install voice mod

        :param changes: Mapping from voice recipients to their donors.
        :param mod_name: In-game identifier for the mod.
        :param mod_id: Technical identifier for the mod.
        """

        if not changes:
            return

        print(f"Installing voice mod named \"{mod_name}\" into {mod_id}.")
        for recipient_name, donor_name in changes.items():
            print(" ", f"{recipient_name} -> {donor_name}")

        mod_dir = self._output_dir/"banks"/"Mods"/mod_id
        OS.makedirs(mod_dir)
        events = {}
        xpaths = ["./AudioModification/ExternalEvent/Container/Path/StateList" +
                  f"/State[Name='CrewName'][Value='{donor_name}']/../.."
                  for donor_name in set(changes.values())]

        for source_mod_file_name \
         in (self._working_dir/"banks"/"OfficialMods").glob("*/mod.xml"):
            tree = ET.parse(source_mod_file_name)
            files_to_move = set()
            source_mod_name = source_mod_file_name.parent.name

            # Identify required audio files.
            file_name_nodes = set().union(*(tree.iterfind(xpath + "/FilesList/File/Name")
                                            for xpath in xpaths))
            for file_name_node in file_name_nodes:
                files_to_move.add(file_name_node.text)
                # Deal with naming conflicts.
                file_name_node.text = f"{source_mod_name}/{file_name_node.text}"

            external_event_nodes = set().union(*(tree.iterfind(xpath + "/../..")
                                                 for xpath in xpaths))
            for external_event_node in external_event_nodes:
                external_event = external_event_node.find("./Name").text
                # The program assumes these conditions when generating the result
                # tree from the Jinja template.
                assert "V" + external_event[5:] == \
                    external_event_node.find("./Container/ExternalId").text, \
                    "Failed to derive ExternalId from ExternalEvent/Name"
                assert external_event_node.find("./Container/Name").text == \
                    "Voice", \
                    "Failed to guess structure of ExternalEvent"
                if external_event not in events:
                    # Register external event. Matching external events from all mod
                    # files will be merged into this list.
                    events[external_event] = []

                for path_node in external_event_node.iterfind("./Container/Path"):
                    name_value_node = \
                        path_node.find("./StateList/State[Name='CrewName']/Value")
                    for recipient_name, donor_name in changes.items():
                        if donor_name == name_value_node.text:
                            # Copy is required for supporting multiple commanders with
                            # same voice over.
                            new_node = CP.deepcopy(path_node)
                            new_node.find("./StateList/State[Name='CrewName']/Value") \
                                .text = recipient_name
                            events[external_event].append(ET.tostring(new_node,
                                                                      "unicode"))

            if files_to_move:
                # Unpacking every wem in the directory is faster than invoking unpacker
                # once for every file.
                self.unpack(PTH.Path("banks", "OfficialMods", source_mod_name, "*.wem"))
                OS.mkdir(mod_dir/source_mod_name)
                for file_name in files_to_move:
                    SHU.move(self._working_dir/"banks"/"OfficialMods"/source_mod_name/
                             file_name,
                             mod_dir/source_mod_name/file_name)
                # Clean used part of the working directory.
                SHU.rmtree(self._working_dir/"banks"/"OfficialMods"/source_mod_name)

        with open("src/voice_mod_template.xml.jinja") as template_file:
            template = JJ.Template(template_file.read())

        with open(mod_dir/"mod.xml", "w") as output_xml:
            for line in template.render(mod_name=mod_name, events=events).split("\n"):
                if not line.isspace():
                    output_xml.write(line)
                    output_xml.write("\n")

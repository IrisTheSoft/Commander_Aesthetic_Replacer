import dataclasses as DC
import os as OS
import pathlib as PTH
import shutil as SHU
import subprocess as SPROC


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

from hldlib.hldlevel import HLDLevel
from typing import Iterable
import os


class HLDBasics:
    @staticmethod
    def find_path() -> str:
        for dir_path, dir_names, file_names in os.walk("."):
            for file_name in file_names:
                if file_name.lower() == "hlddir.txt":
                    with open(os.path.join(dir_path, file_name)) as hld_dir_file:
                        return hld_dir_file.readline().rstrip()
        raise ValueError("No hldDir.txt found.")

    @staticmethod
    def get_levels(path: str, dirs: Iterable[str]):
        for dir_ in dirs:
            for level in [level for level in os.listdir(os.path.join(path, dir_)) if level.endswith(".lvl")]:
                filepath: str = os.path.join(path, dir_, level)
                yield filepath, dir_, level

    class Counter:
        def __init__(self, val: int = 10000):
            self._val = val

        def use(self) -> int:
            self._val += 1
            return self._val

    @staticmethod
    def omega_load(path: str):
        loaded: list[HLDLevel] = []
        for level_path, dir_, level_name in HLDBasics.get_levels(path, ("North", "East", "West", "South", "Central",
                                                                        "Intro", "Abyss",)):
            lvl = HLDLevel.from_file(level_path)
            loaded.append(lvl)
        return loaded

    DIRS = (
        "North",
        "East",
        "West",
        "South",
        "Central",
        "Intro",
        "Abyss",
    )

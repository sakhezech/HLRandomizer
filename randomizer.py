from __future__ import annotations
from hldlib import HLDObj, HLDLevel, HLDType, HLDBasics
from dataclasses import dataclass, field
from enum import Enum
from typing import Callable
from os import path
import json
import os
import random


JSON_DIR = "jsons"
GRAPH_JSON =    path.abspath(os.path.join(path.dirname(__file__),JSON_DIR, "out_graph.json"))  # "jsons\\out_graph.json"
DOOR_JSON =     path.abspath(os.path.join(path.dirname(__file__),JSON_DIR, "out_door.json"))  # "jsons\\out_door.json"
CONNECT_JSON =  path.abspath(os.path.join(path.dirname(__file__),JSON_DIR, "out_connect.json"))  # "jsons\\out_connect.json"
CONNECT2_JSON = path.abspath(os.path.join(path.dirname(__file__),JSON_DIR, "out_connect2.json"))  # "jsons\\out_connect2.json"
MANUAL_JSON =   path.abspath(os.path.join(path.dirname(__file__),JSON_DIR, "out_manual.json"))  # "jsons\\out_manual.json"
MANUAL2_JSON =  path.abspath(os.path.join(path.dirname(__file__),JSON_DIR, "out_manual2.json"))  # "jsons\\out_manual2.json"
OUTPUT_PATH = "game_files"
BACKUP_FOLDER_NAME = "backup"
ITEMLESS_FOLDER_NAME = "itemless"
DOORLESS_FOLDER_NAME = "doorless"
PATH_TO_ITEMLESS = os.path.join(OUTPUT_PATH, ITEMLESS_FOLDER_NAME)
PATH_TO_DOORLESS = os.path.join(OUTPUT_PATH, DOORLESS_FOLDER_NAME)
COUNTER = HLDBasics.Counter()


class RandomizerType(str, Enum):
    def __str__(self):
        return self.value
    CHECK = "check"
    MODULE = "module"
    TABLET = "tablet"
    GEARBIT = "gearbit"
    OUTFIT = "outfit"
    KEY = "key"
    WEAPON = "weapon"
    SHOP = "shop"
    PYLON = "pylon"
    DOOR = "door"
    TELEVATOR = "televator"
    TELEPORTER = "teleporter"


class Direction(str, Enum):
    def __str__(self):
        return self.value
    NORTH = "North"
    EAST = "East"
    WEST = "West"
    SOUTH = "South"
    CENTRAL = "Central"
    INTRO = "Intro"
    ABYSS = "Abyss"


def glue_on_direction(string: str, dir_: Direction):
    return f"{dir_.__str__().lower()}_{string}"


class CoolJSON:

    class_name = "class_name"

    @classmethod
    def dump(cls, obj: any, path: str):
        def encode_custom(custom: any):
            jsonable_custom = custom.__dict__
            jsonable_custom[cls.class_name] = custom.__class__.__name__
            return jsonable_custom
        with open(path, "w") as out:
            json.dump(obj, out, indent=4, default=encode_custom)

    @classmethod
    def load(cls, path: str):
        def decode_custom(custom: dict):
            if cls.class_name in custom:
                name = custom.pop(cls.class_name)
                return globals()[name](**custom)
            return custom
        with open(path) as in_:
            to_return = json.load(in_, object_hook=decode_custom)
            return to_return


class Inventory:

    reached_checks: list[FakeObject] = []

    full = {
        "keys": 16,
        "lasers": 2,
        "north_modules": 8,
        "east_modules": 8,
        "west_modules": 8,
        "south_modules": 8,
        "north_pylons": 0,
        "east_pylons": 0,
        "west_pylons": 0,
        "south_pylons": 0,
        "dash_shops": 1,

        "central_modules": 0,
        "intro_modules": 0,
        "abyss_modules": 0,
    }

    current = dict(full)

    temporary = dict(full)

    @classmethod
    def reset_temporary(cls):
        cls.temporary = dict(cls.current)

    @classmethod
    def reset_current(cls):
        cls.current = dict(cls.full)

    @classmethod
    def reset_reached_checks(cls):
        cls.reached_checks: list[FakeObject] = list()
    
    @classmethod
    def reset(cls):
        cls.reset_reached_checks()
        cls.reset_current()
        cls.reset_temporary()

    @classmethod
    def pick_up_item(cls, obj: FakeObject):
        def _pick_up_module():
            cls.temporary[glue_on_direction("modules", obj.dir_)] += 1

        def _pick_up_weapon():
            if obj.extra_info["weapon_id"] in [21, 23]:
                cls.temporary["lasers"] += 1

        def _pick_up_key():
            cls.temporary["keys"] += 1

        def _pick_up_shop():
            if obj.extra_info["shop_id"] == "UpgradeDash":
                cls.temporary["dash_shops"] += 1

        def _pick_up_pylon():
            cls.temporary[glue_on_direction("pylons", obj.dir_)] += 1

        pick_up_map = {
            RandomizerType.MODULE: _pick_up_module,
            RandomizerType.WEAPON: _pick_up_weapon,
            RandomizerType.KEY: _pick_up_key,
            RandomizerType.SHOP: _pick_up_shop,
            RandomizerType.PYLON: _pick_up_pylon,
        }
        pick_up_func = pick_up_map.get(obj.type)
        if pick_up_func is not None:
            pick_up_func()

    @classmethod
    def place_check_in_reached(cls, obj: FakeObject):
        cls.reached_checks.append(obj)


@dataclass
class FakeLevel:
    name: str
    dir_: Direction | str
    passed: bool = False
    fake_object_list: list[FakeObject] = field(default_factory=list)
    real_object_list: list[HLDObj] = field(default_factory=list)
    connections: list[Connection] = field(default_factory=list)
    extra_info: dict = field(default_factory=dict)

    def ping_all(self):
        self.passed = True
        for check in self.fake_object_list:
            check.ping_object()

        for connection in self.connections:
            connection.ping_connection()

    def convert_fake_objects_into_real(self):
        for fake_object in self.fake_object_list:
            real_object = fake_object.get_real_object()
            self.real_object_list.extend(real_object)


@dataclass
class FakeObject:
    type: RandomizerType
    original_type: str
    dir_: Direction | str
    x: int
    y: int
    requirements: dict
    manual_shift_x: int
    manual_shift_y: int
    enemy_id: int | str
    passed: bool = False
    extra_info: dict = field(default_factory=dict)

    @property
    def passes_requirements(self):
        return all([self.requirements[key] <= Inventory.temporary[key] for key in self.requirements if key != "modules"]) and \
               self.requirements["modules"] <= Inventory.temporary[glue_on_direction("modules", self.dir_)] and not self.passed

    def ping_object(self):
        if self.passes_requirements:
            self.passed = True
            if self.type == RandomizerType.CHECK:
                Inventory.place_check_in_reached(self)
            else:
                Inventory.pick_up_item(self)

    def get_real_object(self) -> list[HLDObj]:
        in_offset_map = {
            "MODULE": {"x": 0, "y": 0},
            "GEARBOX": {"x": -17, "y": 0},
            "TABLET": {"x": -1, "y": 7},
            "BONES": {"x": 0, "y": 0},
            "SHOP": {"x": -8, "y": 20},

            "PYLON": {"x": 0, "y": 0},
            " GEARBIT ENEMY": {"x": 0, "y": 0},  # TODO: CLEAN THIS
            "GEARBIT ENEMY": {"x": 0, "y": 0},
            " ENEMY GEARBIT": {"x": 0, "y": 0},
            "KEY": {"x": 0, "y": 0},
        }

        out_offset_map = {
            RandomizerType.MODULE: {"x": 0, "y": 0},
            RandomizerType.TABLET: {"x": -1, "y": 0},
            RandomizerType.GEARBIT: {"x": -17, "y": 0},
            RandomizerType.OUTFIT: {"x": -12, "y": 14},
            RandomizerType.KEY: {"x": -12, "y": 14},
            RandomizerType.WEAPON: {"x": -12, "y": 14},

            RandomizerType.SHOP: {
                "body": {"x": -8, "y": 0},
                "spirit": {"x": -18, "y": 20},
            },
        }

        def _get_module(obj: FakeObject):
            to_return = HLDObj(
                type=HLDType.MODULESOCKET,
                x=obj.x + obj.manual_shift_x + in_offset_map[obj.original_type]["x"] - out_offset_map[obj.type]["x"],
                y=obj.y + obj.manual_shift_y + in_offset_map[obj.original_type]["y"] - out_offset_map[obj.type]["y"],
                attrs={},
                uid=COUNTER.use(),
            )
            return to_return

        def _get_tablet(obj: FakeObject):
            to_return = HLDObj(
                type=HLDType.LIBRARIANTABLET,
                x=obj.x + obj.manual_shift_x + in_offset_map[obj.original_type]["x"] - out_offset_map[obj.type]["x"],
                y=obj.y + obj.manual_shift_y + in_offset_map[obj.original_type]["y"] - out_offset_map[obj.type]["y"],
                attrs={
                    "m": obj.extra_info["tablet_id"]
                },
                uid=COUNTER.use(),
            )
            return to_return

        def _get_gearbit(obj: FakeObject):
            to_return = HLDObj(
                type=HLDType.SPAWNER,
                x=obj.x + obj.manual_shift_x + in_offset_map[obj.original_type]["x"] - out_offset_map[obj.type]["x"],
                y=obj.y + obj.manual_shift_y + in_offset_map[obj.original_type]["y"] - out_offset_map[obj.type]["y"],
                attrs={
                    "-1": "GearbitCrate",
                    "-2": -999999,
                    "-4": 1,
                    "-5": 0,
                    "-6": -1,
                    "-7": 0,
                    "-8": 0,
                },
                uid=COUNTER.use(),
            )
            if obj.enemy_id:
                to_return.middle_string = f"1,{obj.enemy_id}"
                to_return.attrs["-1"] = "Gearbit"
            return to_return

        def _get_outfit(obj: FakeObject):
            to_return = HLDObj(
                type=HLDType.DRIFTERBONES_OUTFIT,
                x=obj.x + obj.manual_shift_x + in_offset_map[obj.original_type]["x"] - out_offset_map[obj.type]["x"],
                y=obj.y + obj.manual_shift_y + in_offset_map[obj.original_type]["y"] - out_offset_map[obj.type]["y"],
                attrs={
                    "spr": "spr_DrifterBones",
                    "i": 31,
                    "f": 0,
                    "k": 0,
                    "w": -999999,
                    "g": obj.extra_info["companion_id"],
                    "c": obj.extra_info["cape_id"],
                    "s": obj.extra_info["sword_id"],
                },
                uid=COUNTER.use(),
            )
            if obj.enemy_id:
                to_return.middle_string = f"1,{obj.enemy_id},caseScript,4,1,-999999,0"
            return to_return

        def _get_key(obj: FakeObject):
            to_return = HLDObj(
                type=HLDType.DRIFTERBONES_KEY,
                x=obj.x + obj.manual_shift_x + in_offset_map[obj.original_type]["x"] - out_offset_map[obj.type]["x"],
                y=obj.y + obj.manual_shift_y + in_offset_map[obj.original_type]["y"] - out_offset_map[obj.type]["y"],
                attrs={
                    "spr": "spr_DrifterBones",
                    "i": 31,
                    "f": 0,
                    "k": 1,
                    "w": -999999,
                    "g": 0,
                    "c": 0,
                    "s": 0,
                },
                uid=COUNTER.use(),
            )
            if obj.enemy_id:
                to_return.middle_string = f"1,{obj.enemy_id},caseScript,4,1,-999999,0"
            return to_return

        def _get_weapon(obj: FakeObject):
            to_return = HLDObj(
                type=HLDType.DRIFTERBONES_WEAPON,
                x=obj.x + obj.manual_shift_x + in_offset_map[obj.original_type]["x"] - out_offset_map[obj.type]["x"],
                y=obj.y + obj.manual_shift_y + in_offset_map[obj.original_type]["y"] - out_offset_map[obj.type]["y"],
                attrs={
                    "spr": "spr_DrifterBones",
                    "i": 31,
                    "f": 0,
                    "k": 0,
                    "w": obj.extra_info["weapon_id"],
                    "g": 0,
                    "c": 0,
                    "s": 0,
                },
                uid=COUNTER.use(),
            )
            if obj.enemy_id:
                to_return.middle_string = f"1,{obj.enemy_id},caseScript,4,1,-999999,0"
            return to_return

        def _get_shop(obj: FakeObject):
            body_to_return = HLDObj(
                type=HLDType.SCENERY,
                x=obj.x + obj.manual_shift_x + in_offset_map[obj.original_type]["x"] - out_offset_map[obj.type]["body"]["x"],
                y=obj.y + obj.manual_shift_y + in_offset_map[obj.original_type]["y"] - out_offset_map[obj.type]["body"]["y"],
                attrs={
                    "0": "spr_C_dummy",
                    "1": 0,
                    "2": 0,
                    "3": 0,
                    "k": 0,
                    "p": -4,
                    "fp": 0,
                    "4": 0,
                    "5": 0,
                    "f": 0,
                    "l": 0,
                },
                uid=COUNTER.use(),
            )
            spirit_to_return = HLDObj(
                type=obj.extra_info["shop_id"],
                x=obj.x + obj.manual_shift_x + in_offset_map[obj.original_type]["x"] - out_offset_map[obj.type]["spirit"]["x"],
                y=obj.y + obj.manual_shift_y + in_offset_map[obj.original_type]["y"] - out_offset_map[obj.type]["spirit"]["y"],
                attrs={},
                uid=COUNTER.use(),
            )
            return [body_to_return, spirit_to_return]

        def _get_door(obj: FakeObject):
            to_return = HLDObj(
                type=HLDType.DOOR,
                x=obj.x,
                y=obj.y,
                middle_string=f"1,{obj.extra_info['area_id']},caseScript,3,1,-999999,0",
                attrs={
                    "rm": obj.extra_info["room_id"],
                    "dr": obj.extra_info["door_id"],
                    "ed": obj.extra_info["angle"],
                },
                uid=obj.extra_info["self_id"]
            )
            return to_return

        def _get_teleporter(obj: FakeObject):
            to_return = HLDObj(
                type=HLDType.TELEPORTER,
                x=obj.x,
                y=obj.y,
                attrs={
                    "r": obj.extra_info["room_id"],
                    "d": obj.extra_info["door_id"],
                    "t": 1,
                    "i": 0,
                },
                uid=obj.extra_info["self_id"]
            )
            return to_return

        def _get_televator(obj: FakeObject):
            televator_to_return = HLDObj(
                type=HLDType.TELEVATOR,
                x=obj.x,
                y=obj.y,
                attrs={
                    "rm": obj.extra_info["room_id"],
                    "dr": obj.extra_info["door_id"],
                    "ed": obj.extra_info["vertical"],
                    "m": 0,
                    "v": 1,
                    "a": 0,
                    "trn": 4,
                },
                uid=COUNTER.use()
            )
            door_to_return = HLDObj(
                type=HLDType.DOOR,
                x=obj.x,
                y=obj.y,
                attrs={
                    "rm": "<undefined>",
                    "dr": 1,
                    "ed": 0,
                },
                uid=obj.extra_info["self_id"]
            )
            return [televator_to_return, door_to_return]

        def _get_pylon(obj: FakeObject): return []

        type_map = {
            RandomizerType.MODULE: _get_module,
            RandomizerType.TABLET: _get_tablet,
            RandomizerType.GEARBIT: _get_gearbit,
            RandomizerType.OUTFIT: _get_outfit,
            RandomizerType.KEY: _get_key,
            RandomizerType.WEAPON: _get_weapon,
            RandomizerType.SHOP: _get_shop,
            RandomizerType.PYLON: _get_pylon,
            RandomizerType.DOOR: _get_door,
            RandomizerType.TELEPORTER: _get_teleporter,
            RandomizerType.TELEVATOR: _get_televator,
        }

        real_object = type_map[self.type](self)
        if not isinstance(real_object, list):
            real_object = [real_object]
        return real_object


@dataclass
class Connection:
    pointer_to_level: FakeLevel
    dir_: Direction | str
    requirements: dict = field(default_factory=dict)

    @property
    def passes_requirements(self):
        return all([self.requirements[key] <= Inventory.temporary[key] for key in self.requirements if key != "modules"]) and \
               self.requirements["modules"] <= Inventory.temporary[glue_on_direction("modules", self.dir_)] and not self.pointer_to_level.passed

    def ping_connection(self):
        if self.passes_requirements:
            self.pointer_to_level.ping_all()


class LevelHolder(list[HLDLevel | FakeLevel]):
    def dump_all(self, path: str):
        for level in self:
            level.dump_level(os.path.join(path, level.dir_))

    def find_by_name(self, name: str) -> HLDLevel | FakeLevel | None:
        for level in self:
            if level.name == name:
                return level
        else:
            return None

    def find_first_by_partial_name(self, name: str) -> HLDLevel | FakeLevel | None:
        for level in self:
            if name in level.name:
                return level
        else:
            return None

    def connect_levels_from_list(self, list_: list):
        for connect_info in list_:
            from_ = self.find_by_name(connect_info["from"])
            to_ = self.find_by_name(connect_info["to"])
            from_.connections.append(
                Connection(
                    pointer_to_level=to_,
                    dir_=from_.dir_,
                    requirements=connect_info["requirements"]
                )
            )

    def get_empty_object(self, filter_lambda: Callable):
        inventory_before = False
        inventory_after = True

        def _ping_and_clear():
            self[0].ping_all()
            for level in self:
                level.passed = False

        while inventory_before != inventory_after:
            inventory_before = inventory_after
            _ping_and_clear()
            inventory_after = Inventory.temporary

        _ping_and_clear()
        _ping_and_clear()

        for level in self:
            for check in level.fake_object_list:
                check.passed = False

        filtered_checks = [check for check in Inventory.reached_checks if filter_lambda(check)]
        random_check: FakeObject = random.choice(filtered_checks)

        Inventory.reset_reached_checks()
        return random_check

    def debug_empty_finder(self):
        to_return = []
        for level in self:
            for check in level.fake_object_list:
                if check.type == RandomizerType.CHECK:
                    to_return.append([check, level])
        return to_return


def get_randomized_doors(levels: list[FakeLevel]):
    # THIS IS THE DOOR RANDO LOGIC
    # AND THIS IS UNREADABLE I'M SORRY
    for level in levels:
        for door in level.fake_object_list:
            door.extra_info["parent_room"] = level.name

    normal_levels = []
    cap_levels = []
    combined_levels = []

    for level in levels:
        if not level.extra_info["cut"]:
            if level_in_combined := [c_level for c_level in combined_levels if level.name.split("/")[0] == c_level.name]:
                level_in_combined[0].fake_object_list += level.fake_object_list
            else:
                level.name = level.name.split("/")[0]
                combined_levels.append(level)
        else:
            combined_levels.append(level)

    origin = combined_levels.pop(0)
    origin.passed = True
    normal_levels.append(origin)

    for level in combined_levels:
        if len(level.fake_object_list) > 1:
            normal_levels.append(level)
        else:
            cap_levels.append(level)

    def _connecting_doors(door1: FakeObject, door2: FakeObject):
        door1.extra_info["connected_to"] = door2
        door2.extra_info["connected_to"] = door1
        door1.passed = True
        door2.passed = True

    def _merge_lists(args: list[list[FakeObject]]):
        to_return = []
        for arg in args:
            to_return.extend(arg)
        return to_return

    while not all([level.passed for level in normal_levels]):
        # PLACE ALL ROOMS DOWN
        origin: FakeLevel = random.choice([level for level in normal_levels if level.passed and not all([door.passed for door in level.fake_object_list])])
        not_connected_doors = [door for door in origin.fake_object_list if not door.passed]
        not_connected_door = random.choice(not_connected_doors)
        not_placed_rooms = [level for level in normal_levels if not level.passed]
        not_placed_room: FakeLevel = random.choice(not_placed_rooms)
        if priority_doors := [priority_door for priority_door in not_placed_room.fake_object_list if priority_door.extra_info["priority"]]:
            priority_door = random.choice(priority_doors)
            _connecting_doors(priority_door, not_connected_door)
            not_placed_room.passed = True
        else:
            aaa = random.choice(not_placed_room.fake_object_list)
            _connecting_doors(aaa, not_connected_door)
            not_placed_room.passed = True

    while len([door for door in _merge_lists([level.fake_object_list for level in normal_levels]) if not door.passed]) > len(cap_levels):
        # CONNECT ALL DOORS IN PLACED ROOMS AND LEAVE SPACE FOR CAPS
        random_door1 = random.choice([door for door in _merge_lists([level.fake_object_list for level in normal_levels]) if not door.passed])
        random_door2 = random.choice([door for door in _merge_lists([level.fake_object_list for level in normal_levels]) if not door.passed and not door == random_door1])
        _connecting_doors(random_door1, random_door2)

    # PLACE CAPS
    random.shuffle(normal_levels)
    random.shuffle(cap_levels)
    for level in normal_levels:
        not_passed_doors = [door for door in level.fake_object_list if not door.passed]
        for not_passed_door in not_passed_doors:
            to_be_connected = cap_levels.pop()
            cap_door = to_be_connected.fake_object_list[0]
            _connecting_doors(cap_door, not_passed_door)
            to_be_connected.passed = True
            normal_levels.append(to_be_connected)

    return normal_levels


def prepare_and_merge_randomized_doors(graph_levels: LevelHolder, door_levels: list[FakeLevel]):
    def _min_requirements(req1: dict, req2: dict) -> dict:
        to_return = {}
        for key in req1.keys():
            to_return[key] = max(req1[key], req2[key])
        return to_return

    connection_list = []
    for level in door_levels:
        for door in level.fake_object_list:
            door.extra_info["self_id"] = COUNTER.use()
    for level in door_levels:
        for door in level.fake_object_list:
            door.extra_info["room_id"] = door.extra_info["connected_to"].extra_info["parent_room"].split("/")[0]
            door.extra_info["door_id"] = door.extra_info["connected_to"].extra_info["self_id"]
            connection_list.append(
                {
                    "from": door.extra_info["parent_room"],
                    "to": door.extra_info["connected_to"].extra_info["parent_room"],
                    "requirements": _min_requirements(door.requirements, door.extra_info["connected_to"].requirements)#door.requirements
                }
            )
        merge_into = graph_levels.find_first_by_partial_name(level.name.split("/")[0])
        merge_into.fake_object_list += level.fake_object_list
    graph_levels.connect_levels_from_list(connection_list)


def randomize_enemies(levels: LevelHolder):
    list_of_enemies = [
        "slime", "Birdman", "SmallCrystalSpider", "spider", "Grumpshroom",
        "Wolf", "dirk",  "SpiralBombFrog", "RifleDirk",
        "NinjaStarFrog", "TanukiGun", "CultBird", "missiledirk", "TanukiSword",
        "Melty", "GhostBeamBird", "Leaper", "Dirkommander", "BlaDirk", "CrystalBaby"
    ]
    for level in levels:
        for obj in level.object_list:
            if obj.type == HLDType.SPAWNER:
                if obj.attrs["-1"] in list_of_enemies and obj.attrs["-1"] != "Birdman":
                    obj.attrs["-1"] = random.choice(list_of_enemies)
                    obj.attrs["-2"] = 0
                    obj.attrs["-4"] = 1
                    obj.attrs["-5"] = 0
                    obj.attrs["-6"] = -1
                    obj.attrs["-7"] = 0
                    obj.attrs["-8"] = 0


def place_all_items(levels: LevelHolder):

    tablets = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16]
    lasers = [21, 23]
    shotguns = [2, 41, 43]
    shops = ["UpgradeSword", "UpgradeWeapon", "UpgradeHealthPack", "UpgradeSpecial"]
    capes = [2, 3, 4, 5, 6, 7, 9, 11, 12]; random.shuffle(capes)
    swords = [2, 3, 4, 5, 6, 7, 9, 11, 12]; random.shuffle(swords)
    companions = [2, 3, 4, 5, 6, 7, 9, 11, 13]; random.shuffle(companions)

    def place_important(inventory_key: str, place_func: Callable, lambda_filter: Callable = lambda x: True):
        while Inventory.current[inventory_key] > 0:
            Inventory.current[inventory_key] -= 1
            Inventory.reset_temporary()
            empty_check = levels.get_empty_object(lambda_filter)
            place_func(empty_check)

    def place_unimportant(i: int, place_func: Callable, lambda_filter: Callable = lambda x: True):
        for _ in range(i):
            Inventory.reset_temporary()
            empty_check = levels.get_empty_object(lambda_filter)
            place_func(empty_check)

    def _place_module(check: FakeObject):
        check.type = RandomizerType.MODULE

    def _place_key(check: FakeObject):
        check.type = RandomizerType.KEY

    def _place_dash_shop(check: FakeObject):
        check.type = RandomizerType.SHOP
        check.extra_info["shop_id"] = "UpgradeDash"

    def _place_generic_shop(check: FakeObject):
        check.type = RandomizerType.SHOP
        check.extra_info["shop_id"] = shops.pop()

    def _place_tablet(check: FakeObject):
        check.type = RandomizerType.TABLET
        check.extra_info["tablet_id"] = tablets.pop()

    def _place_laser(check: FakeObject):
        check.type = RandomizerType.WEAPON
        check.extra_info["weapon_id"] = lasers.pop()

    def _place_shotgun(check: FakeObject):
        check.type = RandomizerType.WEAPON
        check.extra_info["weapon_id"] = shotguns.pop()

    def _place_outfit(check: FakeObject):
        check.type = RandomizerType.OUTFIT
        check.extra_info["cape_id"] = capes.pop()
        check.extra_info["sword_id"] = swords.pop()
        check.extra_info["companion_id"] = companions.pop()

    def _place_gearbit(check: FakeObject):
        check.type = RandomizerType.GEARBIT

    # THESE ARE PLACED BY RESTRICTIVENESS OF THEIR PLACEMENT
    # SO MOST RESTRICTIVE FIRST LEAST RESTRICTIVE LAST
    # AND IMPORTANT FIRST UNIMPORTANT LAST
    place_important("north_modules", _place_module, lambda x: x.dir_ == Direction.NORTH and not x.enemy_id)
    place_important("east_modules", _place_module, lambda x: x.dir_ == Direction.EAST and not x.enemy_id)
    place_important("west_modules", _place_module, lambda x: x.dir_ == Direction.WEST and not x.enemy_id)
    place_important("south_modules", _place_module, lambda x: x.dir_ == Direction.SOUTH and not x.enemy_id)
    place_important("dash_shops", _place_dash_shop, lambda x: not x.enemy_id)
    place_unimportant(16, _place_tablet, lambda x: not x.enemy_id)
    place_unimportant(4, _place_generic_shop, lambda x: not x.enemy_id)
    place_important("keys", _place_key)
    place_important("dash_shops", _place_dash_shop)
    place_important("lasers", _place_laser)
    place_unimportant(3, _place_shotgun)
    place_unimportant(9, _place_outfit)
    place_unimportant(165, _place_gearbit)


def main(random_doors: bool = False, random_enemies: bool = False, output: bool = True, random_seed: str | None = None, output_folder_name: str = "out"):

    random.seed(random_seed)

    fake_levels = LevelHolder(CoolJSON.load(GRAPH_JSON))
    fake_levels.connect_levels_from_list(CoolJSON.load(CONNECT_JSON))

    if random_doors:
        intermediary_door_levels = get_randomized_doors(CoolJSON.load(DOOR_JSON))
        prepare_and_merge_randomized_doors(fake_levels, intermediary_door_levels)
    else:
        fake_levels.connect_levels_from_list(CoolJSON.load(CONNECT2_JSON))

    fake_levels.find_by_name("rm_NX_TowerLock/2").fake_object_list[0].type = RandomizerType.PYLON
    fake_levels.find_by_name("rm_EC_TempleIshVault").fake_object_list[0].type = RandomizerType.PYLON
    fake_levels.find_by_name("rm_WA_TowerEnter").fake_object_list[0].type = RandomizerType.PYLON
    fake_levels.find_by_name("rm_SX_TowerSouth/3").fake_object_list[0].type = RandomizerType.PYLON

    place_all_items(fake_levels)

    real_levels = LevelHolder(HLDBasics.omega_load(PATH_TO_DOORLESS if random_doors else PATH_TO_ITEMLESS))

    for fake_level in fake_levels:
        fake_level.convert_fake_objects_into_real()
        found = real_levels.find_by_name(fake_level.name.split("/")[0] + ".lvl")
        found.object_list += fake_level.real_object_list

    manual_changes = CoolJSON.load(MANUAL_JSON)
    for level in manual_changes:
        real_levels.find_by_name(level["name"]).object_list += level["object_list"]

    if random_doors:
        manual_changes2 = CoolJSON.load(MANUAL2_JSON)
        for level in manual_changes2:
            real_levels.find_by_name(level["name"]).object_list += level["object_list"]

    if random_enemies:
        randomize_enemies(real_levels)

    Inventory.reset()

    if output:
        real_levels.dump_all(os.path.join(OUTPUT_PATH, output_folder_name))

from randomizer import FakeLevel, FakeObject, RandomizerType, CoolJSON, JSON_DIR
from hldlib import HLDObj, HLDBasics
import re
import os

COUNTER = HLDBasics.Counter(9000)
PATH_TO_GRAPH = "legacy_resources\\graph.txt"
PATH_TO_DOOR = "legacy_resources\\doors.txt"
PATH_TO_CONNECT = "legacy_resources\\connect.txt"
PATH_TO_CONNECT2 = "legacy_resources\\connect2.txt"
PATH_TO_MANUAL = "legacy_resources\\manual.txt"
PATH_TO_MANUAL2 = "legacy_resources\\manual2.txt"


def comma_split(line_: str):
    return ["".join(badly_broken_line) for badly_broken_line in re.findall(r'"(.*?)",|(.*?),', line_ + ",")]


def get_json_from_graph(path: str, out: str):
    with open(path) as graph_file:
        to_export = []
        temp_room = FakeLevel("rm_PLACEHOLDER", "no")
        for line in graph_file:
            split_line = comma_split(line)
            match split_line[0]:
                case "Room":
                    to_export.append(temp_room)
                    temp_room = FakeLevel(name=split_line[2], dir_=split_line[1])
                case "Check":
                    original_type_with_manual = comma_split(split_line[12])
                    manual_shift_x = 0
                    manual_shift_y = 0
                    original_type = original_type_with_manual[0]
                    if len(original_type_with_manual) == 3:
                        manual_shift_x = int(original_type_with_manual[1])
                        manual_shift_y = int(original_type_with_manual[2])
                    check = FakeObject(
                        type=RandomizerType.CHECK,
                        dir_=temp_room.dir_,
                        x=int(split_line[1]),
                        y=int(split_line[2]),
                        enemy_id=split_line[3],
                        original_type=original_type,
                        manual_shift_x=manual_shift_x,
                        manual_shift_y=manual_shift_y,
                        requirements={
                            "keys": int(split_line[4]),
                            "lasers": int(split_line[5]),
                            "modules": int(split_line[6]),
                            "north_pylons": int(split_line[7]),
                            "east_pylons": int(split_line[8]),
                            "west_pylons": int(split_line[9]),
                            "south_pylons": int(split_line[10]),
                            "dash_shops": int(split_line[11]),
                        }
                    )
                    temp_room.fake_object_list.append(check)
                case _:
                    pass
        to_export.append(temp_room)
        to_export.pop(0)
        CoolJSON.dump(to_export, out)


def get_json_from_door(path: str, out: str):
    with open(path) as door_file:
        to_export = []
        temp_room = FakeLevel("rm_PLACEHOLDER", "no")
        for line in door_file:
            split_line = comma_split(line)
            match split_line[0]:
                case "Room":
                    to_export.append(temp_room)
                    temp_room = FakeLevel(name=split_line[2], dir_=split_line[1])
                    temp_room.extra_info = {"cut": split_line[3] == "CUT"}
                case "Door":
                    door = FakeObject(
                        type=RandomizerType.DOOR,
                        dir_=temp_room.dir_,
                        x=int(split_line[1]),
                        y=int(split_line[2]),
                        enemy_id="",
                        original_type="",
                        manual_shift_x=0,
                        manual_shift_y=0,
                        requirements={
                            "keys": int(split_line[3]),
                            "lasers": int(split_line[4]),
                            "modules": int(split_line[5]),
                            "north_pylons": int(split_line[6]),
                            "east_pylons": int(split_line[7]),
                            "west_pylons": int(split_line[8]),
                            "south_pylons": int(split_line[9]),
                            "dash_shops": int(split_line[10]),
                        },
                        extra_info={
                            "area_id": split_line[11],
                            "angle": split_line[12],
                            "priority": split_line[13] == "PRIORITY",
                            "connected_to": None
                        }
                    )
                    temp_room.fake_object_list.append(door)
                case "Teleporter":
                    door = FakeObject(
                        type=RandomizerType.TELEPORTER,
                        dir_=temp_room.dir_,
                        x=int(split_line[1]),
                        y=int(split_line[2]),
                        enemy_id="",
                        original_type="",
                        manual_shift_x=0,
                        manual_shift_y=0,
                        requirements={
                            "keys": int(split_line[3]),
                            "lasers": int(split_line[4]),
                            "modules": int(split_line[5]),
                            "north_pylons": int(split_line[6]),
                            "east_pylons": int(split_line[7]),
                            "west_pylons": int(split_line[8]),
                            "south_pylons": int(split_line[9]),
                            "dash_shops": int(split_line[10]),
                        },
                        extra_info={
                            "priority": split_line[11] == "PRIORITY",
                            "connected_to": None
                        },
                    )
                    temp_room.fake_object_list.append(door)
                case "Televator":
                    door = FakeObject(
                        type=RandomizerType.TELEVATOR,
                        dir_=temp_room.dir_,
                        x=int(split_line[1]),
                        y=int(split_line[2]),
                        enemy_id="",
                        original_type="",
                        manual_shift_x=0,
                        manual_shift_y=0,
                        requirements={
                            "keys": int(split_line[3]),
                            "lasers": int(split_line[4]),
                            "modules": int(split_line[5]),
                            "north_pylons": int(split_line[6]),
                            "east_pylons": int(split_line[7]),
                            "west_pylons": int(split_line[8]),
                            "south_pylons": int(split_line[9]),
                            "dash_shops": int(split_line[10]),
                        },
                        extra_info={
                            "vertical": split_line[11],
                            "priority": split_line[12] == "PRIORITY",
                            "connected_to": None
                        }
                    )
                    temp_room.fake_object_list.append(door)
                case _:
                    pass
        to_export.append(temp_room)
        to_export.pop(0)
        CoolJSON.dump(to_export, out)


def get_json_from_connect(path: str, out: str):
    to_export = []
    with open(path) as connect_file:
        for line in connect_file:
            if line[0] == "#":
                continue
            split_line = comma_split(line)
            to_export.append(
                {
                    "from": split_line[0],
                    "to": split_line[1],
                    "requirements": {
                        "keys": int(split_line[2]),
                        "lasers": int(split_line[3]),
                        "modules": int(split_line[4]),
                        "north_pylons": int(split_line[5]),
                        "east_pylons": int(split_line[6]),
                        "west_pylons": int(split_line[7]),
                        "south_pylons": int(split_line[8]),
                        "dash_shops": int(split_line[9]),
                    }
                }
            )
        CoolJSON.dump(to_export, out)


def get_json_from_manual12(path: str, out: str):
    changes = []
    room_name = "placeholder"
    list_of_objects = []
    with open(path, "r") as f:
        for line in f:
            if line[0] == "#":
                continue
            split_line = comma_split(line)
            match split_line[0]:
                case "Room":
                    changes.append({
                        "name": room_name,
                        "object_list": list_of_objects
                    })
                    list_of_objects = []
                    room_name = split_line[2] + ".lvl"
                case _:
                    list_of_objects.append(HLDObj.from_line(line))
    changes.append({
        "name": room_name,
        "object_list": list_of_objects
    })
    changes.pop(0)
    CoolJSON.dump(changes, out)


def generate_all_jsons():
    os.makedirs("jsons", exist_ok=True)
    get_json_from_graph(PATH_TO_GRAPH, os.path.join(JSON_DIR, "out_graph.json"))
    get_json_from_door(PATH_TO_DOOR, os.path.join(JSON_DIR, "out_door.json"))
    get_json_from_connect(PATH_TO_CONNECT, os.path.join(JSON_DIR, "out_connect.json"))
    get_json_from_connect(PATH_TO_CONNECT2, os.path.join(JSON_DIR, "out_connect2.json"))
    get_json_from_manual12(PATH_TO_MANUAL2, os.path.join(JSON_DIR, "out_manual2.json"))
    get_json_from_manual12(PATH_TO_MANUAL, os.path.join(JSON_DIR, "out_manual.json"))


if __name__ == "__main__":
    generate_all_jsons()

from hldlib.level import Level, LevelName
from hldlib.obj import Object, ObjectType

from .requirements import Req


class WorldGraph:
    def __init__(self) -> None:
        self.rooms: dict[LevelName, Room] = {}

    def add_room(self, name: LevelName) -> 'Room':
        room = Room(name)
        self.rooms[name] = room
        return room

    def sync(self, levels: list[Level]) -> None:
        levels_ = {}
        for level in levels:
            ln = level.name.removeprefix('rm_').removesuffix('.lvl').upper()
            if ln in LevelName._member_names_:
                level_name = LevelName[ln]
                levels_[level_name] = level

        keys = levels_.keys() & self.rooms.keys()
        for key in keys:
            level = levels_[key]
            room = self.rooms[key]

            room.sync(self, level)


class Room:
    def __init__(self, name: LevelName) -> None:
        self.name = name
        self.subrooms: dict[str, Subroom] = {}

    def add_subroom(self, subroom_name: str) -> 'Subroom':
        subroom = Subroom(self, subroom_name)
        self.subrooms[subroom_name] = subroom
        return subroom

    def sync(self, world: WorldGraph, level: Level) -> None:
        self._level = level
        id_to_object = {obj.id: obj for obj in level.objects}

        for subroom in self.subrooms.values():
            for item in subroom.items:
                obj = id_to_object[item.id]
                item.sync(obj)
            for door in subroom.doors:
                obj = id_to_object[door.id]
                door.sync(world, obj)
            for port in subroom.ports:
                port.sync()


class Subroom:
    def __init__(self, room: Room, name: str) -> None:
        self.room = room
        self.name = name
        self.items: list[Item] = []
        self.ports: list[Port] = []
        self.doors: list[Door] = []

    def add_item(self, id: int, x_off: int = 0, y_off: int = 0) -> 'Item':
        item = Item(id, x_off, y_off)
        self.items.append(item)
        return item

    def add_door(
        self, id: int, target_subroom_name: str, requirement: Req = Req.ZERO
    ) -> 'Door':
        door = Door(id, target_subroom_name, requirement, self)
        self.doors.append(door)
        return door

    def add_port(
        self, target_subroom_name: str, requirement: Req = Req.ZERO
    ) -> 'Port':
        port = Port(target_subroom_name, requirement, self)
        self.ports.append(port)
        return port


class Item:
    def __init__(self, id: int, x_off: int = 0, y_off: int = 0) -> None:
        self.id = id
        self.x_off = x_off
        self.y_off = y_off

    def sync(self, obj: Object) -> None:
        self._obj = obj


class Conn:
    pass


class Door(Conn):
    def __init__(
        self,
        id: int,
        target_subroom_name: str,
        requirement: Req,
        subroom: Subroom,
    ) -> None:
        self.id = id
        self.requirement = requirement
        self._target_subroom_name = target_subroom_name
        self.subroom = subroom

    def sync(self, world: WorldGraph, obj: Object) -> None:
        self._obj = obj
        if obj.type is ObjectType.DOOR or obj.type is ObjectType.TELEVATOR:
            name = obj.attrs['rm']
            id = int(obj.attrs['dr'])
        elif obj.type is ObjectType.TELEPORTER:
            name = obj.attrs['r']
            id = int(obj.attrs['d'])
        else:
            raise ValueError(
                'object type is not DOOR, TELEVATOR, or TELEPORTER:'
                f' {self.subroom.room.name.real_name} {obj.id} {obj.type.name}'
            )

        level_name = LevelName[name.removeprefix('rm_').upper()]
        subroom = world.rooms[level_name].subrooms[self._target_subroom_name]

        for door in subroom.doors:
            if door.id == id:
                self.pair = door
                break
        else:
            raise ValueError(
                'door not found:'
                f' {level_name.real_name} {id} for'
                f' {self.subroom.room.name.real_name} {obj.id}'
            )

    @property
    def link(self) -> 'Subroom':
        return self.pair.subroom


class Port(Conn):
    def __init__(
        self, _target_subroom_name: str, requirement: Req, subroom: Subroom
    ) -> None:
        self.requirement = requirement
        self._target_subroom_name = _target_subroom_name
        self.subroom = subroom

    def sync(self) -> None:
        self.link = self.subroom.room.subrooms[self._target_subroom_name]

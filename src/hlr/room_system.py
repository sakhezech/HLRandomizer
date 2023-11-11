from __future__ import annotations

from collections.abc import Iterator, MutableMapping

from hldlib import CaseScriptType, HLDLevel
from hldlib import HLDLevelNames as ln
from hldlib import HLDObj, HLDType

from hlr.requirements import Req


class Subroom:
    def __init__(self, parent: Room | None = None) -> None:
        self.items: list[Item] = []
        self.doors: list[Door] = []
        self.ports: list[Port] = []
        if parent:
            self.parent = parent

    @property
    def conns(self):
        return self.doors + self.ports

    def add_item(self, id: int, x_off: int = 0, y_off: int = 0) -> Item:
        item = Item(id, x_off, y_off, self)
        self.items.append(item)
        return item

    def add_door(self, to: str, id: int, req: Req = Req.ZERO) -> Door:
        same_doors = [d for d in self.doors if d.to == to and d.id == id]
        if same_doors:
            same_doors[0].reqs.append(req)
            return same_doors[0]
        door = Door(to, id, req, self)
        self.doors.append(door)
        return door

    def add_port(self, to: str, req: Req = Req.ZERO):
        same_ports = [p for p in self.ports if p.to == to]
        if same_ports:
            same_ports[0].reqs.append(req)
            return same_ports[0]
        port = Port(to, req, self)
        self.ports.append(port)
        return port


class Room(MutableMapping[str, Subroom]):
    def __init__(self, name: ln) -> None:
        self.name = name

        if not hasattr(self, '_subrooms'):
            self._subrooms: dict[str, Subroom] = {}

    def __getitem__(self, __key: str) -> Subroom:
        return self._subrooms.__getitem__(__key)

    def __setitem__(self, __key: str, __value: Subroom) -> None:
        if not hasattr(__value, 'parent'):
            __value.parent = self
        return self._subrooms.__setitem__(__key, __value)

    def __delitem__(self, __key: str) -> None:
        return self._subrooms.__delitem__(__key)

    def __len__(self) -> int:
        return self._subrooms.__len__()

    def __iter__(self) -> Iterator[str]:
        return self._subrooms.__iter__()


class RoomMaker:
    def __init__(self) -> None:
        self._instaces: dict[ln, Room] = {}

    def get_room(self, name: ln):
        if name in self._instaces:
            return self._instaces[name]
        instance = Room(name)
        self._instaces[name] = instance
        return instance

    def __call__(self, name: ln):
        return self.get_room(name)

    def init(self, levels: dict[ln, HLDLevel]) -> None:
        for level_name, level in levels.items():
            id_obj_map = {obj.uid: obj for obj in level.objects}
            room = self._instaces[level_name]

            reals = [
                real
                for subroom in room.values()
                for real in subroom.items + subroom.doors
            ]

            for real in reals:
                if real.id in id_obj_map:
                    robj = id_obj_map[real.id]
                    real._grab_meta(robj, level)


class Item:
    def __init__(
        self, id: int, x_off: int, y_off: int, parent: Subroom
    ) -> None:
        self.id = id
        self.x_off = x_off
        self.y_off = y_off
        self.parent = parent

    def _grab_meta(self, robj: HLDObj, level: HLDLevel):
        self._obj = robj
        self._level = level

        self.in_enemy = robj.dependencies.casescript == CaseScriptType.ENEMY


class Door:
    def __init__(self, to: str, id: int, req: Req, parent: Subroom) -> None:
        self.to = to
        self.id = id
        self.reqs = [req]
        self.parent = parent

    def _grab_meta(self, robj: HLDObj, level: HLDLevel):
        self._obj = robj
        self._level = level

        if robj.type in {HLDType.DOOR, HLDType.TELEVATOR}:
            room_name = robj.attrs['rm']
            other_id = robj.attrs['dr']
        else:
            room_name = robj.attrs['r']
            other_id = robj.attrs['d']

        room_name = str(room_name)
        other_id = int(other_id)

        room_enum = ln[room_name.removeprefix('rm_').upper()]
        self.link_door = [
            d for d in Room(room_enum)[self.to].doors if d.id == other_id
        ][0]

    @property
    def link_sub(self):
        return self.link_door.parent


class Port:
    def __init__(self, to: str, req: Req, parent: Subroom) -> None:
        self.to = to
        self.reqs = [req]
        self.parent = parent
        self.link_sub = parent.parent[to]

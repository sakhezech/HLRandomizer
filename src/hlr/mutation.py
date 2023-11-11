from enum import Enum
from typing import Any, Callable, Generic, Iterable, TypeVar

from hldlib import HLDDirection, HLDType

from hlr.requirements import Req
from hlr.room_system import Item

T = TypeVar('T')


class ItemTypeInfo(Generic[T]):
    def __init__(
        self,
        mutation_func: Callable[[Item, T], None],
        req_field_name: str | None = None,
        filter_func: Callable[[Item], bool] = lambda _: True,
        variations: Iterable[T] = [],
    ) -> None:
        self.mutation_func = mutation_func
        self.req_field_name = req_field_name
        self.filter_func = filter_func
        self.variations = variations

    def access_req_field(self, req: Req, num: int) -> None:
        if self.req_field_name:
            setattr(
                req,
                self.req_field_name,
                getattr(req, self.req_field_name) + num,
            )

    @property
    def is_important(self) -> bool:
        return bool(self.req_field_name)


def PLACEHOLDER(x: Item, y: Any) -> None:
    return None


def NOT_IN_ENEMY(x: Item) -> bool:
    return not x.in_enemy


class ItemType(Enum):
    N_MODULE = ItemTypeInfo(
        PLACEHOLDER,
        req_field_name='n_modules',
        filter_func=lambda x: x._level.direction == HLDDirection.NORTH
        and not x.in_enemy,
    )

    E_MODULE = ItemTypeInfo(
        PLACEHOLDER,
        req_field_name='e_modules',
        filter_func=lambda x: x._level.direction == HLDDirection.EAST
        and not x.in_enemy,
    )

    W_MODULE = ItemTypeInfo(
        PLACEHOLDER,
        req_field_name='w_modules',
        filter_func=lambda x: x._level.direction == HLDDirection.WEST
        and not x.in_enemy,
    )

    S_MODULE = ItemTypeInfo(
        PLACEHOLDER,
        req_field_name='s_modules',
        filter_func=lambda x: x._level.direction == HLDDirection.SOUTH
        and not x.in_enemy,
    )

    TABLET = ItemTypeInfo(
        PLACEHOLDER,
        filter_func=NOT_IN_ENEMY,
        variations=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16],
    )

    GEARBIT = ItemTypeInfo(
        PLACEHOLDER,
    )

    # TODO: WE SHOULD 12 -> 13 FOR COMPANION
    # BUT I DONT REMEMBER WHY EXACTLY
    OUTFIT = ItemTypeInfo(
        PLACEHOLDER,
        variations=[2, 3, 4, 5, 6, 7, 9, 11, 12],
    )

    KEY = ItemTypeInfo(
        PLACEHOLDER,
        req_field_name='keys',
    )

    LASER = ItemTypeInfo(
        PLACEHOLDER,
        variations=[21, 23],
    )

    SHOTGUN = ItemTypeInfo(
        PLACEHOLDER,
        variations=[2, 41, 43],
    )

    DASH = ItemTypeInfo(
        PLACEHOLDER,
        req_field_name='dash',
        filter_func=NOT_IN_ENEMY,
    )

    SWORD = ItemTypeInfo(
        PLACEHOLDER,
        req_field_name='sword',
        filter_func=NOT_IN_ENEMY,
    )

    SHOP = ItemTypeInfo(
        PLACEHOLDER,
        filter_func=NOT_IN_ENEMY,
        variations=[
            HLDType.UPGRADEWEAPON,
            HLDType.UPGRADEHEALTHPACK,
            HLDType.UPGRADESPECIAL,
        ],
    )

    N_PYLON = ItemTypeInfo(
        PLACEHOLDER,
        req_field_name='n_pylons',
        filter_func=lambda x: x._level.direction == HLDDirection.NORTH
        and not x.in_enemy,
    )

    E_PYLON = ItemTypeInfo(
        PLACEHOLDER,
        req_field_name='e_pylons',
        filter_func=lambda x: x._level.direction == HLDDirection.EAST
        and not x.in_enemy,
    )

    W_PYLON = ItemTypeInfo(
        PLACEHOLDER,
        req_field_name='w_pylons',
        filter_func=lambda x: x._level.direction == HLDDirection.WEST
        and not x.in_enemy,
    )

    S_PYLON = ItemTypeInfo(
        PLACEHOLDER,
        req_field_name='s_pylons',
        filter_func=lambda x: x._level.direction == HLDDirection.SOUTH
        and not x.in_enemy,
    )

    DELETE = ItemTypeInfo(
        lambda x, _: x._level.objects.remove(x._obj),
    )

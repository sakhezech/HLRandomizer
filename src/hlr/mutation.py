from typing import Any, Callable, Generic, Iterable, TypeVar

from hldlib import HLDDirection, HLDType

from hlr.requirements import Req
from hlr.room_system import Item

T = TypeVar('T')


class ItemType(Generic[T]):
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


class ITs:
    N_MODULE = ItemType(
        PLACEHOLDER,
        req_field_name='n_modules',
        filter_func=lambda x: x._level.direction == HLDDirection.NORTH
        and not x.in_enemy,
    )

    E_MODULE = ItemType(
        PLACEHOLDER,
        req_field_name='e_modules',
        filter_func=lambda x: x._level.direction == HLDDirection.EAST
        and not x.in_enemy,
    )

    W_MODULE = ItemType(
        PLACEHOLDER,
        req_field_name='w_modules',
        filter_func=lambda x: x._level.direction == HLDDirection.WEST
        and not x.in_enemy,
    )

    S_MODULE = ItemType(
        PLACEHOLDER,
        req_field_name='s_modules',
        filter_func=lambda x: x._level.direction == HLDDirection.SOUTH
        and not x.in_enemy,
    )

    TABLET = ItemType(
        PLACEHOLDER,
        filter_func=NOT_IN_ENEMY,
        variations=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16],
    )

    GEARBIT = ItemType(
        PLACEHOLDER,
    )

    # TODO: WE SHOULD 12 -> 13 FOR COMPANION
    # BUT I DONT REMEMBER WHY EXACTLY
    OUTFIT = ItemType(
        PLACEHOLDER,
        variations=[2, 3, 4, 5, 6, 7, 9, 11, 12],
    )

    KEY = ItemType(
        PLACEHOLDER,
        req_field_name='keys',
    )

    LASER = ItemType(
        PLACEHOLDER,
        variations=[21, 23],
    )

    SHOTGUN = ItemType(
        PLACEHOLDER,
        variations=[2, 41, 43],
    )

    DASH = ItemType(
        PLACEHOLDER,
        req_field_name='dash',
        filter_func=NOT_IN_ENEMY,
    )

    SWORD = ItemType(
        PLACEHOLDER,
        req_field_name='sword',
        filter_func=NOT_IN_ENEMY,
    )

    SHOP = ItemType(
        PLACEHOLDER,
        filter_func=NOT_IN_ENEMY,
        variations=[
            HLDType.UPGRADEWEAPON,
            HLDType.UPGRADEHEALTHPACK,
            HLDType.UPGRADESPECIAL,
        ],
    )

    N_PYLON = ItemType(
        PLACEHOLDER,
        req_field_name='n_pylons',
        filter_func=lambda x: x._level.direction == HLDDirection.NORTH
        and not x.in_enemy,
    )

    E_PYLON = ItemType(
        PLACEHOLDER,
        req_field_name='e_pylons',
        filter_func=lambda x: x._level.direction == HLDDirection.EAST
        and not x.in_enemy,
    )

    W_PYLON = ItemType(
        PLACEHOLDER,
        req_field_name='w_pylons',
        filter_func=lambda x: x._level.direction == HLDDirection.WEST
        and not x.in_enemy,
    )

    S_PYLON = ItemType(
        PLACEHOLDER,
        req_field_name='s_pylons',
        filter_func=lambda x: x._level.direction == HLDDirection.SOUTH
        and not x.in_enemy,
    )

    DELETE = ItemType(
        lambda x, _: x._level.objects.remove(x._obj),
    )

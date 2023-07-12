from __future__ import annotations

from dataclasses import dataclass, fields
from typing import ClassVar


@dataclass
class Req:
    keys: int = 0
    lasers: int = 0
    n_modules: int = 0
    e_modules: int = 0
    w_modules: int = 0
    s_modules: int = 0
    n_pylons: int = 0
    e_pylons: int = 0
    w_pylons: int = 0
    s_pylons: int = 0
    dash: int = 0
    sword: int = 0

    ZERO: ClassVar[Req]
    FULL: ClassVar[Req]

    def is_satisfied_by(self, other: Req) -> bool:

        return all(
            getattr(self, field.name) <= getattr(other, field.name)
            for field in fields(self.__class__)
        )

    @staticmethod
    def any_satisfied_by(selves: list[Req], other: Req) -> bool:
        return any(slf.is_satisfied_by(other) for slf in selves)


Req.ZERO = Req()
Req.FULL = Req(
    keys=16,
    lasers=2,
    n_modules=8,
    e_modules=8,
    w_modules=8,
    s_modules=8,
    dash=1,
    sword=1,
)

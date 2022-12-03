import re
import copy
from dataclasses import dataclass


@dataclass
class HLDObj:

    type: str
    x: int
    y: int
    attrs: dict
    middle_string: str = "-999999"
    uid: int = 10000
    layer: int = 0

    def translate(self, x: int, y: int) -> None:
        self.x += x
        self.y += y

    @classmethod
    def from_line(cls, line: str):
        match_obj = re.search(r"obj,(?P<type>.*?),(?P<uid>.*?),(?P<x>.*?),(?P<y>.*?),(?P<layer>.*?),(?P<middle_string>.*?),\+\+,(?P<attrs>.*)", line)
        type = match_obj.group("type")
        uid = int(match_obj.group("uid"))
        x = int(match_obj.group("x"))
        y = int(match_obj.group("y"))
        layer = int(match_obj.group("layer"))
        middle_string = match_obj.group("middle_string")
        str_to_attrs = match_obj.group("attrs")
        attrs = {}
        for pair in [pair for pair in str_to_attrs.split(",") if "=" in pair]:
            a = pair.split("=")
            attrs[a[0]] = cls._int_float_str_convert(a[1])
        return cls(type=type, x=x, y=y, uid=uid, layer=layer, middle_string=middle_string, attrs=attrs)

    def get_line(self, uid: int = None) -> str:
        attrs_to_str = ",".join([f"{key}={value}" for key, value in self.attrs.items()])
        return f"\n\t //obj,{self.type},{self.uid if uid is None else uid},{self.x},{self.y},{self.layer},{self.middle_string},++,{attrs_to_str},"

    def copy(self):
        return copy.copy(self)

    @staticmethod
    def _int_float_str_convert(val: str) -> int | float | str:
        try: return int(val)
        except: pass
        try: return float(val)
        except: pass
        return val

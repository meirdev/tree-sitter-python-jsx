import copy
import dataclasses
import json
import re
from typing import Any
from collections.abc import Iterable

SPACES = re.compile(r"\s+")


@dataclasses.dataclass
class String:
    text: bytes

    def __repr__(self) -> str:
        return json.dumps(self.text.decode())


@dataclasses.dataclass
class Code:
    text: bytes

    def __repr__(self) -> str:
        return self.text.decode()


class _Fragment:
    def __repr__(self) -> str:
        return "Fragment"


Fragment = _Fragment()


@dataclasses.dataclass
class JSX:
    type: str | _Fragment = Fragment
    props: dict[str, Any] = dataclasses.field(default_factory=dict)
    spread_props: list[Code] = dataclasses.field(default_factory=list)

    def __repr__(self) -> str:
        props = copy.deepcopy(self.props)

        children = props.get("children")

        if children is not None:
            if not isinstance(children, Iterable):
                children = [children]

            children_ = [
                i
                for i in children
                if not (isinstance(i, String) and SPACES.fullmatch(i.text.decode()))
            ]

            props["children"] = children_[0] if len(children_) == 1 else children_

        props = str(props)

        if len(self.spread_props) > 0:
            props = (
                props[:-1]
                + ", ".join(str(i) for i in [""] + self.spread_props)
                + props[-1:]
            )

        return f"Element('{self.type}', {props})"


@dataclasses.dataclass
class Element:
    type: str
    props: dict[str, Any]

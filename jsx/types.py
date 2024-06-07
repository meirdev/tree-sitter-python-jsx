import dataclasses
import json
from typing import Any


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
        props = str(self.props)

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

import inspect
from typing import Any, Iterable

from jsx.types import Element, _Fragment


def render_attrs(props: dict[str, Any]) -> str:
    return " ".join(
        f"{name}" + ("" if value is True else f'="{value}"')
        for name, value in props.items()
        if value is not False
    )


def render(element: Element) -> str:
    if not isinstance(element, Element):
        return str(element)

    # TODO: the compiler should to search for identifier
    type_ = inspect.currentframe().f_back.f_globals.get(element.type)

    if not isinstance(type_, _Fragment) and "A" <= element.type[0] <= "Z":
        return render(type_(**element.props))

    children = element.props.pop("children", None)

    if children is None:
        inner = ""
    elif isinstance(children, Iterable):
        inner = "".join(map(render, children))
    else:
        inner = render(children)

    if isinstance(type_, _Fragment):
        return inner

    attrs = render_attrs(element.props)

    name = element.type

    if len(attrs) == 0:
        output = f"<{name}"
    else:
        output = f"<{name} {attrs}"

    if not inner:
        return f"{output} />"

    return f"{output}>{inner}</{name}>"

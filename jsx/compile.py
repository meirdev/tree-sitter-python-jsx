import argparse
import pathlib
import re
from typing import Iterator

import tree_sitter_python as tspython
from tree_sitter import Language, Parser, Node

from jsx.types import String, Code, JSX

PY_LANGUAGE = Language(tspython.language())


def element_attributes(nodes: list[Node]):
    attributes, spread_attributes = {}, []

    for node in nodes:
        match node:
            case Node(type="jsx_attribute"):
                attributes |= visit_jsx_attribute(node)
            case Node(type="jsx_spread_attribute"):
                spread_attributes.append(visit_jsx_spread_attribute(node))

    return attributes, spread_attributes


def element_children(nodes: list[Node]):
    if len(nodes) == 0:
        return {}

    children = [visit_jsx_child(node) for node in nodes]

    return children[0] if len(nodes) == 1 else children


def visit_jsx_text(node: Node) -> String:
    return String(re.sub(rb"[^\S ]+", b"", node.text))


def visit_jsx_child(node: Node):
    node_ = node.children[0]

    match node_:
        case Node(type="jsx_text"):
            return visit_jsx_text(node_)
        case Node(type="jsx_code"):
            return Code(node_.children[1].text)
        case Node(type="jsx_element"):
            return visit_jsx_element(node_)
        case Node(type="jsx_fragment"):
            return visit_jsx_fragment(node_)


def visit_jsx_fragment(node: Node):
    return JSX(props={"children": element_children(node.children[1:-1])})


def visit_string(node: Node) -> str:
    return b"".join(i.text for i in node.children[1:-1]).decode()


def visit_interpolation(node: Node) -> Code:
    return Code(node.text[1:-1])


def visit_jsx_attribute(node: Node):
    name = node.children[0].text.decode()

    if node.child_count == 1:
        return {name: True}

    node_value = node.children[2]

    match node_value:
        case Node(type="string"):
            return {name: visit_string(node_value)}
        case Node(type="interpolation"):
            return {name: visit_interpolation(node_value)}


def visit_jsx_spread_attribute(node: Node):
    return Code(node.children[1].text)


def visit_jsx_self_closing_element(node: Node):
    element = JSX(node.children[1].text.decode())

    attributes, spread_attributes = element_attributes(node.children[2:-1])

    element.props = attributes
    element.spread_props = spread_attributes

    return element


def visit_jsx_opening_element(node: Node):
    type_ = node.children[1].text.decode()

    # TODO: assert visit_jsx_closing_element(X) == type_

    attributes, spread_attributes = element_attributes(node.children[2:-1])

    element = JSX(
        type_,
        props=attributes | {"children": element_children(node.parent.children[1:-1])},
    )
    element.spread_props = spread_attributes

    return element


def visit_jsx_closing_element(node: Node) -> str:
    return node.children[1].text.decode()


def visit_jsx_element(node: Node):
    node_ = node.children[0]

    match node_:
        case Node(type="jsx_self_closing_element"):
            element = visit_jsx_self_closing_element(node_)
        case Node(type="jsx_opening_element"):
            element = visit_jsx_opening_element(node_)

    return element


def visit_jsx(node: Node):
    node_ = node.children[0]

    match node_:
        case Node(type="jsx_fragment"):
            element = visit_jsx_fragment(node_)
        case Node(type="jsx_element"):
            element = visit_jsx_element(node_)

    return element


def find_next_jsx(node: Node) -> Node | None:
    # TODO: start search from the last point

    query = PY_LANGUAGE.query("(jsx) @jsx")

    captures = query.captures(node)

    if len(captures) == 0:
        return None
    else:
        return captures[0][0]


def compile(code: bytes) -> bytes:
    parser = Parser(PY_LANGUAGE)

    tree = parser.parse(code)

    while node := find_next_jsx(tree.root_node):
        element = visit_jsx(node)

        code = code[: node.start_byte] + str(element).encode() + code[node.end_byte :]

        # TODO: use tree.edit

        tree = parser.parse(code)

    return tree.root_node.text


def get_files(path: str) -> Iterator[pathlib.Path]:
    path_ = pathlib.Path(path)

    if path_.is_file():
        yield path_
    else:
        yield from path_.rglob("*.pyx")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("path")

    args = parser.parse_args()

    for file in get_files(args.path):
        with open(file, "b+r") as ifp:
            code = compile(ifp.read())

            with open(file.with_suffix(".py"), "w+b") as ofp:
                ofp.write(b"from jsx import Element, Fragment\n")
                ofp.write(code)

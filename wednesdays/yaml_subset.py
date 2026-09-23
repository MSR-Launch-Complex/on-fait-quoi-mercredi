"""A reader for the subset of YAML the data files are written in.

Why not PyYAML: `make build` must run offline on a clean checkout, so the build has no
install step and therefore no third-party import. The data files are ours and small, so
a documented subset is enough.

The subset, in full:

  - block mappings with plain keys matching `[A-Za-z_][A-Za-z0-9_]*`
  - block sequences, including sequences of mappings
  - flow sequences of scalars on one line: `[3, 11]`, `[]`
  - scalars: plain, 'single-quoted', "double-quoted" (\\\\, \\", \\n, \\t), integers,
    floats, true / false, null / ~
  - literal (`|`) and folded (`>`) block scalars, with the `-` chomping indicator
  - `#` comments, where the `#` starts a line or follows a space, and outside a quoted
    scalar. A quote quotes only where a scalar may start, so the apostrophe in a plain
    `L'Ilot jeux` is text and the comment after it is still a comment

Everything else in YAML - anchors, aliases, tags, flow mappings, multiple documents,
tabs for indentation - is rejected by name rather than half-understood. tests/
cross-checks this reader against PyYAML over the real data files when PyYAML happens to
be installed, which is how we know the subset means what YAML means.
"""

from __future__ import annotations

import re

KEY = re.compile(r"^([A-Za-z_][A-Za-z0-9_]*):(?:\s+(.*))?$")
INT = re.compile(r"^-?\d+$")
FLOAT = re.compile(r"^-?\d+\.\d+$")
BLOCK_SCALAR = re.compile(r"^([|>])(-?)$")


class YamlSubsetError(ValueError):
    """A file that is not in the subset, or not YAML at all.

    `problem`, `origin` and `lineno` are kept apart from the formatted message so that a
    caller can report the line the reader stopped on instead of taking the message
    apart again to find it. `lineno` is None when the problem is the file as a whole.
    """

    def __init__(self, problem, origin=None, lineno=None):
        self.problem = problem
        self.origin = origin
        self.lineno = lineno
        super(YamlSubsetError, self).__init__(self._message())

    def _message(self):
        if self.origin is None:
            return self.problem
        if self.lineno is None:
            return "%s: %s" % (self.origin, self.problem)
        return "%s:%d: %s" % (self.origin, self.lineno, self.problem)


def load(path):
    """Read one file. The path is used in error messages, so pass the real one."""
    with open(path, encoding="utf-8") as handle:
        return loads(handle.read(), origin=path)


def loads(text, origin="<string>"):
    lines = _Lines(text, origin)
    if lines.peek() is None:
        raise YamlSubsetError("file is empty", origin)
    indent, _, lineno = lines.peek()
    if indent != 0:
        raise lines.error(lineno, "the file starts indented")
    value = _parse_block(lines, 0)
    rest = lines.peek()
    if rest is not None:
        raise lines.error(rest[2], "unexpected content after the end of the document")
    return value


class _Lines:
    """The file as a cursor over its significant lines, plus its raw lines.

    Block scalars need the raw text, so comments are stripped per line as we read
    rather than up front.
    """

    def __init__(self, text, origin):
        self.raw = text.split("\n")
        self.origin = origin
        self.index = 0

    def peek(self):
        """The next significant line as (indent, content, lineno), or None at the end."""
        while self.index < len(self.raw):
            raw = self.raw[self.index]
            content = _strip_comment(raw)
            if content.strip():
                if "\t" in raw[: len(raw) - len(raw.lstrip())]:
                    raise self.error(self.index + 1, "indented with a tab; use spaces")
                indent = len(content) - len(content.lstrip(" "))
                return indent, content.strip(), self.index + 1
            self.index += 1
        return None

    def advance(self):
        self.index += 1

    def error(self, lineno, problem):
        return YamlSubsetError(problem, self.origin, lineno)


def _strip_comment(line):
    """Drop a trailing comment. A `#` counts only at the start or after a space."""
    out = []
    quote = None
    index = 0
    while index < len(line):
        char = line[index]
        pair = line[index : index + 2]
        if quote is None:
            if char == "#" and (index == 0 or line[index - 1] in " \t"):
                break
            if char in "\"'" and _opens_scalar(line, index):
                quote = char
            out.append(char)
            index += 1
            continue
        # Inside a quoted scalar `''` and `\"` are content, not the end of it.
        if (quote == "'" and pair == "''") or (quote == '"' and char == "\\" and len(pair) == 2):
            out.append(pair)
            index += 2
            continue
        if char == quote:
            quote = None
        out.append(char)
        index += 1
    return "".join(out).rstrip()


def _opens_scalar(text, index):
    """True when the quote at `index` begins a quoted scalar rather than sitting inside one.

    A quote opens a scalar only where a scalar can start. `L'Ilot jeux` is a plain scalar
    holding an apostrophe, not an unterminated string: reading it as a quote left the
    quote open for the rest of the line and swallowed any trailing ` # comment` into the
    value, which is how a French apostrophe used to change what a card said.
    """
    return index == 0 or text[index - 1] in " \t,["


def _parse_block(lines, indent):
    _, content, lineno = lines.peek()
    if content == "-" or content.startswith("- "):
        return _parse_sequence(lines, indent)
    if content.startswith("---"):
        raise lines.error(lineno, "multiple documents are not supported")
    if content.startswith(("&", "*", "!")):
        raise lines.error(lineno, "anchors, aliases and tags are not supported")
    if content.startswith("{"):
        raise lines.error(lineno, "flow mappings are not supported; write a block mapping")
    return _parse_mapping(lines, indent)


def _parse_mapping(lines, indent):
    mapping = {}
    while True:
        head = lines.peek()
        if head is None:
            return mapping
        line_indent, content, lineno = head
        if line_indent < indent:
            return mapping
        if line_indent > indent:
            raise lines.error(lineno, "unexpected indentation inside a mapping")
        if content.startswith("- "):
            raise lines.error(lineno, "a sequence item where a mapping key was expected")
        if content.startswith("---") or content.startswith("..."):
            raise lines.error(lineno, "multiple documents are not supported")
        match = KEY.match(content)
        if not match:
            raise lines.error(lineno, "expected 'key: value', found %r" % content)
        key, rest = match.group(1), match.group(2)
        if key in mapping:
            raise lines.error(lineno, "duplicate key %r" % key)
        lines.advance()
        mapping[key] = _parse_value(lines, indent, key, rest, lineno)


def _parse_value(lines, indent, key, rest, lineno):
    if rest is None or rest == "":
        child = lines.peek()
        if child is None or child[0] <= indent:
            raise lines.error(
                lineno,
                "key %r has no value; write '%s: null', '%s: []', or indent a block under it"
                % (key, key, key),
            )
        return _parse_block(lines, child[0])
    block = BLOCK_SCALAR.match(rest)
    if block:
        return _parse_block_scalar(lines, indent, block.group(1), block.group(2))
    return _parse_scalar(lines, rest, lineno)


def _parse_sequence(lines, indent):
    items = []
    while True:
        head = lines.peek()
        if head is None:
            return items
        line_indent, content, lineno = head
        if line_indent < indent:
            return items
        if line_indent > indent:
            raise lines.error(lineno, "unexpected indentation inside a sequence")
        if not (content == "-" or content.startswith("- ")):
            return items
        rest = content[2:].strip() if content.startswith("- ") else ""
        lines.advance()
        if rest == "":
            child = lines.peek()
            if child is None or child[0] <= indent:
                raise lines.error(lineno, "sequence item has no value")
            items.append(_parse_block(lines, child[0]))
            continue
        if KEY.match(rest):
            # `- key: value`: the item is a mapping whose keys align with that first key.
            items.append(_parse_inline_mapping(lines, indent, rest, lineno))
            continue
        items.append(_parse_scalar(lines, rest, lineno))


def _parse_inline_mapping(lines, indent, rest, lineno):
    """A `- key: value` item: parse the first pair, then any siblings indented under it."""
    match = KEY.match(rest)
    key, value_text = match.group(1), match.group(2)
    child_indent = indent + 2
    mapping = {key: _parse_value(lines, child_indent, key, value_text, lineno)}
    while True:
        head = lines.peek()
        if head is None or head[0] != child_indent:
            return mapping
        line_indent, content, line = head
        if content.startswith("- "):
            return mapping
        pair = KEY.match(content)
        if not pair:
            raise lines.error(line, "expected 'key: value', found %r" % content)
        if pair.group(1) in mapping:
            raise lines.error(line, "duplicate key %r" % pair.group(1))
        lines.advance()
        mapping[pair.group(1)] = _parse_value(
            lines, child_indent, pair.group(1), pair.group(2), line
        )


def _parse_block_scalar(lines, indent, style, chomping):
    """`|` keeps the newlines, `>` folds them into spaces; `-` drops the trailing one."""
    collected = []
    block_indent = None
    while lines.index < len(lines.raw):
        raw = lines.raw[lines.index]
        if raw.strip() == "":
            collected.append("")
            lines.advance()
            continue
        line_indent = len(raw) - len(raw.lstrip(" "))
        if line_indent <= indent:
            break
        if block_indent is None:
            block_indent = line_indent
        collected.append(raw[block_indent:])
        lines.advance()
    while collected and collected[-1] == "":
        collected.pop()
    if style == "|":
        text = "\n".join(collected)
    else:
        text = _fold(collected)
    return text if chomping == "-" else text + "\n"


def _fold(collected):
    """Folded style: a single newline becomes a space, a blank line stays a newline."""
    out = ""
    for line in collected:
        if out == "":
            out = line
        elif line == "":
            out += "\n"
        elif out.endswith("\n"):
            out += line
        else:
            out += " " + line
    return out


def _parse_scalar(lines, text, lineno):
    if text.startswith("["):
        return _parse_flow_sequence(lines, text, lineno)
    if text.startswith("{"):
        raise lines.error(lineno, "flow mappings are not supported")
    if text.startswith(("&", "*", "!")):
        raise lines.error(lineno, "anchors, aliases and tags are not supported")
    if text.startswith('"'):
        if not text.endswith('"') or len(text) < 2:
            raise lines.error(lineno, "unterminated double-quoted string")
        return _unescape(lines, text[1:-1], lineno)
    if text.startswith("'"):
        if not text.endswith("'") or len(text) < 2:
            raise lines.error(lineno, "unterminated single-quoted string")
        return text[1:-1].replace("''", "'")
    return _plain(text)


def _parse_flow_sequence(lines, text, lineno):
    if not text.endswith("]"):
        raise lines.error(lineno, "a flow sequence must open and close on one line")
    inner = text[1:-1].strip()
    if inner == "":
        return []
    items = []
    for piece in _split_flow(lines, inner, lineno):
        piece = piece.strip()
        if piece == "":
            raise lines.error(lineno, "empty item in a flow sequence")
        if piece.startswith("["):
            raise lines.error(lineno, "nested flow sequences are not supported")
        items.append(_parse_scalar(lines, piece, lineno))
    return items


def _split_flow(lines, inner, lineno):
    pieces, current, quote = [], "", None
    for index, char in enumerate(inner):
        if quote:
            current += char
            if char == quote:
                quote = None
        elif char in "\"'" and _opens_scalar(inner, index):
            quote = char
            current += char
        elif char == ",":
            pieces.append(current)
            current = ""
        else:
            current += char
    if quote:
        raise lines.error(lineno, "unterminated quoted string in a flow sequence")
    pieces.append(current)
    return pieces


def _unescape(lines, text, lineno):
    out, i = "", 0
    escapes = {"n": "\n", "t": "\t", '"': '"', "\\": "\\", "/": "/"}
    while i < len(text):
        char = text[i]
        if char != "\\":
            out += char
            i += 1
            continue
        if i + 1 >= len(text):
            raise lines.error(lineno, "string ends with a dangling backslash")
        nxt = text[i + 1]
        if nxt not in escapes:
            raise lines.error(lineno, "unsupported escape '\\%s'" % nxt)
        out += escapes[nxt]
        i += 2
    return out


def _plain(text):
    if text in ("null", "~"):
        return None
    if text == "true":
        return True
    if text == "false":
        return False
    if INT.match(text):
        return int(text)
    if FLOAT.match(text):
        return float(text)
    return text

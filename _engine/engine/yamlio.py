"""YAML subset reader and frontmatter writer. Standard library only.

Reads the YAML that Obsidian writes and that manifests use: block maps,
block lists, flow lists and maps, quoted strings, block scalars, comments.
Anything outside the subset raises YamlError instead of guessing.

Dates stay strings, the same way Obsidian keeps them.
"""

from __future__ import annotations

import re
from typing import Any, Dict, List, Optional, Tuple


class YamlError(ValueError):
    def __init__(self, message: str, line: int = 0):
        super().__init__(message)
        self.message = message
        self.line = line

    def __str__(self) -> str:
        return f"line {self.line}: {self.message}" if self.line else self.message


_INT_RE = re.compile(r"^[-+]?\d+$")
_FLOAT_RE = re.compile(r"^[-+]?(\d+\.\d*|\.\d+|\d+)([eE][-+]?\d+)?$")
_KEY_RE = re.compile(r"""^("(?:[^"\\]|\\.)*"|'(?:[^']|'')*'|[^\s"'\[\]{}#&*!|>%@`,][^#]*?)\s*:(?:\s+|$)""")
_FRONTMATTER_RE = re.compile(r"^---[ \t]*\r?\n(.*?)\r?\n?^---[ \t]*(?:\r?\n|$)", re.S | re.M)
_ESCAPES = {
    "n": "\n", "t": "\t", "r": "\r", "0": "\0", '"': '"', "\\": "\\",
    "/": "/", "a": "\a", "b": "\b", "e": "\x1b", "f": "\f", "v": "\v",
    " ": " ", "_": "\xa0",
}


# ---------------------------------------------------------------------------
# Scalars
# ---------------------------------------------------------------------------


def plain_scalar(raw: str) -> Any:
    s = raw.strip()
    if s in ("", "~", "null", "Null", "NULL"):
        return None
    if s in ("true", "True", "TRUE"):
        return True
    if s in ("false", "False", "FALSE"):
        return False
    if _INT_RE.match(s):
        try:
            return int(s)
        except ValueError:
            return s
    if _FLOAT_RE.match(s) and any(c.isdigit() for c in s):
        try:
            return float(s)
        except ValueError:
            return s
    return s


def _unescape_double(body: str, line: int) -> str:
    out = []
    i = 0
    while i < len(body):
        ch = body[i]
        if ch != "\\":
            out.append(ch)
            i += 1
            continue
        i += 1
        if i >= len(body):
            raise YamlError("string ends with a lone backslash", line)
        esc = body[i]
        if esc in _ESCAPES:
            out.append(_ESCAPES[esc])
            i += 1
        elif esc in "xuU":
            width = {"x": 2, "u": 4, "U": 8}[esc]
            digits = body[i + 1 : i + 1 + width]
            try:
                out.append(chr(int(digits, 16)))
            except ValueError:
                raise YamlError(f"bad escape \\{esc}{digits}", line)
            i += 1 + width
        else:
            raise YamlError(f"unknown escape \\{esc}", line)
    return "".join(out)


def _read_quoted(text: str, pos: int, line: int) -> Tuple[str, int]:
    """Read a quoted string that starts at text[pos]. Return (value, next pos)."""
    quote = text[pos]
    i = pos + 1
    if quote == '"':
        while i < len(text):
            if text[i] == "\\":
                i += 2
                continue
            if text[i] == '"':
                return _unescape_double(text[pos + 1 : i], line), i + 1
            i += 1
    else:
        parts = []
        while i < len(text):
            if text[i] == "'":
                if i + 1 < len(text) and text[i + 1] == "'":
                    parts.append("'")
                    i += 2
                    continue
                return "".join(parts), i + 1
            parts.append(text[i])
            i += 1
    raise YamlError("quoted string is not closed on the same line", line)


def _strip_comment(s: str) -> str:
    """Drop a trailing ' # comment' from a plain scalar."""
    if s.startswith("#"):
        return ""
    idx = s.find(" #")
    return s[:idx].rstrip() if idx != -1 else s


# ---------------------------------------------------------------------------
# Flow collections: [a, b] and {a: 1}
# ---------------------------------------------------------------------------


class _Flow:
    def __init__(self, text: str, line: int):
        self.t = text
        self.i = 0
        self.line = line

    def ws(self) -> None:
        while self.i < len(self.t) and self.t[self.i] in " \t\n\r":
            self.i += 1

    def value(self, in_map_key: bool = False) -> Any:
        self.ws()
        if self.i >= len(self.t):
            raise YamlError("flow collection is not closed", self.line)
        ch = self.t[self.i]
        if ch == "[":
            return self.seq()
        if ch == "{":
            return self.map()
        if ch in "\"'":
            val, self.i = _read_quoted(self.t, self.i, self.line)
            return val
        start = self.i
        while self.i < len(self.t):
            c = self.t[self.i]
            if c in ",]}":
                break
            if c == ":" and in_map_key and (self.i + 1 >= len(self.t) or self.t[self.i + 1] in " \t,]}"):
                break
            self.i += 1
        return plain_scalar(self.t[start : self.i])

    def seq(self) -> List[Any]:
        self.i += 1
        out: List[Any] = []
        while True:
            self.ws()
            if self.i >= len(self.t):
                raise YamlError("flow list is not closed", self.line)
            if self.t[self.i] == "]":
                self.i += 1
                return out
            out.append(self.value())
            self.ws()
            if self.i < len(self.t) and self.t[self.i] == ",":
                self.i += 1

    def map(self) -> Dict[str, Any]:
        self.i += 1
        out: Dict[str, Any] = {}
        while True:
            self.ws()
            if self.i >= len(self.t):
                raise YamlError("flow map is not closed", self.line)
            if self.t[self.i] == "}":
                self.i += 1
                return out
            key = self.value(in_map_key=True)
            self.ws()
            val: Any = None
            if self.i < len(self.t) and self.t[self.i] == ":":
                self.i += 1
                self.ws()
                if self.i < len(self.t) and self.t[self.i] not in ",}":
                    val = self.value()
            out[_key_text(key)] = val
            self.ws()
            if self.i < len(self.t) and self.t[self.i] == ",":
                self.i += 1


def _key_text(key: Any) -> str:
    if key is None:
        return ""
    if isinstance(key, bool):
        return "true" if key else "false"
    return str(key)


# ---------------------------------------------------------------------------
# Block parser
# ---------------------------------------------------------------------------


class _Parser:
    def __init__(self, text: str):
        self.lines = text.replace("\r\n", "\n").replace("\r", "\n").split("\n")
        self.i = 0

    def _peek(self) -> Optional[Tuple[int, str]]:
        while self.i < len(self.lines):
            raw = self.lines[self.i]
            stripped = raw.strip()
            if not stripped or stripped.startswith("#"):
                self.i += 1
                continue
            lead = raw[: len(raw) - len(raw.lstrip())]
            if "\t" in lead:
                raise YamlError("tab used for indentation", self.i + 1)
            return len(lead), raw.rstrip()[len(lead) :]
        return None

    def document(self) -> Any:
        first = self._peek()
        if first is None:
            return None
        node = self.node(first[0])
        rest = self._peek()
        if rest is not None:
            raise YamlError("unexpected indentation or content", self.i + 1)
        return node

    def node(self, indent: int) -> Any:
        cur = self._peek()
        assert cur is not None
        content = cur[1]
        if content == "-" or content.startswith("- "):
            return self.seq(indent)
        if _KEY_RE.match(content):
            return self.map(indent)
        self.i += 1
        return self.inline(content, indent)

    def map(self, indent: int) -> Dict[str, Any]:
        out: Dict[str, Any] = {}
        while True:
            cur = self._peek()
            if cur is None or cur[0] < indent:
                return out
            if cur[0] > indent:
                raise YamlError("unexpected indentation", self.i + 1)
            content = cur[1]
            m = _KEY_RE.match(content)
            if not m:
                if content == "-" or content.startswith("- "):
                    return out
                raise YamlError(f'expected "key: value", got "{content[:40]}"', self.i + 1)
            key_raw = m.group(1)
            if key_raw[0] in "\"'":
                key, _ = _read_quoted(key_raw, 0, self.i + 1)
            else:
                key = key_raw.strip()
            if key in out:
                raise YamlError(f'duplicate key "{key}"', self.i + 1)
            rest = content[m.end() :].strip()
            self.i += 1
            out[key] = self.value(rest, indent, in_map=True)

    def seq(self, indent: int) -> List[Any]:
        out: List[Any] = []
        while True:
            cur = self._peek()
            if cur is None or cur[0] != indent:
                if cur is not None and cur[0] > indent:
                    raise YamlError("unexpected indentation", self.i + 1)
                return out
            content = cur[1]
            if not (content == "-" or content.startswith("- ")):
                return out
            rest = content[1:].lstrip()
            if rest == "-" or rest.startswith("- "):
                # "- - item" starts a nested list at the content column
                inner = indent + (len(content) - len(rest))
                self.lines[self.i] = " " * inner + rest
                out.append(self.seq(inner))
                continue
            if rest and rest[0] not in "\"'[{" and _KEY_RE.match(rest):
                # "- key: value" starts a map whose keys sit at the content column
                inner = indent + (len(content) - len(rest))
                self.lines[self.i] = " " * inner + rest
                out.append(self.map(inner))
                continue
            self.i += 1
            out.append(self.value(rest, indent, in_map=False))

    def value(self, rest: str, indent: int, in_map: bool) -> Any:
        if rest == "" or rest.startswith("#"):
            nxt = self._peek()
            if nxt is None:
                return None
            if nxt[0] > indent:
                return self.node(nxt[0])
            if in_map and nxt[0] == indent and (nxt[1] == "-" or nxt[1].startswith("- ")):
                return self.seq(indent)
            return None
        return self.inline(rest, indent)

    def inline(self, rest: str, indent: int) -> Any:
        line = self.i
        ch = rest[0]
        if ch in "|>":
            return self.block_scalar(rest, indent)
        if ch in "[{":
            return self.flow(rest)
        if ch in "\"'":
            val, end = _read_quoted(rest, 0, line)
            tail = rest[end:].strip()
            if tail and not tail.startswith("#"):
                raise YamlError("unexpected text after quoted string", line)
            return val
        if ch in "&*":
            raise YamlError("anchors and aliases are not supported", line)
        if ch == "!":
            raise YamlError("YAML tags are not supported", line)
        if ch in "%@`":
            raise YamlError(f'a plain value cannot start with "{ch}", quote it', line)
        return plain_scalar(_strip_comment(rest))

    def flow(self, rest: str) -> Any:
        line = self.i
        text = rest
        while not _flow_closed(text):
            if self.i >= len(self.lines):
                raise YamlError("flow collection is not closed", line)
            text += "\n" + self.lines[self.i]
            self.i += 1
        flow = _Flow(text, line)
        val = flow.value()
        tail = text[flow.i :].strip()
        if tail and not tail.startswith("#"):
            raise YamlError("unexpected text after flow collection", line)
        return val

    def block_scalar(self, header: str, indent: int) -> str:
        line = self.i
        m = re.match(r"^([|>])([-+]?)(\d?)([-+]?)\s*(#.*)?$", header)
        if not m:
            raise YamlError(f'bad block scalar header "{header}"', line)
        style = m.group(1)
        chomp = m.group(2) or m.group(4)
        block_indent = indent + int(m.group(3)) if m.group(3) else None
        collected: List[str] = []
        while self.i < len(self.lines):
            raw = self.lines[self.i]
            if raw.strip() == "":
                collected.append("")
                self.i += 1
                continue
            lead = len(raw) - len(raw.lstrip(" "))
            if block_indent is None:
                if lead <= indent:
                    break
                block_indent = lead
            if lead < block_indent:
                break
            collected.append(raw[block_indent:])
            self.i += 1
        while collected and collected[-1] == "":
            collected.pop()
        if style == "|":
            text = "\n".join(collected)
        else:
            text = _fold(collected)
        if not collected:
            return ""
        if chomp == "-":
            return text
        return text + "\n"


def _fold(lines: List[str]) -> str:
    out = ""
    prev_blank = True
    for idx, ln in enumerate(lines):
        if ln == "":
            out += "\n"
            prev_blank = True
            continue
        if idx and not prev_blank:
            out += " "
        out += ln
        prev_blank = False
    return out


def _flow_closed(text: str) -> bool:
    depth = 0
    i = 0
    while i < len(text):
        ch = text[i]
        if ch in "\"'":
            try:
                _, i = _read_quoted(text, i, 0)
            except YamlError:
                return False
            continue
        if ch in "[{":
            depth += 1
        elif ch in "]}":
            depth -= 1
            if depth == 0:
                return True
        i += 1
    return False


def parse(text: str) -> Any:
    """Parse a YAML document. Returns None for an empty document."""
    return _Parser(text).document()


def parse_mapping(text: str) -> Dict[str, Any]:
    data = parse(text)
    if data is None:
        return {}
    if not isinstance(data, dict):
        raise YamlError("frontmatter must be a map of properties")
    return data


# ---------------------------------------------------------------------------
# Frontmatter split and minimal-diff writer
# ---------------------------------------------------------------------------


def split_frontmatter(text: str) -> Tuple[Optional[str], str]:
    """Return (frontmatter text or None, body). Body keeps its exact bytes."""
    if not text.startswith("---"):
        return None, text
    m = _FRONTMATTER_RE.match(text)
    if not m:
        return None, text
    return m.group(1), text[m.end() :]


_PLAIN_SAFE_RE = re.compile(r"^[^\s\-?:,\[\]{}#&*!|>'\"%@`][^\n]*$")


def dump_scalar(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return repr(value) if isinstance(value, float) else str(value)
    s = str(value)
    needs_quotes = (
        s == ""
        or s != s.strip()
        or not _PLAIN_SAFE_RE.match(s)
        or ": " in s
        or " #" in s
        or s.endswith(":")
        or not isinstance(plain_scalar(s), str)
    )
    if not needs_quotes:
        return s
    escaped = s.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n").replace("\t", "\\t")
    return f'"{escaped}"'


def dump_property(key: str, value: Any, indent: int = 0) -> List[str]:
    """Render one property as YAML lines, in the style Obsidian writes."""
    pad = " " * indent
    k = dump_scalar(key) if not re.match(r"^[\w][\w \-./]*$", key) else key
    if isinstance(value, dict):
        if not value:
            return [f"{pad}{k}: {{}}"]
        lines = [f"{pad}{k}:"]
        for sub_key, sub_val in value.items():
            lines += dump_property(str(sub_key), sub_val, indent + 2)
        return lines
    if isinstance(value, (list, tuple)):
        if not value:
            return [f"{pad}{k}: []"]
        lines = [f"{pad}{k}:"]
        for item in value:
            lines += _dump_item(item, indent + 2)
        return lines
    text = dump_scalar(value)
    return [f"{pad}{k}: {text}" if text else f"{pad}{k}:"]


def _dump_item(item: Any, indent: int) -> List[str]:
    pad = " " * indent
    if isinstance(item, dict) and item:
        lines: List[str] = []
        for idx, (sub_key, sub_val) in enumerate(item.items()):
            rendered = dump_property(str(sub_key), sub_val, indent + 2)
            if idx == 0:
                rendered[0] = f"{pad}- {rendered[0].lstrip()}"
            lines += rendered
        return lines
    if isinstance(item, (list, tuple)):
        if not item:
            return [f"{pad}- []"]
        nested: List[str] = []
        for sub in item:
            nested += _dump_item(sub, indent + 2)
        nested[0] = f"{pad}- {nested[0].lstrip()}"
        return nested
    if isinstance(item, dict):
        return [f"{pad}- {{}}"]
    text = dump_scalar(item)
    return [f"{pad}- {text}" if text else f"{pad}-"]


def property_blocks(fm_text: str) -> Tuple[List[str], List[Tuple[str, List[str]]]]:
    """Split frontmatter into (leading lines, [(key, lines)]) by top-level key.

    Used to rewrite single properties and leave every other line untouched.
    """
    head: List[str] = []
    blocks: List[Tuple[str, List[str]]] = []
    for raw in fm_text.replace("\r\n", "\n").split("\n"):
        m = _KEY_RE.match(raw) if raw and raw[0] not in " \t#-" else None
        if m:
            key_raw = m.group(1)
            key = _read_quoted(key_raw, 0, 0)[0] if key_raw[0] in "\"'" else key_raw.strip()
            blocks.append((key, [raw]))
        elif blocks:
            blocks[-1][1].append(raw)
        else:
            head.append(raw)
    return head, blocks


def rewrite_frontmatter(
    fm_text: str,
    changes: Dict[str, Any],
    remove: Optional[List[str]] = None,
    order: Optional[List[str]] = None,
) -> str:
    """Apply property changes with a minimal diff.

    Properties not named in `changes` or `remove` keep their exact lines.
    `order` moves listed keys to the front in that order; the rest follow
    in their current order.
    """
    head, blocks = property_blocks(fm_text)
    removed = set(remove or [])
    seen = set()
    out: List[Tuple[str, List[str]]] = []
    for key, lines in blocks:
        if key in removed:
            continue
        if key in changes:
            trailing = []
            while lines and lines[-1].strip() == "" and len(lines) > 1:
                trailing.insert(0, lines.pop())
            out.append((key, dump_property(key, changes[key]) + trailing))
        else:
            out.append((key, lines))
        seen.add(key)
    for key, value in changes.items():
        if key not in seen and key not in removed:
            out.append((key, dump_property(key, value)))
    if order:
        rank = {k: i for i, k in enumerate(order)}
        ordered = sorted((b for b in out if b[0] in rank), key=lambda b: rank[b[0]])
        rest = [b for b in out if b[0] not in rank]
        out = ordered + rest
    result = list(head)
    for _, lines in out:
        result += lines
    return "\n".join(result)


def join_note(fm_text: str, body: str) -> str:
    fm = fm_text.rstrip("\n")
    return f"---\n{fm}\n---\n{body}" if fm else f"---\n---\n{body}"

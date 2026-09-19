"""Date fields must hold a real date."""

import datetime
import re

from engine.findings import Finding

ID = "date-format"
ORDER = 40
ABOUT = "Date fields hold a valid date, in the manifest format when one is set."

_ISO_RE = re.compile(r"^(\d{4})(?:-(\d{2})(?:-(\d{2}))?)?(?:[T ].*)?$")
_TOKEN_RE = re.compile(r"YYYY|YY|MM|DD|M|D")


def _format_regex(fmt):
    pattern, pos = "", 0
    for m in _TOKEN_RE.finditer(fmt):
        pattern += re.escape(fmt[pos:m.start()])
        token = m.group(0)
        group = {"Y": "y", "M": "m", "D": "d"}[token[0]]
        width = "{4}" if token == "YYYY" else "{2}" if len(token) == 2 else "{1,2}"
        pattern += f"(?P<{group}>\\d{width})"
        pos = m.end()
    return re.compile("^" + pattern + re.escape(fmt[pos:]) + "$")


def _real(year, month, day):
    try:
        datetime.date(year, month, day)
        return True
    except ValueError:
        return False


def run(ctx):
    if ctx.schema is None:
        return []
    out = []
    for name, field in ctx.schema.fields.items():
        value = ctx.frontmatter.get(name)
        if field.get("type") != "date" or not isinstance(value, (str, int)) or isinstance(value, bool):
            continue
        text = str(value).strip()
        if not text:
            continue
        fmt = field.get("format")
        if fmt:
            m = _format_regex(str(fmt)).match(text)
            if not m:
                out.append(Finding(ID, f'"{name}" must match the date format {fmt}, got "{text}".', field=name))
                continue
            parts = m.groupdict()
            if all(parts.get(k) for k in "ymd") and len(parts["y"]) == 4:
                if not _real(int(parts["y"]), int(parts["m"]), int(parts["d"])):
                    out.append(Finding(ID, f'"{name}" is not a real calendar date: "{text}".', field=name))
            continue
        m = _ISO_RE.match(text)
        if not m:
            out.append(Finding(ID, f'"{name}" does not look like a date: "{text}".', field=name,
                               severity="warning", hint="Use YYYY-MM-DD or a full ISO timestamp."))
        elif m.group(3) and not _real(int(m.group(1)), int(m.group(2)), int(m.group(3))):
            out.append(Finding(ID, f'"{name}" is not a real calendar date: "{text}".', field=name))
    return out

"""Content transforms applied to every converted Markdown page.

The flattened project is built with stock Zensical and one small stylesheet,
so the house classes the MkDocs corpus relied on (`.heading` title banners,
`.example` headings, `.shaded` table cells, sprite-sheet toolbar icons, the
binding-strength table's layout classes) have no styling any more. Rather
than restyle them, the content is transformed so the class disappears and the
meaning lives in the Markdown itself. Each transform is a text-to-text
function, idempotent, and a no-op on content that does not carry its pattern,
so the pipeline is safe against both the pre-July source (raw-HTML titles)
and today's (Markdown titles with styling spans).

Fenced code blocks are never touched: every transform walks the prose
segments between fences only.
"""

import posixpath
import re

from bs4 import BeautifulSoup, NavigableString, Tag

# Opening/closing fence marker (3+ backticks or tildes), optionally indented.
_FENCE_RE = re.compile(r"^\s*(`{3,}|~{3,})")


def prose_segments(text):
    """Split text into (is_code, lines) runs at fenced code blocks.

    The fence lines themselves belong to the code run. Joining every run's
    lines back with newlines reproduces the input exactly.
    """
    runs = []
    current = []
    fence = None
    for line in text.split("\n"):
        marker = _FENCE_RE.match(line)
        if fence is None and marker:
            if current:
                runs.append((False, current))
            current = [line]
            fence = marker.group(1)[0]
        elif fence is not None:
            current.append(line)
            if marker and marker.group(1)[0] == fence:
                runs.append((True, current))
                current = []
                fence = None
        else:
            current.append(line)
    if current:
        runs.append((fence is not None, current))
    return runs


def _map_prose_lines(text, fn):
    """Apply fn(line) -> str to every line outside fenced code."""
    out = []
    for is_code, lines in prose_segments(text):
        out.extend(lines if is_code else [fn(line) for line in lines])
    return "\n".join(out)


def _expand_prose_lines(text, fn, always_blank_after=False):
    """Apply fn(line) -> str | None to every line outside fenced code, where
    a str result replaces the line and None leaves it untouched.

    A replacement that spans several lines (or any replacement, with
    always_blank_after) must be followed by a blank line; one is inserted
    only when the original next line is not already blank, so the transform
    never doubles up blank lines.
    """
    out = []
    runs = prose_segments(text)
    for index, (is_code, lines) in enumerate(runs):
        if is_code:
            out.extend(lines)
            continue
        for position, line in enumerate(lines):
            replacement = fn(line)
            if replacement is None:
                out.append(line)
                continue
            out.append(replacement)
            if not (always_blank_after or "\n" in replacement):
                continue
            if position + 1 < len(lines):
                following = lines[position + 1]
            elif index + 1 < len(runs):
                following = runs[index + 1][1][0]
            else:
                following = None
            if following is not None and following.strip():
                out.append("")
    return "\n".join(out)


def _map_prose_blocks(text, fn):
    """Apply fn(block) -> str to every multi-line prose run outside fences."""
    out = []
    for is_code, lines in prose_segments(text):
        block = "\n".join(lines)
        out.append(block if is_code else fn(block))
    return "\n".join(out)


# --- page titles -------------------------------------------------------

# A trailing attr_list on an ATX heading: `# Title {: #id .class}`.
_ATTR_LIST_RE = re.compile(r"\s*\{:\s*([^}]*?)\s*\}\s*$")
# The key-to-notation macro the monorepo appends to command headings.
_KEY_RE = re.compile(r"\s*\{\{\s*key\s*\}\}\s*$")
# Markdown-inline escapes the earlier raw-HTML rewrite inserted.
_MD_UNESCAPE_RE = re.compile(r"\\([\\`*_\[\]{}])")
_BR_RE = re.compile(r"<br\s*/?>", re.I)
# Inline code as the entire text node: `cmd`.
_INLINE_CODE_RE = re.compile(r"^\s*`([^`]*)`\s*$")
# The classifier text that sits to the right of an Object Reference title:
# Property, Object, Event 33, Method 838, Example 3a.
_RIGHT_RE = re.compile(r"^(?:Property|Object|Method|Event|Example)(?:\s+\d+[a-z]?)?$")

KEY_TARGET = "language-reference-guide/key-to-notation.md"
KEY_LINK_TEXT = "Key to notation"


def normalise_titles(text, key_link=None):
    """Rewrite styled title headings to plain Markdown.

    The corpus writes page titles as an h1 carrying styling spans, in two
    generations: the pre-July raw-HTML form the h1 rewrite turns into
    `# <span class="name">N</span> <span class="command">C</span> {: .heading}`,
    and today's `# <span>N</span> \\`C\\`{{key}}` / `# <span>N</span> <span>R</span>`.
    Both become a plain `# N`, with the calling syntax C in an ```apl block
    directly below and a classifier R (Property, Event 33, ...) as a plain
    line, so the title reads cleanly in search results, the nav and screen
    readers. Any other attr_list tokens (an explicit `#id`) are kept; the
    `.heading` class is dropped. A nested command span inside the name becomes
    inline code (`# \\`⎕NA\\` under UNIX`).

    The `{{key}}` macro (an icon link to the notation key, drawn white for the
    old title banner) is replaced by a text link to key_link, the relative path
    to that page from the current one; without key_link the macro is dropped.

    Headings that do not carry title markup are left untouched, as is every
    line that is not an h1. A rewritten title is always followed by a blank
    line, so a syntax block never runs straight into the first paragraph.
    """
    return _expand_prose_lines(text, lambda line: _normalise_title_line(line, key_link))


def _normalise_title_line(line, key_link):
    """The replacement block for a styled title line, or None to keep it."""
    if not line.startswith("# "):
        return None
    body = line[2:]
    if not any(marker in body for marker in ("<span", "<code", "{{", "{:", "`")):
        return None

    attrs = []
    match = _ATTR_LIST_RE.search(body)
    if match:
        attrs = [token for token in match.group(1).split() if token != ".heading"]
        body = body[: match.start()]
    has_key = False
    match = _KEY_RE.search(body)
    if match:
        has_key = True
        body = body[: match.start()]

    parsed = _split_title(body)
    if parsed is None:
        return None
    name, command, right = parsed

    title = f"# {name}"
    if attrs:
        title += " {: " + " ".join(attrs) + "}"
    lines = [title]
    if command:
        lines += ["", "```apl", *command, "```"]
    elif right:
        lines += ["", right]
    if has_key and key_link:
        lines.append(f"[{KEY_LINK_TEXT}]({key_link})")
    return "\n".join(lines)


def _split_title(body):
    """Parse a title's markup into (name, command_lines, right).

    Returns None when the body does not have a recognised title shape, so the
    caller leaves the heading alone.
    """
    if "<" not in body and "`" not in body:
        return None
    soup = BeautifulSoup(body, "html.parser")
    # The pre-July form reaches here via rewrite_h1, which escaped Markdown
    # specials in the span text. The name stays as it is (the escapes are
    # valid heading Markdown); the command is unescaped because it moves into
    # a code block, where escapes would be literal. Today's form is literal
    # already (inline code is never escape-processed), so it is not touched.
    legacy = soup.find("span", class_="name") is not None
    name = command = right = None
    bare_spans = 0
    for node in soup.contents:
        if isinstance(node, NavigableString):
            text = str(node)
            if not text.strip():
                continue
            code = _INLINE_CODE_RE.match(text)
            if code and command is None and name is not None:
                command = code.group(1)
                continue
            return None
        if not isinstance(node, Tag):
            continue
        classes = node.get("class", [])
        if node.name == "span" and "name" in classes:
            name = _name_text(node)
        elif node.name == "span" and "command" in classes:
            command = _command_text(node)
        elif node.name == "span" and "right" in classes:
            right = node.get_text().strip()
        elif node.name == "span" and not classes:
            bare_spans += 1
            if bare_spans == 1:
                name = _name_text(node)
            elif bare_spans == 2 and command is None:
                right = node.get_text().strip()
            else:
                return None
        elif node.name == "code":
            command = _command_text(node)
        else:
            return None
    if name is None:
        return None
    if isinstance(command, str):
        command = _command_lines(command, legacy)
    if command and len(command) == 1 and _RIGHT_RE.match(command[0]) and right is None:
        right, command = command[0], None
    return name, command, right


def _name_text(node):
    """The title text of a name span as heading Markdown: its inner markup
    verbatim (entities and escapes included), with a nested command span
    rendered as inline code."""
    for child in node.find_all("span"):
        if "command" in child.get("class", []):
            child.replace_with(NavigableString(f"`{child.get_text()}`"))
    return node.decode_contents().strip()


def _command_text(node):
    for br in node.find_all("br"):
        br.replace_with("\n")
    return node.get_text()


def _command_lines(text, legacy):
    text = _BR_RE.sub("\n", text)
    if legacy:
        text = _MD_UNESCAPE_RE.sub(r"\1", text)
    return [line.strip() for line in text.split("\n") if line.strip()]


def key_link_for(page_rel_path):
    """Relative link from the page at page_rel_path (POSIX, relative to docs/)
    to the key-to-notation page."""
    return relative_to_page(page_rel_path, KEY_TARGET)


def relative_to_page(page_rel_path, target_rel_path):
    """Relative POSIX path from the directory of page_rel_path to
    target_rel_path, both given relative to the docs root."""
    page_dir = posixpath.dirname(page_rel_path) or "."
    return posixpath.relpath(target_rel_path, page_dir)


# --- example headings --------------------------------------------------

_EXAMPLE_HEADING_RE = re.compile(r"^\s*<h([1-6]) class=\"example\">(.*?)</h\1>\s*$")
# A paragraph label, or the corpus's one malformed heading (`<h*>`).
_EXAMPLE_LABEL_RE = re.compile(r"^\s*<(p|h\*) class=\"example\">(.*?)</\1>\s*$")


def rewrite_example_headings(text):
    """Turn `<hN class="example">Text</hN>` into a real `##...` heading and
    `<p class="example">Text</p>` into a bold `**Text**` label.

    Real headings get anchors and appear in the on-page table of contents. An
    `<h1 class="example">` is demoted to `##`: the page already has its title
    h1, and a second one would be read as a second title. A bold label is
    followed by a blank line so that the code block it introduces is not
    parsed as part of its paragraph.
    """

    def heading(line):
        match = _EXAMPLE_HEADING_RE.match(line)
        if match:
            level = max(2, int(match.group(1)))
            return f"{'#' * level} {match.group(2).strip()}"
        return line

    def label(line):
        match = _EXAMPLE_LABEL_RE.match(line)
        return f"**{match.group(2).strip()}**" if match else None

    return _expand_prose_lines(
        _map_prose_lines(text, heading), label, always_blank_after=True
    )


# --- admonitions -------------------------------------------------------

# Corpus admonition types the theme does not ship, mapped to the stock type
# that carries the same meaning. The OS-specific types collapse to info: their
# titles already name the operating system.
ADMONITION_TYPES = {
    "hint": "tip",
    "legacy": "note",
    "windows": "info",
    "unix": "info",
    "linux": "info",
    "macos": "info",
}

# The type token follows the marker; an admonition may itself sit in a list.
_ADMONITION_RE = re.compile(r"^(\s*(?:[-*+]\s+)?(?:!!!|\?\?\?\+?)\s+)(\S+)(.*)$")


def normalise_admonitions(text):
    """Map the corpus's bespoke admonition types onto the theme's stock set."""

    def rewrite(line):
        match = _ADMONITION_RE.match(line)
        if not match:
            return line
        kind = ADMONITION_TYPES.get(match.group(2).lower())
        if kind is None:
            return line
        return f"{match.group(1)}{kind}{match.group(3)}"

    return _map_prose_lines(text, rewrite)


# --- shaded default markers --------------------------------------------

# A table cell whose value is marked as the default by shading:
# `|0 { .shaded } |`, `|`1` {: .shaded}|`, `| `0` {.shaded} |`.
_SHADED_CELL_RE = re.compile(r"\|([^|{]*?)\s*\{:?\s*\.shaded\s*\}\s*(?=\|)")
# The sentence that explained the shading, in its several spellings.
_SHADED_LEGEND_RE = re.compile(
    r"\s*Default values are highlighted\s*(?:<span class=\"shaded\">\s*)?thus"
    r"(?:\s*</span>)?\s*(?:\{:?\s*\.shaded\s*\})?\s*(?:in the (?:above )?tables?)?\."
)


def replace_shaded_defaults(text):
    """Say "(default)" in text instead of shading the default value's cell.

    `|0 { .shaded } |` becomes `` |`0` (default)| ``; the "Default values are
    highlighted thus" legend is removed (dropping its line, and one adjacent
    blank line, when nothing else was on it).
    """

    def cell(match):
        value = match.group(1).strip().strip("`").strip()
        return f"|`{value}` (default)"

    def block(prose):
        lines = prose.split("\n")
        out = []
        for line in lines:
            if line.lstrip().startswith("|"):
                line = _SHADED_CELL_RE.sub(cell, line)
            if _SHADED_LEGEND_RE.search(line):
                line = _SHADED_LEGEND_RE.sub("", line)
                if not line.strip():
                    if out and not out[-1].strip():
                        out.pop()
                    continue
            out.append(line)
        return "\n".join(out)

    return _map_prose_blocks(text, block)


# --- raw-HTML table layout classes -------------------------------------

_FLEX_PAIR_RE = re.compile(
    r"<div class=\"flex-between\">\s*<span class=\"text-left\">(.*?)</span>"
    r"\s*<span class=\"text-right\">(.*?)</span>\s*</div>",
    re.S,
)
_FLEX_EMPTY_RE = re.compile(
    r"<div class=\"flex-between\">\s*<span>(&#160;|&nbsp;)</span>"
    r"\s*<span>(?:&#160;|&nbsp;)</span>\s*</div>",
    re.S,
)
_LAYOUT_CLASS_RE = re.compile(
    r" class=\"(?:table-bordered|no-border|rowspan|text-left|text-right)\""
)


def simplify_table_markup(text):
    """Drop the house layout classes from raw-HTML tables.

    The binding-strength table's `flex-between` cells (a strength on the left,
    a result on the right) collapse to `strength: result` text; the
    `table-bordered`/`no-border`/`rowspan`/`text-left`/`text-right` classes
    go, leaving the theme's own table styling. The glyph tables'
    `class="Dyalog"` becomes `class="apl"`, the one APL-font class the
    stylesheet keeps.
    """

    def block(prose):
        prose = _FLEX_PAIR_RE.sub(lambda m: f"{m.group(1)}: {m.group(2)}", prose)
        prose = _FLEX_EMPTY_RE.sub(r"\1", prose)
        prose = _LAYOUT_CLASS_RE.sub("", prose)
        return prose.replace('class="Dyalog"', 'class="apl"')

    return _map_prose_blocks(text, block)


# --- toolbar icon sprites ----------------------------------------------

# The Tracer toolbar sprite (trace-theme-sprite-16.png in the old assets),
# by background-position offset: (image slug, button name). Each slice is a
# content-owned image under windows-ui-guide/img/tbt-<slug>.png.
TOOLBAR_ICONS = {
    0: ("back", "Back"),
    -16: ("fwd", "Fwd"),
    -32: ("exit", "Exit"),
    -48: ("edit", "Edit"),
    -64: ("exec", "Exec"),
    -80: ("trace", "Trace"),
    -96: ("continue", "Continue"),
    -112: ("restart", "Restart"),
    -128: ("intr", "Intr"),
    -144: ("reset", "Reset"),
    -160: ("restart-all", "Restart all"),
    -224: ("toggle-line-numbers", "Toggle line numbers"),
    -240: ("search-for-previous-match", "Search for previous match"),
    -256: ("search-for-next-match", "Search for next match"),
    -272: ("search-hidden-text", "Search hidden text"),
    -336: ("match-case", "Match case"),
    -352: ("match-whole-word", "Match whole word"),
    -368: ("use-regular-expressions", "Use Regular Expressions"),
    -432: ("inline-trace", "Inline Trace"),
}
TOOLBAR_IMG_DIR = "windows-ui-guide/img"

# The first icon sits at "0 0", every other at "-Npx 0".
_ICON_SPAN_RE = re.compile(
    r"<span class=\"toolbar-icon\" style=\"background-position: (-?\d+)(?:px)? 0\"></span>"
)
# A bold label immediately preceding the icon on its line names it in prose:
# "click the **Next Primitive** icon <span ...>".
_PRECEDING_LABEL_RE = re.compile(r"\*\*([^*]+)\*\*[^*]*$")


def replace_toolbar_icons(text, img_dir_rel):
    """Replace sprite-sheet icon spans with real images carrying alt text.

    img_dir_rel is the relative path from the page's directory to
    windows-ui-guide/img. Returns (text, slugs): the rewritten text and the
    set of image slugs it now references, so the caller can check each
    tbt-<slug>.png is actually provided. An unknown sprite offset is an error:
    silently keeping the span would publish an invisible icon.
    """
    used = set()

    def rewrite(line):
        def icon(match):
            offset = int(match.group(1))
            if offset not in TOOLBAR_ICONS:
                raise ValueError(f"unknown toolbar sprite offset {offset}px in: {line!r}")
            slug, alt = TOOLBAR_ICONS[offset]
            label = _PRECEDING_LABEL_RE.search(line[: match.start()])
            if label:
                alt = label.group(1)
            used.add(slug)
            return f"![{alt} toolbar button]({img_dir_rel}/tbt-{slug}.png)"

        return _ICON_SPAN_RE.sub(icon, line)

    return _map_prose_lines(text, rewrite), used

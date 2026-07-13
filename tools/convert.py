"""Out-of-place conversion of the Dyalog MkDocs monorepo to this repository.

Reads the monorepo source (read-only) and regenerates this repository's
content and build config:

- copies each sub-project's docs tree to docs/<sub>/, byte-identical,
  preserving the directory-name-equals-mount-point invariant so every
  public URL and relative link survives the flatten,
- copies the root project's docs and the documentation-assets tree,
- consolidates the identical per-sub-project mathjax.js copies into the
  single canonical docs/javascripts/mathjax.js,
- merges the root config and the 14 sub-project configs into one config:
  each "!include ./<sub>/mkdocs.yml" nav entry replaced by that
  sub-project's nav path-prefixed with <sub>/, extensions and extra
  folded into a superset with the root value winning any conflict, and
  extra_css taken from the root alone (the monorepo build reads only the
  root values, so root-wins preserves the rendered baseline; the corpus's
  only sub-only extra_css entries dangle),
- serialises the merged config to zensical.toml, the sole build config.
  The monorepo, site-urls and caption plugins are dropped: the first two
  are retired by the flatten, and caption has no Zensical module and is
  replaced by a Python-Markdown extension in Phase 5.

The source tree is never written to. The output directory is this
repository's zensical/ directory, a self-contained generated project
(zensical.toml and docs/ together) that the script owns wholesale: it is
regenerated from source on every run, so orphaned and stray files do not
survive. Nothing outside zensical/ is ever written.

Forward-looking by design: it reads MkDocs config and writes Zensical
config, with no MkDocs fallback or backwards-compatibility path.

The sub-project list and both filesystem roots are hardcoded (no CLI
arguments): the source monorepo is expected as a sibling checkout of this
repository named "documentation". Functions take explicit paths so tests
can drive them against fixture trees.
"""

import copy
import re
import shutil
from pathlib import Path

import tomli_w
import yaml
from bs4 import BeautifulSoup, NavigableString

# The 14 sub-projects, in root-nav order. The root nav's !include lines are
# the canonical enumeration; a source checkout missing any of these is an
# error, not a partial conversion.
SUBPROJECTS: tuple[str, ...] = (
    "release-notes",
    "earlier-release-notes",
    "language-reference-guide",
    "programming-reference-guide",
    "dotnet-interface-guide",
    "compiler-user-guide",
    "shared-code-files-user-guide",
    "windows-installation-and-configuration-guide",
    "windows-ui-guide",
    "object-reference",
    "interface-guide",
    "dotnet-framework-interface-guide",
    "unix-installation-and-configuration-guide",
    "unix-user-guide",
)

# The generated project directory inside this repository, and the sibling
# monorepo checkout it is generated from.
OUTPUT_ROOT = Path(__file__).resolve().parent.parent / "zensical"
SOURCE_ROOT = Path(__file__).resolve().parent.parent.parent / "documentation"

ASSETS_DIR = "documentation-assets"
MATHJAX_REL = Path("javascripts") / "mathjax.js"

# Dropped from the merged config. monorepo has done its job; site-urls is a
# no-op for this corpus (nothing uses its site: prefix); caption has no
# Zensical module and is replaced by a Python-Markdown extension in Phase 5.
DROPPED_PLUGINS = frozenset({"monorepo", "site-urls", "caption"})

# The Python-Markdown extension that replaces the dropped caption plugin. Named
# by importable module so Zensical hands it to Python-Markdown at build time.
CAPTION_EXTENSION = "dyalog_caption"

_INCLUDE_RE = re.compile(r"^!include \./([^/]+)/mkdocs\.yml$")

# Opening/closing fence marker (3+ backticks or tildes), optionally indented.
_FENCE_RE = re.compile(r"^\s*(`{3,}|~{3,})")
# Markdown-inline-special characters to escape in heading text so content such
# as APL command signatures survives the inline parser verbatim.
_MD_SPECIAL_RE = re.compile(r"[\\`*_\[\]{}]")


def load_yaml(path):
    """Parse a mkdocs.yml, tolerating the monorepo's !include tags by
    loading them as plain strings."""
    with open(path) as f:
        return yaml.safe_load(f)


def _entry_name(entry):
    """The name of a plugins/markdown_extensions list entry: either the
    string itself or the single key of a {name: config} mapping."""
    return entry if isinstance(entry, str) else next(iter(entry))


def prefix_nav(nav, prefix):
    """Return nav with every page path prefixed by "<prefix>/".

    Recurses into sections (dicts and lists); leaves absolute URLs
    untouched. Titles are preserved.
    """
    if isinstance(nav, str):
        return nav if "://" in nav else f"{prefix}/{nav}"
    if isinstance(nav, list):
        return [prefix_nav(entry, prefix) for entry in nav]
    if isinstance(nav, dict):
        return {title: prefix_nav(value, prefix) for title, value in nav.items()}
    return nav


def _replace_includes(nav, sub_configs):
    """Replace "!include ./<sub>/mkdocs.yml" strings with that
    sub-project's nav, path-prefixed with <sub>/."""
    if isinstance(nav, str):
        match = _INCLUDE_RE.match(nav)
        if match:
            name = match.group(1)
            if name not in sub_configs:
                raise ValueError(
                    f"root nav includes a sub-project outside the"
                    f" hardcoded list: {name}"
                )
            return prefix_nav(sub_configs[name]["nav"], name)
        return nav
    if isinstance(nav, list):
        return [_replace_includes(entry, sub_configs) for entry in nav]
    if isinstance(nav, dict):
        return {
            title: _replace_includes(value, sub_configs) for title, value in nav.items()
        }
    return nav


def merge_configs(root_config, sub_configs):
    """Merge the root config and the ordered {name: config} sub-configs.

    Nav: each "!include ./<name>/mkdocs.yml" string is replaced by that
    sub-project's nav, path-prefixed with "<name>/". markdown_extensions
    and extra fold into a superset, root value winning conflicts.
    extra_css comes from the root alone: the monorepo build ignores sub
    extra_css, and the corpus's only sub-only entries dangle (no such
    files in source), so folding them in would break the rendered
    baseline. extra_javascript and the rest of the top-level keys are
    inherited from the root unchanged (the root already references the
    single javascripts/mathjax.js plus the external MathJax URL). The
    monorepo, site-urls and caption plugins are dropped.
    """
    merged = copy.deepcopy(root_config)

    merged["nav"] = _replace_includes(merged.get("nav", []), sub_configs)

    extensions = copy.deepcopy(root_config.get("markdown_extensions", []))
    seen = {_entry_name(e) for e in extensions}
    for sub in sub_configs.values():
        for entry in sub.get("markdown_extensions", []):
            if _entry_name(entry) not in seen:
                extensions.append(copy.deepcopy(entry))
                seen.add(_entry_name(entry))
    # Restore the caption numbering the dropped caption plugin provided, as a
    # Python-Markdown extension Zensical can load (see tools/dyalog_caption.py).
    if CAPTION_EXTENSION not in seen:
        extensions.append(CAPTION_EXTENSION)
    merged["markdown_extensions"] = extensions

    extra = {}
    for sub in sub_configs.values():
        extra.update(copy.deepcopy(sub.get("extra", {})))
    extra.update(copy.deepcopy(root_config.get("extra", {})))
    merged["extra"] = extra

    merged["plugins"] = [
        plugin
        for plugin in merged.get("plugins", [])
        if _entry_name(plugin) not in DROPPED_PLUGINS
    ]

    return merged


def rewrite_h1(md_text):
    """Rewrite raw-HTML page-title headings to Markdown ATX headings.

    The corpus writes page titles as raw HTML (`<h1 class="heading">` with
    inner styling spans) via md_in_html, so neither MkDocs nor Zensical sees
    an ATX heading and both fall back for the page title: MkDocs to the nav
    label, Zensical to the filename. Converting each raw `<h1 ...>INNER</h1>`
    to `# INNER {: attrs}` gives Zensical a heading whose text becomes the
    title, while attr_list carries the original attributes so the class and
    inner spans (hence the styling) survive.

    Markdown-special characters in INNER are escaped so command headings
    containing APL (e.g. `R<-f\\[K]Y`) render verbatim rather than being
    mangled by the inline parser. Raw `<h1>` inside fenced code blocks is
    left alone: it is example text, not a page title.

    Returns the text unchanged when it contains no raw `<h1>`.
    """
    if "<h1" not in md_text:
        return md_text

    lines = md_text.split("\n")
    fence = None
    for i, line in enumerate(lines):
        marker = _FENCE_RE.match(line)
        if fence is None:
            if marker:
                fence = marker.group(1)[0]
            elif _is_standalone_h1(line):
                lines[i] = _rewrite_h1_line(line)
        elif marker and marker.group(1)[0] == fence:
            fence = None
    return "\n".join(lines)


def _is_standalone_h1(line):
    """True when the whole line is a single raw <h1>...</h1> element.

    An <h1> that shares its line with other content is not a page title and is
    left alone: the corpus has an HTML sample `<body><h1>Simple Form</h1>`
    (ends with </h1> but does not start with <h1) and an APL string literal
    building HTML (does neither). <h1> inside fenced code is excluded
    separately, by the caller's fence tracking.
    """
    stripped = line.strip()
    return stripped.startswith("<h1") and stripped.endswith("</h1>")


def _rewrite_h1_line(line):
    """Turn a standalone `<h1 ...>...</h1>` line into `# INNER {: attrs}`,
    parsed with BeautifulSoup so the styling spans survive verbatim and the
    attributes are read structurally, not by regex."""
    h1 = BeautifulSoup(line, "html.parser").find("h1")
    # Escape Markdown specials in every text node (including inside the spans),
    # so APL command text is not consumed by the heading's inline parser.
    for text in list(h1.find_all(string=True)):
        text.replace_with(NavigableString(_escape_md(str(text))))
    inner = h1.decode_contents().strip()
    attrs = _h1_attr_list(h1.attrs)
    suffix = f" {{: {attrs}}}" if attrs else ""
    return f"# {inner}{suffix}"


def _escape_md(text):
    return _MD_SPECIAL_RE.sub(lambda m: "\\" + m.group(0), text)


def _h1_attr_list(attrs):
    """Render an h1's parsed attributes as an attr_list body: id as #id,
    classes as .class, anything else as key="value"."""
    tokens = []
    if "id" in attrs:
        tokens.append(f"#{attrs['id']}")
    tokens += [f".{cls}" for cls in attrs.get("class", [])]
    for key, value in attrs.items():
        if key not in ("id", "class"):
            tokens.append(f'{key}="{value}"')
    return " ".join(tokens)


def copy_content(source, output, subprojects):
    """Copy content out-of-place from the source monorepo to the output.

    <sub>/docs/* copies to <output>/docs/<sub>/* for every sub-project;
    root docs/* to <output>/docs/*; documentation-assets/ to
    <output>/docs/documentation-assets/. Per-sub-project
    docs/javascripts/mathjax.js duplicates are not carried over; the root
    copy becomes the single canonical one. VCS metadata is not carried
    over: documentation-assets is a submodule in the source, so its .git
    gitlink is excluded rather than dragged into the content tree. Content
    bytes are never edited. The output directory is owned wholesale and
    regenerated from source, so orphaned and stray files do not survive a
    re-run. The source tree is never written to.
    """
    source = Path(source)
    output = Path(output)

    ignore_vcs = shutil.ignore_patterns(".git")

    if output.exists():
        shutil.rmtree(output)
    docs = output / "docs"

    shutil.copytree(source / "docs", docs, ignore=ignore_vcs)
    shutil.copytree(source / ASSETS_DIR, docs / ASSETS_DIR, ignore=ignore_vcs)

    for name in subprojects:
        shutil.copytree(source / name / "docs", docs / name, ignore=ignore_vcs)
        duplicate = docs / name / MATHJAX_REL
        if duplicate.exists():
            duplicate.unlink()
            if not any(duplicate.parent.iterdir()):
                duplicate.parent.rmdir()

    # Convert raw-HTML page-title headings to Markdown in the copied files, so
    # Zensical derives the title from the heading text. The source is untouched;
    # files without a raw <h1> are left byte-for-byte as copied.
    for md_file in docs.rglob("*.md"):
        text = md_file.read_text(encoding="utf-8")
        rewritten = rewrite_h1(text)
        if rewritten != text:
            md_file.write_text(rewritten, encoding="utf-8")


def write_zensical_toml(config, path):
    """Serialise the merged config as zensical.toml under [project].

    Plugin exclusions are already applied by merge_configs; this only wraps
    the merged config in the [project] table Zensical expects.
    """
    with open(path, "wb") as f:
        tomli_w.dump({"project": config}, f)


def convert(source, output, subprojects=SUBPROJECTS):
    """Run the full conversion: copy content, merge configs, serialise.

    Deterministic and idempotent: converting the same source twice
    produces byte-identical output. Raises FileNotFoundError naming the
    sub-projects missing from the source.
    """
    source = Path(source)
    output = Path(output)

    missing = [
        name
        for name in subprojects
        if not (source / name / "mkdocs.yml").is_file()
        or not (source / name / "docs").is_dir()
    ]
    if missing:
        raise FileNotFoundError(
            f"sub-projects missing from {source}: {', '.join(missing)}"
        )

    root_config = load_yaml(source / "mkdocs.yml")
    sub_configs = {
        name: load_yaml(source / name / "mkdocs.yml") for name in subprojects
    }
    merged = merge_configs(root_config, sub_configs)

    copy_content(source, output, subprojects)
    write_zensical_toml(merged, output / "zensical.toml")


if __name__ == "__main__":
    convert(SOURCE_ROOT, OUTPUT_ROOT)

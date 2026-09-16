"""Out-of-place conversion of the Dyalog MkDocs monorepo to this repository.

Reads the monorepo source (read-only) and regenerates this repository's
content and build config:

- copies each sub-project's docs tree to docs/<alias>/, where <alias> is the
  mount point mkdocs-monorepo-plugin gave it on the live site (its site_name,
  slugified: twelve guides' aliases equal their directory names, the two .NET
  guides' do not), so every public URL and cross-guide relative link survives
  the flatten; and the root project's docs to docs/,
- applies the content transforms in transforms.py to every copied Markdown
  page, so the house classes the MkDocs stylesheet styled (title banners,
  example headings, shaded default cells, sprite toolbar icons, the
  binding-strength layout classes, bespoke admonition types) are replaced by
  plain Markdown that stock Zensical renders,
- lays the content overlay (tools/content/) over the copied tree: images the
  transforms reference that have no source in the monorepo, and whole-page
  replacements for the few pages that were reworked by hand. A replacement
  carries a sidecar recording the SHA-256 of the source page it was written
  against; the conversion refuses to run while a sidecar no longer matches,
  so an upstream edit to such a page is never silently discarded,
- drops the MathJax loader: nothing in the corpus uses arithmatex, and the
  per-sub-project mathjax.js copies are not carried over,
- merges the root config and the 14 sub-project configs: each
  "!include ./<sub>/mkdocs.yml" nav entry replaced by that sub-project's nav
  path-prefixed with <sub>/, markdown_extensions folded into a superset
  (minus arithmatex, plus the caption extension), extra folded with the root
  winning conflicts,
- renders zensical.toml from tools/zensical.toml.template, which holds the
  house configuration (theme, palette, stylesheet, plugins, copyright) with
  its rationale in comments, and receives the merged site name, repository
  URL, extensions, extra and nav.

The source tree is never written to. The output directory is this
repository's zensical/ directory, a self-contained generated project
(zensical.toml and docs/ together). The script owns everything under it
except the two asset directories under docs/ (documentation-assets, the
retired MkDocs submodule, and documentation-assetsz, the Zensical assets):
it regenerates the owned paths on every run, so orphaned and stray files do
not survive, while leaving the assets intact. Nothing outside zensical/ is
ever written.

Forward-looking by design: it reads MkDocs config and writes Zensical
config, with no MkDocs fallback or backwards-compatibility path.

The sub-project list and both filesystem roots are hardcoded (no CLI
arguments): the source monorepo is expected as a sibling checkout of this
repository named "documentation". Functions take explicit paths so tests
can drive them against fixture trees.
"""

import copy
import hashlib
import re
import shutil
from pathlib import Path, PurePosixPath

import tomli_w
import yaml
from bs4 import BeautifulSoup, NavigableString

import transforms

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

TOOLS_DIR = Path(__file__).resolve().parent

# The generated project directory inside this repository, and the sibling
# monorepo checkout it is generated from.
OUTPUT_ROOT = TOOLS_DIR.parent / "zensical"
SOURCE_ROOT = TOOLS_DIR.parent.parent / "documentation"

# Asset directories under docs/ that convert does not own: the retired MkDocs
# style (a git submodule, kept until its removal is done as its own change)
# and the Zensical style the build actually reads.
PRESERVED_DIRS = frozenset({"documentation-assets", "documentation-assetsz"})

# The MathJax loader the monorepo carried in every sub-project. Nothing in the
# corpus renders maths, so no copy is carried over.
MATHJAX_REL = Path("javascripts") / "mathjax.js"

# Theme override providing the outdated-version warning banner. Kept in a
# top-level overrides/ (not under docs/, where it would be published as a stray
# static file) and pointed at by theme.custom_dir. The template is a committed
# project artefact, copied into the generated project.
OVERRIDES_DIR = "overrides"
OVERRIDE_TEMPLATE = TOOLS_DIR / OVERRIDES_DIR / "main.html"

# The house build configuration with the generated regions as placeholders.
TOML_TEMPLATE = TOOLS_DIR / "zensical.toml.template"

# Content the transforms need that has no source in the monorepo, plus the
# hand-reworked page replacements with their source-hash sidecars.
CONTENT_OVERLAY = TOOLS_DIR / "content"
SIDECAR_SUFFIX = ".source-sha256"

# Dropped from the merged markdown_extensions: arithmatex has no content to
# render (the only `$$` in the corpus is APL output), and dropping it lets the
# MathJax loader go too.
DROPPED_EXTENSIONS = frozenset({"pymdownx.arithmatex"})

# The Python-Markdown extension that replaces the monorepo's caption plugin.
# Named by importable module so Zensical hands it to Python-Markdown at build
# time.
CAPTION_EXTENSION = "dyalog_caption"

# Root config keys carried into the rendered zensical.toml header.
CARRIED_KEYS = ("site_name", "repo_url")

_INCLUDE_RE = re.compile(r"^!include \./([^/]+)/mkdocs\.yml$")

# mkdocs-monorepo-plugin mounts an included project at an alias derived from
# its site_name: the name itself when it is already a plain path token,
# otherwise its slug (python-slugify). ".NET Interface Guide" is therefore
# served at net-interface-guide/, not at its directory dotnet-interface-guide/.
_PLAIN_ALIAS_RE = re.compile(r"^[a-zA-Z0-9_.\-/]+$")


def guide_alias(site_name):
    """The URL path segment mkdocs-monorepo-plugin mounts a guide at."""
    if _PLAIN_ALIAS_RE.fullmatch(site_name):
        return site_name
    return re.sub(r"[^a-z0-9]+", "-", site_name.lower()).strip("-")


def _alias_of(name, config):
    return guide_alias(config.get("site_name", name))


def mount_points(sub_configs):
    """{alias: directory} for the ordered {directory: config} sub-configs,
    the geometry the output docs/ tree takes. Two guides resolving to one
    alias would overwrite each other, so that is an error."""
    mounts = {}
    for name, config in sub_configs.items():
        alias = _alias_of(name, config)
        if alias in mounts:
            raise ValueError(f"sub-projects {mounts[alias]} and {name} both mount at {alias}/")
        mounts[alias] = name
    return mounts

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
    sub-project's nav, path-prefixed with its mount alias."""
    if isinstance(nav, str):
        match = _INCLUDE_RE.match(nav)
        if match:
            name = match.group(1)
            if name not in sub_configs:
                raise ValueError(
                    f"root nav includes a sub-project outside the"
                    f" hardcoded list: {name}"
                )
            return prefix_nav(sub_configs[name]["nav"], _alias_of(name, sub_configs[name]))
        return nav
    if isinstance(nav, list):
        return [_replace_includes(entry, sub_configs) for entry in nav]
    if isinstance(nav, dict):
        return {
            title: _replace_includes(value, sub_configs) for title, value in nav.items()
        }
    return nav


def merge_configs(root_config, sub_configs):
    """Merge the root config and the ordered {name: config} sub-configs into
    the values the rendered zensical.toml takes from the source.

    Nav: each "!include ./<name>/mkdocs.yml" string is replaced by that
    sub-project's nav, path-prefixed with its mount alias. markdown_extensions
    fold into a superset with root precedence, minus DROPPED_EXTENSIONS and
    plus the caption extension. extra folds with the root winning conflicts.
    site_name and repo_url come from the root. Everything else in the source
    configs (theme, stylesheets, scripts, plugins, copyright) is MkDocs house
    configuration that the template replaces, so it is not carried.
    """
    merged = {key: root_config[key] for key in CARRIED_KEYS if key in root_config}

    merged["nav"] = _replace_includes(copy.deepcopy(root_config.get("nav", [])), sub_configs)

    extensions = copy.deepcopy(root_config.get("markdown_extensions", []))
    seen = {_entry_name(e) for e in extensions}
    for sub in sub_configs.values():
        for entry in sub.get("markdown_extensions", []):
            if _entry_name(entry) not in seen:
                extensions.append(copy.deepcopy(entry))
                seen.add(_entry_name(entry))
    extensions = [e for e in extensions if _entry_name(e) not in DROPPED_EXTENSIONS]
    # Restore the caption numbering the monorepo's caption plugin provided, as a
    # Python-Markdown extension Zensical can load (see tools/dyalog_caption.py).
    if CAPTION_EXTENSION not in seen:
        extensions.append(CAPTION_EXTENSION)
    merged["markdown_extensions"] = extensions

    extra = {}
    for sub in sub_configs.values():
        extra.update(copy.deepcopy(sub.get("extra", {})))
    extra.update(copy.deepcopy(root_config.get("extra", {})))
    merged["extra"] = extra

    return merged


def rewrite_h1(md_text):
    """Rewrite raw-HTML page-title headings to Markdown ATX headings.

    The pre-July corpus wrote page titles as raw HTML (`<h1 class="heading">`
    with inner styling spans) via md_in_html, so neither MkDocs nor Zensical
    saw an ATX heading. Converting each raw `<h1 ...>INNER</h1>` to
    `# INNER {: attrs}` gives a heading whose text becomes the title, while
    attr_list carries the original attributes; transforms.normalise_titles
    then reduces the spans to plain Markdown. The monorepo has since made the
    same move itself, so this now only catches stragglers.

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


def transform_markdown(text, page_rel_path):
    """Run the content transform pipeline over one page's Markdown.

    page_rel_path is the page's POSIX path relative to docs/, used to compute
    the relative links the transforms emit. Returns (text, icon_slugs): the
    transformed text and the toolbar icon images it references.
    """
    page_rel_path = PurePosixPath(page_rel_path).as_posix()
    text = transforms.rewrite_example_headings(text)
    text = rewrite_h1(text)
    text = transforms.normalise_titles(text, key_link=transforms.key_link_for(page_rel_path))
    text = transforms.normalise_admonitions(text)
    text = transforms.replace_shaded_defaults(text)
    text = transforms.simplify_table_markup(text)
    img_dir = transforms.relative_to_page(page_rel_path, transforms.TOOLBAR_IMG_DIR)
    return transforms.replace_toolbar_icons(text, img_dir)


def _remove(path):
    if path.is_dir() and not path.is_symlink():
        shutil.rmtree(path)
    else:
        path.unlink()


def _clean_owned(output, preserved):
    """Wipe convert-owned paths under the output, keeping docs/ and the
    preserved asset directories (docs/ children) intact, so a re-run is
    deterministic without disturbing the assets."""
    if not output.exists():
        return
    docs = output / "docs"
    for entry in output.iterdir():
        if entry == docs and docs.is_dir():
            for child in docs.iterdir():
                if child.name not in preserved:
                    _remove(child)
        else:
            _remove(entry)


def source_path_for(rel, source, mounts):
    """The source file a docs/-relative output path was copied from, given
    the {alias: directory} mount points."""
    rel = Path(rel)
    if rel.parts and rel.parts[0] in mounts:
        return Path(source) / mounts[rel.parts[0]] / "docs" / Path(*rel.parts[1:])
    return Path(source) / "docs" / rel


def _sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def overlay_files(overlay):
    """The overlay's content files (sidecars excluded), as paths relative to
    the overlay root."""
    overlay = Path(overlay)
    if not overlay.is_dir():
        return []
    return sorted(
        p.relative_to(overlay)
        for p in overlay.rglob("*")
        if p.is_file() and not p.name.endswith(SIDECAR_SUFFIX)
    )


def check_overlay(overlay, source, mounts):
    """Verify the overlay against the source before anything is written.

    Every overlay file that would replace a source page must carry a sidecar
    naming the SHA-256 of that source page, and the hash must still match;
    otherwise the page changed upstream since the replacement was written
    and the two must be re-merged by hand. Raises ValueError listing every
    offending file.
    """
    overlay = Path(overlay)
    problems = []
    for rel in overlay_files(overlay):
        sidecar = overlay / (str(rel) + SIDECAR_SUFFIX)
        src = source_path_for(rel, source, mounts)
        if src.is_file():
            if not sidecar.is_file():
                problems.append(f"{rel}: replaces a source page but has no {SIDECAR_SUFFIX} sidecar")
            elif sidecar.read_text().strip() != _sha256(src):
                problems.append(
                    f"{rel}: source page changed since the replacement was written"
                    f" (re-merge, then update {sidecar.name})"
                )
        elif sidecar.is_file():
            problems.append(f"{rel}: has a sidecar but its source page no longer exists")
    if problems:
        raise ValueError("content overlay is stale:\n  " + "\n  ".join(problems))


def apply_overlay(overlay, docs):
    """Copy the overlay's content files over the docs tree."""
    overlay = Path(overlay)
    for rel in overlay_files(overlay):
        dest = Path(docs) / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(overlay / rel, dest)


def copy_content(source, output, mounts, overlay=CONTENT_OVERLAY):
    """Copy content out-of-place from the source monorepo to the output.

    <dir>/docs/* copies to <output>/docs/<alias>/* for every {alias: dir} in
    mounts; root docs/* to <output>/docs/*. No javascripts/mathjax.js is
    carried over. Every copied Markdown page then goes through
    transform_markdown, the overlay is laid over the result, and the
    committed theme override is placed in a top-level overrides/
    (theme.custom_dir).

    The preserved asset directories are neither copied nor transformed:
    regeneration wipes only the paths convert owns, so orphaned and stray
    files do not survive a re-run while the assets are left intact. The source
    tree is never written to.
    """
    source = Path(source)
    output = Path(output)
    docs = output / "docs"

    _clean_owned(output, PRESERVED_DIRS)

    output.mkdir(parents=True, exist_ok=True)
    docs.mkdir(exist_ok=True)
    # docs persists (it holds the assets), so merge the root docs into it.
    shutil.copytree(source / "docs", docs, dirs_exist_ok=True)
    for alias, name in mounts.items():
        shutil.copytree(source / name / "docs", docs / alias)
    for stray in [docs / MATHJAX_REL] + [docs / alias / MATHJAX_REL for alias in mounts]:
        if stray.exists():
            stray.unlink()
            if not any(stray.parent.iterdir()):
                stray.parent.rmdir()

    provided_icons = {
        p.stem[len("tbt-") :]
        for p in (Path(overlay) / transforms.TOOLBAR_IMG_DIR).glob("tbt-*.png")
    }
    preserved = [docs / name for name in PRESERVED_DIRS]
    for md_file in sorted(docs.rglob("*.md")):
        if any(root in md_file.parents for root in preserved):
            continue
        text = md_file.read_text(encoding="utf-8")
        rewritten, icons = transform_markdown(text, md_file.relative_to(docs).as_posix())
        missing = icons - provided_icons
        if missing:
            raise ValueError(
                f"{md_file.relative_to(docs)} references toolbar icons the overlay"
                f" does not provide: {', '.join(sorted(missing))}"
            )
        if rewritten != text:
            md_file.write_text(rewritten, encoding="utf-8")

    apply_overlay(overlay, docs)

    # Place the theme override (the outdated-version warning banner) that
    # theme.custom_dir points at.
    override_dir = output / OVERRIDES_DIR
    override_dir.mkdir(parents=True)
    shutil.copy2(OVERRIDE_TEMPLATE, override_dir / "main.html")


def render_zensical_toml(merged, template_text):
    """Fill the house template's generated regions from the merged config.

    The template carries the static house configuration with its rationale
    in comments (tomli_w cannot write comments), and three placeholder lines:
    @@HEADER@@ (site_name, repo_url), @@MARKDOWN_EXTENSIONS@@ and
    @@EXTRA_AND_NAV@@ ([project.extra] and the [[project.nav]] tables). Each
    must appear exactly once.
    """
    regions = {
        "@@HEADER@@\n": tomli_w.dumps({k: merged[k] for k in CARRIED_KEYS if k in merged}),
        "@@MARKDOWN_EXTENSIONS@@\n": tomli_w.dumps(
            {"markdown_extensions": merged["markdown_extensions"]}
        ),
        "@@EXTRA_AND_NAV@@\n": tomli_w.dumps(
            {"project": {"extra": merged["extra"], "nav": merged["nav"]}}
        ),
    }
    text = template_text
    for placeholder, rendered in regions.items():
        if text.count(placeholder) != 1:
            raise ValueError(f"template must contain {placeholder.strip()} exactly once")
        text = text.replace(placeholder, rendered)
    return text


def write_zensical_toml(merged, path, template=TOML_TEMPLATE):
    Path(path).write_text(
        render_zensical_toml(merged, Path(template).read_text(encoding="utf-8")),
        encoding="utf-8",
    )


def convert(
    source,
    output,
    subprojects=SUBPROJECTS,
    overlay=CONTENT_OVERLAY,
    template=TOML_TEMPLATE,
):
    """Run the full conversion: check the overlay, copy and transform content,
    merge configs, render zensical.toml.

    Deterministic and idempotent: converting the same source twice
    produces byte-identical output. Raises FileNotFoundError naming the
    sub-projects missing from the source, and ValueError (before anything is
    written) when the content overlay is stale against the source.
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
    mounts = mount_points(sub_configs)
    check_overlay(overlay, source, mounts)
    merged = merge_configs(root_config, sub_configs)

    copy_content(source, output, mounts, overlay=overlay)
    write_zensical_toml(merged, output / "zensical.toml", template=template)


if __name__ == "__main__":
    import sys

    # Since 2026-09-16 zensical/ is authored in place (tags, the Tutorials and
    # How-to groups, the front page, page rewrites). Regenerating from the
    # monorepo discards all of that, so it is no longer the default action.
    if "--regenerate" not in sys.argv[1:]:
        sys.exit(
            "zensical/ is authored in place; regenerating from the monorepo would"
            " discard the hand edits. Pass --regenerate to do it anyway."
        )
    convert(SOURCE_ROOT, OUTPUT_ROOT)

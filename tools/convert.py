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
- serialises the merged config to zensical.toml (the committed build
  config; monorepo, site-urls and caption removed) and to mkdocs.yml
  (the Phase 3 diff oracle; monorepo and site-urls removed, caption
  retained so the oracle build matches the baseline's table numbering).
  Both are always written; the oracle disappears at cutover along with
  the script itself.

The source tree is never written to. The output directory is this
repository's zensical/ directory, a self-contained generated project
(zensical.toml, mkdocs.yml and docs/ together) that the script owns
wholesale: it is regenerated from source on every run, so orphaned and
stray files do not survive. Nothing outside zensical/ is ever written.

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

# Retired by the flatten: monorepo (its job is done) and site-urls (a no-op
# for this corpus; nothing uses its site: prefix). caption is additionally
# excluded from zensical.toml only, where a Python-Markdown extension
# replaces it in Phase 5.
DROPPED_PLUGINS = frozenset({"monorepo", "site-urls"})
TOML_ONLY_DROPPED_PLUGINS = frozenset({"caption"})

_INCLUDE_RE = re.compile(r"^!include \./([^/]+)/mkdocs\.yml$")


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
    baseline. extra_javascript keeps one javascripts/mathjax.js entry
    plus external URLs. The monorepo and site-urls plugins are removed;
    caption is retained in the merged dict (serialisers decide its fate).
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


def copy_content(source, output, subprojects):
    """Copy content out-of-place from the source monorepo to the output.

    <sub>/docs/* copies to <output>/docs/<sub>/* for every sub-project;
    root docs/* to <output>/docs/*; documentation-assets/ to
    <output>/docs/documentation-assets/. Per-sub-project
    docs/javascripts/mathjax.js duplicates are not carried over; the root
    copy becomes the single canonical one. Content bytes are never edited.
    The output directory is owned wholesale and regenerated from source,
    so orphaned and stray files do not survive a re-run. The source tree
    is never written to.
    """
    source = Path(source)
    output = Path(output)

    if output.exists():
        shutil.rmtree(output)
    docs = output / "docs"

    shutil.copytree(source / "docs", docs)
    shutil.copytree(source / ASSETS_DIR, docs / ASSETS_DIR)

    for name in subprojects:
        shutil.copytree(source / name / "docs", docs / name)
        duplicate = docs / name / MATHJAX_REL
        if duplicate.exists():
            duplicate.unlink()
            if not any(duplicate.parent.iterdir()):
                duplicate.parent.rmdir()


def write_zensical_toml(config, path):
    """Serialise the merged config as zensical.toml under [project].

    The monorepo, site-urls and caption plugins are excluded: the first
    two are retired by the flatten, and caption is replaced by a
    Python-Markdown extension in Phase 5.
    """
    project = copy.deepcopy(config)
    project["plugins"] = [
        plugin
        for plugin in project.get("plugins", [])
        if _entry_name(plugin) not in TOML_ONLY_DROPPED_PLUGINS
    ]
    with open(path, "wb") as f:
        tomli_w.dump({"project": project}, f)


def write_mkdocs_yml(config, path):
    """Serialise the merged config as the transient mkdocs.yml oracle.

    monorepo and site-urls are excluded; caption is retained so the
    MkDocs oracle build reproduces the baseline's table numbering.
    """
    with open(path, "w") as f:
        yaml.safe_dump(config, f, sort_keys=False, allow_unicode=True)


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
    write_mkdocs_yml(merged, output / "mkdocs.yml")


if __name__ == "__main__":
    convert(SOURCE_ROOT, OUTPUT_ROOT)

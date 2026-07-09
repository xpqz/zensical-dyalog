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
  config; monorepo, site-urls and caption removed) and, on demand, to
  mkdocs.yml (the Phase 3 diff oracle; monorepo and site-urls removed,
  caption retained so the oracle build matches the baseline's table
  numbering).

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

from pathlib import Path

# The 14 sub-projects, in root-nav order. The root nav's !include lines are
# the canonical enumeration; a source checkout missing any of these is an
# error, not a partial conversion.
SUBPROJECTS: tuple[str, ...] = ()

# The generated project directory inside this repository, and the sibling
# monorepo checkout it is generated from.
OUTPUT_ROOT = Path(__file__).resolve().parent.parent / "zensical"
SOURCE_ROOT = Path(__file__).resolve().parent.parent.parent / "documentation"


def load_yaml(path):
    """Parse a mkdocs.yml, tolerating the monorepo's !include tags by
    loading them as plain strings."""
    raise NotImplementedError


def prefix_nav(nav, prefix):
    """Return nav with every page path prefixed by "<prefix>/".

    Recurses into sections (dicts and lists); leaves absolute URLs
    untouched. Titles are preserved.
    """
    raise NotImplementedError


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
    raise NotImplementedError


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
    raise NotImplementedError


def write_zensical_toml(config, path):
    """Serialise the merged config as zensical.toml under [project].

    The monorepo, site-urls and caption plugins are excluded: the first
    two are retired by the flatten, and caption is replaced by a
    Python-Markdown extension in Phase 5.
    """
    raise NotImplementedError


def write_mkdocs_yml(config, path):
    """Serialise the merged config as the transient mkdocs.yml oracle.

    monorepo and site-urls are excluded; caption is retained so the
    MkDocs oracle build reproduces the baseline's table numbering.
    """
    raise NotImplementedError


def convert(source, output, subprojects=SUBPROJECTS, emit_mkdocs_yml=True):
    """Run the full conversion: copy content, merge configs, serialise.

    Deterministic and idempotent: converting the same source twice
    produces byte-identical output. Raises FileNotFoundError naming the
    first expected sub-project missing from the source.
    """
    raise NotImplementedError


if __name__ == "__main__":
    convert(SOURCE_ROOT, OUTPUT_ROOT)

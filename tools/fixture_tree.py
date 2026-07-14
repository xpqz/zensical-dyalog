"""Miniature monorepo builder mirroring the real source's shape.

Two sub-projects stand in for the fourteen. Every structure the tests
exercise is copied from the real corpus: quoted !include nav entries,
an extra: value that conflicts with the root (the monorepo build reads
only the root value, so root-wins preserves the rendered baseline),
duplicate pymdownx.highlight blocks, per-sub-project mathjax.js copies,
nested nav sections, a binary asset, and a sub-only extra_css entry whose
target does not exist (shared-code-files-user-guide declares a style/
directory that is absent from its docs; the monorepo build ignores sub
extra_css, so the dangling entries are invisible today).
"""

import hashlib
import textwrap
from pathlib import Path

SUB_NAMES = ("release-notes", "compiler-user-guide")

MATHJAX_JS = (
    "window.MathJax = {};\ndocument$.subscribe(() => MathJax.typesetPromise())\n"
)

PNG_BYTES = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR fake image bytes"

ROOT_MKDOCS = textwrap.dedent(
    """\
    site_name: Documentation
    copyright: Copyright &copy; 1982-$CURRENT_YEAR Dyalog Limited
    theme:
      favicon: documentation-assets/images/favicon-32.png
      logo: documentation-assets/images/dyalog-logo_white.svg
      name: material
      features:
        - navigation.instant
        - navigation.footer
      font:
        text: Be Vietnam Pro
    extra_css:
      - documentation-assets/css/main.css
      - documentation-assets/css/extra.css
      - documentation-assets/css/admonition-ucmdhelp.css
    extra_javascript:
      - javascripts/mathjax.js
      - https://unpkg.com/mathjax@3/es5/tex-mml-chtml.js
    plugins:
      - privacy
      - search
      - macros
      - monorepo
      - caption:
          table:
            enable: true
            position: top
      - minify:
          minify_html: true
    extra:
      version_maj: 21
      version_majmin: "21.0"
    markdown_extensions:
      - admonition
      - pymdownx.highlight:
          use_pygments: false
          pygments_lang_class: true
      - attr_list
      - markdown_tables_extended
      - toc:
          title: On this page
    nav:
      - 'Release Notes':
          - 'v21.0 Release Notes': "!include ./release-notes/mkdocs.yml"
      - 'Code Tooling':
          - 'Compiler': "!include ./compiler-user-guide/mkdocs.yml"
      - 'About':
          - 'Conventions': conventions.md
    """
)

RELEASE_NOTES_MKDOCS = textwrap.dedent(
    """\
    site_name: Release Notes
    theme:
      name: material
      features:
        - navigation.instant
    extra_css:
      - documentation-assets/css/main.css
    extra_javascript:
      - javascripts/mathjax.js
      - https://unpkg.com/mathjax@3/es5/tex-mml-chtml.js
    plugins:
      - privacy
      - search
      - macros
      - site-urls
      - caption:
          table:
            enable: true
            position: top
    extra:
      version_maj: 21
      version_majmin: "21.0"
    markdown_extensions:
      - admonition
      - pymdownx.highlight:
          use_pygments: false
          pygments_lang_class: true
      - footnotes
    nav:
      - index.md
      - Announcements:
          - Announcements: announcements/index.md
          - Deprecated Functionality: announcements/deprecated-functionality.md
      - System Requirements: system-requirements.md
    """
)

COMPILER_MKDOCS = textwrap.dedent(
    """\
    site_name: Compiler User Guide
    theme:
      name: material
    extra_css:
      - documentation-assets/css/main.css
      - documentation-assets/css/extra.css
      - style/main.css
    plugins:
      - privacy
      - search
      - macros
      - site-urls
    extra:
      version_maj: 20
      version_majmin: "20.0"
    markdown_extensions:
      - admonition
      - pymdownx.highlight:
          use_pygments: false
          pygments_lang_class: true
    nav:
      - index.md
      - Basic Usage: basic-usage.md
    """
)


def build_source_tree(root: Path) -> Path:
    """Materialise the miniature monorepo under root and return it."""
    src = root / "documentation"

    (src / "docs" / "javascripts").mkdir(parents=True)
    (src / "mkdocs.yml").write_text(ROOT_MKDOCS)
    (src / "docs" / "index.md").write_text("# Documentation\n")
    (src / "docs" / "conventions.md").write_text("# Conventions\n")
    (src / "docs" / "javascripts" / "mathjax.js").write_text(MATHJAX_JS)

    (src / "documentation-assets" / "css").mkdir(parents=True)
    (src / "documentation-assets" / "css" / "main.css").write_text("body {}\n")

    rn = src / "release-notes"
    (rn / "docs" / "announcements").mkdir(parents=True)
    (rn / "docs" / "javascripts").mkdir(parents=True)
    (rn / "docs" / "images").mkdir(parents=True)
    (rn / "mkdocs.yml").write_text(RELEASE_NOTES_MKDOCS)
    (rn / "docs" / "index.md").write_text("# Release Notes {{ version_majmin }}\n")
    (rn / "docs" / "announcements" / "index.md").write_text("# Announcements\n")
    (rn / "docs" / "announcements" / "deprecated-functionality.md").write_text(
        "# Deprecated\nSee [conventions](../../conventions.md).\n"
    )
    (rn / "docs" / "system-requirements.md").write_text("# System Requirements\n")
    (rn / "docs" / "javascripts" / "mathjax.js").write_text(MATHJAX_JS)
    (rn / "docs" / "images" / "logo.png").write_bytes(PNG_BYTES)

    cu = src / "compiler-user-guide"
    (cu / "docs").mkdir(parents=True)
    (cu / "mkdocs.yml").write_text(COMPILER_MKDOCS)
    (cu / "docs" / "index.md").write_text("# Compiler User Guide\n")
    (cu / "docs" / "basic-usage.md").write_text("# Basic Usage\n")
    # A page whose title is a raw-HTML heading (the object-reference shape),
    # to exercise the rewrite. Body left as plain text.
    (cu / "docs" / "raw-heading.md").write_text(
        '<h1 class="heading"><span class="name">Widget</span>'
        ' <span class="right">Object</span></h1>\n\nBody text.\n'
    )

    return src


def tree_digest(root: Path) -> dict:
    """Map of relative path to content sha256 for every file under root."""
    return {
        str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
        for p in sorted(root.rglob("*"))
        if p.is_file()
    }

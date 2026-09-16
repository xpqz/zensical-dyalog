"""Miniature monorepo builder mirroring the real source's shape.

Three sub-projects stand in for the fourteen, one of them (the .NET
guide) mounted under a slugified alias rather than its directory name. Every structure the tests
exercise is copied from the real corpus: quoted !include nav entries,
an extra: value that conflicts with the root (the monorepo build reads
only the root value, so root-wins preserves the rendered baseline),
duplicate pymdownx.highlight blocks, the arithmatex extension and
per-sub-project mathjax.js copies (neither is carried over), nested nav
sections, a binary asset, and pages carrying each house pattern the content
transforms rewrite: a raw-HTML title, a current-form styled title with the
{{key}} macro, an example heading, a bespoke admonition type, a shaded
default cell, and a sprite toolbar icon.

build_overlay_tree builds the matching content overlay: the toolbar icon
image the sprite page needs, and a front-page replacement with its
source-hash sidecar.
"""

import hashlib
import textwrap
from pathlib import Path

SUB_NAMES = ("release-notes", "compiler-user-guide", "dotnet-interface-guide")

MATHJAX_JS = (
    "window.MathJax = {};\ndocument$.subscribe(() => MathJax.typesetPromise())\n"
)

PNG_BYTES = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR fake image bytes"

INDEX_MD = "# Documentation\n\n!!! Hint \"Hints\"\n    New here?\n"
INDEX_OVERLAY_MD = "# Documentation\n\nReplaced front page.\n"

ROOT_MKDOCS = textwrap.dedent(
    """\
    site_name: Documentation
    repo_url: https://github.com/dyalog/documentation
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
      generator: false
      version:
        provider: mike
    markdown_extensions:
      - admonition
      - pymdownx.arithmatex:
          generic: true
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
          - '.NET Interface': "!include ./dotnet-interface-guide/mkdocs.yml"
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

# The site_name mkdocs-monorepo-plugin slugifies to net-interface-guide: the
# one guide shape whose mount point differs from its directory name.
DOTNET_MKDOCS = textwrap.dedent(
    """\
    site_name: .NET Interface Guide
    theme:
      name: material
    plugins:
      - search
      - macros
    nav:
      - index.md
      - Installation: installation.md
    """
)

STYLED_TITLE_MD = (
    "# <span>Comma Separated Values</span> `{R}←{X} ⎕CSV Y`{{key}}\n\n"
    "This function imports CSV data.\n\n"
    '<h2 class="example">Examples</h2>\n```apl\n      ⎕CSV file\n```\n'
)

EXAMPLES_MD = textwrap.dedent(
    """\
    # Options

    !!! Hint "Hints and Recommendations"
        Use the defaults.

    |---|-------------|
    |0 { .shaded } |do not repair|
    |`1`|repair       |

    Default values are highlighted thus{ .shaded }  in the above tables.

    <h2 class="example">Example</h2>
    ```apl
          1 ⎕FCHK 'f'
    ```
    """
)

TOOLBAR_MD = textwrap.dedent(
    """\
    # Toolbar

    |Button|Name|
    |---|---|
    |<span class="toolbar-icon" style="background-position: -64px 0"></span>|Exec|
    """
)


def build_source_tree(root: Path) -> Path:
    """Materialise the miniature monorepo under root and return it."""
    src = root / "documentation"

    (src / "docs" / "javascripts").mkdir(parents=True)
    (src / "mkdocs.yml").write_text(ROOT_MKDOCS)
    (src / "docs" / "index.md").write_text(INDEX_MD)
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
    # A page whose title is a raw-HTML heading (the pre-July object-reference
    # shape), to exercise the rewrite. Body left as plain text.
    (cu / "docs" / "raw-heading.md").write_text(
        '<h1 class="heading"><span class="name">Widget</span>'
        ' <span class="right">Object</span></h1>\n\nBody text.\n'
    )
    (cu / "docs" / "styled-title.md").write_text(STYLED_TITLE_MD)
    (cu / "docs" / "examples.md").write_text(EXAMPLES_MD)
    (cu / "docs" / "toolbar.md").write_text(TOOLBAR_MD)

    dn = src / "dotnet-interface-guide"
    (dn / "docs").mkdir(parents=True)
    (dn / "mkdocs.yml").write_text(DOTNET_MKDOCS)
    (dn / "docs" / "index.md").write_text("# .NET Interface Guide\n")
    (dn / "docs" / "installation.md").write_text(
        "# Installation\n\nSee [the compiler](../compiler-user-guide/index.md).\n"
    )

    return src


def build_overlay_tree(root: Path, source: Path) -> Path:
    """Materialise a content overlay matching the fixture source: the toolbar
    icon image and a front-page replacement whose sidecar names the current
    source page's hash."""
    overlay = root / "content"
    (overlay / "windows-ui-guide" / "img").mkdir(parents=True)
    (overlay / "windows-ui-guide" / "img" / "tbt-exec.png").write_bytes(PNG_BYTES)
    (overlay / "index.md").write_text(INDEX_OVERLAY_MD)
    (overlay / "index.md.source-sha256").write_text(
        hashlib.sha256((source / "docs" / "index.md").read_bytes()).hexdigest() + "\n"
    )
    return overlay


def tree_digest(root: Path) -> dict:
    """Map of relative path to content sha256 for every file under root."""
    return {
        str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
        for p in sorted(root.rglob("*"))
        if p.is_file()
    }

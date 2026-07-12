"""Python-Markdown extension restoring the monorepo's table numbering.

The MkDocs site used mkdocs-caption to turn a `Table: <text>` paragraph
placed before a table into a numbered caption. Zensical cannot run that
MkDocs plugin, so this extension reproduces its output on the shared
Python-Markdown parser instead.

For each `Table: <text>` paragraph immediately followed by a table, it:

- removes the paragraph,
- gives the table `id="_table-N"` (N numbered per document from 1), and
- inserts `<caption style="caption-side:top">Table N: <text></caption>` as
  the table's first child.

This matches mkdocs-caption 1.3.0 with the corpus's committed configuration
(`start_index: 1`, `caption_prefix: 'Table {index}:'`, `position: top`), so
the `[Table N](#_table-N)` cross-references authored across the corpus resolve
again. The configuration is fixed to those corpus values rather than exposed
as options: the extension exists only to reproduce this one behaviour.
"""

import re

from markdown.extensions import Extension
from markdown.treeprocessors import Treeprocessor

# A caption paragraph is exactly "Table:" followed by the caption text.
_CAPTION_RE = re.compile(r"^Table:\s*(.+)$", re.DOTALL)

# Rendered numbering and anchor, matching mkdocs-caption's committed config.
_CAPTION_PREFIX = "Table {index}:"
_ANCHOR = "_table-{index}"
_CAPTION_STYLE = "caption-side:top"


class CaptionTreeprocessor(Treeprocessor):
    """Attaches numbered captions to tables preceded by a Table: paragraph."""

    def run(self, root):
        raise NotImplementedError


class DyalogCaptionExtension(Extension):
    def extendMarkdown(self, md):
        # Runs after the block parser has built the table elements.
        md.treeprocessors.register(
            CaptionTreeprocessor(md), "dyalog_caption", 5
        )


def makeExtension(**kwargs):
    return DyalogCaptionExtension(**kwargs)

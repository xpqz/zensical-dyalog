"""Python-Markdown extension restoring the monorepo's table numbering.

The MkDocs site used mkdocs-caption to turn a `Table: <text>` paragraph
placed before a table into a numbered caption. Zensical cannot run that
MkDocs plugin, so this extension reproduces its output on the shared
Python-Markdown parser instead.

For each `Table: <text>` paragraph immediately followed by a table, it:

- removes the paragraph,
- gives the table `id="_table-N"` (N numbered per document from 1), or the
  id the author put at the end of the caption (`Table: <text> { #my-id }` or
  `{: #my-id }`; mkdocs-caption parsed this itself, so it is still literal
  text when this extension runs),
- inserts `<caption style="caption-side:top">Table N: <text></caption>` as
  the table's first child, carrying the caption's inline markup, and
- fills every empty-text link to a numbered table (`[](#my-id)`) with the
  reference text `Table N`.

This matches mkdocs-caption 1.3.0 with the corpus's committed configuration
(`start_index: 1`, `caption_prefix: 'Table {index}:'`, `reference_text:
'Table {index}'`, `position: top`), so both the `[Table N](#_table-N)` and
the `[](#custom-id)` cross-references authored across the corpus resolve
again. The configuration is fixed to those corpus values rather than exposed
as options: the extension exists only to reproduce this one behaviour.
"""

import copy
import re
import xml.etree.ElementTree as etree

from markdown.extensions import Extension
from markdown.treeprocessors import Treeprocessor

# A caption paragraph is "Table:" followed by the caption text. The text may
# wrap within the one paragraph, so newlines are folded to spaces below.
_CAPTION_RE = re.compile(r"^Table:\s*(.*)$", re.DOTALL)
# An author-chosen anchor closing the caption: { #id } or {: #id }.
_ID_RE = re.compile(r"\s*\{:?\s*#([\w-]+)\s*\}\s*$")

# Rendered numbering and anchor, matching mkdocs-caption's committed config.
_CAPTION_PREFIX = "Table {index}:"
_REFERENCE_TEXT = "Table {index}"
_ANCHOR = "_table-{index}"
_CAPTION_STYLE = "caption-side:top"


class CaptionTreeprocessor(Treeprocessor):
    """Attaches numbered captions to tables preceded by a Table: paragraph.

    The numbering counter is local to each run, so it restarts at 1 for every
    document (page) rather than leaking across pages.
    """

    def run(self, root):
        numbered = {}
        # Walk each element that can hold block-level children, pairing a
        # Table: paragraph with the table element that immediately follows it.
        for parent in root.iter():
            children = list(parent)
            for position, child in enumerate(children):
                if child.tag != "p" or not child.text:
                    continue
                match = _CAPTION_RE.match(child.text.lstrip())
                if not match:
                    continue
                if position + 1 >= len(children):
                    continue
                table = children[position + 1]
                if table.tag != "table":
                    continue

                index = len(numbered) + 1
                anchor = _pop_caption_id(child) or _ANCHOR.format(index=index)
                numbered[anchor] = index
                self._apply(table, child, anchor, index)
                parent.remove(child)
        self._fill_references(root, numbered)
        return None

    def _apply(self, table, paragraph, anchor, index):
        table.set("id", anchor)
        caption = etree.Element("caption")
        caption.set("style", _CAPTION_STYLE)
        # The paragraph's leading text is the caption text up to its first
        # inline element; inline markup (code spans, emphasis) follows as
        # child elements and is carried across, keeping the space that
        # separated it from the leading text.
        match = _CAPTION_RE.match(paragraph.text.lstrip())
        text = match.group(1) if match else ""
        lead = " ".join(text.split())
        if len(paragraph) and text[-1:].isspace():
            lead += " "
        prefix = _CAPTION_PREFIX.format(index=index)
        caption.text = f"{prefix} {lead}" if lead or len(paragraph) else prefix
        for element in paragraph:
            caption.append(copy.deepcopy(element))
        table.insert(0, caption)

    def _fill_references(self, root, numbered):
        for link in root.iter("a"):
            href = link.get("href", "")
            if not href.startswith("#") or href[1:] not in numbered:
                continue
            if len(link) or (link.text or "").strip():
                continue
            link.text = _REFERENCE_TEXT.format(index=numbered[href[1:]])


def _pop_caption_id(paragraph):
    """Remove a trailing { #id } from the caption paragraph and return the id.

    The id sits in the paragraph's final text run: the tail of its last
    inline element when it has any, else its own text. attr_list leaves it
    alone (a block attr list must be on a line by itself, and the inline form
    must abut the element), so it is literal text here. If attr_list did
    attach an id to the paragraph, that is honoured too.
    """
    if len(paragraph):
        last = paragraph[-1]
        match = _ID_RE.search(last.tail or "")
        if match:
            last.tail = last.tail[: match.start()]
            return match.group(1)
    else:
        match = _ID_RE.search(paragraph.text or "")
        if match:
            paragraph.text = paragraph.text[: match.start()]
            return match.group(1)
    return paragraph.get("id")


class DyalogCaptionExtension(Extension):
    def extendMarkdown(self, md):
        # Runs after the block parser has built the table elements and after
        # attr_list (priority 8) has moved a caption's { #id } onto its <p>.
        md.treeprocessors.register(
            CaptionTreeprocessor(md), "dyalog_caption", 5
        )


def makeExtension(**kwargs):
    return DyalogCaptionExtension(**kwargs)

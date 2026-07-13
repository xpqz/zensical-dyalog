"""Behavioural surface for the caption-numbering extension.

Each test renders Markdown through Python-Markdown with the real table
extension the corpus uses (markdown_tables_extended) plus this extension,
and asserts the rendered HTML against the contract that mkdocs-caption 1.3.0
produced for the corpus: a Table: paragraph before a table becomes
<table id="_table-N"> with a "Table N: <text>" caption as its first child,
numbered per page from 1.
"""

import re

import markdown

import dyalog_caption

TABLE = "|Variable|Notes|\n|---|---|\n|TERM|translate tables|\n"


def render(text):
    return markdown.markdown(
        text,
        extensions=["markdown_tables_extended", dyalog_caption.makeExtension()],
    )


def test_table_caption_becomes_a_numbered_caption_element():
    html = render(f"Table: Commonly used Variables\n\n{TABLE}")
    assert '<table id="_table-1">' in html
    caption = re.search(r"<caption[^>]*>(.*?)</caption>", html, re.S)
    assert caption is not None
    assert caption.group(1) == "Table 1: Commonly used Variables"


def test_caption_carries_the_top_side_style():
    html = render(f"Table: Foo\n\n{TABLE}")
    assert re.search(r'<caption[^>]*caption-side:top[^>]*>', html)


def test_numbering_increments_per_document():
    html = render(
        f"Table: First\n\n{TABLE}\n\nText between.\n\nTable: Second\n\n{TABLE}"
    )
    assert '<table id="_table-1">' in html
    assert '<table id="_table-2">' in html
    assert "Table 1: First" in html
    assert "Table 2: Second" in html


def test_numbering_restarts_at_one_for_each_render():
    # Per-page numbering: a second, independent render must not continue the
    # first page's count. A shared counter would break the next page's
    # [Table 1](#_table-1) cross-reference.
    first = render(f"Table: First page table\n\n{TABLE}")
    second = render(f"Table: Second page table\n\n{TABLE}")
    assert '<table id="_table-1">' in first
    assert '<table id="_table-1">' in second
    assert "Table 1: Second page table" in second


def test_caption_paragraph_is_consumed():
    html = render(f"Table: Commonly used Variables\n\n{TABLE}")
    assert "<p>Table:" not in html


def test_cross_reference_resolves_to_the_table_id():
    html = render(f"See [Table 1](#_table-1).\n\nTable: Commonly used Variables\n\n{TABLE}")
    assert '<a href="#_table-1">Table 1</a>' in html
    assert 'id="_table-1"' in html


def test_caption_is_the_tables_first_child():
    html = render(f"Table: Foo\n\n{TABLE}")
    # The caption element immediately follows the opening <table ...> tag.
    assert re.search(r'<table id="_table-1">\s*<caption', html)


def test_paragraph_without_a_following_table_is_left_untouched():
    html = render("Table: orphan with no table\n\nJust a paragraph.")
    assert "<caption" not in html
    assert "Table: orphan with no table" in html

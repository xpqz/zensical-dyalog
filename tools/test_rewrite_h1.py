"""Behavioural surface for the raw-HTML-heading rewrite in convert.py.

rewrite_h1 is a text->text transform applied to markdown during the copy.
Tests assert both the transform output (raw <h1> becomes an ATX heading)
and, by rendering the result through Python-Markdown with the corpus's
relevant extensions, that the class, inner spans and APL command text
survive.
"""

import markdown

import convert

MD_EXTS = ["attr_list", "md_in_html", "pymdownx.highlight", "toc"]


def render(md_text):
    return markdown.markdown(md_text, extensions=MD_EXTS)


NAME_RIGHT = (
    '<h1 class="heading"><span class="name">Button</span>'
    ' <span class="right">Object</span></h1>\n\nBody.\n'
)
COMMAND = (
    '<h1 class="heading"><span class="command">R←f\\[K]Y</span>'
    ' <span class="name">Scan</span></h1>\n\nBody.\n'
)


# --- transform output --------------------------------------------------


def test_converts_raw_h1_to_an_atx_heading():
    out = convert.rewrite_h1(NAME_RIGHT)
    assert "<h1" not in out
    assert any(line.startswith("# ") for line in out.splitlines())


def test_leaves_content_without_a_raw_h1_untouched():
    text = "# Already Markdown\n\nSome body with an inline `<h1>` mention.\n"
    assert convert.rewrite_h1(text) == text


def test_leaves_an_h1_embedded_in_a_line_untouched():
    # httprequest.md shapes: an <h1> that ends its line but does not start it,
    # and an <h1> inside an APL string literal. Neither is a page title, so the
    # rewrite must leave the text exactly as-is.
    text = (
        "<body><h1>Simple Form</h1>\n\n"
        "An APL line building HTML:\n\n"
        "    response,←'<h1 align=\"center\">Hello '\n"
    )
    assert convert.rewrite_h1(text) == text


# --- rendered result ---------------------------------------------------


def test_preserves_heading_class_and_inner_spans():
    html = render(convert.rewrite_h1(NAME_RIGHT))
    assert '<h1 class="heading"' in html
    assert '<span class="name">Button</span>' in html
    assert '<span class="right">Object</span>' in html


def test_heading_text_becomes_available_as_title():
    # An ATX heading is slugified by toc (gets an id); a raw passthrough is
    # not. The id confirms the title heading is a real ATX heading Zensical
    # will read, and its text is the object title.
    html = render(convert.rewrite_h1(NAME_RIGHT))
    assert 'id="button-object"' in html


def test_preserves_apl_backslash_in_command_heading():
    html = render(convert.rewrite_h1(COMMAND))
    assert "R←f\\[K]Y" in html


def test_maps_id_and_class_attributes():
    raw = '<h1 id="negative" class="heading"><span class="name">Neg</span></h1>\n'
    html = render(convert.rewrite_h1(raw))
    assert 'id="negative"' in html
    assert 'class="heading"' in html


def test_rewrites_a_bare_h1():
    html = render(convert.rewrite_h1("<h1>Plain Title</h1>\n\nBody.\n"))
    assert "<h1" in html
    assert "Plain Title" in html


def test_rewrites_the_title_but_leaves_a_fenced_h1_untouched():
    # A real object-reference page: a raw-HTML title heading and, later, an
    # HTML code example containing a literal <h1>. The title must be rewritten;
    # the fenced example must survive verbatim.
    text = (
        '<h1 class="heading"><span class="name">Widget</span></h1>\n\n'
        "Intro.\n\n"
        "An HTML example:\n\n"
        '```html\n<h1 class="heading">Example</h1>\n```\n'
    )
    out = convert.rewrite_h1(text)
    # fenced example preserved verbatim; the title's raw <h1> is gone, so the
    # only <h1 left is the one inside the fence.
    assert '<h1 class="heading">Example</h1>' in out
    assert out.count("<h1") == 1
    assert any(line.startswith("# ") for line in out.splitlines())


def test_maps_a_general_attribute_as_key_value():
    html = render(convert.rewrite_h1('<h1 align="center">Centered</h1>\n'))
    assert 'align="center"' in html
    assert "Centered" in html


def test_rewrites_every_raw_h1_in_a_document():
    text = (
        '<h1 class="heading"><span class="name">First</span></h1>\n\n'
        "Body.\n\n"
        '<h1 class="heading"><span class="name">Second</span></h1>\n\nMore.\n'
    )
    out = convert.rewrite_h1(text)
    assert "<h1" not in out
    assert sum(line.startswith("# ") for line in out.splitlines()) == 2

"""Behavioural surface for the content transforms in transforms.py.

Each transform is a text-to-text function over one Markdown page. The
inputs here are the exact shapes found in the corpus, in both the pre-July
(raw-HTML title rewritten to spans with classes) and current (bare spans,
inline code, {{key}}) generations.
"""

import pytest

import transforms as t

KEY = "../key-to-notation.md"


# --- fence handling ----------------------------------------------------


def test_prose_segments_round_trip_reproduces_the_text():
    text = "a\n\n```apl\n# not a title\n```\nb\n~~~\nx\n~~~\n"
    runs = t.prose_segments(text)
    assert "\n".join(line for _, lines in runs for line in lines) == text
    assert [is_code for is_code, _ in runs] == [False, True, False, True, False]


def test_transforms_leave_fenced_code_untouched():
    text = "```html\n<h2 class=\"example\">Examples</h2>\n!!! Hint \"x\"\n```\n"
    assert t.rewrite_example_headings(text) == text
    assert t.normalise_admonitions(text) == text
    assert t.normalise_titles(text) == text


# --- titles: pre-July form (after rewrite_h1) --------------------------


def test_legacy_name_and_command_become_title_and_apl_block():
    text = (
        '# <span class="name">File Check and Repair</span>'
        ' <span class="command">R←\\{X\\} ⎕FCHK Y</span> {: .heading}\n\nBody.\n'
    )
    assert t.normalise_titles(text) == (
        "# File Check and Repair\n\n```apl\nR←{X} ⎕FCHK Y\n```\n\nBody.\n"
    )


def test_legacy_name_and_right_become_title_and_plain_line():
    text = '# <span class="name">Caption</span> <span class="right">Property</span> {: .heading}\n\nBody.\n'
    assert t.normalise_titles(text) == "# Caption\n\nProperty\n\nBody.\n"


def test_legacy_name_only_becomes_plain_title():
    text = '# <span class="name">Basic Usage</span> {: .heading}\n\nBody.\n'
    assert t.normalise_titles(text) == "# Basic Usage\n\nBody.\n"


def test_legacy_keeps_other_attr_list_tokens_and_drops_heading_class():
    text = '# <span class="name">Negate</span> <span class="command">R←-Y</span> {: #negative .heading}\n'
    assert t.normalise_titles(text).startswith("# Negate {: #negative}\n\n```apl\nR←-Y\n```")


def test_legacy_nested_command_in_name_becomes_inline_code():
    text = '# <span class="name"><span class="command">⎕NA</span> under UNIX</span> {: .heading}\n'
    assert t.normalise_titles(text) == "# `⎕NA` under UNIX\n"


def test_legacy_keeps_name_escapes_and_entities_as_heading_markdown():
    # rewrite_h1 escaped the underscore; the escape is valid heading Markdown
    # and stays. bs4 re-encodes the ampersand; both render identically.
    text = '# <span class="name">Log\\_File</span> {: .heading}\n'
    assert t.normalise_titles(text) == "# Log\\_File\n"
    text = '# <span class="name">Threads &amp; Niladic Functions</span> {: .heading}\n'
    assert t.normalise_titles(text) == "# Threads &amp; Niladic Functions\n"


def test_legacy_command_with_br_becomes_two_lines():
    text = (
        '# <span class="name">Bind</span>'
        ' <span class="command">\\{R\\}←A∘fY<br/>\\{R\\}←(f∘B)Y</span> {: .heading}\n'
    )
    assert t.normalise_titles(text) == "# Bind\n\n```apl\n{R}←A∘fY\n{R}←(f∘B)Y\n```\n"


def test_legacy_command_that_is_a_classifier_becomes_a_plain_line():
    text = '# <span class="name">SessionTrace</span><span class="command">Event 527</span> {: .heading}\n'
    assert t.normalise_titles(text) == "# SessionTrace\n\nEvent 527\n"


def test_inserts_a_blank_line_when_text_follows_the_title_directly():
    text = '# <span class="name">Dot</span> <span class="command">.</span> {: .heading}\nDot can be used.\n'
    assert t.normalise_titles(text) == "# Dot\n\n```apl\n.\n```\n\nDot can be used.\n"


# --- titles: current form ------------------------------------------------


def test_current_name_code_and_key_become_block_and_key_link():
    text = "# <span>Comma Separated Values</span> `{R}←{X} ⎕CSV Y`{{key}}\n\nBody.\n"
    assert t.normalise_titles(text, key_link=KEY) == (
        "# Comma Separated Values\n\n```apl\n{R}←{X} ⎕CSV Y\n```\n"
        f"[Key to notation]({KEY})\n\nBody.\n"
    )


def test_current_key_macro_is_dropped_without_a_link_target():
    text = "# <span>Zilde</span> `⍬`{{key}}\n"
    assert t.normalise_titles(text) == "# Zilde\n\n```apl\n⍬\n```\n"


def test_current_inline_code_is_literal_so_backslashes_survive():
    text = "# <span>Scan</span> `R←f\\[K]Y`{{key}}\n"
    assert "R←f\\[K]Y\n" in t.normalise_titles(text)


def test_current_name_and_right_span_become_title_and_plain_line():
    text = "# <span>Close</span> <span>Event 33</span>\n\nBody.\n"
    assert t.normalise_titles(text) == "# Close\n\nEvent 33\n\nBody.\n"


def test_current_classifier_in_code_becomes_a_plain_line():
    text = "# <span>WorkspaceLoaded</span> `Event 525`\n"
    assert t.normalise_titles(text) == "# WorkspaceLoaded\n\nEvent 525\n"


def test_current_code_element_with_br_becomes_two_lines():
    text = "# <span>Bind</span> <code>{R}←A∘fY<br>{R}←(f∘B)Y</code>{{key}}\n"
    assert t.normalise_titles(text, key_link=KEY) == (
        f"# Bind\n\n```apl\n{{R}}←A∘fY\n{{R}}←(f∘B)Y\n```\n[Key to notation]({KEY})\n"
    )


def test_plain_headings_are_left_alone():
    for text in (
        "# Basic Usage\n",
        "# Monadic `⎕CSV`\n",
        "# `⎕NA` under UNIX\n",
        "# Signals and `⎕TRAP, 4007⌶`\n",
        "## <span>Not a title</span>\n",
    ):
        assert t.normalise_titles(text) == text


def test_key_link_is_relative_to_the_page():
    assert t.key_link_for("language-reference-guide/system-functions/csv.md") == (
        "../key-to-notation.md"
    )
    assert t.key_link_for("programming-reference-guide/errors/ws-full.md") == (
        "../../language-reference-guide/key-to-notation.md"
    )
    assert t.key_link_for("index.md") == "language-reference-guide/key-to-notation.md"


# --- example headings --------------------------------------------------


def test_example_headings_become_atx_headings_of_the_same_level():
    assert t.rewrite_example_headings('<h2 class="example">Examples</h2>\n') == "## Examples\n"
    assert t.rewrite_example_headings('<h4 class="example">Example</h4>\n') == "#### Example\n"


def test_example_h1_is_demoted_to_h2():
    assert t.rewrite_example_headings('<h1 class="example">Examples</h1>\n') == "## Examples\n"


def test_example_paragraph_label_becomes_bold_followed_by_a_blank_line():
    assert t.rewrite_example_headings('<p class="example">Example</p>\n```apl\nx\n```\n') == (
        "**Example**\n\n```apl\nx\n```\n"
    )
    assert t.rewrite_example_headings('<p class="example">Example</p>\n\ntext\n') == (
        "**Example**\n\ntext\n"
    )


def test_malformed_h_star_example_heading_becomes_bold():
    assert t.rewrite_example_headings('<h* class="example">Example</h*>\n```apl\n') == (
        "**Example**\n\n```apl\n"
    )


# --- admonitions -------------------------------------------------------


@pytest.mark.parametrize(
    "line, expected",
    [
        ('!!! Hint "Hints and Recommendations"', '!!! tip "Hints and Recommendations"'),
        ('!!! Legacy "Legacy"', '!!! note "Legacy"'),
        ('!!! windows "Dyalog on Microsoft Windows"', '!!! info "Dyalog on Microsoft Windows"'),
        ('    !!! unix "Dyalog on Unix"', '    !!! info "Dyalog on Unix"'),
        ('- !!! windows "Dyalog on Microsoft Windows"', '- !!! info "Dyalog on Microsoft Windows"'),
        ('???+ Hint "Open"', '???+ tip "Open"'),
        ('!!! Info "Information"', '!!! Info "Information"'),
        ('!!! Warning "Warning"', '!!! Warning "Warning"'),
    ],
)
def test_admonition_types_map_onto_the_stock_set(line, expected):
    assert t.normalise_admonitions(line + "\n    body\n") == expected + "\n    body\n"


# --- shaded default markers --------------------------------------------


@pytest.mark.parametrize(
    "cell, expected",
    [
        ("|0 { .shaded } |x|", "|`0` (default)|x|"),
        ("|'None' { .shaded } |x|", "|`'None'` (default)|x|"),
        ("|` 0`   { .shaded } | x |", "|`0` (default)| x |"),
        ("|`1` {: .shaded} |x|", "|`1` (default)|x|"),
        ("| `0` {.shaded} | x |", "|`0` (default)| x |"),
        ("|0  |. { .shaded }  |", "|0  |`.` (default)|"),
    ],
)
def test_shaded_cells_say_default_in_text(cell, expected):
    assert t.replace_shaded_defaults(cell + "\n") == expected + "\n"


def test_shaded_legend_line_is_removed_with_one_adjacent_blank():
    text = "|`1`|x|\n\nDefault values are highlighted thus{ .shaded }  in the above tables.\n\n## Examples\n"
    assert t.replace_shaded_defaults(text) == "|`1`|x|\n\n## Examples\n"
    assert t.replace_shaded_defaults("Intro.\n\nDefault values are highlighted thus.\n\nNext.\n") == (
        "Intro.\n\nNext.\n"
    )


def test_shaded_legend_sentence_is_removed_from_a_longer_paragraph():
    text = (
        "The default depends on Style. Default values are highlighted"
        ' <span class="shaded">thus</span> in the above tables.\n'
    )
    assert t.replace_shaded_defaults(text) == "The default depends on Style.\n"


# --- raw-HTML table layout ---------------------------------------------


def test_flex_between_cells_collapse_to_strength_result_text():
    text = (
        "        <td>\n"
        '            <div class="flex-between">\n'
        '                <span class="text-left">6</span>\n'
        '                <span class="text-right">A</span>\n'
        "            </div>\n"
        "        </td>\n"
    )
    assert t.simplify_table_markup(text) == "        <td>\n            6: A\n        </td>\n"


def test_empty_flex_between_cells_collapse_to_a_space_entity():
    text = '<div class="flex-between">\n<span>&#160;</span>\n<span>&#160;</span>\n</div>\n'
    assert t.simplify_table_markup(text) == "&#160;\n"


def test_layout_classes_are_dropped_and_dyalog_class_becomes_apl():
    text = (
        '<table class="table-bordered">\n<td class="no-border">&#160;</td>\n'
        '<td rowspan="10" class="rowspan" style="text-align: center;">X</td>\n'
        '<th class="text-left">Length</th>\n<td class="Dyalog">⍺</td>\n'
    )
    assert t.simplify_table_markup(text) == (
        '<table>\n<td>&#160;</td>\n<td rowspan="10" style="text-align: center;">X</td>\n'
        '<th>Length</th>\n<td class="apl">⍺</td>\n'
    )


# --- toolbar icons -----------------------------------------------------


def test_toolbar_icon_in_a_table_row_becomes_an_image_with_alt_text():
    line = '|<span class="toolbar-icon" style="background-position: -64px 0"></span>|Exec|x|\n'
    text, used = t.replace_toolbar_icons(line, "../img")
    assert text == "|![Exec toolbar button](../img/tbt-exec.png)|Exec|x|\n"
    assert used == {"exec"}


def test_toolbar_icon_at_offset_zero_is_recognised():
    line = '|<span class="toolbar-icon" style="background-position: 0 0"></span>|Back|\n'
    text, used = t.replace_toolbar_icons(line, "img")
    assert text == "|![Back toolbar button](img/tbt-back.png)|Back|\n"
    assert used == {"back"}


def test_toolbar_icon_in_prose_takes_the_preceding_bold_label_as_alt():
    line = (
        '- click the **Next Primitive** icon <span class="toolbar-icon"'
        ' style="background-position: -432px 0"></span> in the toolbar.\n'
    )
    text, used = t.replace_toolbar_icons(line, "img")
    assert text == (
        "- click the **Next Primitive** icon ![Next Primitive toolbar button]"
        "(img/tbt-inline-trace.png) in the toolbar.\n"
    )
    assert used == {"inline-trace"}


def test_unknown_toolbar_sprite_offset_is_an_error():
    line = '<span class="toolbar-icon" style="background-position: -999px 0"></span>\n'
    with pytest.raises(ValueError, match="-999"):
        t.replace_toolbar_icons(line, "img")


def test_relative_to_page_computes_posix_paths_from_the_page_directory():
    assert t.relative_to_page("windows-ui-guide/tracer.md", "windows-ui-guide/img") == "img"
    assert t.relative_to_page("windows-ui-guide/tracer/index.md", "windows-ui-guide/img") == "../img"

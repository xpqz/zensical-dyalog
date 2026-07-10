"""Unit surface for the Zensical-checker validation tool.

The parser and differ are exercised with captured checker output; the
full-corpus `zensical build` in main() is an integration step, run during
the cycle and recorded in docs/prs/21.md, not unit-tested here.
"""

import textwrap

import check_flatten

# One diagnostic block as Zensical emits it, colour escapes and all.
ANSI_ONE_ISSUE = (
    "\x1b[33mWarning:\x1b[0m anchor does not exist\n"
    "   \x1b[38;5;246m╭─\x1b[0m\x1b[38;5;246m[\x1b[0m guide/page.md:3:98 \x1b[38;5;246m]\x1b[0m\n"
    "   \x1b[38;5;246m│\x1b[0m\n"
    " \x1b[38;5;246m3 │\x1b[0m APL text with a [](#Missing) link.\n"
    "   \x1b[38;5;240m│\x1b[0m                 \x1b[33m────┬───\x1b[0m\n"
    "   \x1b[38;5;240m│\x1b[0m                     \x1b[33m╰──\x1b[0m anchor does not exist\n"
    "\x1b[38;5;246m───╯\x1b[0m\n"
)

TWO_ISSUES = textwrap.dedent(
    """\
    Build started
    Warning: anchor does not exist
       ╭─[ guide/page.md:3:98 ]
       │
     3 │ text [](#Missing)
    ───╯
    Warning: page does not exist
       ╭─[ other/index.md:16:13 ]
       │
     16 │ see [x](nope.md)
    ───╯
    2 issues found
    Build finished in 1.00s
    """
)

CLEAN = "Build started\nNo issues found\nBuild finished in 1.00s\n"

# A build that died before the checker ran: no summary line at all.
CRASHED = "Build started\nthread 'main' panicked\n"


# --- parse_issues ------------------------------------------------------


def test_parse_extracts_type_and_location():
    assert check_flatten.parse_issues(TWO_ISSUES) == {
        "anchor does not exist @ guide/page.md:3:98",
        "page does not exist @ other/index.md:16:13",
    }


def test_parse_strips_ansi_colour_escapes():
    assert check_flatten.parse_issues(ANSI_ONE_ISSUE) == {
        "anchor does not exist @ guide/page.md:3:98"
    }


def test_parse_returns_empty_set_on_a_clean_build():
    assert check_flatten.parse_issues(CLEAN) == set()


# --- parse_issue_count -------------------------------------------------


def test_count_reads_the_summary_tally():
    assert check_flatten.parse_issue_count(TWO_ISSUES) == 2


def test_count_is_zero_for_a_clean_build():
    assert check_flatten.parse_issue_count(CLEAN) == 0


def test_count_is_none_when_the_summary_line_is_absent():
    assert check_flatten.parse_issue_count(CRASHED) is None


# --- load_baseline -----------------------------------------------------


def test_load_baseline_ignores_comments_and_blank_lines(tmp_path):
    baseline = tmp_path / "known-issues.txt"
    baseline.write_text(
        "# a comment\n"
        "anchor does not exist @ guide/page.md:3:98\n"
        "\n"
        "page does not exist @ other/index.md:16:13\n"
    )
    assert check_flatten.load_baseline(baseline) == {
        "anchor does not exist @ guide/page.md:3:98",
        "page does not exist @ other/index.md:16:13",
    }


# --- diff_issues -------------------------------------------------------


def test_diff_flags_issues_absent_from_the_baseline():
    current = {"anchor does not exist @ a.md:1:1", "page does not exist @ b.md:2:2"}
    baseline = {"anchor does not exist @ a.md:1:1"}
    new, resolved = check_flatten.diff_issues(current, baseline)
    assert new == {"page does not exist @ b.md:2:2"}
    assert resolved == set()


def test_diff_reports_baseline_issues_no_longer_present():
    current = {"anchor does not exist @ a.md:1:1"}
    baseline = {"anchor does not exist @ a.md:1:1", "page does not exist @ b.md:2:2"}
    new, resolved = check_flatten.diff_issues(current, baseline)
    assert new == set()
    assert resolved == {"page does not exist @ b.md:2:2"}


def test_diff_is_clean_when_current_is_a_subset_of_the_baseline():
    baseline = {"anchor does not exist @ a.md:1:1", "page does not exist @ b.md:2:2"}
    new, resolved = check_flatten.diff_issues(set(), baseline)
    assert new == set()


# --- assess (the gate policy) ------------------------------------------

BASELINE = {
    "anchor does not exist @ guide/page.md:3:98",
    "page does not exist @ other/index.md:16:13",
}


def test_assess_passes_when_issues_match_the_baseline():
    result = check_flatten.assess(TWO_ISSUES, 0, BASELINE)
    assert result.ok
    assert result.new == set()


def test_assess_fails_on_a_non_zero_build_exit():
    result = check_flatten.assess(TWO_ISSUES, 1, BASELINE)
    assert not result.ok


def test_assess_fails_when_the_summary_line_is_missing():
    result = check_flatten.assess(CRASHED, 0, set())
    assert not result.ok


def test_assess_fails_when_parsed_count_disagrees_with_the_summary():
    # Summary claims two, but only one diagnostic block is present.
    mangled = TWO_ISSUES.replace(
        "Warning: page does not exist\n   ╭─[ other/index.md:16:13 ]\n   │\n"
        " 16 │ see [x](nope.md)\n───╯\n",
        "",
    )
    result = check_flatten.assess(mangled, 0, BASELINE)
    assert not result.ok


def test_assess_fails_and_names_an_issue_outside_the_baseline():
    # Baseline knows only the anchor issue; the page issue is new.
    partial = {"anchor does not exist @ guide/page.md:3:98"}
    result = check_flatten.assess(TWO_ISSUES, 0, partial)
    assert not result.ok
    assert result.new == {"page does not exist @ other/index.md:16:13"}


def test_assess_passes_and_reports_resolved_baseline_entries():
    extra = BASELINE | {"anchor does not exist @ gone/page.md:9:9"}
    result = check_flatten.assess(TWO_ISSUES, 0, extra)
    assert result.ok
    assert result.resolved == {"anchor does not exist @ gone/page.md:9:9"}


# --- main exit-code wiring ---------------------------------------------


def test_main_returns_zero_on_a_clean_gate(tmp_path):
    baseline = tmp_path / "known-issues.txt"
    baseline.write_text(
        "anchor does not exist @ guide/page.md:3:98\n"
        "page does not exist @ other/index.md:16:13\n"
    )
    rc = check_flatten.main(
        ["--baseline", str(baseline)], runner=lambda _dir: (TWO_ISSUES, 0)
    )
    assert rc == 0


def test_main_returns_one_when_the_gate_fails(tmp_path):
    baseline = tmp_path / "known-issues.txt"
    baseline.write_text("anchor does not exist @ guide/page.md:3:98\n")
    rc = check_flatten.main(
        ["--baseline", str(baseline)], runner=lambda _dir: (TWO_ISSUES, 0)
    )
    assert rc == 1

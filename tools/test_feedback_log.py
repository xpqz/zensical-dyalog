"""Behavioural surface for the feedback access-log reducer.

A combined Apache line for /feedback.gif must yield (page, rating); the page
comes from the Referer when it is one of the allowed hosts and from the `p`
parameter otherwise; foreign or missing Referers are handled explicitly. The
aggregate written for the dashboard has the same shape the stub produces.
"""

from feedback_log import (
    load_aggregate,
    normalize_page,
    parse_line,
    write_aggregate,
)

HOSTS = {"docs.dyalog.com", "localhost"}

CSV = (
    '192.0.2.10 - - [18/Sep/2026:14:33:00 +0100] '
    '"GET /feedback.gif?r=1&p=/ignored/&n=1695037000000 HTTP/1.1" 200 43 '
    '"https://docs.dyalog.com/language-reference-guide/system-functions/csv/" '
    '"Mozilla/5.0 (X11; Linux x86_64)"'
)


def test_combined_line_yields_page_from_referer_and_rating():
    assert parse_line(CSV, HOSTS) == (
        "/language-reference-guide/system-functions/csv/",
        "1",
    )


def test_version_prefix_is_stripped():
    line = CSV.replace(
        "/language-reference-guide/system-functions/csv/",
        "/21.0/programming-reference-guide/introduction/arrays/numbers/",
    )
    assert parse_line(line, HOSTS) == (
        "/programming-reference-guide/introduction/arrays/numbers/",
        "1",
    )


def test_referer_wins_over_the_p_parameter():
    line = CSV.replace("p=/ignored/", "p=/other/page/")
    result = parse_line(line, HOSTS)
    assert result is not None
    page, _ = result
    assert page == "/language-reference-guide/system-functions/csv/"


def test_foreign_referer_is_dropped():
    line = CSV.replace("https://docs.dyalog.com/", "https://spam.example/")
    assert parse_line(line, HOSTS) is None


def test_missing_referer_falls_back_to_p():
    line = CSV.replace(
        '"https://docs.dyalog.com/language-reference-guide/system-functions/csv/"',
        '"-"',
    ).replace("p=/ignored/", "p=/fallback/page/")
    assert parse_line(line, HOSTS) == ("/fallback/page/", "1")


def test_line_without_rating_is_ignored():
    line = CSV.replace("r=1&", "")
    assert parse_line(line, HOSTS) is None


def test_unrelated_line_is_ignored():
    assert parse_line('192.0.2.1 - - [18/Sep/2026:14:33:00 +0100] "GET / HTTP/1.1" 200 1', HOSTS) is None


def test_normalize_page_adds_slash_and_strips_prefix():
    assert normalize_page("21.0/foo/bar/") == "/foo/bar/"
    assert normalize_page("/foo/bar/") == "/foo/bar/"


def test_write_and_load_aggregate_round_trip(tmp_path):
    out = tmp_path / "feedback.json"
    pages = {"/a/": {"0": 2, "1": 3}, "/b/": {"0": 1}}
    total = write_aggregate(out, pages, ["access.log"])
    assert total == 6
    assert load_aggregate(out) == {"/a/": {"0": 2, "1": 3}, "/b/": {"0": 1}}


def test_merge_accumulates(tmp_path):
    out = tmp_path / "feedback.json"
    write_aggregate(out, {"/a/": {"1": 1}}, ["one.log"])
    pages = load_aggregate(out)
    pages.setdefault("/a/", {})["1"] = pages["/a/"].get("1", 0) + 1
    write_aggregate(out, pages, ["two.log"])
    assert load_aggregate(out) == {"/a/": {"1": 2}}

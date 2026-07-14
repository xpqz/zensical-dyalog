"""Behavioural surface for the out-of-place conversion script.

Every test drives the public functions of convert.py against the
miniature monorepo fixture in conftest.py. The fixture uses two
sub-projects; the hardcoded fourteen-name default is asserted separately
against the root nav of the real corpus.
"""

import tomllib

import pytest

import convert
from fixture_tree import SUB_NAMES, MATHJAX_JS, PNG_BYTES, tree_digest


def run(source, output, **kwargs):
    kwargs.setdefault("subprojects", SUB_NAMES)
    return convert.convert(source, output, **kwargs)


# --- content copying ---------------------------------------------------


def test_copies_each_subproject_docs_tree_to_docs_sub_preserving_bytes(
    source_tree, out_dir
):
    run(source_tree, out_dir)
    copied = (
        out_dir
        / "docs"
        / "release-notes"
        / "announcements"
        / "deprecated-functionality.md"
    )
    original = (
        source_tree
        / "release-notes"
        / "docs"
        / "announcements"
        / "deprecated-functionality.md"
    )
    assert copied.read_bytes() == original.read_bytes()
    assert (out_dir / "docs" / "compiler-user-guide" / "basic-usage.md").is_file()


def test_copies_binary_assets_byte_identical(source_tree, out_dir):
    run(source_tree, out_dir)
    assert (
        out_dir / "docs" / "release-notes" / "images" / "logo.png"
    ).read_bytes() == PNG_BYTES


def test_copies_root_docs_pages_to_the_docs_root(source_tree, out_dir):
    run(source_tree, out_dir)
    assert (out_dir / "docs" / "conventions.md").is_file()
    assert (out_dir / "docs" / "index.md").read_text() == "# Documentation\n"


def test_copies_documentation_assets_into_docs(source_tree, out_dir):
    run(source_tree, out_dir)
    assert (
        out_dir / "docs" / "documentation-assets" / "css" / "main.css"
    ).read_text() == "body {}\n"


def test_does_not_carry_vcs_metadata_into_the_output(source_tree, out_dir):
    run(source_tree, out_dir)
    assert not (out_dir / "docs" / "documentation-assets" / ".git").exists()
    assert list(out_dir.rglob(".git")) == []


def test_places_the_version_warning_theme_override(source_tree, out_dir):
    run(source_tree, out_dir)
    override = out_dir / "overrides" / "main.html"
    assert override.is_file()
    text = override.read_text()
    assert 'extends "base.html"' in text
    assert "block outdated" in text
    # The block must carry the warning and a link to latest, not be empty (an
    # empty outdated block renders a blank banner, the no-op this exists to
    # prevent).
    assert "<a " in text
    assert "latest" in text.lower()


def test_rewrites_raw_html_headings_in_output_markdown(source_tree, out_dir):
    run(source_tree, out_dir)
    page = (out_dir / "docs" / "compiler-user-guide" / "raw-heading.md").read_text()
    assert "<h1" not in page
    assert any(line.startswith("# ") for line in page.splitlines())
    assert "Widget" in page and "Object" in page


def test_leaves_markdown_without_a_raw_heading_unchanged(source_tree, out_dir):
    run(source_tree, out_dir)
    original = (source_tree / "compiler-user-guide" / "docs" / "basic-usage.md").read_text()
    copied = (out_dir / "docs" / "compiler-user-guide" / "basic-usage.md").read_text()
    assert copied == original


def test_does_not_carry_subproject_mathjax_duplicates(source_tree, out_dir):
    run(source_tree, out_dir)
    assert not (
        out_dir / "docs" / "release-notes" / "javascripts" / "mathjax.js"
    ).exists()


def test_keeps_one_canonical_mathjax_at_docs_javascripts(source_tree, out_dir):
    run(source_tree, out_dir)
    copies = list((out_dir / "docs").rglob("mathjax.js"))
    assert copies == [out_dir / "docs" / "javascripts" / "mathjax.js"]
    assert copies[0].read_text() == MATHJAX_JS


def test_never_writes_to_the_source_tree(source_tree, out_dir):
    before = tree_digest(source_tree)
    run(source_tree, out_dir)
    assert tree_digest(source_tree) == before


def test_rerun_removes_output_files_whose_source_disappeared(source_tree, out_dir):
    run(source_tree, out_dir)
    removed = source_tree / "release-notes" / "docs" / "system-requirements.md"
    removed.unlink()
    run(source_tree, out_dir)
    assert not (out_dir / "docs" / "release-notes" / "system-requirements.md").exists()


def test_rerun_removes_stray_files_planted_in_the_output(source_tree, out_dir):
    run(source_tree, out_dir)
    (out_dir / "junk.txt").write_text("stray\n")
    (out_dir / "docs" / "stray.md").write_text("# Stray\n")
    run(source_tree, out_dir)
    assert not (out_dir / "junk.txt").exists()
    assert not (out_dir / "docs" / "stray.md").exists()


def test_raises_file_not_found_when_an_expected_subproject_is_missing(
    source_tree, out_dir
):
    with pytest.raises(FileNotFoundError, match="object-reference"):
        convert.convert(
            source_tree, out_dir, subprojects=SUB_NAMES + ("object-reference",)
        )


def test_writes_nothing_outside_the_output_directory(source_tree, out_dir, tmp_path):
    repo_docs = tmp_path / "repo" / "docs" / "plans"
    repo_docs.mkdir(parents=True)
    (repo_docs / "plan.md").write_text("# Plan\n")

    def outside_digest():
        prefix = out_dir.name + "/"
        return {
            path: digest
            for path, digest in tree_digest(tmp_path).items()
            if not path.startswith(prefix)
        }

    before = outside_digest()
    run(source_tree, out_dir)
    assert outside_digest() == before


# --- config merging ----------------------------------------------------


@pytest.fixture
def merged(source_tree):
    root = convert.load_yaml(source_tree / "mkdocs.yml")
    subs = {
        name: convert.load_yaml(source_tree / name / "mkdocs.yml") for name in SUB_NAMES
    }
    return convert.merge_configs(root, subs)


def plugin_names(plugins):
    return [p if isinstance(p, str) else next(iter(p)) for p in plugins]


def test_raises_value_error_when_nav_includes_an_unknown_subproject(source_tree):
    root = convert.load_yaml(source_tree / "mkdocs.yml")
    subs = {
        "release-notes": convert.load_yaml(source_tree / "release-notes" / "mkdocs.yml")
    }
    with pytest.raises(ValueError, match="compiler-user-guide"):
        convert.merge_configs(root, subs)


def test_replaces_include_entries_with_prefixed_subproject_nav(merged):
    release_notes_section = merged["nav"][0]["Release Notes"]
    included = release_notes_section[0]["v21.0 Release Notes"]
    assert included[0] == "release-notes/index.md"
    assert included[2] == {
        "System Requirements": "release-notes/system-requirements.md"
    }


def test_preserves_top_level_heading_order_and_titles(merged):
    assert [next(iter(entry)) for entry in merged["nav"]] == [
        "Release Notes",
        "Code Tooling",
        "About",
    ]


def test_prefixes_nested_nav_sections_recursively(merged):
    included = merged["nav"][0]["Release Notes"][0]["v21.0 Release Notes"]
    announcements = included[1]["Announcements"]
    assert announcements[0] == {"Announcements": "release-notes/announcements/index.md"}
    assert announcements[1] == {
        "Deprecated Functionality": "release-notes/announcements/deprecated-functionality.md"
    }


def test_keeps_root_level_nav_pages_unprefixed(merged):
    about = merged["nav"][2]["About"]
    assert about == [{"Conventions": "conventions.md"}]


def test_drops_monorepo_site_urls_and_caption_plugins(merged):
    names = plugin_names(merged["plugins"])
    assert "monorepo" not in names
    assert "site-urls" not in names
    assert "caption" not in names
    assert {"privacy", "search", "macros", "minify"} <= set(names)


def test_folds_markdown_extensions_into_a_superset_with_root_precedence(merged):
    extensions = merged["markdown_extensions"]
    names = [e if isinstance(e, str) else next(iter(e)) for e in extensions]
    assert names.count("pymdownx.highlight") == 1
    assert "footnotes" in names
    assert "markdown_tables_extended" in names
    highlight = next(
        e for e in extensions if not isinstance(e, str) and "pymdownx.highlight" in e
    )
    assert highlight["pymdownx.highlight"] == {
        "use_pygments": False,
        "pygments_lang_class": True,
    }


def test_folds_extra_with_root_precedence(merged):
    assert merged["extra"]["version_maj"] == 21
    assert merged["extra"]["version_majmin"] == "21.0"


def test_wires_the_caption_extension_into_markdown_extensions(merged):
    names = [
        e if isinstance(e, str) else next(iter(e))
        for e in merged["markdown_extensions"]
    ]
    assert "dyalog_caption" in names


def test_takes_extra_css_from_the_root_alone(merged):
    assert merged["extra_css"] == [
        "documentation-assets/css/main.css",
        "documentation-assets/css/extra.css",
        "documentation-assets/css/admonition-ucmdhelp.css",
    ]


def test_consolidates_extra_javascript_to_single_mathjax_and_external_urls(merged):
    assert merged["extra_javascript"] == [
        "javascripts/mathjax.js",
        "https://unpkg.com/mathjax@3/es5/tex-mml-chtml.js",
    ]


def test_takes_site_name_copyright_and_theme_from_root(merged):
    assert merged["site_name"] == "Documentation"
    assert merged["copyright"].startswith("Copyright &copy; 1982-$CURRENT_YEAR")
    assert (
        merged["theme"]["logo"] == "documentation-assets/images/dyalog-logo_white.svg"
    )
    assert merged["theme"]["font"] == {"text": "Be Vietnam Pro"}


def test_sets_site_url_to_the_production_canonical(merged):
    # Versioned deploy needs site_url: Zensical prefixes it with the version
    # (docs.dyalog.com/21.0/) only when it is set, and the source config has
    # none. The canonical production host is docs.dyalog.com.
    assert merged["site_url"] == "https://docs.dyalog.com/"


def test_sets_theme_custom_dir_for_the_version_warning(merged):
    # The outdated-version warning banner is a theme override; custom_dir points
    # Zensical at it. A top-level overrides/ (not under docs/) keeps the template
    # out of the published content. The selector itself is native.
    assert merged["theme"]["custom_dir"] == "overrides"


# --- helpers -----------------------------------------------------------


def test_prefix_nav_prefixes_page_paths_and_leaves_urls_and_titles():
    nav = [
        "index.md",
        {"Section": [{"Page": "sub/page.md"}, "sub/other.md"]},
        {"External": "https://example.com/x/"},
    ]
    assert convert.prefix_nav(nav, "guide") == [
        "guide/index.md",
        {"Section": [{"Page": "guide/sub/page.md"}, "guide/sub/other.md"]},
        {"External": "https://example.com/x/"},
    ]


def test_load_yaml_reads_quoted_include_entries_as_plain_strings(source_tree):
    root = convert.load_yaml(source_tree / "mkdocs.yml")
    release_notes_section = root["nav"][0]["Release Notes"]
    assert release_notes_section[0] == {
        "v21.0 Release Notes": "!include ./release-notes/mkdocs.yml"
    }


# --- serialisation -----------------------------------------------------


def test_writes_zensical_toml_under_project_with_merged_values(source_tree, out_dir):
    run(source_tree, out_dir)
    with open(out_dir / "zensical.toml", "rb") as f:
        data = tomllib.load(f)
    project = data["project"]
    assert project["site_name"] == "Documentation"
    assert project["extra"]["version_majmin"] == "21.0"
    assert "navigation.instant" in project["theme"]["features"]
    assert "markdown_tables_extended" in str(project["markdown_extensions"])


def test_zensical_toml_plugins_are_exactly_the_supported_four(source_tree, out_dir):
    run(source_tree, out_dir)
    with open(out_dir / "zensical.toml", "rb") as f:
        project = tomllib.load(f)["project"]
    names = plugin_names(project["plugins"])
    assert set(names) == {"privacy", "search", "macros", "minify"}


def test_zensical_toml_includes_the_caption_extension(source_tree, out_dir):
    run(source_tree, out_dir)
    with open(out_dir / "zensical.toml", "rb") as f:
        project = tomllib.load(f)["project"]
    assert "dyalog_caption" in str(project["markdown_extensions"])


def test_zensical_toml_carries_site_url(source_tree, out_dir):
    run(source_tree, out_dir)
    with open(out_dir / "zensical.toml", "rb") as f:
        project = tomllib.load(f)["project"]
    assert project["site_url"] == "https://docs.dyalog.com/"


def test_zensical_toml_sets_theme_custom_dir(source_tree, out_dir):
    run(source_tree, out_dir)
    with open(out_dir / "zensical.toml", "rb") as f:
        project = tomllib.load(f)["project"]
    assert project["theme"]["custom_dir"] == "overrides"


def test_zensical_toml_is_the_only_config_emitted(source_tree, out_dir):
    run(source_tree, out_dir)
    assert (out_dir / "zensical.toml").is_file()
    assert not (out_dir / "mkdocs.yml").exists()


def test_two_runs_produce_byte_identical_output(source_tree, out_dir):
    run(source_tree, out_dir)
    first = tree_digest(out_dir)
    run(source_tree, out_dir)
    assert tree_digest(out_dir) == first


def test_default_subproject_list_is_the_fourteen_from_the_root_nav():
    assert convert.SUBPROJECTS == (
        "release-notes",
        "earlier-release-notes",
        "language-reference-guide",
        "programming-reference-guide",
        "dotnet-interface-guide",
        "compiler-user-guide",
        "shared-code-files-user-guide",
        "windows-installation-and-configuration-guide",
        "windows-ui-guide",
        "object-reference",
        "interface-guide",
        "dotnet-framework-interface-guide",
        "unix-installation-and-configuration-guide",
        "unix-user-guide",
    )

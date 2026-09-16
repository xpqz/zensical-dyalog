"""Behavioural surface for the out-of-place conversion script.

Every test drives the public functions of convert.py against the
miniature monorepo fixture in conftest.py. The fixture uses two
sub-projects; the hardcoded fourteen-name default is asserted separately
against the root nav of the real corpus.
"""

import tomllib

import pytest

import convert
from fixture_tree import (
    INDEX_OVERLAY_MD,
    PNG_BYTES,
    SUB_NAMES,
    tree_digest,
)


def run(source, output, overlay, **kwargs):
    kwargs.setdefault("subprojects", SUB_NAMES)
    return convert.convert(source, output, overlay=overlay, **kwargs)


def read_toml(out_dir):
    with open(out_dir / "zensical.toml", "rb") as f:
        return tomllib.load(f)["project"]


# --- content copying ---------------------------------------------------


def test_copies_each_subproject_docs_tree_to_docs_sub_preserving_bytes(
    source_tree, out_dir, overlay
):
    run(source_tree, out_dir, overlay)
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


def test_copies_binary_assets_byte_identical(source_tree, out_dir, overlay):
    run(source_tree, out_dir, overlay)
    assert (
        out_dir / "docs" / "release-notes" / "images" / "logo.png"
    ).read_bytes() == PNG_BYTES


def test_copies_root_docs_pages_to_the_docs_root(source_tree, out_dir, overlay):
    run(source_tree, out_dir, overlay)
    assert (out_dir / "docs" / "conventions.md").is_file()


def test_does_not_copy_documentation_assets(source_tree, out_dir, overlay):
    # documentation-assets is a git submodule in the output repo, tracking the
    # retired MkDocs style. It is not convert's to manage, so convert must not
    # copy the source checkout's copy in.
    run(source_tree, out_dir, overlay)
    assert not (out_dir / "docs" / "documentation-assets").exists()


@pytest.mark.parametrize("assets", ["documentation-assets", "documentation-assetsz"])
def test_preserves_the_asset_directories_on_regen(source_tree, out_dir, overlay, assets):
    run(source_tree, out_dir, overlay)
    # Stand in for the asset checkout landing at its path.
    sub = out_dir / "docs" / assets / "css"
    sub.mkdir(parents=True, exist_ok=True)
    (sub / "main.css").write_text("ASSET SENTINEL\n")
    # Regenerating must not wipe the assets.
    run(source_tree, out_dir, overlay)
    assert (sub / "main.css").read_text() == "ASSET SENTINEL\n"


def test_does_not_rewrite_markdown_inside_the_asset_directories(source_tree, out_dir, overlay):
    run(source_tree, out_dir, overlay)
    # A markdown file inside the assets with a raw <h1> must be left
    # byte-for-byte: the transforms must never write into the assets.
    sub = out_dir / "docs" / "documentation-assetsz"
    sub.mkdir(parents=True, exist_ok=True)
    raw = '<h1 class="heading"><span class="name">Asset</span></h1>\n\n!!! Hint "x"\n'
    (sub / "README.md").write_text(raw)
    run(source_tree, out_dir, overlay)
    assert (sub / "README.md").read_text() == raw


def test_places_the_version_warning_theme_override(source_tree, out_dir, overlay):
    run(source_tree, out_dir, overlay)
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


def test_rewrites_raw_html_title_to_plain_heading_and_classifier(source_tree, out_dir, overlay):
    run(source_tree, out_dir, overlay)
    page = (out_dir / "docs" / "compiler-user-guide" / "raw-heading.md").read_text()
    assert page == "# Widget\n\nObject\n\nBody text.\n"


def test_rewrites_styled_title_with_syntax_block_and_key_link(source_tree, out_dir, overlay):
    run(source_tree, out_dir, overlay)
    page = (out_dir / "docs" / "compiler-user-guide" / "styled-title.md").read_text()
    assert page.startswith(
        "# Comma Separated Values\n\n```apl\n{R}←{X} ⎕CSV Y\n```\n"
        "[Key to notation](../language-reference-guide/key-to-notation.md)\n\n"
    )
    assert "## Examples\n```apl\n" in page
    assert "{{key}}" not in page


def test_applies_admonition_shaded_and_example_transforms(source_tree, out_dir, overlay):
    run(source_tree, out_dir, overlay)
    page = (out_dir / "docs" / "compiler-user-guide" / "examples.md").read_text()
    assert '!!! tip "Hints and Recommendations"' in page
    assert "|`0` (default)|do not repair|" in page
    assert "highlighted thus" not in page
    assert "## Example\n```apl" in page


def test_replaces_toolbar_icons_with_overlay_images(source_tree, out_dir, overlay):
    run(source_tree, out_dir, overlay)
    page = (out_dir / "docs" / "compiler-user-guide" / "toolbar.md").read_text()
    assert "![Exec toolbar button](../windows-ui-guide/img/tbt-exec.png)" in page
    assert (out_dir / "docs" / "windows-ui-guide" / "img" / "tbt-exec.png").read_bytes() == PNG_BYTES


def test_refuses_a_toolbar_icon_the_overlay_does_not_provide(source_tree, out_dir, overlay):
    (overlay / "windows-ui-guide" / "img" / "tbt-exec.png").unlink()
    with pytest.raises(ValueError, match="exec"):
        run(source_tree, out_dir, overlay)


def test_leaves_markdown_without_a_house_pattern_unchanged(source_tree, out_dir, overlay):
    run(source_tree, out_dir, overlay)
    original = (source_tree / "compiler-user-guide" / "docs" / "basic-usage.md").read_text()
    copied = (out_dir / "docs" / "compiler-user-guide" / "basic-usage.md").read_text()
    assert copied == original


def test_carries_no_mathjax(source_tree, out_dir, overlay):
    run(source_tree, out_dir, overlay)
    assert list((out_dir / "docs").rglob("mathjax.js")) == []
    assert not (out_dir / "docs" / "javascripts").exists()
    assert not (out_dir / "docs" / "release-notes" / "javascripts").exists()


def test_never_writes_to_the_source_tree(source_tree, out_dir, overlay):
    before = tree_digest(source_tree)
    run(source_tree, out_dir, overlay)
    assert tree_digest(source_tree) == before


def test_rerun_removes_output_files_whose_source_disappeared(source_tree, out_dir, overlay):
    run(source_tree, out_dir, overlay)
    removed = source_tree / "release-notes" / "docs" / "system-requirements.md"
    removed.unlink()
    run(source_tree, out_dir, overlay)
    assert not (out_dir / "docs" / "release-notes" / "system-requirements.md").exists()


def test_rerun_removes_stray_files_planted_in_the_output(source_tree, out_dir, overlay):
    run(source_tree, out_dir, overlay)
    (out_dir / "junk.txt").write_text("stray\n")
    (out_dir / "docs" / "stray.md").write_text("# Stray\n")
    run(source_tree, out_dir, overlay)
    assert not (out_dir / "junk.txt").exists()
    assert not (out_dir / "docs" / "stray.md").exists()


def test_raises_file_not_found_when_an_expected_subproject_is_missing(
    source_tree, out_dir, overlay
):
    with pytest.raises(FileNotFoundError, match="object-reference"):
        convert.convert(
            source_tree,
            out_dir,
            subprojects=SUB_NAMES + ("object-reference",),
            overlay=overlay,
        )


def test_writes_nothing_outside_the_output_directory(source_tree, out_dir, overlay, tmp_path):
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
    run(source_tree, out_dir, overlay)
    assert outside_digest() == before


# --- content overlay ---------------------------------------------------


def test_overlay_replacement_page_is_used_when_its_sidecar_matches(
    source_tree, out_dir, overlay
):
    run(source_tree, out_dir, overlay)
    assert (out_dir / "docs" / "index.md").read_text() == INDEX_OVERLAY_MD


def test_stale_overlay_sidecar_aborts_before_anything_is_written(
    source_tree, out_dir, overlay
):
    (source_tree / "docs" / "index.md").write_text("# Documentation\n\nEdited upstream.\n")
    with pytest.raises(ValueError, match="index.md"):
        run(source_tree, out_dir, overlay)
    assert not out_dir.exists()


def test_overlay_replacement_without_a_sidecar_is_refused(source_tree, out_dir, overlay):
    (overlay / "index.md.source-sha256").unlink()
    with pytest.raises(ValueError, match="sidecar"):
        run(source_tree, out_dir, overlay)


def test_overlay_sidecar_for_a_vanished_source_page_is_refused(source_tree, out_dir, overlay):
    (source_tree / "docs" / "index.md").unlink()
    with pytest.raises(ValueError, match="no longer exists"):
        run(source_tree, out_dir, overlay)


def test_source_path_for_maps_output_paths_back_to_the_monorepo(source_tree):
    mounts = {"compiler-user-guide": "compiler-user-guide", "net-interface-guide": "dotnet-interface-guide"}
    assert convert.source_path_for("index.md", source_tree, mounts) == (
        source_tree / "docs" / "index.md"
    )
    assert convert.source_path_for(
        "compiler-user-guide/basic-usage.md", source_tree, mounts
    ) == (source_tree / "compiler-user-guide" / "docs" / "basic-usage.md")
    assert convert.source_path_for(
        "net-interface-guide/installation.md", source_tree, mounts
    ) == (source_tree / "dotnet-interface-guide" / "docs" / "installation.md")


# --- mount points ------------------------------------------------------


def test_guide_alias_matches_the_live_site_geometry():
    # mkdocs-monorepo-plugin mounts a guide at its site_name when that is a
    # plain path token, otherwise at its slug. The live site serves the .NET
    # guides at net-interface-guide/ and net-framework-interface-guide/.
    assert convert.guide_alias("Language Reference Guide") == "language-reference-guide"
    assert convert.guide_alias("UNIX User Guide") == "unix-user-guide"
    assert convert.guide_alias(".NET Interface Guide") == "net-interface-guide"
    assert convert.guide_alias(".NET Framework Interface Guide") == "net-framework-interface-guide"
    assert convert.guide_alias("object-reference") == "object-reference"


def test_mount_points_map_alias_to_directory_and_reject_collisions():
    subs = {
        "dotnet-interface-guide": {"site_name": ".NET Interface Guide"},
        "release-notes": {"site_name": "Release Notes"},
        "unnamed": {},
    }
    assert convert.mount_points(subs) == {
        "net-interface-guide": "dotnet-interface-guide",
        "release-notes": "release-notes",
        "unnamed": "unnamed",
    }
    with pytest.raises(ValueError, match="both mount at"):
        convert.mount_points({"a": {"site_name": "Same Name"}, "b": {"site_name": "same-name"}})


def test_mounts_each_guide_at_its_alias(source_tree, out_dir, overlay):
    run(source_tree, out_dir, overlay)
    assert (out_dir / "docs" / "net-interface-guide" / "installation.md").is_file()
    assert not (out_dir / "docs" / "dotnet-interface-guide").exists()
    project = read_toml(out_dir)
    dotnet = project["nav"][1]["Code Tooling"][0][".NET Interface"]
    assert dotnet == ["net-interface-guide/index.md", {"Installation": "net-interface-guide/installation.md"}]


# --- config merging ----------------------------------------------------


@pytest.fixture
def merged(source_tree):
    root = convert.load_yaml(source_tree / "mkdocs.yml")
    subs = {
        name: convert.load_yaml(source_tree / name / "mkdocs.yml") for name in SUB_NAMES
    }
    return convert.merge_configs(root, subs)


def entry_names(entries):
    return [e if isinstance(e, str) else next(iter(e)) for e in entries]


def test_raises_value_error_when_nav_includes_an_unknown_subproject(source_tree):
    root = convert.load_yaml(source_tree / "mkdocs.yml")
    subs = {
        "release-notes": convert.load_yaml(source_tree / "release-notes" / "mkdocs.yml")
    }
    with pytest.raises(ValueError, match="dotnet-interface-guide"):
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


def test_prefixes_included_nav_with_the_mount_alias_not_the_directory(merged):
    dotnet = merged["nav"][1]["Code Tooling"][0][".NET Interface"]
    assert dotnet[0] == "net-interface-guide/index.md"


def test_keeps_root_level_nav_pages_unprefixed(merged):
    about = merged["nav"][2]["About"]
    assert about == [{"Conventions": "conventions.md"}]


def test_carries_only_the_source_values_the_template_needs(merged):
    # theme, stylesheets, scripts, plugins and copyright are MkDocs house
    # configuration; the Zensical template owns their replacements.
    assert set(merged) == {"site_name", "repo_url", "nav", "markdown_extensions", "extra"}
    assert merged["site_name"] == "Documentation"
    assert merged["repo_url"] == "https://github.com/dyalog/documentation"


def test_folds_markdown_extensions_into_a_superset_with_root_precedence(merged):
    extensions = merged["markdown_extensions"]
    names = entry_names(extensions)
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


def test_drops_arithmatex_and_wires_the_caption_extension(merged):
    names = entry_names(merged["markdown_extensions"])
    assert "pymdownx.arithmatex" not in names
    assert "dyalog_caption" in names


def test_folds_extra_with_root_precedence(merged):
    assert merged["extra"]["version_maj"] == 21
    assert merged["extra"]["version_majmin"] == "21.0"
    assert merged["extra"]["version"] == {"provider": "mike"}


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


def test_writes_zensical_toml_under_project_with_merged_values(source_tree, out_dir, overlay):
    run(source_tree, out_dir, overlay)
    project = read_toml(out_dir)
    assert project["site_name"] == "Documentation"
    assert project["repo_url"] == "https://github.com/dyalog/documentation"
    assert project["extra"]["version_majmin"] == "21.0"
    assert project["nav"][0]["Release Notes"][0]["v21.0 Release Notes"][0] == (
        "release-notes/index.md"
    )
    assert "markdown_tables_extended" in str(project["markdown_extensions"])
    assert "dyalog_caption" in str(project["markdown_extensions"])
    assert "arithmatex" not in str(project["markdown_extensions"])


def test_zensical_toml_takes_the_house_configuration_from_the_template(
    source_tree, out_dir, overlay
):
    project = (run(source_tree, out_dir, overlay), read_toml(out_dir))[1]
    assert entry_names(project["plugins"]) == ["search", "macros"]
    assert project["extra_css"] == ["documentation-assetsz/css/dyalog.css"]
    assert "extra_javascript" not in project
    assert project["site_url"] == "https://docs.dyalog.com/"
    assert project["theme"]["custom_dir"] == "overrides"
    assert project["theme"]["variant"] == "classic"
    assert project["theme"]["font"] is False
    assert "content.code.copy" in project["theme"]["features"]
    assert "navigation.footer" not in project["theme"]["features"]
    assert [p["scheme"] for p in project["theme"]["palette"]] == ["default", "slate"]
    assert "Zensical" in project["copyright"]


def test_zensical_toml_keeps_the_template_comments(source_tree, out_dir, overlay):
    run(source_tree, out_dir, overlay)
    text = (out_dir / "zensical.toml").read_text()
    assert "# House style" in text
    assert "@@" not in text


def test_render_refuses_a_template_missing_a_placeholder(merged):
    with pytest.raises(ValueError, match="@@HEADER@@"):
        convert.render_zensical_toml(merged, "[project]\n@@MARKDOWN_EXTENSIONS@@\n@@EXTRA_AND_NAV@@\n")


def test_zensical_toml_is_the_only_config_emitted(source_tree, out_dir, overlay):
    run(source_tree, out_dir, overlay)
    assert (out_dir / "zensical.toml").is_file()
    assert not (out_dir / "mkdocs.yml").exists()


def test_two_runs_produce_byte_identical_output(source_tree, out_dir, overlay):
    run(source_tree, out_dir, overlay)
    first = tree_digest(out_dir)
    run(source_tree, out_dir, overlay)
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

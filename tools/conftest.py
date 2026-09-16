import pytest

from fixture_tree import build_overlay_tree, build_source_tree


@pytest.fixture
def source_tree(tmp_path):
    """The miniature monorepo's root path."""
    return build_source_tree(tmp_path)


@pytest.fixture
def overlay(tmp_path, source_tree):
    """The content overlay matching the miniature monorepo."""
    return build_overlay_tree(tmp_path, source_tree)


@pytest.fixture
def out_dir(tmp_path):
    return tmp_path / "output"

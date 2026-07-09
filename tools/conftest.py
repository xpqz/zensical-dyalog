import pytest

from fixture_tree import build_source_tree


@pytest.fixture
def source_tree(tmp_path):
    """The miniature monorepo's root path."""
    return build_source_tree(tmp_path)


@pytest.fixture
def out_dir(tmp_path):
    return tmp_path / "output"

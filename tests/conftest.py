"""Pytest configuration and shared fixtures."""

import pytest
from pathlib import Path


@pytest.fixture
def project_root() -> Path:
    """Return the project root directory."""
    return Path(__file__).parent.parent


@pytest.fixture
def fixtures_dir(project_root: Path) -> Path:
    """Return the path to the test fixtures directory."""
    return project_root / "tests" / "fixtures"


@pytest.fixture
def examples_dir(project_root: Path) -> Path:
    """Return the path to the examples directory."""
    return project_root / "examples"









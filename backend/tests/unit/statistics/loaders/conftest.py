"""Shared fixtures for StatisticsSourceLoader unit tests."""

import pytest

from backend.statistics.loaders import StatisticsSourceLoader

@pytest.fixture
def statistics_loader() -> StatisticsSourceLoader:
    """Create a statistics source loader for unit tests."""
    return StatisticsSourceLoader(seasons=[2024, 2025], positions=["QB", "RB", "WR", "TE"])

"""Shared fixtures for Statistics unit tests."""

import pytest

from backend.statistics.statistics import Statistics


@pytest.fixture
def statistics() -> Statistics:
    """Create a statistics instance for unit tests."""
    return Statistics(seasons=[2024, 2025], positions=["QB", "RB", "WR", "TE"])

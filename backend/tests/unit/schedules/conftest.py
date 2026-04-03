"""Shared fixtures for schedules unit tests."""

import pytest

from backend.schedules.schedules import Schedules


@pytest.fixture
def schedules() -> Schedules:
    """Create a schedules instance for unit tests."""
    return Schedules(seasons=[2024, 2025])

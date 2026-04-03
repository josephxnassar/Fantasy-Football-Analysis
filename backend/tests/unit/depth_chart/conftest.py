"""Shared fixtures for NRP depth chart unit tests."""

import pytest

from backend.depth_chart.nrp import NRPDepthChart

@pytest.fixture
def nrp_depth_chart() -> NRPDepthChart:
    """Create an NRP depth chart instance for unit tests."""
    return NRPDepthChart(seasons=[2024, 2025], positions=["QB", "RB"])

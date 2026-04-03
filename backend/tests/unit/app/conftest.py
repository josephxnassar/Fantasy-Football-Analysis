"""Shared fixtures for App unit tests."""

from unittest.mock import MagicMock

import pytest

from backend import app as app_module
from backend.app import App


@pytest.fixture
def app(monkeypatch: pytest.MonkeyPatch) -> App:
    """Create an App instance with a mocked repository and fixed settings."""
    repository_mock = MagicMock()
    monkeypatch.setattr(app_module, "Repository", MagicMock(return_value=repository_mock))
    monkeypatch.setattr(app_module, "get_seasons", lambda: [2024, 2025])
    monkeypatch.setattr(app_module, "get_positions", lambda: ["QB", "RB", "WR", "TE"])
    return App()

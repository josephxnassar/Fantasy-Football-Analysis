"""Unit tests for App.close."""

import pytest

from backend.app import App

# normal

def test_app_close_calls_repository_close(app: App) -> None:
    """close calls the repository close method."""
    app.close()

    app.db.close.assert_called_once_with()

# exception

def test_app_close_propagates_repository_failure(app: App) -> None:
    """close propagates a repository close failure."""
    app.db.close.side_effect = RuntimeError("dummy")

    with pytest.raises(RuntimeError, match="dummy"):
        app.close()

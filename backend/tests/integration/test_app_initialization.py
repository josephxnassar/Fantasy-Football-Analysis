from unittest.mock import MagicMock

from backend.app import App


def test_app_initialize_loads_from_cache_when_available(monkeypatch) -> None:
    app = App()
    try:
        monkeypatch.setattr(app.db, "has_cached_data", lambda: True)
        app.load = MagicMock()
        app.run = MagicMock()
        app.save = MagicMock()

        app.initialize()

        app.load.assert_called_once()
        app.run.assert_not_called()
        app.save.assert_not_called()
    finally:
        app.db.close()


def test_app_initialize_fetches_and_saves_when_cache_missing(monkeypatch) -> None:
    app = App()
    try:
        monkeypatch.setattr(app.db, "has_cached_data", lambda: False)
        app.load = MagicMock()
        app.run = MagicMock()
        app.save = MagicMock()

        app.initialize()

        app.run.assert_called_once()
        app.save.assert_called_once()
        app.load.assert_not_called()
    finally:
        app.db.close()

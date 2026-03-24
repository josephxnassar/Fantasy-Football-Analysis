"""Application entry point."""

from backend.app import App
from backend.config.logging_config import setup_logging

def main() -> None:
    """Run the app."""
    setup_logging()
    app = App()
    try:
        app.run(refresh=True)
    finally:
        app.close()

if __name__ == "__main__":
    main()

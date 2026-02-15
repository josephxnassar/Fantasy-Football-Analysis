"""Refresh script to regenerate all data and save to database cache."""

from backend import config  # Imports and runs setup_logging() from __init__.py
from backend.app import App

if __name__ == "__main__":
    print("=" * 60)
    print("Refreshing Fantasy Football Data Cache")
    print("=" * 60)
    print()
    
    app = App()
    
    print(">> Downloading fresh data from all sources...")
    print("   - ESPN Depth Charts (web scraping)")
    print("   - NFL Schedules ")
    print("   - Player Statistics ")
    print()
    print(">> Loading...")
    print()
    
    app.run()
    
    print(">> Data fetched successfully!")
    print()
    print(">> Saving to database cache...")
    
    app.save()
    
    print(">> Database cache updated!")
    print()
    print("=" * 60)
    print("Done! Restart the API server to use the new data.")
    print("=" * 60)

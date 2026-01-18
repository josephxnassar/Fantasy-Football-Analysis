"""
Refresh script to regenerate all data and save to database cache.
This will fetch fresh data from all sources and apply the new column name mappings.
"""
import config  # Required for logging setup
from backend.app import App

if __name__ == "__main__":
    print("=" * 60)
    print("Refreshing Fantasy Football Data Cache")
    print("=" * 60)
    print()
    
    app = App()
    
    print("📊 Fetching fresh data from all sources...")
    print("   - ESPN Depth Charts (web scraping)")
    print("   - NFL Data Py Depth Charts")
    print("   - NFL Schedules (2025)")
    print("   - Player Statistics (2024)")
    print()
    print("⏳ This may take 1-2 minutes...")
    print()
    
    app.run()
    
    print("✅ Data fetched successfully!")
    print()
    print("💾 Saving to database cache...")
    
    app.save()
    
    print("✅ Database cache updated!")
    print()
    print("=" * 60)
    print("Done! Restart the API server to use the new data.")
    print("=" * 60)

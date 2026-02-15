"""Search helper utilities for API routes."""

from typing import Dict, List

def filter_search_results(all_players: List[Dict], query: str) -> List[Dict]:
    """Filter players by search query (case-insensitive substring match)."""
    query_lower = query.lower()
    return [p for p in all_players if query_lower in p["name"].lower()]

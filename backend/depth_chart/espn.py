"""ESPN depth chart scraping and processing"""

import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Optional, Tuple

import pandas as pd
import requests
from bs4 import BeautifulSoup

from backend.base_source import BaseSource
from backend.util import constants
from backend.util.exceptions import ScrapingError

logger = logging.getLogger(__name__)
_REQUEST_TIMEOUT = 10
_MAX_WORKERS = 8

class ESPNDepthChart(BaseSource):
    """Scrapes and parses ESPN depth charts for all NFL teams"""
    
    def __init__(self) -> None:
        super().__init__([constants.CURRENT_SEASON])

    def _load(self) -> pd.DataFrame:
        """Not used for depth charts"""
        pass

    def _get_soup(self, team: str) -> BeautifulSoup:
        """Fetch and parse ESPN depth chart page"""
        try:
            url = f"https://www.espn.com/nfl/team/depth/_/name/{team}"
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"}
            response = requests.get(url, headers=headers, timeout=_REQUEST_TIMEOUT)
            response.raise_for_status()
            return BeautifulSoup(response.text, "html.parser")
        except Exception as e:
            logger.error(f"Failed to fetch depth chart for '{team}': {e}")
            raise ScrapingError(f"Failed to fetch depth chart for '{team}': {e}", source="ESPNDepthChart") from e

    def _parse_soup(self, soup: BeautifulSoup) -> Tuple[List[str], List[str]]:
        """Extract positions and players from parsed HTML"""
        try:
            position_table = soup.find_all("table")[0]
            player_table = soup.find_all("table")[1]

            positions = []
            for td in position_table.find_all("td"):
                text = td.get_text(strip=True)
                if text:
                    positions.append(text)
            
            players = []
            tbody = player_table.find("tbody")
            if tbody:
                for td in tbody.find_all("td"):
                    players.append(td.get_text(strip=True))

            return positions, players
        except Exception as e:
            logger.error(f"Failed to parse depth chart HTML: {e}")
            raise ScrapingError(f"Failed to parse depth chart HTML: {e}", source="ESPNDepthChart") from e

    def _create_depth_chart(self, positions: List[str], players: List[str]) -> pd.DataFrame:
        """Create structured depth chart DataFrame"""
        try:
            roster: dict[str, List[List[str]]] = {}
            for idx, pos in enumerate(positions):
                if pos in constants.POSITIONS:
                    start_idx = idx * 4
                    group = players[start_idx:start_idx + 4]
                    if pos not in roster:
                        roster[pos] = []
                    roster[pos].append(group)
                    
            rows = []
            for pos, position_group in roster.items():
                for g in position_group:
                    rows.append({'position': pos,
                                 'starter':  g[0] if len(g) > 0 else None,
                                 '2nd':      g[1] if len(g) > 1 else None,
                                 '3rd':      g[2] if len(g) > 2 else None,
                                 '4th':      g[3] if len(g) > 3 else None})

            return pd.DataFrame(rows).set_index("position").replace(r'(Q|D|O|IR|PUP|NFI|SUS)$', '', regex=True)
        except Exception as e:
            logger.error(f"Failed to create depth chart: {e}")
            raise ScrapingError(f"Failed to create depth chart: {e}", source="ESPNDepthChart") from e

    def _fetch_team_depth_chart(self, team: str) -> Tuple[str, Optional[pd.DataFrame]]:
        """Fetch and parse depth chart for a single team."""
        try:
            soup = self._get_soup(team)
            positions, players = self._parse_soup(soup)
            return team, self._create_depth_chart(positions, players).rename_axis(team)
        except Exception as e:
            logger.warning(f"Skipping team '{team}': {e}")
            return team, None

    def run(self) -> None:
        """Fetch and process depth charts for all teams."""
        depth_charts = {}
        with ThreadPoolExecutor(max_workers=_MAX_WORKERS) as executor:
            futures = [executor.submit(self._fetch_team_depth_chart, team) for team in constants.TEAMS]
            for future in as_completed(futures):
                team, chart = future.result()
                if chart is not None:
                    depth_charts[team] = chart
        self.set_cache(depth_charts)
    

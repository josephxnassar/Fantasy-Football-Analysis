"""Flat NRP depth chart cache draft."""

import logging
from typing import Dict, List

import nflreadpy as nfl
import pandas as pd

from backend.base_source import BaseSource
from backend.util import teams
from backend.util.exceptions import DataLoadError, DataProcessingError

logger = logging.getLogger(__name__)

class NRPDepthChart(BaseSource):
    """Build team depth charts from nflreadpy depth chart data."""

    def __init__(self, seasons: list[int], positions: list[str] | None = None) -> None:
        super().__init__(seasons, positions)
        self.current_season = max(self.seasons)
        self.primary_keys = ["team", "position", "position_slot"]

    def _load_depth_charts(self) -> pd.DataFrame:
        """Load seasonal depth chart snapshots from nflreadpy."""
        try:
            required_columns = ["dt", "team", "pos_abb", "player_name", "pos_rank", "pos_slot"]
            depth = nfl.load_depth_charts(seasons=self.current_season).to_pandas()
            depth = depth[required_columns].copy()
            depth["team"] = depth["team"].replace(teams.TEAM_ABBR_NORMALIZATION)
            depth["dt"] = pd.to_datetime(depth["dt"], errors="coerce", utc=True)
            depth["pos_rank"] = pd.to_numeric(depth["pos_rank"], errors="coerce")
            depth["pos_slot"] = pd.to_numeric(depth["pos_slot"], errors="coerce")
            depth = depth[depth["team"].isin(teams.TEAM_METADATA)]
            depth = depth[depth["pos_abb"].isin(self.positions)]
            return depth
        except Exception as e:
            logger.error(f"Failed to load depth charts from nflreadpy: {e}")
            raise DataLoadError(f"Failed to load depth charts from nflreadpy: {e}", source="NRPDepthChart") from e

    def _clean_depth_charts(self, depth: pd.DataFrame) -> pd.DataFrame:
        """Clean raw depth chart rows."""
        try:
            depth = depth.dropna(subset=["dt", "team", "pos_abb", "player_name", "pos_rank", "pos_slot"])
            depth["player_name"] = depth["player_name"].astype(str).str.strip()
            depth = depth[depth["player_name"] != ""]
            depth["pos_rank"] = depth["pos_rank"].astype(int)
            depth["pos_slot"] = depth["pos_slot"].astype(int)
            depth = depth.drop_duplicates(subset=["team", "pos_abb", "pos_slot", "pos_rank", "player_name"])
            return depth.sort_values(["team", "pos_abb", "pos_slot", "pos_rank", "player_name"])
        except Exception as e:
            logger.error(f"Failed to clean depth charts: {e}")
            raise DataProcessingError(f"Failed to clean depth charts: {e}", source="NRPDepthChart") from e

    def _group_depth_charts(self, depth: pd.DataFrame) -> Dict[str, Dict[str, Dict[int, List[str]]]]:
        """Group latest rows by team, position, and slot."""
        try:
            slots_by_team: Dict[str, Dict[str, Dict[int, List[str]]]] = {}
            for (team, position, slot), group in depth.groupby(["team", "pos_abb", "pos_slot"], sort=False):
                players = group["player_name"].drop_duplicates().tolist()[:4]
                slots_by_team.setdefault(team, {}).setdefault(position, {})[int(slot)] = players
            return slots_by_team
        except Exception as e:
            logger.error(f"Failed to group depth charts: {e}")
            raise DataProcessingError(f"Failed to group depth charts: {e}", source="NRPDepthChart") from e

    def run(self) -> None:
        """Build depth-chart cache across all teams."""
        try:
            depth = self._load_depth_charts()
            depth = self._clean_depth_charts(depth)
            depth = depth[depth["dt"].eq(depth.groupby("team")["dt"].transform("max"))] # latest snapshot from import
            slots_by_team = self._group_depth_charts(depth)

            depth_charts: List[Dict[str, object]] = []
            for team in teams.TEAM_METADATA:
                team_slots = slots_by_team.get(team)
                if not team_slots:
                    logger.warning(f"No NRP depth chart rows found for team '{team}' in season(s) {self.seasons}.")
                    continue
                for position in self.positions:
                    for slot in sorted(team_slots.get(position, {})):
                        players = team_slots[position][slot] + [None] * (4 - len(team_slots[position][slot]))
                        depth_charts.append({"team": team, "position": position, "position_slot": slot, "starter": players[0], "2nd": players[1], "3rd": players[2], "4th": players[3]})

            self.set_cache(depth_charts)
        except Exception as e:
            logger.error(f"Failed to build depth charts: {e}")
            raise DataProcessingError(f"Failed to build depth charts: {e}", source="NRPDepthChart") from e

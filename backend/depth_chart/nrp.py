"""Flat NRP depth chart cache draft."""

import logging
from typing import Dict, List

import nflreadpy as nfl
import pandas as pd

from backend.base_source import BaseSource
from backend.util import constants
from backend.util.exceptions import DataLoadError, DataProcessingError

logger = logging.getLogger(__name__)


class NRPDepthChart(BaseSource):
    """Build team depth charts from nflreadpy depth chart data."""

    def __init__(self) -> None:
        super().__init__([constants.CURRENT_SEASON])

    def _load_depth_charts(self) -> pd.DataFrame:
        """Load seasonal depth chart snapshots from nflreadpy."""
        try:
            required_columns = ["dt", "team", "pos_abb", "player_name", "pos_rank", "pos_slot"]
            depth = nfl.load_depth_charts(seasons=self.seasons).to_pandas().loc[:, required_columns].copy()
            depth["team"] = depth["team"].replace(constants.TEAM_ABBR_NORMALIZATION)
            depth["dt"] = pd.to_datetime(depth["dt"], errors="coerce", utc=True)
            depth["pos_rank"] = pd.to_numeric(depth["pos_rank"], errors="coerce")
            depth["pos_slot"] = pd.to_numeric(depth["pos_slot"], errors="coerce")
            return depth.loc[depth["team"].isin(constants.TEAM_METADATA) & depth["pos_abb"].isin(constants.POSITIONS)]
        except Exception as e:
            logger.error("Failed to load depth charts from nflreadpy: %s", e)
            raise DataLoadError(f"Failed to load depth charts from nflreadpy: {e}", source="NRPDepthChart") from e

    def _latest_team_rows(self, raw: pd.DataFrame) -> pd.DataFrame:
        """Clean rows and keep the latest snapshot per team."""
        try:
            depth = raw.copy()
            depth = depth.dropna(subset=["dt", "team", "pos_abb", "player_name", "pos_rank", "pos_slot"])
            depth["player_name"] = depth["player_name"].astype(str).str.strip()
            depth = depth.loc[depth["player_name"] != ""]
            depth = depth.loc[depth["dt"].eq(depth.groupby("team")["dt"].transform("max"))]
            depth["pos_rank"] = depth["pos_rank"].astype(int)
            depth["pos_slot"] = depth["pos_slot"].astype(int)
            return depth
        except Exception as e:
            logger.error("Failed to normalize nflreadpy depth chart rows: %s", e)
            raise DataProcessingError(f"Failed to normalize nflreadpy depth chart rows: {e}", source="NRPDepthChart") from e

    def _build_team_rows(self, team: str, team_rows: pd.DataFrame) -> List[Dict[str, object]]:
        """Build one flat row per position slot for one team."""
        try:
            deduped = team_rows.drop_duplicates(subset=["pos_abb", "pos_slot", "pos_rank", "player_name"])
            grouped = {(position, int(position_slot)): group for (position, position_slot), group in deduped.sort_values(["pos_abb", "pos_slot", "pos_rank", "player_name"]).groupby(["pos_abb", "pos_slot"], sort=False)}

            flat_rows: List[Dict[str, object]] = []
            for position in constants.POSITIONS:
                slot_numbers = sorted(slot for pos, slot in grouped if pos == position)
                for slot in slot_numbers:
                    players = grouped[(position, slot)]["player_name"].drop_duplicates().tolist()[:4]
                    players += [None] * (4 - len(players))
                    flat_rows.append({"team": team, "position": position, "position_slot": slot, "starter": players[0], "2nd": players[1], "3rd": players[2], "4th": players[3]})

            return flat_rows
        except Exception as e:
            logger.error("Failed to create NRP depth chart dataframe: %s", e)
            raise DataProcessingError(f"Failed to create NRP depth chart dataframe: {e}", source="NRPDepthChart") from e

    def run(self) -> None:
        """Build a flat depth-chart cache across all teams."""
        depth_rows = self._load_depth_charts()
        latest_rows = self._latest_team_rows(depth_rows)
        rows_by_team = {team: group for team, group in latest_rows.groupby("team")}

        flat_depth_charts: List[Dict[str, object]] = []
        for team in constants.TEAM_METADATA:
            team_rows = rows_by_team.get(team)
            if team_rows is None or team_rows.empty:
                logger.warning("No NRP depth chart rows found for team '%s' in season(s) %s.", team, self.seasons)
                continue
            flat_depth_charts.extend(self._build_team_rows(team, team_rows))

        self.set_cache(flat_depth_charts)

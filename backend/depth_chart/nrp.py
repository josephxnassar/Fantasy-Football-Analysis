"""NRP depth chart loading and processing via nflreadpy."""

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
            return nfl.load_depth_charts(seasons=self.seasons).to_pandas()
        except Exception as e:
            logger.error(f"Failed to load depth charts from nflreadpy: {e}")
            raise DataLoadError(f"Failed to load depth charts from nflreadpy: {e}", source="NRPDepthChart") from e

    def _latest_team_rows(self, raw: pd.DataFrame) -> pd.DataFrame:
        """Keep latest snapshot rows per team for fantasy positions."""
        try:
            depth = raw.copy()
            depth["team"] = depth["team"].replace({"LA": "LAR", "WAS": "WSH"})
            depth = depth.loc[depth["team"].isin(constants.TEAMS) & depth["pos_abb"].isin(constants.POSITIONS)]
            depth = depth.dropna(subset=["dt", "team", "pos_abb", "player_name", "pos_rank", "pos_slot"])
            depth["dt"] = pd.to_datetime(depth["dt"], errors="coerce", utc=True)
            depth["pos_rank"] = pd.to_numeric(depth["pos_rank"], errors="coerce")
            depth["pos_slot"] = pd.to_numeric(depth["pos_slot"], errors="coerce")
            depth = depth.dropna(subset=["dt", "pos_rank", "pos_slot"])
            depth["player_name"] = depth["player_name"].astype(str).str.strip()
            depth = depth.loc[depth["player_name"] != ""]
            depth = depth.loc[depth["dt"].eq(depth.groupby("team")["dt"].transform("max"))]
            depth["pos_rank"] = depth["pos_rank"].astype(int)
            depth["pos_slot"] = depth["pos_slot"].astype(int)
            return depth
        except Exception as e:
            logger.error(f"Failed to normalize nflreadpy depth chart rows: {e}")
            raise DataProcessingError(f"Failed to normalize nflreadpy depth chart rows: {e}", source="NRPDepthChart") from e

    def _create_depth_chart(self, team_rows: pd.DataFrame) -> pd.DataFrame:
        """Create ESPN-style depth chart dataframe for one team."""
        try:
            rows: List[Dict[str, str | None]] = []
            deduped = team_rows.drop_duplicates(subset=["pos_abb", "pos_slot", "pos_rank", "player_name"])
            grouped = deduped.sort_values(["pos_abb", "pos_slot", "pos_rank", "player_name"]).groupby(["pos_abb", "pos_slot"], sort=False)

            for (position, _slot), group in grouped:
                depth_players = group["player_name"].drop_duplicates().tolist()[:4]
                depth_players += [None] * (4 - len(depth_players))
                rows.append({"position": position,
                             "starter": depth_players[0],
                             "2nd": depth_players[1],
                             "3rd": depth_players[2],
                             "4th": depth_players[3]})

            if not rows:
                return pd.DataFrame(columns=["starter", "2nd", "3rd", "4th"]).rename_axis("position")
            return pd.DataFrame(rows).set_index("position")
        except Exception as e:
            logger.error(f"Failed to create NRP depth chart dataframe: {e}")
            raise DataProcessingError(f"Failed to create NRP depth chart dataframe: {e}", source="NRPDepthChart") from e

    def run(self) -> None:
        """Build depth-chart cache keyed by team abbreviation."""
        team_depth_charts: Dict[str, pd.DataFrame] = {}
        latest_rows = self._latest_team_rows(self._load_depth_charts())
        rows_by_team = {team: group for team, group in latest_rows.groupby("team")}

        for team in constants.TEAMS:
            team_rows = rows_by_team.get(team)
            if team_rows is None or team_rows.empty:
                logger.warning(f"No NRP depth chart rows found for team '{team}' in season(s) {self.seasons}.")
                continue
            team_depth_charts[team] = self._create_depth_chart(team_rows).rename_axis(team)

        self.set_cache(team_depth_charts)

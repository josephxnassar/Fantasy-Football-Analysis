"""Player statistics processing and cache generation."""

import logging
from typing import Dict, List, Tuple, cast

import nflreadpy as nfl
import pandas as pd

from backend import base_source
from backend.statistics.util import stats_helpers
from backend.util import constants
from backend.util.exceptions import DataLoadError, DataProcessingError
from backend.util.timing import timed

logger = logging.getLogger(__name__)

class Statistics(base_source.BaseSource):
    """Processes player statistics and builds stat caches."""
    
    def __init__(self, seasons: List[int]) -> None:
        """Initialize with seasons"""
        super().__init__(seasons)

    def get_keys(self) -> List[str]:
        return constants.POSITIONS

    @timed("Statistics._load_rosters")
    def _load_rosters(self) -> pd.DataFrame:
        """Load roster data from nflreadpy"""
        try:
            return nfl.load_rosters(seasons=self.seasons).to_pandas()
        except Exception as e:
            logger.error(f"Failed to load rosters: {e}")
            raise DataLoadError(f"Failed to load rosters: {e}", source="Statistics") from e

    @timed("Statistics._load")
    def _load(self) -> pd.DataFrame:
        """Load player stats from nflreadpy"""
        try:
            return nfl.load_player_stats(seasons=self.seasons).to_pandas()
        except Exception as e:
            logger.error(f"Failed to load player stats: {e}")
            raise DataLoadError(f"Failed to load player stats: {e}", source="Statistics") from e

    @timed("Statistics._load_snap_counts")
    def _load_snap_counts(self) -> pd.DataFrame:
        """Load weekly snap count percentages from nflreadpy."""
        try:
            snap_seasons = self.seasons
            if min(self.seasons) < 2012:
                snap_seasons = [season for season in self.seasons if season >= 2012]
            return nfl.load_snap_counts(seasons=snap_seasons).to_pandas()
        except Exception as e:
            logger.error(f"Failed to load snap counts: {e}")
            raise DataLoadError(f"Failed to load snap counts: {e}", source="Statistics") from e

    @timed("Statistics._extract_all_roster_data")
    def _extract_all_roster_data(self, rosters: pd.DataFrame) -> Tuple[Dict[str, int], set[str], Dict[str, str], Dict[str, str], Dict[str, bool]]:
        """Extract all roster-based data in a single pass through the dataframe."""
        try:
            current_season = constants.CURRENT_SEASON
            today = pd.Timestamp.now().normalize()
            player_ages: Dict[str, int] = {}
            eligible_players: set[str] = set()
            player_headshots: Dict[str, str] = {}
            player_teams: Dict[str, str] = {}
            rookies: Dict[str, bool] = {}
            for row in rosters.itertuples(index=False):
                name_raw = getattr(row, "full_name", None)
                if not isinstance(name_raw, str) or not name_raw:
                    continue
                name = name_raw
                season_raw = getattr(row, "season", None)
                season_int: int | None = None
                if pd.notna(season_raw):
                    try:
                        season_int = int(cast(int | float | str, season_raw))
                    except (TypeError, ValueError):
                        season_int = None
                position = getattr(row, "position", None)
                if position in constants.POSITIONS and pd.notna(birth_date := getattr(row, "birth_date", None)):
                    birth_ts = pd.to_datetime(birth_date)
                    age = (today - birth_ts).days // 365
                    if age > 0:
                        player_ages[name] = int(age)
                if season_int == current_season and position in constants.POSITIONS:
                    if getattr(row, "status", None) != "RET":
                        eligible_players.add(name)
                    if isinstance(headshot := getattr(row, "headshot_url", None), str) and headshot:
                        player_headshots[name] = headshot
                    if isinstance(team := getattr(row, "team", None), str) and team:
                        player_teams[name] = team
                    if (entry_year := getattr(row, "entry_year", None)) == current_season and pd.notna(entry_year):
                        rookies[name] = True
            logger.info(f"Ages: {len(player_ages)} | Eligible: {len(eligible_players)} | Headshots: {len(player_headshots)} | Player-Teams: {len(player_teams)} | Rookies: {sum(1 for v in rookies.values() if v)}")
            
            return player_ages, eligible_players, player_headshots, player_teams, rookies
        except Exception as e:
            logger.error(f"Failed to extract roster data: {e}")
            raise DataProcessingError(f"Failed to extract roster data: {e}", source="Statistics") from e
        
    @timed("Statistics._partition_data")
    def _partition_data(self, raw_stats: pd.DataFrame, snap_counts: pd.DataFrame) -> Tuple[Dict, Dict, Dict, pd.DataFrame]:
        """Aggregate raw weekly data by player/season, partition by position/year, and collect weekly stats."""
        try:
            df = raw_stats.loc[(raw_stats["season_type"] == "REG") & raw_stats["position"].isin(constants.POSITIONS)]
            weekly_source_df = df.copy()
            
            numeric_cols = df.select_dtypes(include="number").columns.difference(["week", "season"])
            non_numeric_cols = ["season", "position", "player_display_name", "player_id"]
            df = df[non_numeric_cols + numeric_cols.tolist()]

            player_positions = df.drop_duplicates("player_display_name").set_index("player_display_name")["position"].to_dict()
            
            seasonal_df = stats_helpers.add_derived_stats(df.groupby(["season", "position", "player_display_name", "player_id"], as_index=False)[numeric_cols].sum().rename(columns=constants.COLUMN_NAME_MAP))
            seasonal_data_df = {season: {position: stats_helpers.build_position_df(position_group) for position, position_group in season_group.groupby("position")} for season, season_group in seasonal_df.groupby("season")}

            weekly_cols = non_numeric_cols + numeric_cols.tolist() + ["week", "opponent_team"]
            weekly_df = stats_helpers.add_derived_stats(weekly_source_df[weekly_cols].rename(columns=constants.COLUMN_NAME_MAP))

            snap_df = snap_counts.loc[(snap_counts["game_type"] == "REG") & snap_counts["position"].isin(constants.POSITIONS), ["season", "week", "player", "position", "offense_pct"]].rename(columns={"player": "player_display_name", "offense_pct": "Snap Share"})
            weekly_df = weekly_df.merge(snap_df, on=["season", "week", "player_display_name", "position"], how="left")
            
            new_weekly_cols = stats_helpers.select_useful_cols(weekly_df, ["season", "week", "Snap Share", "opponent_team"])
            weekly_player_stats = {player: group[new_weekly_cols].to_dict("records") for player, group in weekly_df.groupby("player_display_name")}

            return player_positions, seasonal_data_df, weekly_player_stats, seasonal_df
        except Exception as e:
            logger.error(f"Failed to partition seasonal data: {e}")
            raise DataProcessingError(f"Failed to partition seasonal data: {e}", source="Statistics") from e

    @timed("Statistics.run")
    def run(self) -> None:
        """Load data, process statistics, and store cache data."""
        rosters = self._load_rosters()
        player_ages, eligible, headshots, teams, rookies = self._extract_all_roster_data(rosters)

        raw_stats = self._load()
        snap_counts = self._load_snap_counts()
        positions, seasonal_data, weekly_stats, seasonal_df = self._partition_data(raw_stats, snap_counts)

        if seasonal_df.empty:
            raise DataProcessingError("No seasonal statistics were produced.", source="Statistics")

        all_players = stats_helpers.build_all_players(
            positions,
            eligible,
            player_ages,
            headshots,
            teams,
            rookies,
        )

        self.set_cache({constants.STATS["ALL_PLAYERS"]:         all_players,
                        constants.STATS["BY_YEAR"]:             seasonal_data,
                        constants.STATS["PLAYER_WEEKLY_STATS"]: weekly_stats})

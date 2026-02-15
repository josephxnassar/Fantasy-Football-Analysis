"""Player statistics processing and ML-based ratings generation"""

import logging
from typing import Dict, List, Tuple

import nflreadpy as nfl
import pandas as pd

from backend import base_source
from backend.statistics.util import stats_helpers
from backend.util import constants
from backend.util.exceptions import DataLoadError, DataProcessingError

logger = logging.getLogger(__name__)

class Statistics(base_source.BaseSource):
    """Processes player statistics and generates ML-based ratings"""
    
    def __init__(self, seasons: List[int], method: str = "ridge") -> None:
        """Initialize with seasons and regression method"""
        super().__init__(seasons)
        self.ratings_method: str = method

    def get_keys(self) -> List[str]:
        return constants.POSITIONS

    def _load_rosters(self) -> pd.DataFrame:
        """Load roster data from nflreadpy"""
        try:
            return nfl.load_rosters(seasons=self.seasons).to_pandas()
        except Exception as e:
            logger.error(f"Failed to load rosters: {e}")
            raise DataLoadError(f"Failed to load rosters: {e}", source="Statistics") from e

    def _load(self) -> pd.DataFrame:
        """Load player stats from nflreadpy"""
        try:
            return nfl.load_player_stats(seasons=self.seasons).to_pandas()
        except Exception as e:
            logger.error(f"Failed to load player stats: {e}")
            raise DataLoadError(f"Failed to load player stats: {e}", source="Statistics") from e

    def _load_snap_counts(self) -> pd.DataFrame:
        """Load weekly snap count percentages from nflreadpy."""
        try:
            return nfl.load_snap_counts(seasons=self.seasons).to_pandas()
        except Exception as e:
            logger.error(f"Failed to load snap counts: {e}")
            raise DataLoadError(f"Failed to load snap counts: {e}", source="Statistics") from e

    def _extract_all_roster_data(self, rosters: pd.DataFrame) -> Tuple[Dict, set, Dict, Dict, Dict]:
        """Extract all roster-based data in a single pass through the dataframe."""
        try:
            current_season = constants.CURRENT_SEASON
            age_tracker, eligible_players, player_headshots, player_teams, rookies = {}, set(), {}, {}, {}
            for row in rosters.itertuples(index=False):
                name = getattr(row, "full_name", None)
                season = getattr(row, "season", None)
                if pd.isna(name):
                    continue
                if pd.notna(birth_date := getattr(row, "birth_date", None)):
                    age = (pd.Timestamp(year=season, month=9, day=1) - pd.to_datetime(birth_date)).days // 365
                    prev = age_tracker.get(name)
                    if age > 0 and (not prev or season > prev[0]):
                        age_tracker[name] = (season, age)
                if season == current_season:
                    if getattr(row, "status", None) != "RET":
                        eligible_players.add(name)
                    if pd.notna(headshot := getattr(row, "headshot_url", None)):
                        player_headshots[name] = headshot
                    if pd.notna(team := getattr(row, "team", None)):
                        player_teams[name] = team
                    if (entry_year := getattr(row, "entry_year", None)) == current_season and pd.notna(entry_year):
                        rookies[name] = True
            player_ages = {name: age for name, (_, age) in age_tracker.items()}
            logger.info(f"Ages: {len(player_ages)} | Eligible: {len(eligible_players)} | Headshots: {len(player_headshots)} | Player-Teams: {len(player_teams)} | Rookies: {sum(1 for v in rookies.values() if v)}")
            
            return player_ages, eligible_players, player_headshots, player_teams, rookies
        except Exception as e:
            logger.error(f"Failed to extract roster data: {e}")
            raise DataProcessingError(f"Failed to extract roster data: {e}", source="Statistics") from e
        
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

            def _build_position_df(group: pd.DataFrame) -> pd.DataFrame:
                df_out = group.drop(columns=["season", "position", "player_id"]).set_index("player_display_name").dropna(axis=1, how="all")
                df_out[constants.USEFUL_STATS] = df_out[constants.USEFUL_STATS].astype(int)
                return df_out

            seasonal_data_df = {season: {position: _build_position_df(position_group) for position, position_group in season_group.groupby("position")} for season, season_group in seasonal_df.groupby("season")}
            weekly_cols = non_numeric_cols + numeric_cols.tolist() + ["week", "opponent_team"]
            weekly_df = stats_helpers.add_derived_stats(weekly_source_df[weekly_cols].rename(columns=constants.COLUMN_NAME_MAP))
            snap_df = snap_counts.loc[(snap_counts["game_type"] == "REG") & snap_counts["position"].isin(constants.POSITIONS), ["season", "week", "player", "position", "offense_pct"]].rename(columns={"player": "player_display_name", "offense_pct": "Snap Share"})
            weekly_df = weekly_df.merge(snap_df, on=["season", "week", "player_display_name", "position"], how="left")
            new_weekly_cols = weekly_df.select_dtypes(include="number").columns.tolist() + ["opponent_team"]
            weekly_player_stats = {player: group[new_weekly_cols].to_dict("records") for player, group in weekly_df.groupby("player_display_name")}

            return player_positions, seasonal_data_df, weekly_player_stats, seasonal_df
        except Exception as e:
            logger.error(f"Failed to partition seasonal data: {e}")
            raise DataProcessingError(f"Failed to partition seasonal data: {e}", source="Statistics") from e

    def _calculate_ratings_from_averages(self, seasonal_df: pd.DataFrame, player_ages: Dict) -> Tuple[Dict, Dict]:
        """Calculate career averages by position and generate ratings."""
        try:
            stat_cols = seasonal_df.select_dtypes(include="number").columns.difference(["season", "player_id"])
            averages_df = seasonal_df.groupby(["position", "player_display_name"])[stat_cols].mean()
            present_positions = set(averages_df.index.get_level_values("position"))
            dynasty_ratings, redraft_ratings = {}, {}
            for position in (pos for pos in constants.POSITIONS if pos in present_positions):
                default_age = constants.AGE_MULTIPLIERS.get(position, {}).get("peak_age", 26)
                redraft_mult = constants.REDRAFT_MULTIPLIERS.get(position, 1.0)
                base_ratings = stats_helpers.create_ratings(averages_df.loc[position], self.ratings_method)
                dynasty_ratings.update({player_name: base_rating * stats_helpers.calculate_age_multiplier(player_ages.get(player_name, default_age), position) for player_name, base_rating in base_ratings.items()})
                redraft_ratings.update({player_name: base_rating * redraft_mult for player_name, base_rating in base_ratings.items()})

            return dynasty_ratings, redraft_ratings
        except Exception as e:
            logger.error(f"Failed to calculate ratings: {e}")
            raise DataProcessingError(f"Failed to calculate ratings: {e}", source="Statistics") from e

    def run(self) -> None:
        """Load data, process statistics, calculate ratings, and store in cache"""
        rosters = self._load_rosters()
        player_ages, eligible, headshots, teams, rookies = self._extract_all_roster_data(rosters)

        raw_stats = self._load()
        snap_counts = self._load_snap_counts()
        positions, seasonal_data, weekly_stats, seasonal_df = self._partition_data(raw_stats, snap_counts)

        dynasty, redraft = self._calculate_ratings_from_averages(seasonal_df, player_ages)

        overall_rank_dyn = stats_helpers.calculate_overall_ranks(dynasty, eligible)
        overall_rank_red = stats_helpers.calculate_overall_ranks(redraft, eligible)
        pos_rank_dyn = stats_helpers.calculate_position_ranks(dynasty, positions, eligible)
        pos_rank_red = stats_helpers.calculate_position_ranks(redraft, positions, eligible)

        all_players = stats_helpers.build_all_players(redraft, dynasty, positions, eligible, player_ages, headshots, teams, rookies, overall_rank_red, overall_rank_dyn, pos_rank_red, pos_rank_dyn)

        self.set_cache({'available_seasons':                    self.seasons,
                        constants.STATS["ALL_PLAYERS"]:         all_players,
                        constants.STATS["BY_YEAR"]:             seasonal_data,
                        constants.STATS["PLAYER_WEEKLY_STATS"]: weekly_stats})

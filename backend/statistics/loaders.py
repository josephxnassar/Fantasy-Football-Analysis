"""nflreadpy loaders for the statistics pipeline."""

import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Callable

import nflreadpy as nfl
import pandas as pd

from backend.statistics import stats_config
from backend.statistics.util import stats_helpers
from backend.util.exceptions import DataLoadError
from backend.util.timing import timed

logger = logging.getLogger(__name__)


class StatisticsSourceLoader:
    """Loads and normalizes raw source tables for the statistics pipeline."""

    def __init__(self, seasons: list[int]) -> None:
        self.seasons = seasons

    @timed("StatisticsSourceLoader.load_rosters")
    def load_rosters(self) -> pd.DataFrame:
        """Load roster data from nflreadpy."""
        try:
            source = nfl.load_rosters(seasons=self.seasons).to_pandas()
            return stats_helpers.team_normalization(source)
        except Exception as e:
            logger.error("Failed to load rosters: %s", e)
            raise DataLoadError(f"Failed to load rosters: {e}", source="Statistics") from e

    @timed("StatisticsSourceLoader.load_player_weekly_stats")
    def load_player_weekly_stats(self) -> pd.DataFrame:
        """Load and normalize weekly regular-season player stats."""
        try:
            source = nfl.load_player_stats(summary_level="week", seasons=self.seasons).to_pandas()
            source = stats_helpers.team_normalization(source)
            source = stats_helpers.filter_regular_and_position(source)
            return stats_helpers.select_columns(source, stats_config.PLAYER_WEEKLY_COLUMN_MAP, stats_config.PLAYER_WEEKLY_REQUIRED_COLUMNS, "player_weekly")
        except Exception as e:
            logger.error("Failed to load player weekly stats: %s", e)
            raise DataLoadError(f"Failed to load player stats: {e}", source="Statistics") from e

    @timed("StatisticsSourceLoader.load_player_seasonal_stats")
    def load_player_seasonal_stats(self) -> pd.DataFrame:
        """Load and normalize seasonal regular-season player stats."""
        try:
            source = nfl.load_player_stats(summary_level="reg", seasons=self.seasons).to_pandas().rename(columns={"recent_team": "team"})
            source = stats_helpers.team_normalization(source)
            source = stats_helpers.filter_regular_and_position(source)
            return stats_helpers.select_columns(source, stats_config.PLAYER_SEASONAL_COLUMN_MAP, stats_config.PLAYER_SEASONAL_REQUIRED_COLUMNS, "player_seasonal")
        except Exception as e:
            logger.error("Failed to load player seasonal stats: %s", e)
            raise DataLoadError(f"Failed to load player stats: {e}", source="Statistics") from e

    @timed("StatisticsSourceLoader.load_ff_opportunity_weekly")
    def load_ff_opportunity_weekly(self) -> pd.DataFrame:
        """Load weekly fantasy opportunity stats from nflreadpy."""
        try:
            source = nfl.load_ff_opportunity(stat_type="weekly", seasons=self.seasons).to_pandas().rename(columns={"full_name": "player_display_name", "posteam": "team"})
            source = stats_helpers.team_normalization(source)
            source["season"] = pd.to_numeric(source["season"], errors="coerce")
            source["week"] = pd.to_numeric(source["week"], errors="coerce")
            source = source.dropna(subset=["season", "week"]).astype({"season": "int32", "week": "int32"})
            source = stats_helpers.filter_regular_and_position(source)
            return stats_helpers.select_columns(source, stats_config.FF_OPP_WEEKLY_COLUMN_MAP, stats_config.FF_OPP_WEEKLY_REQUIRED_COLUMNS, "ff_opp_weekly")
        except Exception as e:
            logger.error("Failed to load weekly fantasy opportunity stats: %s", e)
            raise DataLoadError(f"Failed to load weekly fantasy opportunity stats: {e}", source="Statistics") from e

    @timed("StatisticsSourceLoader.load_nextgen_passing_stats")
    def load_nextgen_passing_stats(self) -> pd.DataFrame:
        """Load Next Gen passing stats from nflreadpy."""
        try:
            source = nfl.load_nextgen_stats(stat_type="passing", seasons=self.seasons).to_pandas().rename(columns={"player_position": "position", "team_abbr": "team"})
            source = stats_helpers.team_normalization(source)
            source = stats_helpers.filter_regular_and_position(source)
            return stats_helpers.select_columns(source, stats_config.NEXTGEN_PASS_COLUMN_MAP, stats_config.NEXTGEN_PASS_REQUIRED_COLUMNS, "nextgen_pass_weekly")
        except Exception as e:
            logger.error("Failed to load Next Gen passing stats: %s", e)
            raise DataLoadError(f"Failed to load Next Gen passing stats: {e}", source="Statistics") from e

    @timed("StatisticsSourceLoader.load_nextgen_receiving_stats")
    def load_nextgen_receiving_stats(self) -> pd.DataFrame:
        """Load Next Gen receiving stats from nflreadpy."""
        try:
            source = nfl.load_nextgen_stats(stat_type="receiving", seasons=self.seasons).to_pandas().rename(columns={"player_position": "position", "team_abbr": "team"})
            source = stats_helpers.team_normalization(source)
            source = stats_helpers.filter_regular_and_position(source)
            return stats_helpers.select_columns(source, stats_config.NEXTGEN_REC_COLUMN_MAP, stats_config.NEXTGEN_REC_REQUIRED_COLUMNS, "nextgen_rec_weekly")
        except Exception as e:
            logger.error("Failed to load Next Gen receiving stats: %s", e)
            raise DataLoadError(f"Failed to load Next Gen receiving stats: {e}", source="Statistics") from e

    @timed("StatisticsSourceLoader.load_nextgen_rushing_stats")
    def load_nextgen_rushing_stats(self) -> pd.DataFrame:
        """Load Next Gen rushing stats from nflreadpy."""
        try:
            source = nfl.load_nextgen_stats(stat_type="rushing", seasons=self.seasons).to_pandas().rename(columns={"player_position": "position", "team_abbr": "team"})
            source = stats_helpers.team_normalization(source)
            source = stats_helpers.filter_regular_and_position(source)
            return stats_helpers.select_columns(source, stats_config.NEXTGEN_RUSH_COLUMN_MAP, stats_config.NEXTGEN_RUSH_REQUIRED_COLUMNS, "nextgen_rush_weekly")
        except Exception as e:
            logger.error("Failed to load Next Gen rushing stats: %s", e)
            raise DataLoadError(f"Failed to load Next Gen rushing stats: {e}", source="Statistics") from e

    @timed("StatisticsSourceLoader.load_pfr_adv_pass_weekly")
    def load_pfr_adv_pass_weekly(self) -> pd.DataFrame:
        """Load weekly PFR advanced passing stats from nflreadpy."""
        try:
            source = nfl.load_pfr_advstats(stat_type="pass", summary_level="week", seasons=stats_helpers.pfr_seasons(self.seasons)).to_pandas().rename(columns={"pfr_player_name": "player_display_name"})
            source = stats_helpers.team_normalization(source)
            return stats_helpers.select_columns(source, stats_config.PFR_PASS_WEEKLY_COLUMN_MAP, stats_config.PFR_PASS_WEEKLY_REQUIRED_COLUMNS, "pfr_pass_weekly")
        except Exception as e:
            logger.error("Failed to load weekly PFR advanced pass stats: %s", e)
            raise DataLoadError(f"Failed to load weekly PFR advanced pass stats: {e}", source="Statistics") from e

    @timed("StatisticsSourceLoader.load_pfr_adv_rush_weekly")
    def load_pfr_adv_rush_weekly(self) -> pd.DataFrame:
        """Load weekly PFR advanced rushing stats from nflreadpy."""
        try:
            source = nfl.load_pfr_advstats(stat_type="rush", summary_level="week", seasons=stats_helpers.pfr_seasons(self.seasons)).to_pandas().rename(columns={"pfr_player_name": "player_display_name"})
            source = stats_helpers.team_normalization(source)
            return stats_helpers.select_columns(source, stats_config.PFR_RUSH_WEEKLY_COLUMN_MAP, stats_config.PFR_RUSH_WEEKLY_REQUIRED_COLUMNS, "pfr_rush_weekly")
        except Exception as e:
            logger.error("Failed to load weekly PFR advanced rush stats: %s", e)
            raise DataLoadError(f"Failed to load weekly PFR advanced rush stats: {e}", source="Statistics") from e

    @timed("StatisticsSourceLoader.load_pfr_adv_rec_weekly")
    def load_pfr_adv_rec_weekly(self) -> pd.DataFrame:
        """Load weekly PFR advanced receiving stats from nflreadpy."""
        try:
            source = nfl.load_pfr_advstats(stat_type="rec", summary_level="week", seasons=stats_helpers.pfr_seasons(self.seasons)).to_pandas().rename(columns={"pfr_player_name": "player_display_name"})
            source = stats_helpers.team_normalization(source)
            return stats_helpers.select_columns(source, stats_config.PFR_REC_WEEKLY_COLUMN_MAP, stats_config.PFR_REC_WEEKLY_REQUIRED_COLUMNS, "pfr_rec_weekly")
        except Exception as e:
            logger.error("Failed to load weekly PFR advanced receiving stats: %s", e)
            raise DataLoadError(f"Failed to load weekly PFR advanced receiving stats: {e}", source="Statistics") from e

    @timed("StatisticsSourceLoader.load_pfr_adv_pass_season")
    def load_pfr_adv_pass_season(self) -> pd.DataFrame:
        """Load seasonal PFR advanced passing stats from nflreadpy."""
        try:
            source = nfl.load_pfr_advstats(stat_type="pass", summary_level="season", seasons=stats_helpers.pfr_seasons(self.seasons)).to_pandas().rename(columns={"player": "player_display_name"})
            source = stats_helpers.team_normalization(source)
            return stats_helpers.select_columns(source, stats_config.PFR_PASS_SEASON_COLUMN_MAP, stats_config.PFR_PASS_SEASON_REQUIRED_COLUMNS, "pfr_pass_season")
        except Exception as e:
            logger.error("Failed to load seasonal PFR advanced pass stats: %s", e)
            raise DataLoadError(f"Failed to load seasonal PFR advanced pass stats: {e}", source="Statistics") from e

    @timed("StatisticsSourceLoader.load_pfr_adv_rush_season")
    def load_pfr_adv_rush_season(self) -> pd.DataFrame:
        """Load seasonal PFR advanced rushing stats from nflreadpy."""
        try:
            source = nfl.load_pfr_advstats(stat_type="rush", summary_level="season", seasons=stats_helpers.pfr_seasons(self.seasons)).to_pandas().rename(columns={"player": "player_display_name", "tm": "team", "pos": "position"})
            source = stats_helpers.team_normalization(source)
            return stats_helpers.select_columns(source, stats_config.PFR_RUSH_SEASON_COLUMN_MAP, stats_config.PFR_RUSH_SEASON_REQUIRED_COLUMNS, "pfr_rush_season")
        except Exception as e:
            logger.error("Failed to load seasonal PFR advanced rush stats: %s", e)
            raise DataLoadError(f"Failed to load seasonal PFR advanced rush stats: {e}", source="Statistics") from e

    @timed("StatisticsSourceLoader.load_pfr_adv_rec_season")
    def load_pfr_adv_rec_season(self) -> pd.DataFrame:
        """Load seasonal PFR advanced receiving stats from nflreadpy."""
        try:
            source = nfl.load_pfr_advstats(stat_type="rec", summary_level="season", seasons=stats_helpers.pfr_seasons(self.seasons)).to_pandas().rename(columns={"player": "player_display_name", "tm": "team", "pos": "position"})
            source = stats_helpers.team_normalization(source)
            return stats_helpers.select_columns(source, stats_config.PFR_REC_SEASON_COLUMN_MAP, stats_config.PFR_REC_SEASON_REQUIRED_COLUMNS, "pfr_rec_season")
        except Exception as e:
            logger.error("Failed to load seasonal PFR advanced receiving stats: %s", e)
            raise DataLoadError(f"Failed to load seasonal PFR advanced receiving stats: {e}", source="Statistics") from e

    @timed("StatisticsSourceLoader.load_snap_counts")
    def load_snap_counts(self) -> pd.DataFrame:
        """Load and normalize weekly regular-season snap counts."""
        try:
            source = nfl.load_snap_counts(seasons=stats_helpers.pfr_seasons(self.seasons)).to_pandas().rename(columns={"player": "player_display_name"})
            source = stats_helpers.team_normalization(source)
            source = stats_helpers.filter_regular_and_position(source)
            source = stats_helpers.select_columns(source, stats_config.SNAP_COUNTS_COLUMN_MAP, stats_config.SNAP_COUNTS_REQUIRED_COLUMNS, "snap_counts")
            return source.drop_duplicates(subset=["season", "week", "player_display_name", "position"])
        except Exception as e:
            logger.error("Failed to load snap counts: %s", e)
            raise DataLoadError(f"Failed to load snap counts: {e}", source="Statistics") from e

    @timed("StatisticsSourceLoader.load_statistics_sources")
    def load_statistics_sources(self) -> dict[str, pd.DataFrame]:
        """Load all statistics data sources in parallel."""
        loaders = self._build_loader_map()
        results: dict[str, pd.DataFrame] = {}
        with ThreadPoolExecutor(max_workers=min(len(loaders), 8)) as executor:
            futures = {executor.submit(loader): name for name, loader in loaders.items()}
            for future in as_completed(futures):
                results[futures[future]] = future.result()
        return results

    def _build_loader_map(self) -> dict[str, Callable[[], pd.DataFrame]]:
        """Return the source-name to loader-function mapping."""
        return {
            "player_weekly": self.load_player_weekly_stats,
            "player_seasonal": self.load_player_seasonal_stats,
            "ff_opp_weekly": self.load_ff_opportunity_weekly,
            "nextgen_pass_weekly": self.load_nextgen_passing_stats,
            "nextgen_rec_weekly": self.load_nextgen_receiving_stats,
            "nextgen_rush_weekly": self.load_nextgen_rushing_stats,
            "pfr_pass_weekly": self.load_pfr_adv_pass_weekly,
            "pfr_rush_weekly": self.load_pfr_adv_rush_weekly,
            "pfr_rec_weekly": self.load_pfr_adv_rec_weekly,
            "pfr_pass_season": self.load_pfr_adv_pass_season,
            "pfr_rush_season": self.load_pfr_adv_rush_season,
            "pfr_rec_season": self.load_pfr_adv_rec_season,
            "snap_counts": self.load_snap_counts,
        }

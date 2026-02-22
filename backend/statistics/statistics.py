"""Player statistics processing and cache generation."""

from concurrent.futures import ThreadPoolExecutor, as_completed
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

    @timed("Statistics._load_player_weekly_stats")
    def _load_player_weekly_stats(self) -> pd.DataFrame:
        """Load and normalize weekly regular-season player stats."""
        try:
            source = nfl.load_player_stats(summary_level="week", seasons=self.seasons).to_pandas()
            source = stats_helpers.filter_regular_and_position(source)
            return stats_helpers.select_columns(source, constants.PLAYER_WEEKLY_COLUMN_MAP)
        except Exception as e:
            logger.error(f"Failed to load player weekly stats: {e}")
            raise DataLoadError(f"Failed to load player stats: {e}", source="Statistics") from e
        
    @timed("Statistics._load_player_seasonal_stats")
    def _load_player_seasonal_stats(self) -> pd.DataFrame:
        """Load and normalize seasonal regular-season player stats."""
        try:
            source = nfl.load_player_stats(summary_level="reg", seasons=self.seasons).to_pandas()
            if "team" not in source.columns and "recent_team" in source.columns:
                source = source.rename(columns={"recent_team": "team"})
            source = stats_helpers.filter_regular_and_position(source)
            return stats_helpers.select_columns(source, constants.PLAYER_SEASONAL_COLUMN_MAP)
        except Exception as e:
            logger.error(f"Failed to load player seasonal stats: {e}")
            raise DataLoadError(f"Failed to load player stats: {e}", source="Statistics") from e
        
    @timed("Statistics._load_ff_opportunity_weekly")
    def _load_ff_opportunity_weekly(self) -> pd.DataFrame:
        """Load weekly fantasy opportunity stats from nflreadpy."""
        try:
            source = nfl.load_ff_opportunity(stat_type="weekly", seasons=self.seasons).to_pandas().rename(columns={"full_name": "player_display_name", "posteam": "team"})
            source["season"] = pd.to_numeric(source["season"], errors="coerce")
            source["week"] = pd.to_numeric(source["week"], errors="coerce")
            source = source.dropna(subset=["season", "week"]).astype({"season": "int32", "week": "int32"})
            source = stats_helpers.filter_regular_and_position(source)
            return stats_helpers.select_columns(source, constants.FF_OPP_WEEKLY_COLUMN_MAP)
        except Exception as e:
            logger.error(f"Failed to load weekly fantasy opportunity stats: {e}")
            raise DataLoadError(f"Failed to load weekly fantasy opportunity stats: {e}", source="Statistics") from e

    @timed("Statistics._load_nextgen_passing_stats")
    def _load_nextgen_passing_stats(self) -> pd.DataFrame:
        """Load Next Gen passing stats from nflreadpy."""
        try:
            source = nfl.load_nextgen_stats(stat_type="passing", seasons=self.seasons).to_pandas().rename(columns={"player_position": "position", "team_abbr": "team"})
            source = stats_helpers.filter_regular_and_position(source)
            return stats_helpers.select_columns(source, constants.NEXTGEN_PASS_COLUMN_MAP)
        except Exception as e:
            logger.error(f"Failed to load Next Gen passing stats: {e}")
            raise DataLoadError(f"Failed to load Next Gen passing stats: {e}", source="Statistics") from e

    @timed("Statistics._load_nextgen_receiving_stats")
    def _load_nextgen_receiving_stats(self) -> pd.DataFrame:
        """Load Next Gen receiving stats from nflreadpy."""
        try:
            source = nfl.load_nextgen_stats(stat_type="receiving", seasons=self.seasons).to_pandas().rename(columns={"player_position": "position", "team_abbr": "team"})
            source = stats_helpers.filter_regular_and_position(source)
            return stats_helpers.select_columns(source, constants.NEXTGEN_REC_COLUMN_MAP)
        except Exception as e:
            logger.error(f"Failed to load Next Gen receiving stats: {e}")
            raise DataLoadError(f"Failed to load Next Gen receiving stats: {e}", source="Statistics") from e

    @timed("Statistics._load_nextgen_rushing_stats")
    def _load_nextgen_rushing_stats(self) -> pd.DataFrame:
        """Load Next Gen rushing stats from nflreadpy."""
        try:
            source = nfl.load_nextgen_stats(stat_type="rushing", seasons=self.seasons).to_pandas().rename(columns={"player_position": "position", "team_abbr": "team"})
            source = stats_helpers.filter_regular_and_position(source)
            return stats_helpers.select_columns(source, constants.NEXTGEN_RUSH_COLUMN_MAP)
        except Exception as e:
            logger.error(f"Failed to load Next Gen rushing stats: {e}")
            raise DataLoadError(f"Failed to load Next Gen rushing stats: {e}", source="Statistics") from e

    @timed("Statistics._load_pfr_adv_pass_weekly")
    def _load_pfr_adv_pass_weekly(self) -> pd.DataFrame:
        """Load weekly PFR advanced passing stats from nflreadpy."""
        try:
            pfr_seasons = self.seasons
            if min(self.seasons) < 2018:
                pfr_seasons = [season for season in self.seasons if season >= 2018]
            source = nfl.load_pfr_advstats(stat_type="pass", summary_level="week", seasons=pfr_seasons).to_pandas().rename(columns={"pfr_player_name": "player_display_name"})
            return stats_helpers.select_columns(source, constants.PFR_PASS_WEEKLY_COLUMN_MAP)
        except Exception as e:
            logger.error(f"Failed to load weekly PFR advanced pass stats: {e}")
            raise DataLoadError(f"Failed to load weekly PFR advanced pass stats: {e}", source="Statistics") from e

    @timed("Statistics._load_pfr_adv_rush_weekly")
    def _load_pfr_adv_rush_weekly(self) -> pd.DataFrame:
        """Load weekly PFR advanced rushing stats from nflreadpy."""
        try:
            pfr_seasons = self.seasons
            if min(self.seasons) < 2018:
                pfr_seasons = [season for season in self.seasons if season >= 2018]
            source = nfl.load_pfr_advstats(stat_type="rush", summary_level="week", seasons=pfr_seasons).to_pandas().rename(columns={"pfr_player_name": "player_display_name"})
            return stats_helpers.select_columns(source, constants.PFR_RUSH_WEEKLY_COLUMN_MAP)
        except Exception as e:
            logger.error(f"Failed to load weekly PFR advanced rush stats: {e}")
            raise DataLoadError(f"Failed to load weekly PFR advanced rush stats: {e}", source="Statistics") from e

    @timed("Statistics._load_pfr_adv_rec_weekly")
    def _load_pfr_adv_rec_weekly(self) -> pd.DataFrame:
        """Load weekly PFR advanced receiving stats from nflreadpy."""
        try:
            pfr_seasons = self.seasons
            if min(self.seasons) < 2018:
                pfr_seasons = [season for season in self.seasons if season >= 2018]
            source = nfl.load_pfr_advstats(stat_type="rec", summary_level="week", seasons=pfr_seasons).to_pandas().rename(columns={"pfr_player_name": "player_display_name"})
            return stats_helpers.select_columns(source, constants.PFR_REC_WEEKLY_COLUMN_MAP)
        except Exception as e:
            logger.error(f"Failed to load weekly PFR advanced receiving stats: {e}")
            raise DataLoadError(f"Failed to load weekly PFR advanced receiving stats: {e}", source="Statistics") from e

    @timed("Statistics._load_pfr_adv_pass_season")
    def _load_pfr_adv_pass_season(self) -> pd.DataFrame:
        """Load seasonal PFR advanced passing stats from nflreadpy."""
        try:
            pfr_seasons = self.seasons
            if min(self.seasons) < 2018:
                pfr_seasons = [season for season in self.seasons if season >= 2018]
            source = nfl.load_pfr_advstats(stat_type="pass", summary_level="season", seasons=pfr_seasons).to_pandas().rename(columns={"player": "player_display_name"})
            return stats_helpers.select_columns(source, constants.PFR_PASS_SEASON_COLUMN_MAP)
        except Exception as e:
            logger.error(f"Failed to load seasonal PFR advanced pass stats: {e}")
            raise DataLoadError(f"Failed to load seasonal PFR advanced pass stats: {e}", source="Statistics") from e

    @timed("Statistics._load_pfr_adv_rush_season")
    def _load_pfr_adv_rush_season(self) -> pd.DataFrame:
        """Load seasonal PFR advanced rushing stats from nflreadpy."""
        try:
            pfr_seasons = self.seasons
            if min(self.seasons) < 2018:
                pfr_seasons = [season for season in self.seasons if season >= 2018]
            source = nfl.load_pfr_advstats(stat_type="rush", summary_level="season", seasons=pfr_seasons).to_pandas().rename(columns={"player": "player_display_name", "tm": "team", "pos": "position"})
            return stats_helpers.select_columns(source, constants.PFR_RUSH_SEASON_COLUMN_MAP)
        except Exception as e:
            logger.error(f"Failed to load seasonal PFR advanced rush stats: {e}")
            raise DataLoadError(f"Failed to load seasonal PFR advanced rush stats: {e}", source="Statistics") from e

    @timed("Statistics._load_pfr_adv_rec_season")
    def _load_pfr_adv_rec_season(self) -> pd.DataFrame:
        """Load seasonal PFR advanced receiving stats from nflreadpy."""
        try:
            pfr_seasons = self.seasons
            if min(self.seasons) < 2018:
                pfr_seasons = [season for season in self.seasons if season >= 2018]
            source = nfl.load_pfr_advstats(stat_type="rec", summary_level="season", seasons=pfr_seasons).to_pandas().rename(columns={"player": "player_display_name", "tm": "team", "pos": "position"})
            return stats_helpers.select_columns(source, constants.PFR_REC_SEASON_COLUMN_MAP)
        except Exception as e:
            logger.error(f"Failed to load seasonal PFR advanced receiving stats: {e}")
            raise DataLoadError(f"Failed to load seasonal PFR advanced receiving stats: {e}", source="Statistics") from e
        
    @timed("Statistics._load_snap_counts")
    def _load_snap_counts(self) -> pd.DataFrame:
        """Load and normalize weekly regular-season snap counts."""
        try:
            snap_seasons = self.seasons
            if min(self.seasons) < 2012:
                snap_seasons = [season for season in self.seasons if season >= 2012]
            source = nfl.load_snap_counts(seasons=snap_seasons).to_pandas().rename(columns={"player": "player_display_name"})
            source = stats_helpers.filter_regular_and_position(source)
            source = stats_helpers.select_columns(source, constants.SNAP_COUNTS_COLUMN_MAP)
            return source.drop_duplicates(subset=["season", "week", "player_display_name", "position"])
        except Exception as e:
            logger.error(f"Failed to load snap counts: {e}")
            raise DataLoadError(f"Failed to load snap counts: {e}", source="Statistics") from e

    @timed("Statistics._extract_all_roster_data")
    def _extract_all_roster_data(self, rosters: pd.DataFrame) -> Tuple[Dict[str, str], Dict[str, int], set[str], Dict[str, str], Dict[str, str], Dict[str, bool]]:
        """Extract all roster-based data in a single pass through the dataframe."""
        try:
            current_season = constants.CURRENT_SEASON
            today = pd.Timestamp.now().normalize()
            player_positions: Dict[str, str] = {}
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
                if position in constants.POSITIONS:
                    player_positions[name] = position
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
            logger.info("Positions: %s | Ages: %s | Eligible: %s | Headshots: %s | Player-Teams: %s | Rookies: %s", len(player_positions), len(player_ages), len(eligible_players), len(player_headshots), len(player_teams), sum(1 for v in rookies.values() if v))
            
            return player_positions, player_ages, eligible_players, player_headshots, player_teams, rookies
        except Exception as e:
            logger.error(f"Failed to extract roster data: {e}")
            raise DataProcessingError(f"Failed to extract roster data: {e}", source="Statistics") from e

    @timed("Statistics._load_statistics_sources")
    def _load_statistics_sources(self) -> Dict[str, pd.DataFrame]:
        """Load all statistics data sources in parallel."""
        loaders = {
            "player_weekly": self._load_player_weekly_stats,
            "player_seasonal": self._load_player_seasonal_stats,
            "ff_opp_weekly": self._load_ff_opportunity_weekly,
            "nextgen_pass_weekly": self._load_nextgen_passing_stats,
            "nextgen_rec_weekly": self._load_nextgen_receiving_stats,
            "nextgen_rush_weekly": self._load_nextgen_rushing_stats,
            "pfr_pass_weekly": self._load_pfr_adv_pass_weekly,
            "pfr_rush_weekly": self._load_pfr_adv_rush_weekly,
            "pfr_rec_weekly": self._load_pfr_adv_rec_weekly,
            "pfr_pass_season": self._load_pfr_adv_pass_season,
            "pfr_rush_season": self._load_pfr_adv_rush_season,
            "pfr_rec_season": self._load_pfr_adv_rec_season,
            "snap_counts": self._load_snap_counts,
        }
        results: Dict[str, pd.DataFrame] = {}
        with ThreadPoolExecutor(max_workers=min(len(loaders), 8)) as executor:
            futures = {executor.submit(loader): name for name, loader in loaders.items()}
            for future in as_completed(futures):
                results[futures[future]] = future.result()
        return results

    @timed("Statistics._partition_data")
    def _merge_and_partition_data(self, player_weekly: pd.DataFrame, player_seasonal: pd.DataFrame, ff_opp_weekly: pd.DataFrame, nextgen_pass_weekly: pd.DataFrame, nextgen_rec_weekly: pd.DataFrame, nextgen_rush_weekly: pd.DataFrame, pfr_pass_weekly: pd.DataFrame, pfr_rush_weekly: pd.DataFrame, pfr_rec_weekly: pd.DataFrame, pfr_pass_season: pd.DataFrame, pfr_rush_season: pd.DataFrame, pfr_rec_season: pd.DataFrame, snap_counts: pd.DataFrame) -> Tuple[Dict[int, Dict[str, pd.DataFrame]], Dict[str, List[Dict]]]:
        """Build cache views from pre-loaded statistics sources."""
        try:
            weekly_df = player_weekly
            seasonal_df = player_seasonal

            weekly_df = stats_helpers.merge_prefixed(weekly_df, snap_counts, ["season", "week", "game_id", "player_display_name", "position", "team"], "")
            weekly_df = stats_helpers.merge_prefixed(weekly_df, ff_opp_weekly, ["season", "week", "game_id", "player_id", "player_display_name", "position", "team"], "")
            weekly_df = stats_helpers.merge_prefixed(weekly_df, nextgen_pass_weekly, ["season", "week", "player_display_name", "position", "team"], "")
            weekly_df = stats_helpers.merge_prefixed(weekly_df, nextgen_rec_weekly, ["season", "week", "player_display_name", "position", "team"], "")
            weekly_df = stats_helpers.merge_prefixed(weekly_df, nextgen_rush_weekly, ["season", "week", "player_display_name", "position", "team"], "")
            weekly_df = stats_helpers.merge_prefixed(weekly_df, pfr_pass_weekly, ["season", "week", "game_id", "player_display_name", "team"], "")
            weekly_df = stats_helpers.merge_prefixed(weekly_df, pfr_rush_weekly, ["season", "week", "game_id", "player_display_name", "team"], "")
            weekly_df = stats_helpers.merge_prefixed(weekly_df, pfr_rec_weekly, ["season", "week", "game_id", "player_display_name", "team"], "")

            seasonal_df = stats_helpers.merge_prefixed(seasonal_df, pfr_pass_season, ["season", "player_display_name", "team"], "")
            seasonal_df = stats_helpers.merge_prefixed(seasonal_df, pfr_rush_season, ["season", "player_display_name", "team", "position"], "")
            seasonal_df = stats_helpers.merge_prefixed(seasonal_df, pfr_rec_season, ["season", "player_display_name", "team", "position"], "")

            weekly_df = stats_helpers.add_derived_stats(weekly_df)
            seasonal_df = stats_helpers.add_derived_stats(seasonal_df)
            weekly_df = stats_helpers.add_interpreted_metrics(weekly_df, include_week=True)
            seasonal_df = stats_helpers.add_interpreted_metrics(seasonal_df)

            seasonal_data = stats_helpers.build_seasonal_data(seasonal_df)
            weekly_player_stats = stats_helpers.build_weekly_player_stats(weekly_df)

            return seasonal_data, weekly_player_stats
        except Exception as e:
            logger.error(f"Failed to partition statistics data: {e}")
            raise DataProcessingError(f"Failed to partition statistics data: {e}", source="Statistics") from e

    @timed("Statistics.run")
    def run(self) -> None:
        """Load data, process statistics, and store cache data."""
        loaders = {"rosters": self._load_rosters, "sources": self._load_statistics_sources}
        results: Dict[str, object] = {}
        with ThreadPoolExecutor(max_workers=2) as executor:
            futures = {executor.submit(loader): name for name, loader in loaders.items()}
            for future in as_completed(futures):
                results[futures[future]] = future.result()

        rosters = cast(pd.DataFrame, results["rosters"])
        sources = cast(Dict[str, pd.DataFrame], results["sources"])

        player_positions, player_ages, eligible, headshots, teams, rookies = self._extract_all_roster_data(rosters)
        seasonal_data, weekly_stats = self._merge_and_partition_data(sources["player_weekly"], sources["player_seasonal"], sources["ff_opp_weekly"], sources["nextgen_pass_weekly"], sources["nextgen_rec_weekly"], sources["nextgen_rush_weekly"], sources["pfr_pass_weekly"], sources["pfr_rush_weekly"], sources["pfr_rec_weekly"], sources["pfr_pass_season"], sources["pfr_rush_season"], sources["pfr_rec_season"], sources["snap_counts"])

        stats_player_names = stats_helpers.collect_stats_player_names(seasonal_data, weekly_stats)
        player_name_aliases = stats_helpers.build_player_name_aliases(set(player_positions.keys()), stats_player_names)
        all_players = stats_helpers.build_all_players(player_positions, eligible, player_ages, headshots, teams, rookies, valid_player_names=stats_player_names)

        self.set_cache(
            {
                constants.STATS["ALL_PLAYERS"]: all_players,
                constants.STATS["BY_YEAR"]: seasonal_data,
                constants.STATS["PLAYER_WEEKLY_STATS"]: weekly_stats,
                constants.STATS["PLAYER_NAME_ALIASES"]: player_name_aliases,
            }
        )

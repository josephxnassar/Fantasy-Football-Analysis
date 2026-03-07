"""Player statistics processing and cache generation."""

import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List, NamedTuple, Tuple, cast

import nflreadpy as nfl
import pandas as pd

from backend import base_source
from backend.statistics.util import stats_helpers
from backend.util import constants
from backend.util.exceptions import DataLoadError, DataProcessingError
from backend.util.timing import timed

logger = logging.getLogger(__name__)


class RosterData(NamedTuple):
    """Extracted roster-level lookups produced by _extract_all_roster_data."""
    positions: Dict[str, str]
    ages: Dict[str, int]
    eligible: set[str]
    headshots: Dict[str, str]
    teams: Dict[str, str]
    rookies: Dict[str, bool]


class Statistics(base_source.BaseSource):
    """Processes player statistics and builds stat caches."""

    def __init__(self, seasons: List[int]) -> None:
        """Initialize with seasons"""
        super().__init__(seasons)

    @timed("Statistics._load_rosters")
    def _load_rosters(self) -> pd.DataFrame:
        """Load roster data from nflreadpy"""
        try:
            return nfl.load_rosters(seasons=self.seasons).to_pandas()
        except Exception as e:
            logger.error("Failed to load rosters: %s", e)
            raise DataLoadError(f"Failed to load rosters: {e}", source="Statistics") from e

    def _pfr_seasons(self, min_year: int = 2018) -> List[int]:
        """Filter self.seasons to those >= min_year (PFR/snap data availability guard)."""
        return [s for s in self.seasons if s >= min_year]

    @timed("Statistics._load_player_weekly_stats")
    def _load_player_weekly_stats(self) -> pd.DataFrame:
        """Load and normalize weekly regular-season player stats."""
        try:
            source = nfl.load_player_stats(summary_level="week", seasons=self.seasons).to_pandas()
            source = stats_helpers.filter_regular_and_position(source, constants.POSITIONS)
            return stats_helpers.select_columns(source, constants.PLAYER_WEEKLY_COLUMN_MAP)
        except Exception as e:
            logger.error("Failed to load player weekly stats: %s", e)
            raise DataLoadError(f"Failed to load player stats: {e}", source="Statistics") from e
        
    @timed("Statistics._load_player_seasonal_stats")
    def _load_player_seasonal_stats(self) -> pd.DataFrame:
        """Load and normalize seasonal regular-season player stats."""
        try:
            source = nfl.load_player_stats(summary_level="reg", seasons=self.seasons).to_pandas()
            source = source.rename(columns={"recent_team": "team"})
            source = stats_helpers.filter_regular_and_position(source, constants.POSITIONS)
            return stats_helpers.select_columns(source, constants.PLAYER_SEASONAL_COLUMN_MAP)
        except Exception as e:
            logger.error("Failed to load player seasonal stats: %s", e)
            raise DataLoadError(f"Failed to load player stats: {e}", source="Statistics") from e
        
    @timed("Statistics._load_ff_opportunity_weekly")
    def _load_ff_opportunity_weekly(self) -> pd.DataFrame:
        """Load weekly fantasy opportunity stats from nflreadpy."""
        try:
            source = nfl.load_ff_opportunity(stat_type="weekly", seasons=self.seasons).to_pandas().rename(columns={"full_name": "player_display_name", "posteam": "team"})
            source["season"] = pd.to_numeric(source["season"], errors="coerce")
            source["week"] = pd.to_numeric(source["week"], errors="coerce")
            source = source.dropna(subset=["season", "week"]).astype({"season": "int32", "week": "int32"})
            source = stats_helpers.filter_regular_and_position(source, constants.POSITIONS)
            return stats_helpers.select_columns(source, constants.FF_OPP_WEEKLY_COLUMN_MAP)
        except Exception as e:
            logger.error("Failed to load weekly fantasy opportunity stats: %s", e)
            raise DataLoadError(f"Failed to load weekly fantasy opportunity stats: {e}", source="Statistics") from e

    @timed("Statistics._load_nextgen_passing_stats")
    def _load_nextgen_passing_stats(self) -> pd.DataFrame:
        """Load Next Gen passing stats from nflreadpy."""
        try:
            source = nfl.load_nextgen_stats(stat_type="passing", seasons=self.seasons).to_pandas().rename(columns={"player_position": "position", "team_abbr": "team"})
            source = stats_helpers.filter_regular_and_position(source, constants.POSITIONS)
            return stats_helpers.select_columns(source, constants.NEXTGEN_PASS_COLUMN_MAP)
        except Exception as e:
            logger.error("Failed to load Next Gen passing stats: %s", e)
            raise DataLoadError(f"Failed to load Next Gen passing stats: {e}", source="Statistics") from e

    @timed("Statistics._load_nextgen_receiving_stats")
    def _load_nextgen_receiving_stats(self) -> pd.DataFrame:
        """Load Next Gen receiving stats from nflreadpy."""
        try:
            source = nfl.load_nextgen_stats(stat_type="receiving", seasons=self.seasons).to_pandas().rename(columns={"player_position": "position", "team_abbr": "team"})
            source = stats_helpers.filter_regular_and_position(source, constants.POSITIONS)
            return stats_helpers.select_columns(source, constants.NEXTGEN_REC_COLUMN_MAP)
        except Exception as e:
            logger.error("Failed to load Next Gen receiving stats: %s", e)
            raise DataLoadError(f"Failed to load Next Gen receiving stats: {e}", source="Statistics") from e

    @timed("Statistics._load_nextgen_rushing_stats")
    def _load_nextgen_rushing_stats(self) -> pd.DataFrame:
        """Load Next Gen rushing stats from nflreadpy."""
        try:
            source = nfl.load_nextgen_stats(stat_type="rushing", seasons=self.seasons).to_pandas().rename(columns={"player_position": "position", "team_abbr": "team"})
            source = stats_helpers.filter_regular_and_position(source, constants.POSITIONS)
            return stats_helpers.select_columns(source, constants.NEXTGEN_RUSH_COLUMN_MAP)
        except Exception as e:
            logger.error("Failed to load Next Gen rushing stats: %s", e)
            raise DataLoadError(f"Failed to load Next Gen rushing stats: {e}", source="Statistics") from e

    @timed("Statistics._load_pfr_adv_pass_weekly")
    def _load_pfr_adv_pass_weekly(self) -> pd.DataFrame:
        """Load weekly PFR advanced passing stats from nflreadpy."""
        try:
            source = nfl.load_pfr_advstats(stat_type="pass", summary_level="week", seasons=self._pfr_seasons()).to_pandas().rename(columns={"pfr_player_name": "player_display_name"})
            return stats_helpers.select_columns(source, constants.PFR_PASS_WEEKLY_COLUMN_MAP)
        except Exception as e:
            logger.error("Failed to load weekly PFR advanced pass stats: %s", e)
            raise DataLoadError(f"Failed to load weekly PFR advanced pass stats: {e}", source="Statistics") from e

    @timed("Statistics._load_pfr_adv_rush_weekly")
    def _load_pfr_adv_rush_weekly(self) -> pd.DataFrame:
        """Load weekly PFR advanced rushing stats from nflreadpy."""
        try:
            source = nfl.load_pfr_advstats(stat_type="rush", summary_level="week", seasons=self._pfr_seasons()).to_pandas().rename(columns={"pfr_player_name": "player_display_name"})
            return stats_helpers.select_columns(source, constants.PFR_RUSH_WEEKLY_COLUMN_MAP)
        except Exception as e:
            logger.error("Failed to load weekly PFR advanced rush stats: %s", e)
            raise DataLoadError(f"Failed to load weekly PFR advanced rush stats: {e}", source="Statistics") from e

    @timed("Statistics._load_pfr_adv_rec_weekly")
    def _load_pfr_adv_rec_weekly(self) -> pd.DataFrame:
        """Load weekly PFR advanced receiving stats from nflreadpy."""
        try:
            source = nfl.load_pfr_advstats(stat_type="rec", summary_level="week", seasons=self._pfr_seasons()).to_pandas().rename(columns={"pfr_player_name": "player_display_name"})
            return stats_helpers.select_columns(source, constants.PFR_REC_WEEKLY_COLUMN_MAP)
        except Exception as e:
            logger.error("Failed to load weekly PFR advanced receiving stats: %s", e)
            raise DataLoadError(f"Failed to load weekly PFR advanced receiving stats: {e}", source="Statistics") from e

    @timed("Statistics._load_pfr_adv_pass_season")
    def _load_pfr_adv_pass_season(self) -> pd.DataFrame:
        """Load seasonal PFR advanced passing stats from nflreadpy."""
        try:
            source = nfl.load_pfr_advstats(stat_type="pass", summary_level="season", seasons=self._pfr_seasons()).to_pandas().rename(columns={"player": "player_display_name"})
            return stats_helpers.select_columns(source, constants.PFR_PASS_SEASON_COLUMN_MAP)
        except Exception as e:
            logger.error("Failed to load seasonal PFR advanced pass stats: %s", e)
            raise DataLoadError(f"Failed to load seasonal PFR advanced pass stats: {e}", source="Statistics") from e

    @timed("Statistics._load_pfr_adv_rush_season")
    def _load_pfr_adv_rush_season(self) -> pd.DataFrame:
        """Load seasonal PFR advanced rushing stats from nflreadpy."""
        try:
            source = nfl.load_pfr_advstats(stat_type="rush", summary_level="season", seasons=self._pfr_seasons()).to_pandas().rename(columns={"player": "player_display_name", "tm": "team", "pos": "position"})
            return stats_helpers.select_columns(source, constants.PFR_RUSH_SEASON_COLUMN_MAP)
        except Exception as e:
            logger.error("Failed to load seasonal PFR advanced rush stats: %s", e)
            raise DataLoadError(f"Failed to load seasonal PFR advanced rush stats: {e}", source="Statistics") from e

    @timed("Statistics._load_pfr_adv_rec_season")
    def _load_pfr_adv_rec_season(self) -> pd.DataFrame:
        """Load seasonal PFR advanced receiving stats from nflreadpy."""
        try:
            source = nfl.load_pfr_advstats(stat_type="rec", summary_level="season", seasons=self._pfr_seasons()).to_pandas().rename(columns={"player": "player_display_name", "tm": "team", "pos": "position"})
            return stats_helpers.select_columns(source, constants.PFR_REC_SEASON_COLUMN_MAP)
        except Exception as e:
            logger.error("Failed to load seasonal PFR advanced receiving stats: %s", e)
            raise DataLoadError(f"Failed to load seasonal PFR advanced receiving stats: {e}", source="Statistics") from e
        
    @timed("Statistics._load_snap_counts")
    def _load_snap_counts(self) -> pd.DataFrame:
        """Load and normalize weekly regular-season snap counts."""
        try:
            source = nfl.load_snap_counts(seasons=self._pfr_seasons(2012)).to_pandas().rename(columns={"player": "player_display_name"})
            source = stats_helpers.filter_regular_and_position(source, constants.POSITIONS)
            source = stats_helpers.select_columns(source, constants.SNAP_COUNTS_COLUMN_MAP)
            return source.drop_duplicates(subset=["season", "week", "player_display_name", "position"])
        except Exception as e:
            logger.error("Failed to load snap counts: %s", e)
            raise DataLoadError(f"Failed to load snap counts: {e}", source="Statistics") from e

    @timed("Statistics._extract_all_roster_data")
    def _extract_all_roster_data(self, rosters: pd.DataFrame) -> RosterData:
        """Extract all roster-based data in a single pass through the dataframe."""
        current_season = constants.CURRENT_SEASON
        today = pd.Timestamp.now().normalize()
        player_positions: Dict[str, str] = {}
        player_ages: Dict[str, int] = {}
        eligible_players: set[str] = set()
        player_headshots: Dict[str, str] = {}
        player_teams: Dict[str, str] = {}
        rookies: Dict[str, bool] = {}
        for row in rosters.itertuples(index=False):
            name = getattr(row, "full_name", None)
            if not isinstance(name, str) or not name:
                continue
            season_raw = getattr(row, "season", None)
            season_int: int | None = None
            if pd.notna(season_raw):
                try:
                    season_int = int(cast(int | float | str, season_raw))
                except (TypeError, ValueError):
                    season_int = None
            position = getattr(row, "position", None)
            if not isinstance(position, str) or position not in constants.POSITIONS:
                continue
            player_positions[name] = position
            if pd.notna(birth_date := getattr(row, "birth_date", None)):
                birth_ts = pd.to_datetime(birth_date)
                age = (today - birth_ts).days // 365
                if age > 0:
                    player_ages[name] = int(age)
            if season_int == current_season:
                if getattr(row, "status", None) != "RET":
                    eligible_players.add(name)
                if isinstance(headshot := getattr(row, "headshot_url", None), str) and headshot:
                    player_headshots[name] = headshot
                if isinstance(team := getattr(row, "team", None), str) and team:
                    player_teams[name] = constants.TEAM_ABBR_NORMALIZATION.get(team, team)
                if (entry_year := getattr(row, "entry_year", None)) == current_season and pd.notna(entry_year):
                    rookies[name] = True
        logger.info("Positions: %s | Ages: %s | Eligible: %s | Headshots: %s | Player-Teams: %s | Rookies: %s", len(player_positions), len(player_ages), len(eligible_players), len(player_headshots), len(player_teams), sum(1 for v in rookies.values() if v))
        return RosterData(player_positions, player_ages, eligible_players, player_headshots, player_teams, rookies)

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
    
    @timed("Statistics._merge_statistics_data")
    def _merge_statistics_data(self, sources: Dict[str, pd.DataFrame]) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Merge weekly and seasonal source tables into base dataframes."""
        mergers = {
            "weekly": self._merge_weekly_statistics_data,
            "seasonal": self._merge_seasonal_statistics_data,
        }
        results: Dict[str, pd.DataFrame] = {}
        with ThreadPoolExecutor(max_workers=2) as executor:
            futures = {executor.submit(merge_fn, sources): name for name, merge_fn in mergers.items()}
            for future in as_completed(futures):
                results[futures[future]] = future.result()
        return results["weekly"], results["seasonal"]

    @timed("Statistics._merge_weekly_statistics_data")
    def _merge_weekly_statistics_data(self, sources: Dict[str, pd.DataFrame]) -> pd.DataFrame:
        """Merge weekly source tables into base weekly dataframe."""
        weekly_df = sources["player_weekly"]
        weekly_df = stats_helpers.merge_source(weekly_df, sources["snap_counts"], ["season", "week", "game_id", "player_display_name", "position", "team"])
        weekly_df = stats_helpers.merge_source(weekly_df, sources["ff_opp_weekly"], ["season", "week", "game_id", "player_id", "player_display_name", "position", "team"])
        weekly_df = stats_helpers.merge_source(weekly_df, sources["nextgen_pass_weekly"], ["season", "week", "player_display_name", "position", "team"])
        weekly_df = stats_helpers.merge_source(weekly_df, sources["nextgen_rec_weekly"], ["season", "week", "player_display_name", "position", "team"])
        weekly_df = stats_helpers.merge_source(weekly_df, sources["nextgen_rush_weekly"], ["season", "week", "player_display_name", "position", "team"])
        weekly_df = stats_helpers.merge_source(weekly_df, sources["pfr_pass_weekly"], ["season", "week", "game_id", "player_display_name", "team"])
        weekly_df = stats_helpers.merge_source(weekly_df, sources["pfr_rush_weekly"], ["season", "week", "game_id", "player_display_name", "team"])
        weekly_df = stats_helpers.merge_source(weekly_df, sources["pfr_rec_weekly"], ["season", "week", "game_id", "player_display_name", "team"])
        return weekly_df

    @timed("Statistics._merge_seasonal_statistics_data")
    def _merge_seasonal_statistics_data(self, sources: Dict[str, pd.DataFrame]) -> pd.DataFrame:
        """Merge seasonal source tables into base seasonal dataframe."""
        seasonal_df = sources["player_seasonal"]
        return stats_helpers.merge_aligned_pfr_seasonal_sources(seasonal_df, sources, [("pfr_pass_season", ["season", "player_display_name", "team"]),
                                                                                       ("pfr_rush_season", ["season", "player_display_name", "team", "position"]),
                                                                                       ("pfr_rec_season", ["season", "player_display_name", "team", "position"])])

    @timed("Statistics._shape_statistics_data")
    def _shape_statistics_data(self, weekly_df: pd.DataFrame, seasonal_df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Shape merged dataframes with derived metrics, aliases, aggregates, and ranks."""
        weekly_df = stats_helpers.add_derived_stats(weekly_df)
        seasonal_df = stats_helpers.add_derived_stats(seasonal_df)

        weekly_df = stats_helpers.combine_aliases(weekly_df, constants.INTERPRETED_METRIC_SOURCES)
        seasonal_df = stats_helpers.combine_aliases(seasonal_df, constants.INTERPRETED_METRIC_SOURCES)

        seasonal_df = stats_helpers.merge_weekly_aggregates_into_seasonal(seasonal_df, weekly_df, constants.WEEKLY_SUM_AGGREGATE_METRICS, constants.WEEKLY_WEIGHTED_AGGREGATE_METRICS)

        weekly_df = stats_helpers.add_group_ranks(weekly_df, constants.INTERPRETED_RANK_METRICS, ["season", "position", "week"])
        seasonal_df = stats_helpers.add_group_ranks(seasonal_df, constants.INTERPRETED_RANK_METRICS, ["season", "position"])

        return weekly_df, seasonal_df
    
    @timed("Statistics._collect_stats_player_names")
    def _collect_stats_player_names(self, seasonal_df: pd.DataFrame, weekly_df: pd.DataFrame) -> set[str]:
        """Collect player names from shaped weekly and seasonal dataframes."""
        names = set(weekly_df["player_display_name"].dropna().astype(str))
        names.update(seasonal_df.loc[seasonal_df["position"].isin(constants.POSITIONS), "player_display_name"].dropna().astype(str))
        return names

    @timed("Statistics._build_statistics_data")
    def _build_statistics_data(self, weekly_df: pd.DataFrame, seasonal_df: pd.DataFrame, roster_data: RosterData, stats_player_names: set[str]) -> Tuple[Dict[int, Dict[str, pd.DataFrame]], Dict[str, List[Dict]], List[Dict]]:
        """Build seasonal stats, weekly stats, and all players in parallel."""
        builders = {
            "seasonal_player_stats": (self._build_seasonal_player_stats, (seasonal_df,)),
            "weekly_player_stats": (self._build_weekly_player_stats, (weekly_df,)),
            "all_players": (self._build_all_players, (roster_data, stats_player_names)),
        }
        results: Dict[str, object] = {}
        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = {executor.submit(fn, *args): name for name, (fn, args) in builders.items()}
            for future in as_completed(futures):
                results[futures[future]] = future.result()

        return (cast(Dict[int, Dict[str, pd.DataFrame]], results["seasonal_player_stats"]),
                cast(Dict[str, List[Dict]], results["weekly_player_stats"]),
                cast(List[Dict], results["all_players"]))

    @timed("Statistics._build_seasonal_player_stats")
    def _build_seasonal_player_stats(self, seasonal_df: pd.DataFrame) -> Dict[int, Dict[str, pd.DataFrame]]:
        """Build season -> position -> DataFrame view for chart endpoints."""
        allowed_positions = set(constants.POSITIONS)
        drop_cols = ["season", "position", "player_id", "player_name", "position_group"]
        return {
            int(season): by_position
            for season, season_group in seasonal_df.groupby("season")
            if (
                by_position := {
                    position: stats_helpers.clean_numeric_stats(
                        group.drop_duplicates(
                            subset=["player_id" if "player_id" in group.columns else "player_display_name"]
                        )
                        .drop(columns=drop_cols, errors="ignore")
                        .set_index("player_display_name")
                    )
                    for position, group in season_group.groupby("position")
                    if position in allowed_positions
                }
            )
        }

    @timed("Statistics._build_weekly_player_stats")
    def _build_weekly_player_stats(self, weekly_df: pd.DataFrame) -> Dict[str, List[Dict]]:
        """Build player -> weekly record list view for player modal."""
        ordered = weekly_df.sort_values(["season", "week", "player_display_name"])
        ordered = stats_helpers.clean_weekly_records(ordered)
        return {
            player_name: group.drop(columns=["player_display_name"], errors="ignore").to_dict("records")
            for player_name, group in ordered.groupby("player_display_name", sort=False)
        }

    @timed("Statistics._build_all_players")
    def _build_all_players(self, roster_data: RosterData, valid_player_names: set[str] | None = None) -> List[Dict]:
        """Build pre-assembled player list with player metadata for API consumption."""
        return [
            {
                "name": player_name,
                "position": roster_data.positions.get(player_name),
                "age": roster_data.ages.get(player_name),
                "headshot_url": roster_data.headshots.get(player_name),
                "team": roster_data.teams.get(player_name),
                "is_rookie": roster_data.rookies.get(player_name, False),
                "is_eligible": player_name in roster_data.eligible,
            } for player_name in roster_data.positions if valid_player_names is None or player_name in valid_player_names
        ]

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

        try:
            roster_data = self._extract_all_roster_data(rosters)
        except Exception as e:
            logger.exception("Failed to extract roster data")
            raise DataProcessingError(f"Failed to extract roster data: {e}", source="Statistics") from e

        try:
            weekly_df, seasonal_df = self._merge_statistics_data(sources)
            weekly_df, seasonal_df = self._shape_statistics_data(weekly_df, seasonal_df)
        except Exception as e:
            logger.exception("Failed to merge/shape statistics data")
            raise DataProcessingError(f"Failed to merge/shape statistics data: {e}", source="Statistics") from e

        try:
            stats_player_names = self._collect_stats_player_names(seasonal_df, weekly_df)
            seasonal_player_stats, weekly_player_stats, all_players = self._build_statistics_data(weekly_df, seasonal_df, roster_data, stats_player_names)
        except Exception as e:
            logger.exception("Failed to build statistics payloads")
            raise DataProcessingError(f"Failed to build statistics payloads: {e}", source="Statistics") from e

        self.set_cache({constants.STATS["ALL_PLAYERS"]: all_players,
                        constants.STATS["BY_YEAR"]: seasonal_player_stats,
                        constants.STATS["PLAYER_WEEKLY_STATS"]: weekly_player_stats})

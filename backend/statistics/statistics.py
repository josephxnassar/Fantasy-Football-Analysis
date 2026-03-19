"""Player statistics processing and cache generation."""

import logging
from concurrent.futures import Future, ThreadPoolExecutor, as_completed
from typing import Dict, List, NamedTuple, Tuple, cast

import pandas as pd

from backend import base_source
from backend.statistics.loaders import StatisticsSourceLoader
from backend.statistics.util import stats_helpers
from backend.util import constants
from backend.util.exceptions import DataProcessingError
from backend.util.timing import timed

logger = logging.getLogger(__name__)


class RosterData(NamedTuple):
    """Extracted roster-level lookups produced by _extract_all_roster_data."""
    positions: Dict[str, str]
    ages: Dict[str, int]
    eligible: set[str]
    headshots: Dict[str, str]
    teams: Dict[str, str]
    rookies: set[str]


class Statistics(base_source.BaseSource):
    """Processes player statistics and builds stat caches."""

    def __init__(self, seasons: List[int]) -> None:
        """Initialize with seasons"""
        super().__init__(seasons)
        self._source_loader = StatisticsSourceLoader(self.seasons)

    @timed("Statistics._extract_all_roster_data")
    def _extract_all_roster_data(self, rosters: pd.DataFrame) -> RosterData:
        """Extract all roster-based data in a single pass through the dataframe."""
        current_season = constants.CURRENT_SEASON
        today = pd.Timestamp.now().normalize()
        player_positions: Dict[str, str] = {}
        player_ages: Dict[str, int] = {}
        eligible_players: set[str] = set()
        headshot_tracker: Dict[str, tuple[int, str]] = {}
        player_headshots: Dict[str, str] = {}
        player_teams: Dict[str, str] = {}
        rookies: set[str] = set()
        for row in rosters.itertuples(index=False):
            name = getattr(row, "base_player_display_name", None)
            if not isinstance(name, str) or not name:
                continue
            season_raw = getattr(row, "base_season", None)
            season_int: int | None = None
            if pd.notna(season_raw):
                try:
                    season_int = int(cast(int | float | str, season_raw))
                except (TypeError, ValueError):
                    season_int = None
            position = getattr(row, "base_pos", None)
            if not isinstance(position, str) or position not in constants.POSITIONS:
                continue
            player_positions[name] = position
            if pd.notna(birth_date := getattr(row, "base_birth_date", None)):
                birth_ts = pd.to_datetime(birth_date)
                age = (today - birth_ts).days // 365
                if age > 0:
                    player_ages[name] = int(age)
            if isinstance(headshot := getattr(row, "base_headshot_url", None), str) and headshot and season_int is not None:
                prev = headshot_tracker.get(name)
                if not prev or season_int > prev[0]:
                    headshot_tracker[name] = (season_int, headshot)
            if season_int == current_season:
                if getattr(row, "base_status", None) != "RET":
                    eligible_players.add(name)
                if isinstance(team := getattr(row, "base_team", None), str) and team:
                    player_teams[name] = team
                if (entry_year := getattr(row, "base_entry_year", None)) == current_season and pd.notna(entry_year):
                    rookies.add(name)
        player_headshots = {name: headshot for name, (_, headshot) in headshot_tracker.items()}
        logger.info("Positions: %s | Ages: %s | Eligible: %s | Headshots: %s | Player-Teams: %s | Rookies: %s", len(player_positions), len(player_ages), len(eligible_players), len(player_headshots), len(player_teams), len(rookies))
        return RosterData(player_positions, player_ages, eligible_players, player_headshots, player_teams, rookies)

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
        weekly_join_specs: List[Tuple[str, List[str]]] = [
            ("snap_counts", ["base_season", "base_week", "base_player_display_name", "base_pos", "base_team"]),
            ("ff_opp_weekly", ["base_season", "base_week", "base_player_id", "base_player_display_name", "base_pos", "base_team"]),
            ("nextgen_pass_weekly", ["base_season", "base_week", "base_player_display_name", "base_pos", "base_team"]),
            ("nextgen_rec_weekly", ["base_season", "base_week", "base_player_display_name", "base_pos", "base_team"]),
            ("nextgen_rush_weekly", ["base_season", "base_week", "base_player_display_name", "base_pos", "base_team"]),
            ("pfr_pass_weekly", ["base_season", "base_week", "base_game_id", "base_player_display_name", "base_team"]),
            ("pfr_rush_weekly", ["base_season", "base_week", "base_game_id", "base_player_display_name", "base_team"]),
            ("pfr_rec_weekly", ["base_season", "base_week", "base_game_id", "base_player_display_name", "base_team"]),
        ]
        for source_key, join_keys in weekly_join_specs:
            source_df = stats_helpers.align_pfr_seasonal_names(sources[source_key], weekly_df)
            weekly_df = stats_helpers.merge_source(weekly_df, source_df, join_keys)
        return weekly_df

    @timed("Statistics._merge_seasonal_statistics_data")
    def _merge_seasonal_statistics_data(self, sources: Dict[str, pd.DataFrame]) -> pd.DataFrame:
        """Merge seasonal source tables into base seasonal dataframe."""
        seasonal_df = sources["player_seasonal"]
        seasonal_join_specs: List[Tuple[str, List[str]]] = [
            ("pfr_pass_season", ["base_season", "base_player_display_name", "base_team"]),
            ("pfr_rush_season", ["base_season", "base_player_display_name", "base_pos"]),
            ("pfr_rec_season", ["base_season", "base_player_display_name", "base_pos"]),
        ]

        for source_key, join_keys in seasonal_join_specs:
            aligned = stats_helpers.align_pfr_seasonal_names(sources[source_key], seasonal_df)
            # Only seasonal PFR rush/rec need this: weekly rows stay team-specific, but seasonal rows can be 2TM/3TM for traded players.
            if "base_team" in aligned.columns and "base_team" not in join_keys:
                aligned = aligned.drop(columns=["base_team"])
            seasonal_df = stats_helpers.merge_source(seasonal_df, aligned, join_keys)

        return seasonal_df

    @timed("Statistics._shape_statistics_data")
    def _shape_statistics_data(self, weekly_df: pd.DataFrame, seasonal_df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Shape merged dataframes with aggregates and ranks."""
        summed_metrics = [
            "fantasy_fp_ppr_exp", "fantasy_fp_ppr_diff",
            "pass_1st_exp", "pass_1st_diff", "pass_2pt_exp", "pass_2pt_diff", "pass_comp_exp", "pass_comp_diff",
            "pass_fp_std", "pass_fp_std_exp", "pass_fp_std_diff", "pass_ints_exp", "pass_ints_diff",
            "pass_tds_exp", "pass_tds_diff", "pass_yds_exp", "pass_yds_diff",
            "rec_1st_exp", "rec_1st_diff", "rec_2pt_exp", "rec_2pt_diff", "rec_fp_ppr", "rec_fp_ppr_exp",
            "rec_fp_ppr_diff", "rec_ints_exp", "rec_ints_diff", "rec_recs_exp", "rec_recs_diff",
            "rec_tds_exp", "rec_tds_diff", "rec_yds_exp", "rec_yds_diff",
            "rush_1st_exp", "rush_1st_diff", "rush_2pt_exp", "rush_2pt_diff", "rush_fp_std", "rush_fp_std_exp",
            "rush_fp_std_diff", "rush_tds_exp", "rush_tds_diff", "rush_yds_exp", "rush_yds_diff", "rush_yds_over_exp",
            "total_1st", "total_1st_exp", "total_1st_diff", "total_tds", "total_tds_exp", "total_tds_diff",
            "total_yds", "total_yds_exp", "total_yds_diff", "snap_off", "snap_spec",
        ]
        averaged_metrics = [
            "pass_aggressiveness", "pass_avg_air_dist", "pass_avg_air_yds_diff", "pass_avg_air_yds_to_sticks",
            "pass_avg_comp_air_yds", "pass_avg_intended_air_yds", "pass_avg_time_to_throw", "pass_comp_pct",
            "pass_comp_pct_exp", "pass_max_air_dist", "pass_max_completed_air_dist", "pass_rating",
            "rec_air_yds_share_pct", "rec_avg_cushion", "rec_avg_intended_air_yds", "rec_avg_sep",
            "rec_avg_yac", "rec_avg_yac_above_exp", "rec_avg_yac_exp", "rec_catch_pct",
            "rush_att_gte_eight_def_pct", "rush_avg_time_to_los", "rush_avg_yds", "rush_efficiency",
            "rush_pct_over_exp", "rush_yds_over_exp_per_att", "snap_off_pct", "snap_spec_pct", "kick_gwfg_dist",
        ]
        rank_metrics = [
            "fantasy_fp_ppr", "fantasy_fp_std", "fantasy_fp_ppr_exp",
            "pass_att", "pass_yds", "pass_tds", "pass_cpoe", "pass_rating", "pass_epa",
            "rush_att", "rush_yds", "rush_tds", "rush_epa",
            "rec_recs", "rec_tgts", "rec_yds", "rec_tds", "rec_epa",
        ]
        seasonal_df = stats_helpers.merge_weekly_aggregates_into_seasonal(seasonal_df, weekly_df, summed_metrics, averaged_metrics)
        weekly_df = stats_helpers.add_group_ranks(weekly_df, ["base_season", "base_pos", "base_week"], rank_metrics)
        seasonal_df = stats_helpers.add_group_ranks(seasonal_df, ["base_season", "base_pos"], rank_metrics)
        return weekly_df, seasonal_df
    
    @timed("Statistics._collect_stats_player_names")
    def _collect_stats_player_names(self, seasonal_df: pd.DataFrame, weekly_df: pd.DataFrame) -> set[str]:
        """Collect player names from shaped weekly and seasonal dataframes."""
        names = set(weekly_df["base_player_display_name"].dropna().astype(str))
        names.update(seasonal_df["base_player_display_name"].dropna().astype(str))
        return names

    @timed("Statistics._build_statistics_data")
    def _build_statistics_data(self, weekly_df: pd.DataFrame, seasonal_df: pd.DataFrame, roster_data: RosterData, stats_player_names: set[str]) -> Tuple[Dict[int, Dict[str, pd.DataFrame]], Dict[str, List[Dict]], List[Dict]]:
        """Build seasonal stats, weekly stats, and all players in parallel."""
        results: Dict[str, object] = {}
        with ThreadPoolExecutor(max_workers=3) as executor:
            futures: Dict[Future[object], str] = {
                executor.submit(self._build_seasonal_player_stats, seasonal_df): "seasonal_player_stats",
                executor.submit(self._build_weekly_player_stats, weekly_df): "weekly_player_stats",
                executor.submit(self._build_all_players, roster_data, stats_player_names): "all_players",
            }
            for future in as_completed(futures):
                results[futures[future]] = future.result()

        return (cast(Dict[int, Dict[str, pd.DataFrame]], results["seasonal_player_stats"]),
                cast(Dict[str, List[Dict]], results["weekly_player_stats"]),
                cast(List[Dict], results["all_players"]))

    @timed("Statistics._build_seasonal_player_stats")
    def _build_seasonal_player_stats(self, seasonal_df: pd.DataFrame) -> Dict[int, Dict[str, pd.DataFrame]]:
        """Build season -> position -> DataFrame view for chart endpoints."""
        allowed_positions = set(constants.POSITIONS)
        drop_cols = ["base_season", "base_pos", "base_player_id", "base_player_name", "base_pos_group"]
        return {
            int(season): by_position
            for season, season_group in seasonal_df.groupby("base_season")
            if (
                by_position := {
                    position: stats_helpers.clean_numeric_stats(
                        group.drop_duplicates(
                            subset=["base_player_id" if "base_player_id" in group.columns else "base_player_display_name"]
                        )
                        .drop(columns=drop_cols, errors="ignore")
                        .set_index("base_player_display_name")
                    )
                    for position, group in season_group.groupby("base_pos")
                    if position in allowed_positions
                }
            )
        }

    @timed("Statistics._build_weekly_player_stats")
    def _build_weekly_player_stats(self, weekly_df: pd.DataFrame) -> Dict[str, List[Dict]]:
        """Build player -> weekly record list view for player modal."""
        ordered = weekly_df.sort_values(["base_season", "base_week", "base_player_display_name"])
        ordered = stats_helpers.clean_weekly_records(ordered)
        return {
            player_name: group.drop(columns=["base_player_display_name"], errors="ignore").to_dict("records")
            for player_name, group in ordered.groupby("base_player_display_name", sort=False)
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
                "is_rookie": player_name in roster_data.rookies,
                "is_eligible": player_name in roster_data.eligible,
            } for player_name in roster_data.positions if valid_player_names is None or player_name in valid_player_names
        ]

    @timed("Statistics.run")
    def run(self) -> None:
        """Load data, process statistics, and store cache data."""
        loaders = {
            "rosters": self._source_loader.load_rosters,
            "sources": self._source_loader.load_statistics_sources,
        }
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
                        constants.STATS["SEASONAL"]: seasonal_player_stats,
                        constants.STATS["WEEKLY_PLAYER_STATS"]: weekly_player_stats})

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
    rookies: Dict[str, bool]


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
            if isinstance(headshot := getattr(row, "headshot_url", None), str) and headshot and season_int is not None:
                prev = headshot_tracker.get(name)
                if not prev or season_int > prev[0]:
                    headshot_tracker[name] = (season_int, headshot)
            if season_int == current_season:
                if getattr(row, "status", None) != "RET":
                    eligible_players.add(name)
                if isinstance(team := getattr(row, "team", None), str) and team:
                    player_teams[name] = team
                if (entry_year := getattr(row, "entry_year", None)) == current_season and pd.notna(entry_year):
                    rookies[name] = True
        player_headshots = {name: headshot for name, (_, headshot) in headshot_tracker.items()}
        logger.info("Positions: %s | Ages: %s | Eligible: %s | Headshots: %s | Player-Teams: %s | Rookies: %s", len(player_positions), len(player_ages), len(eligible_players), len(player_headshots), len(player_teams), sum(1 for v in rookies.values() if v))
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
            ("snap_counts", ["season", "week", "player_display_name", "position", "team"]),
            ("ff_opp_weekly", ["season", "week", "player_id", "player_display_name", "position", "team"]),
            ("nextgen_pass_weekly", ["season", "week", "player_display_name", "position", "team"]),
            ("nextgen_rec_weekly", ["season", "week", "player_display_name", "position", "team"]),
            ("nextgen_rush_weekly", ["season", "week", "player_display_name", "position", "team"]),
            ("pfr_pass_weekly", ["season", "week", "game_id", "player_display_name", "team"]),
            ("pfr_rush_weekly", ["season", "week", "game_id", "player_display_name", "team"]),
            ("pfr_rec_weekly", ["season", "week", "game_id", "player_display_name", "team"]),
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
            ("pfr_pass_season", ["season", "player_display_name", "team"]),
            ("pfr_rush_season", ["season", "player_display_name", "position"]),
            ("pfr_rec_season", ["season", "player_display_name", "position"]),
        ]

        for source_key, join_keys in seasonal_join_specs:
            aligned = stats_helpers.align_pfr_seasonal_names(sources[source_key], seasonal_df)
            # Only seasonal PFR rush/rec need this: weekly rows stay team-specific, but seasonal rows can be 2TM/3TM for traded players.
            if "team" in aligned.columns and "team" not in join_keys:
                aligned = aligned.drop(columns=["team"])
            seasonal_df = stats_helpers.merge_source(seasonal_df, aligned, join_keys)

        return seasonal_df

    @timed("Statistics._shape_statistics_data")
    def _shape_statistics_data(self, weekly_df: pd.DataFrame, seasonal_df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Shape merged dataframes with derived metrics, aliases, aggregates, and ranks."""
        weekly_df = stats_helpers.add_derived_stats(weekly_df)
        seasonal_df = stats_helpers.add_derived_stats(seasonal_df)

        weekly_df = stats_helpers.combine_aliases(weekly_df)
        seasonal_df = stats_helpers.combine_aliases(seasonal_df)

        seasonal_df = stats_helpers.merge_weekly_aggregates_into_seasonal(seasonal_df, weekly_df)

        weekly_df = stats_helpers.add_group_ranks(weekly_df, ["season", "position", "week"])
        seasonal_df = stats_helpers.add_group_ranks(seasonal_df, ["season", "position"])

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
                        constants.STATS["BY_YEAR"]: seasonal_player_stats,
                        constants.STATS["PLAYER_WEEKLY_STATS"]: weekly_player_stats})

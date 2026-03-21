"""Player statistics processing and cache generation."""

import logging
from concurrent.futures import Future, ThreadPoolExecutor, as_completed
from typing import Dict, List, Tuple, cast

import pandas as pd

from backend import base_source
from backend.statistics.loaders import StatisticsSourceLoader
from backend.statistics.util import stats_helpers
from backend.util import constants
from backend.util.exceptions import DataProcessingError
from backend.util.timing import timed

logger = logging.getLogger(__name__)


class Statistics(base_source.BaseSource):
    """Processes player statistics and builds stat caches."""

    def __init__(self, seasons: List[int]) -> None:
        """Initialize with seasons"""
        super().__init__(seasons)
        self._source_loader = StatisticsSourceLoader(self.seasons)

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
            ("snap_counts", ["base_season", "base_week", "base_player_display_name", "base_team"]),
            ("ff_opp_weekly", ["base_season", "base_week", "base_player_id"]),
            ("nextgen_pass_weekly", ["base_season", "base_week", "base_player_id"]),
            ("nextgen_rec_weekly", ["base_season", "base_week", "base_player_id"]),
            ("nextgen_rush_weekly", ["base_season", "base_week", "base_player_id"]),
            ("pfr_pass_weekly", ["base_season", "base_week", "base_player_display_name", "base_team"]),
            ("pfr_rush_weekly", ["base_season", "base_week", "base_player_display_name", "base_team"]),
            ("pfr_rec_weekly", ["base_season", "base_week", "base_player_display_name", "base_team"]),
        ]
        for source_key, join_keys in weekly_join_specs:
            source_df = stats_helpers.apply_name_map(sources[source_key])
            weekly_df = stats_helpers.merge_source(weekly_df, source_df, join_keys)
        return weekly_df

    @timed("Statistics._merge_seasonal_statistics_data")
    def _merge_seasonal_statistics_data(self, sources: Dict[str, pd.DataFrame]) -> pd.DataFrame:
        """Merge seasonal source tables into base seasonal dataframe."""
        seasonal_df = sources["player_seasonal"]
        seasonal_join_specs: List[Tuple[str, List[str]]] = [
            ("pfr_pass_season", ["base_season", "base_player_display_name", "base_team"]),
            ("pfr_rush_season", ["base_season", "base_player_display_name"]),
            ("pfr_rec_season", ["base_season", "base_player_display_name"]),
        ]

        for source_key, join_keys in seasonal_join_specs:
            aligned = stats_helpers.apply_name_map(sources[source_key])
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
        seasonal_df = stats_helpers.merge_weekly_aggregates_into_seasonal(seasonal_df, weekly_df, ["base_season", "base_pos", "base_player_display_name", "base_player_id"], summed_metrics, averaged_metrics)
        weekly_df = stats_helpers.add_group_ranks(weekly_df, ["base_season", "base_pos", "base_week"], rank_metrics)
        seasonal_df = stats_helpers.add_group_ranks(seasonal_df, ["base_season", "base_pos"], rank_metrics)
        return weekly_df, seasonal_df
    
    @timed("Statistics._collect_stats_player_keys")
    def _collect_stats_player_keys(self, seasonal_df: pd.DataFrame, weekly_df: pd.DataFrame) -> set[Tuple[str, str]]:
        """Collect player name/id keys from shaped weekly and seasonal dataframes."""
        weekly_keys = set(weekly_df[["base_player_display_name", "base_player_id"]].dropna().astype(str).itertuples(index=False, name=None))
        weekly_keys.update(seasonal_df[["base_player_display_name", "base_player_id"]].dropna().astype(str).itertuples(index=False, name=None))
        return weekly_keys

    @timed("Statistics._build_statistics_data")
    def _build_statistics_data(self, rosters: pd.DataFrame, weekly_df: pd.DataFrame, seasonal_df: pd.DataFrame, stats_player_keys: set[Tuple[str, str]]) -> Tuple[List[Dict], List[Dict], List[Dict], Dict[str, int]]:
        """Build seasonal stats, weekly stats, all players, and their meta in parallel."""
        results: Dict[str, object] = {}
        with ThreadPoolExecutor(max_workers=3) as executor:
            futures: Dict[Future[object], str] = {
                executor.submit(self._build_seasonal_player_stats, seasonal_df): "seasonal_player_stats",
                executor.submit(self._build_weekly_player_stats, weekly_df): "weekly_player_stats",
                executor.submit(self._build_all_players, rosters, stats_player_keys): "all_players",
            }
            for future in as_completed(futures):
                results[futures[future]] = future.result()

        seasonal_player_stats, seasonal_meta = cast(Tuple[List[Dict], Dict[str, int]], results["seasonal_player_stats"])
        weekly_player_stats, weekly_meta = cast(Tuple[List[Dict], Dict[str, int]], results["weekly_player_stats"])
        all_players, roster_meta = cast(Tuple[List[Dict], Dict[str, int]], results["all_players"])
        return (seasonal_player_stats,
                weekly_player_stats,
                all_players,
                {**roster_meta, **seasonal_meta, **weekly_meta})

    @timed("Statistics._build_seasonal_player_stats")
    def _build_seasonal_player_stats(self, seasonal_df: pd.DataFrame) -> Tuple[List[Dict], Dict[str, int]]:
        """Build flat seasonal record list for app/API consumption."""
        seasonal_stats = cast(List[Dict], seasonal_df.to_dict("records"))
        
        seasonal_meta = {"seasonal_record_count": len(seasonal_df)}
        
        logger.info("Seasonal-Records: %s", seasonal_meta["seasonal_record_count"])
        return seasonal_stats, seasonal_meta

    @timed("Statistics._build_weekly_player_stats")
    def _build_weekly_player_stats(self, weekly_df: pd.DataFrame) -> Tuple[List[Dict], Dict[str, int]]:
        """Build flat weekly record list for app/API consumption."""
        weekly_stats = cast(List[Dict], weekly_df.to_dict("records"))

        weekly_meta = {"weekly_record_count": len(weekly_df)}

        logger.info("Weekly-Records: %s", weekly_meta["weekly_record_count"])
        return weekly_stats, weekly_meta

    @timed("Statistics._build_all_players")
    def _build_all_players(self, rosters: pd.DataFrame, valid_player_keys: set[Tuple[str, str]]) -> Tuple[List[Dict], Dict[str, int]]:
        """Build pre-assembled player list and roster-derived meta for app/API consumption."""
        player_positions, player_ages, eligible_players, player_headshots, player_teams, rookie_players = stats_helpers.build_all_players_lookups(rosters, constants.CURRENT_SEASON)

        all_players = [{
            "name": player_key[0],
            "player_id": player_key[1],
            "position": player_positions.get(player_key),
            "age": player_ages.get(player_key),
            "headshot_url": player_headshots.get(player_key),
            "team": player_teams.get(player_key),
            "is_rookie": player_key in rookie_players,
            "is_eligible": player_key in eligible_players,
        } for player_key in player_positions if player_key in valid_player_keys]

        roster_meta = {"player_positions_count": len(player_positions),
                       "player_ages_count": len(player_ages),
                       "eligible_player_count": len(eligible_players),
                       "headshot_player_count": len(player_headshots),
                       "player_teams_count": len(player_teams),
                       "rookie_player_count": len(rookie_players)}

        logger.info("All-Players: %s | Player-Positions: %s | Player-Ages: %s | Eligible-Players: %s | Headshot-Players: %s | Player-Teams: %s | Rookie-Players: %s", len(all_players), roster_meta["player_positions_count"], roster_meta["player_ages_count"], roster_meta["eligible_player_count"], roster_meta["headshot_player_count"], roster_meta["player_teams_count"], roster_meta["rookie_player_count"])
        return all_players, roster_meta

    @timed("Statistics.run")
    def run(self) -> None:
        """Load data, process statistics, and store cache data."""
        import_data = self._source_loader.load_import_data()

        rosters = import_data["rosters"]
        sources = {name: frame for name, frame in import_data.items() if name != "rosters"}

        try:
            weekly_df, seasonal_df = self._merge_statistics_data(sources)
            weekly_df, seasonal_df = self._shape_statistics_data(weekly_df, seasonal_df)
        except Exception as e:
            logger.exception("Failed to merge/shape statistics data")
            raise DataProcessingError(f"Failed to merge/shape statistics data: {e}", source="Statistics") from e

        try:
            stats_player_keys = self._collect_stats_player_keys(seasonal_df, weekly_df)
            seasonal_player_stats, weekly_player_stats, all_players, meta = self._build_statistics_data(rosters, weekly_df, seasonal_df, stats_player_keys)
        except Exception as e:
            logger.exception("Failed to build statistics payloads")
            raise DataProcessingError(f"Failed to build statistics payloads: {e}", source="Statistics") from e

        self.set_cache({constants.STATS["ALL_PLAYERS"]: all_players,
                        constants.STATS["SEASONAL_PLAYER_STATS"]: seasonal_player_stats,
                        constants.STATS["WEEKLY_PLAYER_STATS"]: weekly_player_stats,
                        constants.STATS["META"]: meta})

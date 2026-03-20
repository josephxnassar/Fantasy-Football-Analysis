"""Helper functions for statistics transformations and cache shaping."""

import logging
from typing import List, Mapping

import pandas as pd

from backend.statistics.column_maps import PLAYER_NAME_MAP
from backend.util import constants

logger = logging.getLogger(__name__)


def pfr_seasons(seasons: List[int], min_year: int = 2018) -> List[int]:
    """Filter self.seasons to those >= min_year (PFR/snap data availability guard)."""
    return [s for s in seasons if s >= min_year]

def select_and_rename_columns(source: pd.DataFrame, column_map: Mapping[str, str], required_columns: List[str] | None = None, source_name: str | None = None) -> pd.DataFrame:
    """Return only mapped columns present in source, renamed to target names."""
    present = [column for column in column_map if column in source.columns]
    selected = source[present].rename(columns=column_map)

    required = required_columns or []
    missing_required = [column for column in required if column not in selected.columns]
    if missing_required:
        missing = ", ".join(sorted(missing_required))
        raise ValueError(f"{source_name or 'source'} missing required columns: {missing}")

    if source_name:
        missing_optional = [column for column in column_map if column not in source.columns]
        if missing_optional:
            logger.warning("%s missing optional columns: %s", source_name, ", ".join(sorted(missing_optional)))
    return selected

def team_normalization(source: pd.DataFrame) -> pd.DataFrame:
    if "base_team" in source.columns:
        source["base_team"] = source["base_team"].replace(constants.TEAM_ABBR_NORMALIZATION)
    if "base_opp_team" in source.columns:
        source["base_opp_team"] = source["base_opp_team"].replace(constants.TEAM_ABBR_NORMALIZATION)
    return source

def filter_regular_season(source: pd.DataFrame) -> pd.DataFrame:
    """Filter to regular-season rows when a season-type field is available."""
    if "base_season_type" not in source.columns:
        return source
    return source.loc[source["base_season_type"] == "REG"]

def filter_positions(source: pd.DataFrame) -> pd.DataFrame:
    """Filter to the supported fantasy positions when a position field is available."""
    if "base_pos" not in source.columns:
        return source
    return source.loc[source["base_pos"].isin(constants.POSITIONS)]

def filter_regular_and_position(source: pd.DataFrame) -> pd.DataFrame:
    """Filter to regular season and fantasy positions when available."""
    return filter_positions(filter_regular_season(source))

def apply_name_map(source: pd.DataFrame) -> pd.DataFrame:
    """Apply the explicit player name alias map to a source dataframe."""
    if "base_player_display_name" in source.columns:
        source["base_player_display_name"] = source["base_player_display_name"].replace(PLAYER_NAME_MAP)
    return source

def merge_source(base: pd.DataFrame, source: pd.DataFrame, join_candidates: List[str]) -> pd.DataFrame:
    """Left-join source onto base and use merge order to fill overlapping stats."""
    join_keys = [key for key in join_candidates if key in base.columns and key in source.columns]
    if not join_keys:
        return base

    base_indexed = base.set_index(join_keys)
    source_deduped = source.drop_duplicates(subset=join_keys)
    source_indexed = source_deduped.set_index(join_keys)

    source_aligned = source_indexed.reindex(base_indexed.index)
    combined = base_indexed.combine_first(source_aligned).copy()
    return combined.reset_index()

def merge_weekly_aggregates_into_seasonal(seasonal_df: pd.DataFrame, weekly_df: pd.DataFrame, summed_metrics: list[str], averaged_metrics: list[str]) -> pd.DataFrame:
    """Merge weekly-derived season aggregates into seasonal rows, filling only missing values."""
    if seasonal_df.empty or weekly_df.empty:
        return seasonal_df

    group_keys = [key for key in ["base_season", "base_pos", "base_player_display_name", "base_player_id"] if key in seasonal_df.columns and key in weekly_df.columns]
    if not group_keys:
        return seasonal_df

    aggregate_frames = [frame for frame in [_aggregate_weekly_metrics(weekly_df, group_keys, summed_metrics, "sum"),
                                            _aggregate_weekly_metrics(weekly_df, group_keys, averaged_metrics, "mean")] if frame is not None]
    if not aggregate_frames:
        return seasonal_df
    aggregates = aggregate_frames[0]
    for frame in aggregate_frames[1:]:
        aggregates = aggregates.merge(frame, on=group_keys, how="outer")

    metric_cols = [col for col in aggregates.columns if col not in group_keys]
    return _merge_aggregates_and_fill_missing(seasonal_df, aggregates, group_keys, metric_cols)

def _aggregate_weekly_metrics(weekly_df: pd.DataFrame, group_keys: list[str], metrics: list[str], reducer: str) -> pd.DataFrame | None:
    """Reduce available weekly metrics by player-season using the requested reducer."""
    available_metrics = [metric for metric in metrics if metric in weekly_df.columns]
    if not group_keys or not available_metrics:
        return None

    grouped_input = weekly_df[group_keys + available_metrics].copy()
    grouped_input[available_metrics] = grouped_input[available_metrics].apply(pd.to_numeric, errors="coerce")
    grouped = grouped_input.groupby(group_keys, dropna=False, sort=False)[available_metrics]

    reduced = grouped.sum(min_count=1) if reducer == "sum" else grouped.mean()
    return reduced.reset_index()

def _merge_aggregates_and_fill_missing(seasonal_df: pd.DataFrame, aggregates_df: pd.DataFrame, group_keys: list[str], metric_cols: list[str]) -> pd.DataFrame:
    """Merge aggregate metrics and backfill only missing seasonal values."""
    if not metric_cols:
        return seasonal_df

    seasonal_indexed = seasonal_df.set_index(group_keys)
    aggregates_indexed = aggregates_df[group_keys + metric_cols].set_index(group_keys)
    aggregates_aligned = aggregates_indexed.reindex(seasonal_indexed.index)
    return seasonal_indexed.combine_first(aggregates_aligned).reset_index().copy()

def add_group_ranks(df: pd.DataFrame, group_cols: List[str], rank_metrics: List[str]) -> pd.DataFrame:
    """Add positional rank columns for metrics within contextual groups (1 = best)."""
    ranked = df.copy()

    groups = [ranked[col] for col in group_cols if col in ranked.columns]
    if not groups:
        return ranked

    for metric in rank_metrics:
        if metric not in ranked.columns:
            continue
        numeric = pd.to_numeric(ranked[metric], errors="coerce")
        ranked[f"{metric}_rank"] = numeric.groupby(groups).rank(ascending=False, method="min").astype("Int64")
    return ranked

def build_all_players_lookups(rosters: pd.DataFrame, current_season: int) -> tuple[dict[tuple[str, str], str], dict[tuple[str, str], int], set[tuple[str, str]], dict[tuple[str, str], str], dict[tuple[str, str], str], set[tuple[str, str]]]:
    """Build the roster-derived lookups used by the all-players builder."""
    roster_view = rosters.loc[rosters["base_player_display_name"].notna() & rosters["base_player_id"].notna()].copy()
    roster_view["player_key"] = list(zip(roster_view["base_player_display_name"], roster_view["base_player_id"]))
    roster_view["base_entry_year"] = pd.to_numeric(roster_view["base_entry_year"], errors="coerce")

    player_positions = dict(zip(roster_view["player_key"], roster_view["base_pos"]))

    today = pd.Timestamp.now().normalize()
    birth_dates = pd.to_datetime(roster_view["base_birth_date"], errors="coerce")
    ages = ((today - birth_dates).dt.days // 365).where(lambda values: values > 0)
    age_rows = roster_view.loc[ages.notna(), ["player_key"]].copy()
    age_rows["age"] = ages.loc[ages.notna()].astype(int).to_numpy()
    player_ages = dict(zip(age_rows["player_key"], age_rows["age"]))

    headshot_rows = roster_view.loc[roster_view["base_headshot_url"].fillna("").ne("") & roster_view["base_season"].notna(), ["player_key", "base_season", "base_headshot_url"]].sort_values("base_season").drop_duplicates(subset="player_key", keep="last")
    player_headshots = dict(zip(headshot_rows["player_key"], headshot_rows["base_headshot_url"]))

    current_rows = roster_view.loc[roster_view["base_season"].eq(current_season)]
    eligible_players = set(current_rows.loc[current_rows["base_status"] != "RET", "player_key"])

    team_rows = current_rows.loc[current_rows["base_team"].fillna("").ne(""), ["player_key", "base_team"]]
    player_teams = dict(zip(team_rows["player_key"], team_rows["base_team"]))

    rookie_players = set(current_rows.loc[current_rows["base_entry_year"].eq(current_season), "player_key"])
    return player_positions, player_ages, eligible_players, player_headshots, player_teams, rookie_players

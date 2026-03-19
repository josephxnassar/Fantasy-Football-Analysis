"""Helper functions for statistics transformations and cache shaping."""

import logging
import re
from typing import Dict, List, Mapping

import pandas as pd

from backend.util import constants

logger = logging.getLogger(__name__)


def pfr_seasons(seasons: List[int], min_year: int = 2018) -> List[int]:
    """Filter self.seasons to those >= min_year (PFR/snap data availability guard)."""
    return [s for s in seasons if s >= min_year]

def select_columns(source: pd.DataFrame, column_map: Mapping[str, str], required_columns: List[str] | None = None, source_name: str | None = None) -> pd.DataFrame:
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

def filter_regular_and_position(source: pd.DataFrame) -> pd.DataFrame:
    """Filter to regular season and fantasy positions when available."""
    filtered = source
    if "base_season_type" in filtered.columns:
        filtered = filtered.loc[filtered["base_season_type"] == "REG"]
    return filtered.loc[filtered["base_pos"].isin(constants.POSITIONS)]

def align_pfr_seasonal_names(pfr_df: pd.DataFrame, base_df: pd.DataFrame) -> pd.DataFrame:
    """Map PFR seasonal short names to base full names for merge compatibility."""
    col = "base_player_display_name"
    if col not in pfr_df.columns or col not in base_df.columns:
        return pfr_df.copy()
    
    full_names = _build_unique_normalized_name_lookup(base_df[col])
    if not full_names:
        return pfr_df.copy()

    name_map: Dict[str, str] = {}
    for name in pfr_df[col].dropna().unique():
        if not isinstance(name, str):
            continue
        match = full_names.get(_normalize_name(name))
        if match:
            name_map[name] = match

    if not name_map:
        return pfr_df.copy()

    aligned = pfr_df.copy()
    aligned[col] = aligned[col].map(name_map).fillna(pfr_df[col])
    return aligned

def _build_unique_normalized_name_lookup(base_names: pd.Series) -> Dict[str, str]:
    """Build normalized name lookup and remove ambiguous matches."""
    full_names: Dict[str, str] = {}
    ambiguous: set[str] = set()
    for name in base_names.dropna().unique():
        if not isinstance(name, str):
            continue
        normalized = _normalize_name(name)
        if normalized in full_names and full_names[normalized] != name:
            ambiguous.add(normalized)
            continue
        full_names[normalized] = name
    for normalized in ambiguous:
        full_names.pop(normalized, None)
    return full_names

def _normalize_name(name: str, suffix_re: re.Pattern[str] = re.compile(r"\s+(?:Jr\.?|Sr\.?|II|III|IV|V)$")) -> str:
    """Reduce a player name to a normalized form for fuzzy matching."""
    n = suffix_re.sub("", name.strip())
    return n.replace("'", "").replace(".", "").lower()

def merge_source(base: pd.DataFrame, source: pd.DataFrame, join_candidates: List[str]) -> pd.DataFrame:
    """Left-join source onto base and use merge order to fill overlapping stats."""
    join_keys = [key for key in join_candidates if key in base.columns and key in source.columns]
    if not join_keys:
        return base
    base_indexed = base.set_index(join_keys)
    source_indexed = source.drop_duplicates(subset=join_keys).set_index(join_keys)
    source_aligned = source_indexed.reindex(base_indexed.index)
    combined = base_indexed.combine_first(source_aligned).copy()
    return combined.reset_index()

def merge_weekly_aggregates_into_seasonal(seasonal_df: pd.DataFrame, weekly_df: pd.DataFrame, summed_metrics: list[str], averaged_metrics: list[str]) -> pd.DataFrame:
    """Merge weekly-derived season aggregates into seasonal rows, filling only missing values."""
    if seasonal_df.empty or weekly_df.empty:
        return seasonal_df

    group_keys = [key for key in ["base_season", "base_pos", "base_player_display_name"] if key in seasonal_df.columns and key in weekly_df.columns]

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

def clean_numeric_stats(df: pd.DataFrame) -> pd.DataFrame:
    """Replace non-finite numeric values with 0 for JSON-safe chart payloads."""
    cleaned = df.copy()
    numeric_cols = cleaned.select_dtypes(include="number").columns
    text_cols = [col for col in cleaned.columns if col not in numeric_cols]
    cleaned.loc[:, numeric_cols] = cleaned.loc[:, numeric_cols].replace([float("inf"), -float("inf")], 0).fillna(0)
    cleaned.loc[:, text_cols] = cleaned.loc[:, text_cols].where(pd.notna(cleaned.loc[:, text_cols]), None)
    return cleaned

def clean_weekly_records(df: pd.DataFrame) -> pd.DataFrame:
    """Replace non-finite/NaN values with None for JSON-safe weekly record lists."""
    cleaned = df.replace([float("inf"), -float("inf")], pd.NA)
    return cleaned.astype(object).where(pd.notna(cleaned), None)

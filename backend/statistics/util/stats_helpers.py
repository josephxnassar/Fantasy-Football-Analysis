"""Helper functions for statistics transformations and cache shaping."""

import logging
import re
from typing import Dict, List, Mapping

import pandas as pd

from backend.statistics import stats_config
from backend.util import constants

logger = logging.getLogger(__name__)


def pfr_seasons(seasons: List[int], min_year: int = 2018) -> List[int]:
    """Filter self.seasons to those >= min_year (PFR/snap data availability guard)."""
    return [s for s in seasons if s >= min_year]

def team_normalization(source: pd.DataFrame) -> pd.DataFrame:
    for team_col in ("team", "recent_team", "posteam", "team_abbr", "tm"):
        if team_col in source.columns:
            source[team_col] = source[team_col].replace(constants.TEAM_ABBR_NORMALIZATION)
    return source

def filter_regular_and_position(source: pd.DataFrame) -> pd.DataFrame:
    """Filter to regular season and fantasy positions when available."""
    filtered = source
    for season_col in ("season_type", "game_type"):
        if season_col in filtered.columns:
            filtered = filtered.loc[filtered[season_col] == "REG"]
            break
    position_col = next((candidate for candidate in ("position", "player_position", "pos") if candidate in filtered.columns), None)
    if not position_col:
        return filtered.iloc[0:0].copy()
    return filtered.loc[filtered[position_col].isin(constants.POSITIONS)]

def select_columns(source: pd.DataFrame, column_map: Mapping[str, str], required_columns: List[str] | None = None, source_name: str | None = None) -> pd.DataFrame:
    """Return only mapped columns present in source, renamed to target names."""
    required = required_columns or []
    missing_required = [column for column in required if column not in source.columns]
    if missing_required:
        missing = ", ".join(sorted(missing_required))
        raise ValueError(f"{source_name or 'source'} missing required columns: {missing}")

    present = [column for column in column_map if column in source.columns]
    if source_name:
        missing_optional = [column for column in column_map if column not in source.columns and column not in required]
        if missing_optional:
            logger.warning("%s missing optional columns: %s", source_name, ", ".join(sorted(missing_optional)))
    return source[present].rename(columns=column_map)

def merge_source(base: pd.DataFrame, source: pd.DataFrame, join_candidates: List[str]) -> pd.DataFrame:
    """Left-join source onto base using available join keys."""
    join_keys = [key for key in join_candidates if key in base.columns and key in source.columns]
    if not join_keys:
        return base
    return base.merge(source.drop_duplicates(subset=join_keys), on=join_keys, how="left")

def align_pfr_seasonal_names(pfr_df: pd.DataFrame, base_df: pd.DataFrame) -> pd.DataFrame:
    """Map PFR seasonal short names to base full names for merge compatibility."""
    col = "player_display_name"
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

def add_derived_stats(df: pd.DataFrame) -> pd.DataFrame:
    """Add derived stats (Yds/Rec, Yds/Rush) from available base columns."""
    derived: Dict[str, pd.Series] = {}
    if {"receiving_yards", "receptions"}.issubset(df.columns):
        derived["Yds/Rec"] = _safe_rate(df, "receiving_yards", "receptions")
    if {"rushing_yards", "carries"}.issubset(df.columns):
        derived["Yds/Rush"] = _safe_rate(df, "rushing_yards", "carries")
    if not derived:
        return df
    return pd.concat([df, pd.DataFrame(derived, index=df.index)], axis=1)

def _safe_rate(df: pd.DataFrame, numerator: str, denominator: str) -> pd.Series:
    """Compute a rounded per-unit rate while handling divide-by-zero/NaN."""
    return (df[numerator].div(df[denominator]).replace([float("inf"), -float("inf")], 0).fillna(0).round(1))

def combine_aliases(df: pd.DataFrame) -> pd.DataFrame:
    """Fill each unified stat column with the first non-null value from prioritized source columns."""
    interpreted = df.copy()
    for out_col, sources in stats_config.INTERPRETED_METRIC_SOURCES.items():
        cols = [col for col in sources if col in interpreted.columns]
        if cols:
            interpreted[out_col] = interpreted[cols].bfill(axis=1).iloc[:, 0]
    return interpreted

def merge_weekly_aggregates_into_seasonal(seasonal_df: pd.DataFrame, weekly_df: pd.DataFrame) -> pd.DataFrame:
    """Merge weekly-derived season aggregates into seasonal rows, filling only missing values."""
    if seasonal_df.empty or weekly_df.empty:
        return seasonal_df

    group_keys = [key for key in ["season", "position", "player_display_name"] if key in seasonal_df.columns and key in weekly_df.columns]

    if not group_keys:
        return seasonal_df

    aggregates = weekly_df[group_keys].drop_duplicates().copy()
    
    summed_metric_sources = {metric_name: (metric_name,) for metric_name in stats_config.WEEKLY_SUM_AGGREGATE_METRICS}
    aggregates = _append_aggregated_metrics(aggregates, weekly_df, group_keys, summed_metric_sources, "sum")

    averaged_metric_sources = {metric_name: (metric_name,) for metric_name in stats_config.WEEKLY_AVERAGED_AGGREGATE_METRICS}
    aggregates = _append_aggregated_metrics(aggregates, weekly_df, group_keys, averaged_metric_sources, "mean")

    metric_cols = [col for col in aggregates.columns if col not in group_keys]
    if not metric_cols:
        return seasonal_df

    return _merge_aggregates_and_fill_missing(seasonal_df, aggregates, group_keys, metric_cols)

def _append_aggregated_metrics(aggregates_df: pd.DataFrame, weekly_df: pd.DataFrame, group_keys: list[str], metric_sources: Mapping[str, tuple[str, ...]], reducer: str) -> pd.DataFrame:
    """Append grouped reductions for configured source metrics."""
    if not group_keys:
        return aggregates_df
    
    for out_col, source_candidates in metric_sources.items():
        source_col = next((col for col in source_candidates if col in weekly_df.columns), None)
        if source_col is None:
            continue
        grouped = (weekly_df[group_keys + [source_col]].assign(**{source_col: lambda frame: pd.to_numeric(frame[source_col], errors="coerce")}).groupby(group_keys, dropna=False, sort=False)[source_col])
        reduced = grouped.sum(min_count=1) if reducer == "sum" else grouped.mean()
        aggregates_df = aggregates_df.merge(reduced.rename(out_col).reset_index(), on=group_keys, how="left")
    return aggregates_df

def _merge_aggregates_and_fill_missing(seasonal_df: pd.DataFrame, aggregates_df: pd.DataFrame, group_keys: list[str], metric_cols: list[str]) -> pd.DataFrame:
    """Merge aggregate metrics and backfill only missing seasonal values."""
    weekly_cols = {col: f"__weekly_agg__{col}" for col in metric_cols}
    merged = seasonal_df.merge(aggregates_df.rename(columns=weekly_cols), on=group_keys, how="left")
    for metric_col, weekly_col in weekly_cols.items():
        if metric_col in merged.columns:
            merged[metric_col] = merged[metric_col].where(merged[metric_col].notna(), merged[weekly_col])
        else:
            merged[metric_col] = merged[weekly_col]
    return merged.drop(columns=list(weekly_cols.values()))

def add_group_ranks(df: pd.DataFrame, group_cols: List[str]) -> pd.DataFrame:
    """Add positional rank columns for metrics within contextual groups (1 = best)."""
    ranked = df.copy()

    groups = [ranked[col] for col in group_cols if col in ranked.columns]
    if not groups:
        return ranked

    for metric in stats_config.INTERPRETED_RANK_METRICS:
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

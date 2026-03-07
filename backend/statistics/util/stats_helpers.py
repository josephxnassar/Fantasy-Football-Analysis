"""Helper functions for statistics transformations and cache shaping."""

import re
from typing import Dict, Iterable, List, Mapping

import pandas as pd

_WEEKLY_AGGREGATE_GROUP_KEYS = ["season", "position", "player_display_name"]


def filter_regular_and_position(source: pd.DataFrame, positions: Iterable[str]) -> pd.DataFrame:
    """Filter to regular season and fantasy positions when available."""
    filtered = source
    for season_col in ("season_type", "game_type"):
        if season_col in filtered.columns:
            filtered = filtered.loc[filtered[season_col] == "REG"]
            break
    return filtered.loc[filtered["position"].isin(positions)]

def select_columns(source: pd.DataFrame, column_map: Mapping[str, str]) -> pd.DataFrame:
    """Return only mapped columns present in source, renamed to target names."""
    present = [column for column in column_map if column in source.columns]
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
    full_names = _build_unambiguous_name_lookup(base_df[col])
    if not full_names:
        return pfr_df.copy()

    name_map: Dict[str, str] = {}
    for name in pfr_df[col].dropna().unique():
        match = full_names.get(_normalize_name(name))
        if match:
            name_map[name] = match
    if not name_map:
        return pfr_df.copy()

    aligned = pfr_df.copy()
    aligned[col] = aligned[col].map(name_map).fillna(pfr_df[col])
    return aligned

def _build_unambiguous_name_lookup(base_names: pd.Series) -> Dict[str, str]:
    """Build normalized name lookup and remove ambiguous matches."""
    full_names: Dict[str, str] = {}
    ambiguous: set[str] = set()
    for name in base_names.dropna().unique():
        normalized = _normalize_name(name)
        if normalized in full_names and full_names[normalized] != name:
            ambiguous.add(normalized)
            continue
        full_names[normalized] = name
    for normalized in ambiguous:
        full_names.pop(normalized, None)
    return full_names

def merge_aligned_pfr_seasonal_sources(seasonal_df: pd.DataFrame, sources: Mapping[str, pd.DataFrame], join_specs: List[tuple[str, List[str]]]) -> pd.DataFrame:
    """Align seasonal PFR names and merge each source into the seasonal dataframe."""
    merged = seasonal_df
    for source_key, join_keys in join_specs:
        aligned = align_pfr_seasonal_names(sources[source_key], merged)
        merged = merge_source(merged, aligned, join_keys)
    return merged

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

def combine_aliases(df: pd.DataFrame, metric_sources: Mapping[str, List[str]]) -> pd.DataFrame:
    """Fill each unified stat column with the first non-null value from prioritized source columns."""
    interpreted = df.copy()
    for out_col, sources in metric_sources.items():
        cols = [col for col in sources if col in interpreted.columns]
        if cols:
            interpreted[out_col] = interpreted[cols].bfill(axis=1).iloc[:, 0]
    return interpreted

def merge_weekly_aggregates_into_seasonal(seasonal_df: pd.DataFrame, weekly_df: pd.DataFrame, sum_aggregate_metrics: dict[str, tuple[str, ...]], weighted_aggregate_metrics: dict[str, tuple[tuple[str, ...], tuple[str, ...]]]) -> pd.DataFrame:
    """Merge weekly-derived season aggregates into seasonal rows, filling only missing values."""
    weekly_aggregates = aggregate_weekly_metrics_by_season(weekly_df, sum_aggregate_metrics, weighted_aggregate_metrics)
    if weekly_aggregates.empty:
        return seasonal_df

    weekly_col_map = _build_weekly_aggregate_column_map(weekly_aggregates.columns)
    renamed = weekly_aggregates.rename(columns=weekly_col_map)
    merged = seasonal_df.merge(renamed, on=_WEEKLY_AGGREGATE_GROUP_KEYS, how="left")
    _fill_seasonal_from_weekly_aggregates(merged, weekly_col_map)
    return merged.drop(columns=list(weekly_col_map.values()), errors="ignore")

def _build_weekly_aggregate_column_map(columns: Iterable[str]) -> Dict[str, str]:
    """Map aggregate metric names to temporary merge-safe column names."""
    return {metric: f"weekly_aggregate_{metric}" for metric in columns if metric not in _WEEKLY_AGGREGATE_GROUP_KEYS}

def _fill_seasonal_from_weekly_aggregates(merged: pd.DataFrame, weekly_col_map: Mapping[str, str]) -> None:
    """Fill seasonal metrics with weekly aggregates only where seasonal values are missing."""
    for metric, aggregate_col in weekly_col_map.items():
        aggregate_values = pd.to_numeric(merged[aggregate_col], errors="coerce")
        if metric in merged.columns:
            base_values = pd.to_numeric(merged[metric], errors="coerce")
            merged[metric] = base_values.fillna(aggregate_values)
        else:
            merged[metric] = aggregate_values

def aggregate_weekly_metrics_by_season(weekly_df: pd.DataFrame, sum_aggregate_metrics: dict[str, tuple[str, ...]], weighted_aggregate_metrics: dict[str, tuple[tuple[str, ...], tuple[str, ...]]]) -> pd.DataFrame:
    """Aggregate selected weekly metrics into season-level player stats."""
    if weekly_df.empty:
        return pd.DataFrame(columns=list(_WEEKLY_AGGREGATE_GROUP_KEYS))

    columns = set(weekly_df.columns)
    aggregates: List[pd.Series] = []
    _append_sum_aggregates(aggregates, weekly_df, sum_aggregate_metrics, columns)
    _append_weighted_aggregates(aggregates, weekly_df, weighted_aggregate_metrics, columns)

    if not aggregates:
        return pd.DataFrame(columns=list(_WEEKLY_AGGREGATE_GROUP_KEYS))

    return pd.concat(aggregates, axis=1).reset_index()

def _append_sum_aggregates(aggregates: List[pd.Series], weekly_df: pd.DataFrame, sum_aggregate_metrics: Mapping[str, tuple[str, ...]], columns: set[str]) -> None:
    """Append sum-based aggregate series into aggregates list."""
    for stat_key, value_keys in sum_aggregate_metrics.items():
        value_col = _first_present_column(value_keys, columns)
        if not value_col:
            continue
        aggregates.append(_aggregate_group_stat(weekly_df, value_col, "sum", None).rename(stat_key))

def _append_weighted_aggregates(aggregates: List[pd.Series], weekly_df: pd.DataFrame, weighted_aggregate_metrics: Mapping[str, tuple[tuple[str, ...], tuple[str, ...]]], columns: set[str]) -> None:
    """Append weighted-mean aggregate series into aggregates list."""
    for stat_key, (value_keys, weight_keys) in weighted_aggregate_metrics.items():
        value_col = _first_present_column(value_keys, columns)
        if not value_col:
            continue
        weight_col = _first_present_column(weight_keys, columns)
        aggregates.append(_aggregate_group_stat(weekly_df, value_col, "weighted_mean", weight_col).rename(stat_key))

def _first_present_column(candidates: Iterable[str], columns: set[str]) -> str | None:
    """Return the first candidate column that exists in columns."""
    for candidate in candidates:
        if candidate in columns:
            return candidate
    return None

def _aggregate_group_stat(weekly_df: pd.DataFrame, value_col: str, reducer: str, weight_col: str | None) -> pd.Series:
    group_fields = [weekly_df[key] for key in _WEEKLY_AGGREGATE_GROUP_KEYS]
    value = pd.to_numeric(weekly_df[value_col], errors="coerce")
    grouped_value = value.groupby(group_fields)

    if reducer == "sum":
        return grouped_value.sum(min_count=1)

    if reducer == "weighted_mean" and weight_col:
        weight = pd.to_numeric(weekly_df[weight_col], errors="coerce")
        positive_weights = weight.where(weight > 0)
        weighted_sum = (value * positive_weights).groupby(group_fields).sum(min_count=1)
        weight_sum = positive_weights.groupby(group_fields).sum(min_count=1)
        weighted_mean = weighted_sum.div(weight_sum)
        return weighted_mean.where(weight_sum > 0, grouped_value.mean())

    return grouped_value.mean()

def add_group_ranks(df: pd.DataFrame, metrics: Iterable[str], group_cols: List[str]) -> pd.DataFrame:
    """Add positional rank columns for metrics within contextual groups (1 = best)."""
    ranked = df.copy()
    groups = [ranked[col] for col in group_cols if col in ranked.columns]
    if not groups:
        return ranked

    for metric in metrics:
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

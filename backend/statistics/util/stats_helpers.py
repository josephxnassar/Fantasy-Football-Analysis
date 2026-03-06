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

    full_names: Dict[str, str] = {}
    ambiguous: set[str] = set()
    for name in base_df[col].dropna().unique():
        normalized = _normalize_name(name)
        if normalized in full_names and full_names[normalized] != name:
            ambiguous.add(normalized)
            continue
        full_names[normalized] = name
    for normalized in ambiguous:
        full_names.pop(normalized, None)

    name_map: Dict[str, str] = {}
    for name in pfr_df[col].dropna().unique():
        match = full_names.get(_normalize_name(name))
        if match:
            name_map[name] = match

    aligned = pfr_df.copy()
    aligned[col] = aligned[col].map(name_map).fillna(pfr_df[col])
    return aligned

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

    weekly_col_map = {metric: f"weekly_aggregate_{metric}" for metric in weekly_aggregates.columns if metric not in _WEEKLY_AGGREGATE_GROUP_KEYS}
    renamed = weekly_aggregates.rename(columns=weekly_col_map)
    merged = seasonal_df.merge(renamed, on=_WEEKLY_AGGREGATE_GROUP_KEYS, how="left")

    for metric, aggregate_col in weekly_col_map.items():
        aggregate_values = pd.to_numeric(merged[aggregate_col], errors="coerce")
        if metric in merged.columns:
            base_values = pd.to_numeric(merged[metric], errors="coerce")
            merged[metric] = base_values.fillna(aggregate_values)
        else:
            merged[metric] = aggregate_values

    return merged.drop(columns=list(weekly_col_map.values()), errors="ignore")

def aggregate_weekly_metrics_by_season(weekly_df: pd.DataFrame, sum_aggregate_metrics: dict[str, tuple[str, ...]], weighted_aggregate_metrics: dict[str, tuple[tuple[str, ...], tuple[str, ...]]]) -> pd.DataFrame:
    """Aggregate selected weekly metrics into season-level player stats."""
    if weekly_df.empty:
        return pd.DataFrame(columns=[*_WEEKLY_AGGREGATE_GROUP_KEYS])

    columns = weekly_df.columns
    aggregates: List[pd.Series] = []
    for stat_key, value_keys in sum_aggregate_metrics.items():
        value_col = next((candidate for candidate in value_keys if candidate in columns), None)
        if not value_col:
            continue
        aggregates.append(_aggregate_group_stat(weekly_df, value_col, "sum", None).rename(stat_key))

    for stat_key, metric_keys in weighted_aggregate_metrics.items():
        value_keys, weight_keys = metric_keys
        value_col = next((candidate for candidate in value_keys if candidate in columns), None)
        if not value_col:
            continue

        weight_col = next((candidate for candidate in weight_keys if candidate in columns), None)

        aggregates.append(_aggregate_group_stat(weekly_df, value_col, "weighted_mean", weight_col).rename(stat_key))

    if not aggregates:
        return pd.DataFrame(columns=[*_WEEKLY_AGGREGATE_GROUP_KEYS])

    return pd.concat(aggregates, axis=1).reset_index()

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

def build_seasonal_data(seasonal_df: pd.DataFrame, positions: Iterable[str]) -> Dict[int, Dict[str, pd.DataFrame]]:
    """Build season -> position -> DataFrame view for chart endpoints."""
    allowed_positions = set(positions)
    drop_cols = ["season", "position", "player_id", "player_name", "position_group"]
    result: Dict[int, Dict[str, pd.DataFrame]] = {}

    for (season, position), group in seasonal_df.groupby(["season", "position"]):
        if position not in allowed_positions:
            continue

        dedupe_key = "player_id" if "player_id" in group.columns else "player_display_name"
        cleaned = _clean_numeric_stats(group.drop_duplicates(subset=[dedupe_key]).drop(columns=drop_cols, errors="ignore").set_index("player_display_name"))
        result.setdefault(int(season), {})[position] = cleaned

    return result

def _clean_numeric_stats(df: pd.DataFrame) -> pd.DataFrame:
    """Replace non-finite numeric values with 0 for JSON-safe chart payloads."""
    cleaned = df.copy()
    numeric_cols = cleaned.select_dtypes(include="number").columns
    text_cols = [col for col in cleaned.columns if col not in numeric_cols]
    cleaned.loc[:, numeric_cols] = cleaned.loc[:, numeric_cols].replace([float("inf"), -float("inf")], 0).fillna(0)
    cleaned.loc[:, text_cols] = cleaned.loc[:, text_cols].where(pd.notna(cleaned.loc[:, text_cols]), None)
    return cleaned

def build_weekly_player_stats(weekly_df: pd.DataFrame) -> Dict[str, List[Dict]]:
    """Build player -> weekly record list view for player modal."""
    ordered = weekly_df.sort_values(["season", "week", "player_display_name"])
    ordered = _clean_weekly_records(ordered)
    return {player_name: group.drop(columns=["player_display_name"], errors="ignore").to_dict("records") for player_name, group in ordered.groupby("player_display_name", sort=False)}

def _clean_weekly_records(df: pd.DataFrame) -> pd.DataFrame:
    """Replace non-finite/NaN values with None for JSON-safe weekly record lists."""
    cleaned = df.replace([float("inf"), -float("inf")], pd.NA)
    return cleaned.astype(object).where(pd.notna(cleaned), None)

def collect_stats_player_names(seasonal_data: Dict[int, Dict[str, pd.DataFrame]], weekly_stats: Dict[str, List[Dict]]) -> set[str]:
    """Collect all player names represented in seasonal or weekly stats views."""
    names = set(weekly_stats.keys())
    for season_map in seasonal_data.values():
        for df in season_map.values():
            names.update(str(name) for name in df.index)
    return names

def build_all_players(player_positions: Dict[str, str], eligible_players: set[str], player_ages: Dict[str, int], player_headshots: Dict[str, str], player_teams: Dict[str, str], player_rookies: Dict[str, bool], valid_player_names: set[str] | None = None) -> List[Dict]:
    """Build pre-assembled player list with player metadata for API consumption."""
    return [
        {
            "name": player_name,
            "position": player_positions.get(player_name),
            "age": player_ages.get(player_name),
            "headshot_url": player_headshots.get(player_name),
            "team": player_teams.get(player_name),
            "is_rookie": player_rookies.get(player_name, False),
            "is_eligible": player_name in eligible_players,
        } for player_name in player_positions if valid_player_names is None or player_name in valid_player_names
    ]

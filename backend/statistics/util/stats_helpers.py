"""Helper functions for statistics transformations and cache shaping."""

import re
from typing import Dict, Iterable, List, Mapping, cast

import pandas as pd

from backend.util import constants

_NAME_SUFFIX_RE = re.compile(r"\s+(?:Jr\.?|Sr\.?|II|III|IV|V)$")
_WEEKLY_SEASON_ROLLUP_SPECS: Dict[str, Dict[str, object]] = {
    "exp_fp": {
        "value_keys": ("exp_fp", "ffo_total_fp_exp"),
        "reducer": "sum",
    },
    "ng_pass_passer_rating": {
        "value_keys": ("ng_pass_passer_rating",),
        "reducer": "weighted_mean",
        "weight_keys": ("ng_pass_att", "pass_att", "attempts"),
    },
    "ng_pass_avg_time_to_throw": {
        "value_keys": ("ng_pass_avg_time_to_throw",),
        "reducer": "weighted_mean",
        "weight_keys": ("ng_pass_att", "pass_att", "attempts"),
    },
    "ng_rec_avg_separation": {
        "value_keys": ("ng_rec_avg_separation",),
        "reducer": "weighted_mean",
        "weight_keys": ("ng_rec_targets", "targets"),
    },
    "ng_rec_avg_yac": {
        "value_keys": ("ng_rec_avg_yac",),
        "reducer": "weighted_mean",
        "weight_keys": ("ng_rec_rec", "rec", "receptions"),
    },
    "ng_rec_avg_yac_above_expectation": {
        "value_keys": ("ng_rec_avg_yac_above_expectation",),
        "reducer": "weighted_mean",
        "weight_keys": ("ng_rec_rec", "rec", "receptions"),
    },
    "ng_rec_catch_pct": {
        "value_keys": ("ng_rec_catch_pct",),
        "reducer": "weighted_mean",
        "weight_keys": ("ng_rec_targets", "targets"),
    },
    "ng_rush_rush_yds_over_exp_per_att": {
        "value_keys": ("ng_rush_rush_yds_over_exp_per_att",),
        "reducer": "weighted_mean",
        "weight_keys": ("ng_rush_rush_att", "rush_att", "carries"),
    },
    "ng_rush_efficiency": {
        "value_keys": ("ng_rush_efficiency",),
        "reducer": "weighted_mean",
        "weight_keys": ("ng_rush_rush_att", "rush_att", "carries"),
    },
    "sc_offense_pct": {
        "value_keys": ("sc_offense_pct",),
        "reducer": "weighted_mean",
        "weight_keys": ("sc_offense_snaps",),
    },
}
_WEEKLY_ROLLUP_GROUP_KEYS = ["season", "position", "player_display_name"]


def filter_regular_and_position(source: pd.DataFrame) -> pd.DataFrame:
    """Filter to regular season and fantasy positions when available."""
    filtered = source
    for season_col in ("season_type", "game_type"):
        if season_col in filtered.columns:
            filtered = filtered.loc[filtered[season_col] == "REG"]
            break
    return filtered.loc[filtered["position"].isin(constants.POSITIONS)]

def select_columns(source: pd.DataFrame, column_map: Mapping[str, str]) -> pd.DataFrame:
    """Return only mapped columns present in source, renamed to target names."""
    present = [column for column in column_map if column in source.columns]
    return source[present].rename(columns={column: column_map[column] for column in present})

def merge_source(base: pd.DataFrame, source: pd.DataFrame, join_candidates: List[str]) -> pd.DataFrame:
    """Left-join source onto base using available join keys."""
    join_keys = [key for key in join_candidates if key in base.columns and key in source.columns]
    return base.merge(source.drop_duplicates(subset=join_keys), on=join_keys, how="left")

def align_pfr_seasonal_names(pfr_df: pd.DataFrame, base_df: pd.DataFrame) -> pd.DataFrame:
    """Map PFR seasonal short names to base full names for merge compatibility."""
    col = "player_display_name"
    full_names = {_normalize_name(n): n for n in base_df[col].dropna().unique()}
    name_map = {n: match for n in pfr_df[col].dropna().unique() if (match := full_names.get(_normalize_name(n)))}
    aligned = pfr_df.copy()
    aligned[col] = aligned[col].map(name_map).fillna(pfr_df[col])
    return aligned

def _normalize_name(name: str) -> str:
    """Reduce a player name to a normalized form for fuzzy matching."""
    n = _NAME_SUFFIX_RE.sub("", name.strip())
    return n.replace("'", "").replace(".", "").lower()

def add_derived_stats(df: pd.DataFrame) -> pd.DataFrame:
    """Add derived stats (Yds/Rec, Yds/Rush) from available base columns."""
    derived = {}
    if {"receiving_yards", "receptions"}.issubset(df.columns):
        derived["Yds/Rec"] = _safe_rate(df, "receiving_yards", "receptions")
    if {"rushing_yards", "carries"}.issubset(df.columns):
        derived["Yds/Rush"] = _safe_rate(df, "rushing_yards", "carries")
    return pd.concat([df, pd.DataFrame(derived, index=df.index)], axis=1) if derived else df

def _safe_rate(df: pd.DataFrame, numerator: str, denominator: str) -> pd.Series:
    """Compute a rounded per-unit rate while handling divide-by-zero/NaN."""
    return (df[numerator].div(df[denominator]).replace([float("inf"), -float("inf")], 0).fillna(0).round(1))

def resolve_metric_sources(df: pd.DataFrame, metric_sources: Mapping[str, List[str]]) -> pd.DataFrame:
    """Fill each unified stat column with the first non-null value from prioritized source columns."""
    interpreted = df.copy()
    for out_col, sources in metric_sources.items():
        cols = [col for col in sources if col in interpreted.columns]
        if cols:
            interpreted[out_col] = interpreted[cols].bfill(axis=1).iloc[:, 0]
    return interpreted

def _first_present_column(df: pd.DataFrame, candidates: Iterable[str]) -> str | None:
    for candidate in candidates:
        if candidate in df.columns:
            return candidate
    return None

def _build_grouped_rollup(
    weekly_df: pd.DataFrame,
    value_col: str,
    reducer: str,
    weight_col: str | None,
) -> pd.Series:
    value = pd.to_numeric(weekly_df[value_col], errors="coerce")
    grouped_value = value.groupby([weekly_df[key] for key in _WEEKLY_ROLLUP_GROUP_KEYS])

    if reducer == "sum":
        return grouped_value.sum(min_count=1)

    if reducer == "weighted_mean" and weight_col:
        weight = pd.to_numeric(weekly_df[weight_col], errors="coerce")
        valid_weights = weight.where(weight > 0)
        weighted_sum = (value * valid_weights).groupby([weekly_df[key] for key in _WEEKLY_ROLLUP_GROUP_KEYS]).sum(min_count=1)
        weight_sum = valid_weights.groupby([weekly_df[key] for key in _WEEKLY_ROLLUP_GROUP_KEYS]).sum(min_count=1)
        weighted = weighted_sum.div(weight_sum.where(weight_sum > 0))
        return weighted.where(weight_sum > 0, grouped_value.mean())

    return grouped_value.mean()

def build_weekly_season_rollups(weekly_df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate selected weekly metrics into season-level player stats."""
    if weekly_df.empty or any(key not in weekly_df.columns for key in _WEEKLY_ROLLUP_GROUP_KEYS):
        return pd.DataFrame(columns=[*_WEEKLY_ROLLUP_GROUP_KEYS])

    rollups: List[pd.Series] = []
    for stat_key, spec in _WEEKLY_SEASON_ROLLUP_SPECS.items():
        value_keys = cast(Iterable[str], spec.get("value_keys", ()))
        value_col = _first_present_column(weekly_df, value_keys)
        if not value_col:
            continue
        weight_keys = cast(Iterable[str], spec.get("weight_keys", ()))
        weight_col = _first_present_column(weekly_df, weight_keys)
        reducer = str(spec.get("reducer", "mean"))
        rollup_series = _build_grouped_rollup(weekly_df, value_col, reducer, weight_col).rename(stat_key)
        rollups.append(rollup_series)

    if not rollups:
        return pd.DataFrame(columns=[*_WEEKLY_ROLLUP_GROUP_KEYS])

    return pd.concat(rollups, axis=1).reset_index()

def merge_weekly_rollups_into_seasonal(seasonal_df: pd.DataFrame, weekly_df: pd.DataFrame) -> pd.DataFrame:
    """Merge weekly-derived season rollups into seasonal rows, filling only missing values."""
    rollups = build_weekly_season_rollups(weekly_df)
    if rollups.empty:
        return seasonal_df

    metric_cols = [column for column in rollups.columns if column not in _WEEKLY_ROLLUP_GROUP_KEYS]
    renamed = rollups.rename(columns={column: f"weekly_rollup_{column}" for column in metric_cols})
    merged = seasonal_df.merge(renamed, on=_WEEKLY_ROLLUP_GROUP_KEYS, how="left")

    for metric in metric_cols:
        rollup_col = f"weekly_rollup_{metric}"
        rollup_numeric = pd.to_numeric(merged[rollup_col], errors="coerce")
        if metric in merged.columns:
            base_numeric = pd.to_numeric(merged[metric], errors="coerce")
            merged[metric] = base_numeric.where(base_numeric.notna(), rollup_numeric)
        else:
            merged[metric] = rollup_numeric

    return merged.drop(columns=[f"weekly_rollup_{metric}" for metric in metric_cols], errors="ignore")

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

def build_seasonal_data(seasonal_df: pd.DataFrame) -> Dict[int, Dict[str, pd.DataFrame]]:
    """Build season -> position -> DataFrame view for chart endpoints."""
    drop_cols = ["season", "position", "player_id", "player_name", "position_group"]
    result: Dict[int, Dict[str, pd.DataFrame]] = {}
    for (season, position), group in seasonal_df.groupby(["season", "position"]):
        if position not in constants.POSITIONS:
            continue
        cleaned = _clean_numeric_stats(group.drop(columns=drop_cols, errors="ignore").drop_duplicates(subset=["player_display_name"]).set_index("player_display_name"))
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
    ordered = _clean_weekly_records(weekly_df.sort_values(["season", "week", "player_display_name"]))
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

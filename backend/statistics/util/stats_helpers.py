"""Helper functions for statistics transformations and cache shaping."""

import re
from typing import Dict, Iterable, List, Mapping, Tuple

import pandas as pd

from backend.util import constants

_NAME_SUFFIX_RE = re.compile(r"\s+(?:Jr\.?|Sr\.?|II|III|IV|V)$")


def _normalize_name(name: str) -> str:
    """Reduce a player name to a canonical form for fuzzy matching."""
    n = _NAME_SUFFIX_RE.sub("", name.strip())
    return n.replace("'", "").replace(".", "").lower()

def align_pfr_seasonal_names(pfr_df: pd.DataFrame, base_df: pd.DataFrame) -> pd.DataFrame:
    """Map PFR seasonal short names to base canonical names for merge compatibility."""
    col = "player_display_name"
    if col not in pfr_df.columns or col not in base_df.columns:
        return pfr_df
    base_names = base_df[col].dropna().unique()
    norm_to_canonical = {_normalize_name(n): n for n in base_names}
    aligned = pfr_df.copy()
    aligned[col] = aligned[col].map(lambda n: norm_to_canonical.get(_normalize_name(n), n) if isinstance(n, str) else n)
    return aligned

def merge_pfr_seasonal(seasonal_df: pd.DataFrame, pfr_sources: List[Tuple[pd.DataFrame, List[str]]]) -> pd.DataFrame:
    """Align PFR seasonal names to base canonical names and merge all sources."""
    merged = seasonal_df
    for pfr_df, join_keys in pfr_sources:
        aligned = align_pfr_seasonal_names(pfr_df, merged)
        merged = merge_prefixed(merged, aligned, join_keys, "")
    return merged

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

def merge_prefixed(base: pd.DataFrame, source: pd.DataFrame, join_candidates: List[str], prefix: str) -> pd.DataFrame:
    """Left-join source onto base using available keys and prefix source metrics."""
    join_keys = [key for key in join_candidates if key in base.columns and key in source.columns]
    if source.empty or not join_keys:
        return base
    source_copy = source.drop_duplicates(subset=join_keys)
    if prefix:
        rename_map = {col: f"{prefix}{col}" for col in source_copy.columns if col not in join_keys}
        source_copy = source_copy.rename(columns=rename_map)
    return base.merge(source_copy, on=join_keys, how="left")

def add_derived_stats(df: pd.DataFrame) -> pd.DataFrame:
    """Add derived stats (Yds/Rec, Yds/Rush) from available stat column variants."""
    source_options = {
        "Yds/Rec": [("receiving_yards", "receptions"), ("Rec Yds", "Rec")],
        "Yds/Rush": [("rushing_yards", "carries"), ("Rush Yds", "Carries")],
    }
    derived = {}
    for out_col, options in source_options.items():
        for num_col, den_col in options:
            if {num_col, den_col}.issubset(df.columns):
                derived[out_col] = _safe_rate(df, num_col, den_col)
                break
    return pd.concat([df, pd.DataFrame(derived, index=df.index)], axis=1) if derived else df

def _safe_rate(df: pd.DataFrame, numerator: str, denominator: str) -> pd.Series:
    """Compute a rounded per-unit rate while handling divide-by-zero/NaN."""
    return (df[numerator].div(df[denominator]).replace([float("inf"), -float("inf")], 0).fillna(0).round(1))

def coalesce_canonical_metrics(df: pd.DataFrame, metric_sources: Mapping[str, List[str]]) -> pd.DataFrame:
    """Create canonical metric columns from ordered source preferences."""
    interpreted = df.copy()
    for out_col, sources in metric_sources.items():
        cols = [col for col in sources if col in interpreted.columns]
        if cols:
            interpreted[out_col] = interpreted[cols].bfill(axis=1).iloc[:, 0]
    return interpreted

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
    seasonal_data: Dict[int, Dict[str, pd.DataFrame]] = {}
    drop_cols = ["season", "position", "player_id", "player_name", "position_group"]
    for season, season_group in seasonal_df.groupby("season"):
        season_map: Dict[str, pd.DataFrame] = {}
        for position in constants.POSITIONS:
            position_df = season_group.loc[season_group["position"] == position]
            if position_df.empty:
                continue
            season_map[position] = _clean_numeric_stats(position_df.drop(columns=drop_cols, errors="ignore").drop_duplicates(subset=["player_display_name"]).set_index("player_display_name"))
        if season_map:
            seasonal_data[int(season)] = season_map
    return seasonal_data

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
    sort_cols = [col for col in ("season", "week", "player_display_name") if col in weekly_df.columns]
    ordered = weekly_df.sort_values(sort_cols) if sort_cols else weekly_df
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

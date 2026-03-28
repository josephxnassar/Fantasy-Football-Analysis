"""Helper functions for statistics transformations and cache shaping."""

import logging
from typing import List, Mapping

import pandas as pd

from backend.util import teams

PLAYER_NAME_MAP = {
    "A.J. McCarron": "AJ McCarron",
    "AJ Brown": "A.J. Brown",
    "AJ Derby": "A.J. Derby",
    "AJ Green": "A.J. Green",
    "AT Perry": "A.T. Perry",
    "Adrian Killins": "Adrian Killins Jr.",
    "Aidan OConnell": "Aidan O'Connell",
    "Amon-Ra St Brown": "Amon-Ra St. Brown",
    "Anthony McFarland Jr.": "Anthony McFarland",
    "Ben Watson": "Benjamin Watson",
    "Benny Snell Jr.": "Benny Snell",
    "Brian Robinson Jr.": "Brian Robinson",
    "Brian Thomas": "Brian Thomas Jr.",
    "CJ Anderson": "C.J. Anderson",
    "CJ Beathard": "C.J. Beathard",
    "CJ Board": "C.J. Board",
    "CJ Prosise": "C.J. Prosise",
    "CJ Saunders": "C.J. Saunders",
    "CJ Stroud": "C.J. Stroud",
    "CJ Uzomah": "C.J. Uzomah",
    "Calvin Austin": "Calvin Austin III",
    "Cam Batson": "Cameron Batson",
    "Cedrick Wilson": "Cedrick Wilson Jr.",
    "Chigoziem Okonkwo": "Chig Okonkwo",
    "Chris Godwin": "Chris Godwin Jr.",
    "Chris Rodriguez": "Chris Rodriguez Jr.",
    "D.J. Moore": "DJ Moore",
    "D.K. Metcalf": "DK Metcalf",
    "DAndre Swift": "D'Andre Swift",
    "DErnest Johnson": "D'Ernest Johnson",
    "DJ Foster": "D.J. Foster",
    "DJ Montgomery": "D.J. Montgomery",
    "DOnta Foreman": "D'Onta Foreman",
    "DWayne Eskridge": "Dee Eskridge",
    "DaMari Scott": "Da'Mari Scott",
    "David Sills V": "David Sills",
    "De'Angelo Henderson": "De'Angelo Henderson Sr.",
    "DeAngelo Henderson": "De'Angelo Henderson Sr.",
    "DeAnthony Thomas": "De'Anthony Thomas",
    "DeLance Turner": "De'Lance Turner",
    "DeMichael Harris": "De'Michael Harris",
    "DeVon Achane": "De'Von Achane",
    "Deebo Samuel": "Deebo Samuel Sr.",
    "Demario Douglas": "DeMario Douglas",
    "Dont'e Thornton": "Dont'e Thornton Jr.",
    "Donte Thornton": "Dont'e Thornton Jr.",
    "EJ Jenkins": "E.J. Jenkins",
    "Efton Chism": "Efton Chism III",
    "Equanimeous St Brown": "Equanimeous St. Brown",
    "Gabriel Davis": "Gabe Davis",
    "Gardner Minshew II": "Gardner Minshew",
    "Grant Dubose": "Grant DuBose",
    "Harold Fannin": "Harold Fannin Jr.",
    "Henry Ruggs": "Henry Ruggs III",
    "Irv Smith Jr.": "Irv Smith",
    "JD McKissic": "J.D. McKissic",
    "JJ Arcega-Whiteside": "J.J. Arcega-Whiteside",
    "JJ Jones": "J.J. Jones",
    "JJ McCarthy": "J.J. McCarthy",
    "JJ Nelson": "J.J. Nelson",
    "JJ Taylor": "J.J. Taylor",
    "JK Dobbins": "J.K. Dobbins",
    "JMon Moore": "J'Mon Moore",
    "JP Holtz": "J.P. Holtz",
    "JaLynn Polk": "Ja'Lynn Polk",
    "JaMarcus Bradley": "Ja'Marcus Bradley",
    "JaMarr Chase": "Ja'Marr Chase",
    "JaTavion Sanders": "Ja'Tavion Sanders",
    "James OShaughnessy": "James O'Shaughnessy",
    "Jamycal Hasty": "JaMycal Hasty",
    "JhaQuan Jackson": "Jha'Quan Jackson",
    "Jimmy Horn": "Jimmy Horn Jr.",
    "Joe Milton": "Joe Milton III",
    "John Metchie": "John Metchie III",
    "John Samuel Shenker": "John Shenker",
    "Jojo Natson": "JoJo Natson",
    "Joshua Perkins": "Josh Perkins",
    "KJ Osborn": "K.J. Osborn",
    "KeShawn Vaughn": "Ke'Shawn Vaughn",
    "KeShawn Williams": "Ke'Shawn Williams",
    "Kenneth Walker": "Kenneth Walker III",
    "Kerrith Whyte Jr": "Kerrith Whyte",
    "Kevin Austin": "Kevin Austin Jr.",
    "Kwamie Lassiter": "Kwamie Lassiter II",
    "LaMical Perine": "La'Mical Perine",
    "Larry Rountree": "Larry Rountree III",
    "Laviska Shenault": "Laviska Shenault Jr.",
    "LeQuint Allen": "LeQuint Allen Jr.",
    "LeVante Bellamy": "Levante Bellamy",
    "LeVeon Bell": "Le'Veon Bell",
    "LilJordan Humphrey": "Lil'Jordan Humphrey",
    "Luther Burden": "Luther Burden III",
    "Lynn Bowden Jr.": "Lynn Bowden",
    "Marvin Harrison": "Marvin Harrison Jr.",
    "Marvin Mims": "Marvin Mims Jr.",
    "Michael Penix": "Michael Penix Jr.",
    "Michael Pittman Jr.": "Michael Pittman",
    "NKeal Harry": "N'Keal Harry",
    "Nick OLeary": "Nick O'Leary",
    "OJ Howard": "O.J. Howard",
    "Odell Beckham": "Odell Beckham Jr.",
    "Olabisi Johnson": "Bisi Johnson",
    "Ollie Gordon": "Ollie Gordon II",
    "Oronde Gadsden": "Oronde Gadsden II",
    "P.J. Walker": "PJ Walker",
    "Robert Griffin": "Robert Griffin III",
    "Ronald Jones II": "Ronald Jones",
    "Rodney Williams": "Rod Williams",
    "Seth Devalve": "Seth DeValve",
    "Stanley Morgan Jr.": "Stanley Morgan",
    "TJ Hockenson": "T.J. Hockenson",
    "TJ Jones": "T.J. Jones",
    "TJ Yeldon": "T.J. Yeldon",
    "TY Hilton": "T.Y. Hilton",
    "Ted Ginn Jr.": "Ted Ginn",
    "Terrace Marshall": "Terrace Marshall Jr.",
    "Theo Wease": "Theo Wease Jr.",
    "Tre McKitty": "Tre' McKitty",
    "TreQuan Smith": "Tre'Quan Smith",
    "TySon Williams": "Ty'Son Williams",
    "Tyrone Tracy": "Tyrone Tracy Jr.",
    "Ulysses Bentley": "Ulysses Bentley IV",
    "Velus Jones": "Velus Jones Jr.",
    "WanDale Robinson": "Wan'Dale Robinson",
}

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

    missing_optional = [column for column in column_map.values() if column not in selected.columns]
    if missing_optional:
        logger.warning(f"{source_name} missing optional columns: {', '.join(sorted(missing_optional))}")
    return selected

def team_normalization(source: pd.DataFrame) -> pd.DataFrame:
    if "base_team" in source.columns:
        source["base_team"] = source["base_team"].replace(teams.TEAM_ABBR_NORMALIZATION)
    if "base_opp_team" in source.columns:
        source["base_opp_team"] = source["base_opp_team"].replace(teams.TEAM_ABBR_NORMALIZATION)
    return source

def apply_pfr_playerid_map(source: pd.DataFrame, ff_playerid_map: Mapping[str, str] | None = None) -> pd.DataFrame:
    """Attach player ids to PFR sources when a PFR->GSIS map is available."""
    if ff_playerid_map and "base_pfr_id" in source.columns:
        source["base_player_id"] = source["base_pfr_id"].map(ff_playerid_map)
    return source

def filter_regular_season(source: pd.DataFrame) -> pd.DataFrame:
    """Filter to regular-season rows when a season-type field is available."""
    if "base_season_type" not in source.columns:
        return source
    return source.loc[source["base_season_type"] == "REG"]

def filter_positions(source: pd.DataFrame, positions: list[str]) -> pd.DataFrame:
    """Filter to the supported fantasy positions when a position field is available."""
    if "base_pos" not in source.columns:
        return source
    return source.loc[source["base_pos"].isin(positions)]

def apply_name_map(source: pd.DataFrame) -> pd.DataFrame:
    """Apply the explicit player name alias map to a source dataframe."""
    if "base_player_display_name" in source.columns:
        source["base_player_display_name"] = source["base_player_display_name"].replace(PLAYER_NAME_MAP)
    return source

def left_merge_fill(base: pd.DataFrame, df: pd.DataFrame, join_candidates: List[str]) -> pd.DataFrame:
    """Left-join df onto base and fill overlapping columns from right to left."""
    join_keys = [key for key in join_candidates if key in base.columns and key in df.columns]

    # Guard for when merge_weekly calls because it has no team col
    if "base_team" in df.columns and "base_team" not in join_keys:
        df = df.sort_values(join_keys + ["base_team"], na_position="last")

    base_indexed = base.set_index(join_keys)
    df_indexed = df.drop_duplicates(subset=join_keys).set_index(join_keys)
    df_aligned = df_indexed.reindex(base_indexed.index)
    combined = base_indexed.combine_first(df_aligned).copy()
    return combined.reset_index()

def merge_weekly_aggregates_into_seasonal(seasonal_df: pd.DataFrame, weekly_df: pd.DataFrame, group_keys: list[str], summed_metrics: list[str], averaged_metrics: list[str]) -> pd.DataFrame:
    """Merge weekly-derived season aggregates into seasonal rows, filling only missing values."""
    summed = _aggregate_weekly_metrics(weekly_df, group_keys, summed_metrics, "sum")
    averaged = _aggregate_weekly_metrics(weekly_df, group_keys, averaged_metrics, "mean")
    aggregate = summed.merge(averaged, on=group_keys, how="outer")
    return left_merge_fill(seasonal_df, aggregate, group_keys)

def _aggregate_weekly_metrics(weekly_df: pd.DataFrame, group_keys: list[str], metrics: list[str], reducer: str) -> pd.DataFrame | None:
    """Reduce available weekly metrics by player-season using the requested reducer."""
    available_metrics = [metric for metric in metrics if metric in weekly_df.columns]
    grouped_input = weekly_df[group_keys + available_metrics].copy()
    grouped_input[available_metrics] = grouped_input[available_metrics].apply(pd.to_numeric, errors="coerce")
    grouped = grouped_input.groupby(group_keys, dropna=False, sort=False)[available_metrics]
    reduced = grouped.sum(min_count=1) if reducer == "sum" else grouped.mean()
    return reduced.reset_index()

def add_group_ranks(df: pd.DataFrame, group_cols: List[str], rank_metrics: List[str]) -> pd.DataFrame:
    """Add positional rank columns for metrics within contextual groups (1 = best)."""
    ranked = df.copy()
    groups = [ranked[col] for col in group_cols if col in ranked.columns]
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

"""Pydantic models for API request/response validation and documentation."""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


class AppInfoResponse(BaseModel):
    """Response for application overview metadata."""
    seasons: List[int] = Field(..., description="Available season years")
    current_season: int = Field(..., description="Most recent season")
    total_players: int = Field(..., description="Total historical players tracked")
    current_season_players: int = Field(..., description="Players active in the current season")
    total_game_logs: int = Field(..., description="Total weekly game log records")
    rookie_count: int = Field(..., description="Number of rookies in current data")
    stat_columns: int = Field(..., description="Number of distinct stat metrics tracked per player")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "seasons": [2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025],
                "current_season": 2025,
                "total_players": 1842,
                "current_season_players": 520,
                "total_game_logs": 85000,
                "rookie_count": 120,
                "stat_columns": 65,
            }
        }
    )


class PlayerResponse(BaseModel):
    """Response for individual player details."""
    name: str = Field(..., description="Player name")
    position: str = Field(..., description="Player position: QB, RB, WR, TE")
    team: Optional[str] = Field(None, description="Team abbreviation")
    stats: Dict[str, Any] = Field(..., description="Player statistics (season total or average)")
    available_seasons: List[int] = Field(default_factory=list, description="Seasons where player has data")
    age: Optional[int] = Field(None, description="Player age")
    is_rookie: bool = Field(default=False, description="Whether player is a rookie")
    is_eligible: bool = Field(default=True, description="Whether player is active/eligible")
    headshot_url: Optional[str] = Field(None, description="URL to player headshot image")
    weekly_stats: Optional[List[Dict[str, Any]]] = Field(None, description="Weekly breakdown of player statistics by season and week")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Ja'Marr Chase",
                "position": "WR",
                "team": "CIN",
                "stats": {"receptions": 127.0, "receiving_yards": 1716.0},
                "available_seasons": [2021, 2022, 2023, 2024],
                "age": 25,
                "is_rookie": False,
                "is_eligible": True,
                "headshot_url": "https://example.com/images/jamarre-chase.png",
                "weekly_stats": [
                    {"season": 2024, "week": 1, "receptions": 6, "rec_yds": 89},
                    {"season": 2024, "week": 2, "receptions": 8, "rec_yds": 102},
                ],
            }
        }
    )


class PlayerSearchResult(BaseModel):
    """Player search result."""
    name: str = Field(..., description="Player name")
    position: str = Field(..., description="Player position")
    age: Optional[int] = Field(None, description="Player age")
    team: Optional[str] = Field(None, description="Team abbreviation")
    is_rookie: bool = Field(default=False, description="Whether player is a rookie")
    is_eligible: bool = Field(default=True, description="Whether player is active/eligible")
    headshot_url: Optional[str] = Field(None, description="URL to player headshot image")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Ja'Marr Chase",
                "position": "WR",
                "age": 24,
                "team": "CIN",
                "is_rookie": False,
                "is_eligible": True,
                "headshot_url": "https://example.com/images/jamarre-chase.png",
            }
        }
    )


class SearchResponse(BaseModel):
    """Response for player search"""
    query: str = Field(..., description="Search query")
    results: List[PlayerSearchResult] = Field(..., description="Search results")
    count: int = Field(..., description="Number of results")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "query": "chase",
                "results": [
                    {"name": "Ja'Marr Chase", "position": "WR", "team": "CIN"},
                    {"name": "JK Dobbins", "position": "RB", "team": "LAC"},
                ],
                "count": 2,
            }
        }
    )


class ChartPlayerEntry(BaseModel):
    """Single player entry for chart data"""
    name: str = Field(..., description="Player name")
    position: Optional[str] = Field(None, description="Player position")
    age: Optional[int] = Field(None, description="Player age")
    team: Optional[str] = Field(None, description="Team abbreviation")
    headshot_url: Optional[str] = Field(None, description="URL to player headshot image")
    stats: Dict[str, float] = Field(..., description="Stat name → value mapping")


class ChartDataResponse(BaseModel):
    """Response for chart data endpoint"""
    season: int = Field(..., description="Season year")
    position: str = Field(..., description="Position: QB, RB, WR, or TE")
    available_seasons: List[int] = Field(..., description="Available seasons to choose from")
    stat_columns: List[str] = Field(..., description="Available stat column names")
    players: List[ChartPlayerEntry] = Field(..., description="Player data for charting")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "season": 2024,
                "position": "RB",
                "available_seasons": [2024, 2023, 2022],
                "stat_columns": ["Carries", "Rush Yds", "Rush TD"],
                "players": [
                    {
                        "name": "Saquon Barkley",
                        "team": "PHI",
                        "headshot_url": None,
                        "stats": {"Carries": 345, "Rush Yds": 2005, "Rush TD": 13},
                    }
                ],
            }
        }
    )

class ConsistencyChartEntry(BaseModel):
    """Single player entry for consistency/upside scatter chart."""
    name: str = Field(..., description="Player name")
    position: Optional[str] = Field(None, description="Player position")
    age: Optional[int] = Field(None, description="Player age")
    team: Optional[str] = Field(None, description="Team abbreviation")
    headshot_url: Optional[str] = Field(None, description="URL to player headshot image")
    games: int = Field(..., description="Weekly game count included in the profile")
    avg_fp_ppr: float = Field(..., description="Average weekly PPR fantasy points")
    ceiling_fp_ppr: float = Field(..., description="Highest weekly PPR fantasy points")
    volatility_fp_ppr: float = Field(..., description="Weekly PPR standard deviation")


class ConsistencyChartResponse(BaseModel):
    """Response for consistency/upside chart data endpoint."""
    season: int = Field(..., description="Season year")
    position: str = Field(..., description="Position: QB, RB, WR, TE, or Overall")
    available_seasons: List[int] = Field(..., description="Available seasons to choose from")
    players: List[ConsistencyChartEntry] = Field(..., description="Weekly consistency/upside player profiles")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "season": 2025,
                "position": "WR",
                "available_seasons": [2025, 2024, 2023],
                "players": [
                    {
                        "name": "Ja'Marr Chase",
                        "position": "WR",
                        "age": 25,
                        "team": "CIN",
                        "headshot_url": "https://example.com/images/jamarre-chase.png",
                        "games": 17,
                        "avg_fp_ppr": 19.8,
                        "ceiling_fp_ppr": 35.7,
                        "volatility_fp_ppr": 6.2,
                    }
                ],
            }
        }
    )


class PlayerTrendPoint(BaseModel):
    """Single season point for a player's trend chart."""
    season: int = Field(..., description="Season year")
    value: Optional[float] = Field(None, description="Selected stat value for the season")


class PlayerTrendResponse(BaseModel):
    """Response for single-player season trend endpoint."""
    player_name: str = Field(..., description="Player name")
    position: str = Field(..., description="Position scope used to query data")
    stat: str = Field(..., description="Selected stat column key")
    available_seasons: List[int] = Field(..., description="Available seasons in descending order")
    points: List[PlayerTrendPoint] = Field(..., description="Season points in ascending season order")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "player_name": "Patrick Mahomes",
                "position": "QB",
                "stat": "Pass Yds",
                "available_seasons": [2025, 2024],
                "points": [
                    {"season": 2024, "value": 4065.0},
                    {"season": 2025, "value": 4280.0},
                ],
            }
        }
    )


class DivisionsResponse(BaseModel):
    """Response for NFL divisions structure"""
    divisions: Dict[str, Dict[str, List[str]]] = Field(..., description="NFL divisions by conference")
    team_names: Dict[str, str] = Field(..., description="Team abbreviation to full name mapping")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "divisions": {
                    "AFC": {"North": ["BAL", "CIN", "CLE", "PIT"]},
                    "NFC": {"North": ["CHI", "DET", "GB", "MIN"]},
                },
                "team_names": {"BAL": "Baltimore Ravens", "CIN": "Cincinnati Bengals"},
            }
        }
    )


class TeamScheduleGame(BaseModel):
    """Single game in a team's schedule"""
    week: int = Field(..., description="Week number")
    opponent: str = Field(..., description="Opponent team abbreviation or BYE")
    home_away: Optional[str] = Field(None, description="HOME or AWAY (null for BYE)")
    
    model_config = ConfigDict(json_schema_extra={"example": {"week": 1, "opponent": "KC", "home_away": "AWAY"}})


class TeamScheduleResponse(BaseModel):
    """Response for team schedule"""
    team: str = Field(..., description="Team abbreviation")
    team_name: str = Field(..., description="Full team name")
    season: int = Field(..., description="Season year")
    available_seasons: List[int] = Field(..., description="Available schedule seasons")
    schedule: List[TeamScheduleGame] = Field(..., description="List of games by week")
    bye_week: Optional[int] = Field(None, description="Bye week number")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "team": "KC",
                "team_name": "Kansas City Chiefs",
                "season": 2025,
                "available_seasons": [2025, 2024, 2023],
                "schedule": [
                    {"week": 1, "opponent": "BAL", "home_away": "HOME"},
                    {"week": 2, "opponent": "CIN", "home_away": "AWAY"},
                ],
                "bye_week": 6,
            }
        }
    )


class DepthChartEntry(BaseModel):
    """Single position row in a depth chart"""
    position: str = Field(..., description="Position abbreviation (QB, RB, WR, TE)")
    starter: Optional[str] = Field(None, description="Starting player")
    second: Optional[str] = Field(None, description="2nd string player")
    third: Optional[str] = Field(None, description="3rd string player")
    fourth: Optional[str] = Field(None, description="4th string player")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "position": "QB",
                "starter": "Patrick Mahomes",
                "second": "Carson Wentz",
                "third": None,
                "fourth": None,
            }
        }
    )


class TeamDepthChartResponse(BaseModel):
    """Response for a single team's depth chart"""
    team: str = Field(..., description="Team abbreviation")
    team_name: str = Field(..., description="Full team name")
    depth_chart: List[DepthChartEntry] = Field(..., description="Depth chart entries by position")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "team": "KC",
                "team_name": "Kansas City Chiefs",
                "depth_chart": [
                    {
                        "position": "QB",
                        "starter": "Patrick Mahomes",
                        "second": "Carson Wentz",
                        "third": None,
                        "fourth": None,
                    },
                    {
                        "position": "RB",
                        "starter": "Isiah Pacheco",
                        "second": "Clyde Edwards-Helaire",
                        "third": None,
                        "fourth": None,
                    },
                ],
            }
        }
    )

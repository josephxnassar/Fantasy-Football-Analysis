"""
Pydantic models for API request/response validation and documentation.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any


class PlayerRankingRecord(BaseModel):
    """Individual player ranking record"""
    name: str = Field(..., description="Player name")
    rating: float = Field(..., description="Calculated rating score")
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "Ja'Marr Chase",
                "rating": 401.52
            }
        }


class RankingsResponse(BaseModel):
    """Response for player rankings endpoint"""
    format: str = Field(..., description="Format: redraft or dynasty")
    position: Optional[str] = Field(None, description="Position filter: QB, RB, WR, or TE")
    model: str = Field(..., description="Model used: linear, ridge, or lasso")
    rankings: Dict[str, List[Dict[str, Any]]] = Field(..., description="Rankings grouped by position")
    
    class Config:
        json_schema_extra = {
            "example": {
                "format": "redraft",
                "position": "WR",
                "model": "ridge",
                "rankings": {
                    "WR": [
                        {"name": "Ja'Marr Chase", "rating": 401.52},
                        {"name": "Justin Jefferson", "rating": 314.54}
                    ]
                }
            }
        }


class PlayerStats(BaseModel):
    """Player statistical data"""
    completions: Optional[float] = None
    attempts: Optional[float] = None
    passing_yards: Optional[float] = None
    passing_touchdowns: Optional[float] = None
    carries: Optional[float] = None
    rushing_yards: Optional[float] = None
    rushing_touchdowns: Optional[float] = None
    receiving_yards: Optional[float] = None
    receiving_touchdowns: Optional[float] = None
    receptions: Optional[float] = None
    rating: Optional[float] = None
    
    class Config:
        extra = "allow"  # Allow additional stats fields


class GameMatchup(BaseModel):
    """Single game matchup in schedule"""
    week: int = Field(..., description="Week number")
    opponent: str = Field(..., description="Opponent team abbreviation or 'BYE'")
    
    class Config:
        json_schema_extra = {
            "example": {
                "week": 1,
                "opponent": "LAR"
            }
        }


class PlayerResponse(BaseModel):
    """Response for individual player details"""
    name: str = Field(..., description="Player name")
    position: str = Field(..., description="Player position: QB, RB, WR, TE")
    team: Optional[str] = Field(None, description="Team abbreviation")
    stats: Dict[str, Any] = Field(..., description="Player statistics")
    schedule: List[Dict[str, Any]] = Field(..., description="Upcoming schedule matchups")
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "Ja'Marr Chase",
                "position": "WR",
                "team": "CIN",
                "stats": {"rating": 401.52, "receptions": 127.0},
                "schedule": [
                    {"week": 1, "opponent": "LAR"},
                    {"week": 2, "opponent": "NO"}
                ]
            }
        }


class ScheduleResponse(BaseModel):
    """Response for team schedule"""
    team: str = Field(..., description="Team abbreviation")
    schedule: List[Dict[str, Any]] = Field(..., description="Weekly schedule with opponents/bye weeks")
    
    class Config:
        json_schema_extra = {
            "example": {
                "team": "KC",
                "schedule": [
                    {"week": 1, "opponent": "BAL"},
                    {"week": 9, "opponent": "BYE"},
                    {"week": 18, "opponent": "LV"}
                ]
            }
        }


class ErrorResponse(BaseModel):
    """Standard error response"""
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Additional error details")
    
    class Config:
        json_schema_extra = {
            "example": {
                "error": "Player not found",
                "detail": "Player 'Unknown Player' does not exist in the database"
            }
        }


class MatchupQuality(BaseModel):
    """Matchup quality rating for a position vs opponent"""
    opponent: str = Field(..., description="Opponent team abbreviation")
    quality: str = Field(..., description="Matchup quality: elite, good, neutral, bad, worst")
    
    class Config:
        json_schema_extra = {
            "example": {
                "opponent": "LAR",
                "quality": "elite"
            }
        }


class GameMatchupDetailed(BaseModel):
    """Single game matchup with quality rating"""
    week: int = Field(..., description="Week number")
    opponent: str = Field(..., description="Opponent team abbreviation or 'BYE'")
    matchup_quality: Optional[str] = Field(None, description="Matchup quality rating: elite, good, neutral, bad, worst")
    
    class Config:
        json_schema_extra = {
            "example": {
                "week": 1,
                "opponent": "LAR",
                "matchup_quality": "elite"
            }
        }

"""
Pydantic models for API request/response validation and documentation.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any


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


class PlayerResponse(BaseModel):
    """Response for individual player details"""
    name: str = Field(..., description="Player name")
    position: str = Field(..., description="Player position: QB, RB, WR, TE")
    team: Optional[str] = Field(None, description="Team abbreviation")
    stats: Dict[str, Any] = Field(..., description="Player statistics")
    available_seasons: List[int] = Field(default_factory=list, description="Seasons where player has data")
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "Ja'Marr Chase",
                "position": "WR",
                "team": "CIN",
                "stats": {"rating": 401.52, "receptions": 127.0},
                "available_seasons": [2021, 2022, 2023, 2024]
            }
        }


class PlayerSearchResult(BaseModel):
    """Player search result"""
    name: str = Field(..., description="Player name")
    position: str = Field(..., description="Player position")
    rating: float = Field(..., description="Player rating")
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "Ja'Marr Chase",
                "position": "WR",
                "rating": 401.52
            }
        }


class SearchResponse(BaseModel):
    """Response for player search"""
    query: str = Field(..., description="Search query")
    results: List[PlayerSearchResult] = Field(..., description="Search results")
    count: int = Field(..., description="Number of results")
    
    class Config:
        json_schema_extra = {
            "example": {
                "query": "chase",
                "results": [
                    {"name": "Ja'Marr Chase", "position": "WR", "rating": 401.52},
                    {"name": "JK Dobbins", "position": "RB", "rating": 250.0}
                ],
                "count": 2
            }
        }

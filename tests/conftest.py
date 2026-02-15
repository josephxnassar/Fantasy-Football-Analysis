from __future__ import annotations

from contextlib import contextmanager
from pathlib import Path
from typing import Any, Dict
import sys

import pandas as pd
import pytest
from fastapi.testclient import TestClient

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.util import constants

def _build_statistics_cache() -> Dict[str, Any]:
    qb_2025 = pd.DataFrame(
        {
            "Comp": [401],
            "Att": [590],
            "Pass Yds": [4280],
            "Pass TD": [32],
            "INT": [11],
            "PPR Pts": [352.4],
            "Non-PPR Pts": [298.2],
        },
        index=pd.Index(["Patrick Mahomes"], name="player_display_name"),
    )
    wr_2025 = pd.DataFrame(
        {
            "Rec": [109],
            "Tgt": [151],
            "Rec Yds": [1462],
            "Rec TD": [11],
            "PPR Pts": [311.8],
            "Non-PPR Pts": [202.8],
        },
        index=pd.Index(["JaMarr Chase"], name="player_display_name"),
    )
    qb_2024 = pd.DataFrame(
        {
            "Comp": [389],
            "Att": [575],
            "Pass Yds": [4065],
            "Pass TD": [30],
            "INT": [12],
            "PPR Pts": [334.1],
            "Non-PPR Pts": [282.0],
        },
        index=pd.Index(["Patrick Mahomes"], name="player_display_name"),
    )

    return {
        "available_seasons": [2024, 2025],
        constants.STATS["ALL_PLAYERS"]: [
            {
                "name": "Patrick Mahomes",
                "position": "QB",
                "Age": 30,
                "RedraftRating": 401.5,
                "DynastyRating": 372.9,
                "headshot_url": "https://example.com/mahomes.png",
                "team": "KC",
                "is_rookie": False,
                "is_eligible": True,
                "overall_rank_redraft": 1,
                "overall_rank_dynasty": 2,
                "pos_rank_redraft": 1,
                "pos_rank_dynasty": 1,
            },
            {
                "name": "JaMarr Chase",
                "position": "WR",
                "Age": 26,
                "RedraftRating": 356.2,
                "DynastyRating": 421.0,
                "headshot_url": "https://example.com/chase.png",
                "team": "CIN",
                "is_rookie": False,
                "is_eligible": True,
                "overall_rank_redraft": 2,
                "overall_rank_dynasty": 1,
                "pos_rank_redraft": 1,
                "pos_rank_dynasty": 1,
            },
            {
                "name": "Retired Veteran",
                "position": "QB",
                "Age": 41,
                "RedraftRating": 999.0,
                "DynastyRating": 999.0,
                "headshot_url": None,
                "team": None,
                "is_rookie": False,
                "is_eligible": False,
                "overall_rank_redraft": None,
                "overall_rank_dynasty": None,
                "pos_rank_redraft": None,
                "pos_rank_dynasty": None,
            },
        ],
        constants.STATS["BY_YEAR"]: {
            2025: {"QB": qb_2025, "WR": wr_2025},
            2024: {"QB": qb_2024},
        },
        constants.STATS["PLAYER_WEEKLY_STATS"]: {
            "Patrick Mahomes": [
                {
                    "season": 2025,
                    "week": 1,
                    "Pass Yds": 320,
                    "Pass TD": 3,
                    "INT": 0,
                    "opponent_team": "BAL",
                    "Snap Share": 0.98,
                }
            ],
            "JaMarr Chase": [
                {
                    "season": 2025,
                    "week": 1,
                    "Rec": 8,
                    "Rec Yds": 112,
                    "Rec TD": 1,
                    "opponent_team": "CLE",
                    "Snap Share": 0.91,
                }
            ],
        },
    }

def _build_schedules_cache() -> Dict[int, Dict[str, pd.DataFrame]]:
    kc_schedule = pd.DataFrame(
        {
            "Opponent": ["BAL", "BYE", "CIN"],
            "HomeAway": ["HOME", None, "AWAY"],
        },
        index=pd.Index([1, 2, 3], name="week"),
    )
    cin_schedule = pd.DataFrame(
        {
            "Opponent": ["CLE", "PIT", "KC"],
            "HomeAway": ["HOME", "AWAY", "HOME"],
        },
        index=pd.Index([1, 2, 3], name="week"),
    )
    return {
        2025: {"KC": kc_schedule, "CIN": cin_schedule},
        2024: {"KC": kc_schedule.copy()},
    }

def _build_depth_chart_cache() -> Dict[str, pd.DataFrame]:
    kc = (
        pd.DataFrame(
            [
                {"Position": "QB", "Starter": "Patrick Mahomes", "2nd": "Carson Wentz", "3rd": None, "4th": None},
                {"Position": "RB", "Starter": "Isiah Pacheco", "2nd": "Kareem Hunt", "3rd": None, "4th": None},
                {"Position": "WR", "Starter": "Rashee Rice", "2nd": "Xavier Worthy", "3rd": None, "4th": None},
                {"Position": "TE", "Starter": "Travis Kelce", "2nd": "Noah Gray", "3rd": None, "4th": None},
            ]
        )
        .set_index("Position")
        .rename_axis("KC")
    )

    cin = (
        pd.DataFrame(
            [
                {"Position": "QB", "Starter": "Joe Burrow", "2nd": "Jake Browning", "3rd": None, "4th": None},
                {"Position": "RB", "Starter": "Chase Brown", "2nd": "Zack Moss", "3rd": None, "4th": None},
                {"Position": "WR", "Starter": "JaMarr Chase", "2nd": "Tee Higgins", "3rd": None, "4th": None},
                {"Position": "TE", "Starter": "Mike Gesicki", "2nd": "Tanner Hudson", "3rd": None, "4th": None},
            ]
        )
        .set_index("Position")
        .rename_axis("CIN")
    )

    return {"KC": kc, "CIN": cin}

def _build_app_caches() -> Dict[str, Any]:
    return {
        constants.CACHE["STATISTICS"]: _build_statistics_cache(),
        constants.CACHE["SCHEDULES"]: _build_schedules_cache(),
        constants.CACHE["DEPTH_CHART"]: _build_depth_chart_cache(),
    }

@pytest.fixture
def stats_cache() -> Dict[str, Any]:
    return _build_statistics_cache()

@pytest.fixture
def schedules_cache() -> Dict[int, Dict[str, pd.DataFrame]]:
    return _build_schedules_cache()

@pytest.fixture
def depth_chart_cache() -> Dict[str, pd.DataFrame]:
    return _build_depth_chart_cache()

@pytest.fixture
def app_caches() -> Dict[str, Any]:
    return _build_app_caches()

@pytest.fixture
def client_factory(monkeypatch):
    import backend.api.api as api_module

    @contextmanager
    def _factory(caches: Dict[str, Any]):
        class DummyDB:
            def close(self) -> None:
                return None

        class FakeApp:
            def __init__(self) -> None:
                self.caches = caches
                self.db = DummyDB()

            def initialize(self) -> None:
                return None

        monkeypatch.setattr(api_module, "App", FakeApp)
        with TestClient(api_module.api) as client:
            yield client

    return _factory

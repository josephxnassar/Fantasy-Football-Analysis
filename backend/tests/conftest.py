from __future__ import annotations

import sys
from contextlib import contextmanager
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pandas as pd
import pytest
from fastapi.testclient import TestClient

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.util import constants


def _indexed_frame(rows: list[dict[str, Any]], index_column: str, axis_name: str | None = None) -> pd.DataFrame:
    frame = pd.DataFrame(rows).set_index(index_column)
    return frame.rename_axis(axis_name or index_column)


def _season_stats_frame(rows: list[dict[str, Any]]) -> pd.DataFrame:
    return _indexed_frame(rows, "player_display_name")


def _schedule_frame(rows: list[dict[str, Any]]) -> pd.DataFrame:
    return _indexed_frame(rows, "week")


def _depth_chart_frame(team: str, rows: list[dict[str, Any]]) -> pd.DataFrame:
    return _indexed_frame(rows, "position", axis_name=team)


def _build_statistics_cache() -> dict[str, Any]:
    by_year = {
        2025: {
            "QB": _season_stats_frame(
                [
                    {
                        "player_display_name": "Patrick Mahomes",
                        "Comp": 401,
                        "Att": 590,
                        "Pass Yds": 4280,
                        "Pass TD": 32,
                        "INT": 11,
                        "PPR Pts": 352.4,
                        "Non-PPR Pts": 298.2,
                    }
                ]
            ),
            "WR": _season_stats_frame(
                [
                    {
                        "player_display_name": "JaMarr Chase",
                        "Rec": 109,
                        "Tgt": 151,
                        "Rec Yds": 1462,
                        "Rec TD": 11,
                        "PPR Pts": 311.8,
                        "Non-PPR Pts": 202.8,
                    }
                ]
            ),
        },
        2024: {
            "QB": _season_stats_frame(
                [
                    {
                        "player_display_name": "Patrick Mahomes",
                        "Comp": 389,
                        "Att": 575,
                        "Pass Yds": 4065,
                        "Pass TD": 30,
                        "INT": 12,
                        "PPR Pts": 334.1,
                        "Non-PPR Pts": 282.0,
                    }
                ]
            )
        },
    }

    all_players = [
        {
            "name": "Patrick Mahomes",
            "position": "QB",
            "age": 30,
            "redraft_rating": 401.5,
            "dynasty_rating": 372.9,
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
            "age": 26,
            "redraft_rating": 356.2,
            "dynasty_rating": 421.0,
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
            "age": 41,
            "redraft_rating": 999.0,
            "dynasty_rating": 999.0,
            "headshot_url": None,
            "team": None,
            "is_rookie": False,
            "is_eligible": False,
            "overall_rank_redraft": None,
            "overall_rank_dynasty": None,
            "pos_rank_redraft": None,
            "pos_rank_dynasty": None,
        },
    ]

    player_weekly_stats = {
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
    }

    return {
        constants.STATS["ALL_PLAYERS"]: all_players,
        constants.STATS["BY_YEAR"]: by_year,
        constants.STATS["PLAYER_WEEKLY_STATS"]: player_weekly_stats,
    }


def _build_schedules_cache() -> dict[int, dict[str, pd.DataFrame]]:
    kc_schedule = _schedule_frame(
        [
            {"week": 1, "opponent": "BAL", "home_away": "HOME", "team_score": 24, "opponent_score": 20},
            {"week": 2, "opponent": "BYE", "home_away": None, "team_score": None, "opponent_score": None},
            {"week": 3, "opponent": "CIN", "home_away": "AWAY", "team_score": 17, "opponent_score": 21},
        ]
    )
    cin_schedule = _schedule_frame(
        [
            {"week": 1, "opponent": "CLE", "home_away": "HOME", "team_score": 27, "opponent_score": 14},
            {"week": 2, "opponent": "PIT", "home_away": "AWAY", "team_score": 20, "opponent_score": 24},
            {"week": 3, "opponent": "KC", "home_away": "HOME", "team_score": 21, "opponent_score": 17},
        ]
    )
    return {
        2025: {"KC": kc_schedule, "CIN": cin_schedule},
        2024: {"KC": kc_schedule.copy()},
    }


def _build_depth_chart_cache() -> dict[str, pd.DataFrame]:
    return {
        "KC": _depth_chart_frame(
            "KC",
            [
                {"position": "QB", "starter": "Patrick Mahomes", "2nd": "Carson Wentz", "3rd": None, "4th": None},
                {"position": "RB", "starter": "Isiah Pacheco", "2nd": "Kareem Hunt", "3rd": None, "4th": None},
                {"position": "WR", "starter": "Rashee Rice", "2nd": "Xavier Worthy", "3rd": None, "4th": None},
                {"position": "TE", "starter": "Travis Kelce", "2nd": "Noah Gray", "3rd": None, "4th": None},
            ],
        ),
        "CIN": _depth_chart_frame(
            "CIN",
            [
                {"position": "QB", "starter": "Joe Burrow", "2nd": "Jake Browning", "3rd": None, "4th": None},
                {"position": "RB", "starter": "Chase Brown", "2nd": "Zack Moss", "3rd": None, "4th": None},
                {"position": "WR", "starter": "JaMarr Chase", "2nd": "Tee Higgins", "3rd": None, "4th": None},
                {"position": "TE", "starter": "Mike Gesicki", "2nd": "Tanner Hudson", "3rd": None, "4th": None},
            ],
        ),
    }


@pytest.fixture
def stats_cache() -> dict[str, Any]:
    return _build_statistics_cache()


@pytest.fixture
def schedules_cache() -> dict[int, dict[str, pd.DataFrame]]:
    return _build_schedules_cache()


@pytest.fixture
def depth_chart_cache() -> dict[str, pd.DataFrame]:
    return _build_depth_chart_cache()


@pytest.fixture
def app_caches(stats_cache: dict[str, Any], schedules_cache: dict[int, dict[str, pd.DataFrame]], depth_chart_cache: dict[str, pd.DataFrame]) -> dict[str, Any]:
    return {
        constants.CACHE["STATISTICS"]: stats_cache,
        constants.CACHE["SCHEDULES"]: schedules_cache,
        constants.CACHE["DEPTH_CHART"]: depth_chart_cache,
    }


def _noop() -> None:
    return None


@pytest.fixture
def client_factory(monkeypatch):
    import backend.api.api as api_module

    @contextmanager
    def _factory(caches: dict[str, Any]):
        monkeypatch.setattr(
            api_module,
            "App",
            lambda: SimpleNamespace(
                caches=caches,
                db=SimpleNamespace(close=_noop),
                initialize=_noop,
            ),
        )
        with TestClient(api_module.api) as client:
            yield client

    return _factory

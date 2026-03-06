from copy import deepcopy

import pandas as pd
import pytest

from backend.util import constants

pytestmark = pytest.mark.integration

def test_search_endpoint_omits_legacy_rating_fields(client_factory, app_caches) -> None:
    with client_factory(app_caches) as client:
        response = client.get("/api/search", params={"q": "maho"})

    assert response.status_code == 200
    payload = response.json()
    assert payload["count"] >= 1
    assert payload["results"][0]["name"] == "Patrick Mahomes"
    assert "redraft_rating" not in payload["results"][0]

def test_player_endpoint_returns_profile_weekly_stats_and_player_metadata(client_factory, app_caches) -> None:
    with client_factory(app_caches) as client:
        response = client.get("/api/player/Patrick%20Mahomes")

    assert response.status_code == 200
    payload = response.json()
    assert payload["name"] == "Patrick Mahomes"
    assert payload["position"] == "QB"
    assert payload["team"] == "KC"
    assert payload["age"] == 30
    assert payload["is_eligible"] is True
    assert payload["weekly_stats"][0]["week"] == 1

def test_player_endpoint_requires_canonical_name(client_factory, app_caches) -> None:
    with client_factory(app_caches) as client:
        response = client.get("/api/player/patrick%20mahomes%20ii")

    assert response.status_code == 404

def test_schedule_and_depth_chart_endpoints_return_team_data(client_factory, app_caches) -> None:
    with client_factory(app_caches) as client:
        schedule_response = client.get("/api/schedules/KC", params={"season": 2025})
        depth_response = client.get("/api/depth-charts/KC")

    assert schedule_response.status_code == 200
    assert depth_response.status_code == 200

    schedule = schedule_response.json()
    depth = depth_response.json()

    assert schedule["bye_week"] == 2
    assert schedule["schedule"][1]["opponent"] == "BYE"
    assert depth["team"] == "KC"
    assert any(row["position"] == "QB" and row["starter"] == "Patrick Mahomes" for row in depth["depth_chart"])

def test_chart_data_endpoint_returns_overall_and_stat_columns(client_factory, app_caches) -> None:
    with client_factory(app_caches) as client:
        response = client.get("/api/chart-data", params={"position": "Overall", "season": 2025})

    assert response.status_code == 200
    payload = response.json()
    names = {player["name"] for player in payload["players"]}
    players_by_name = {player["name"]: player for player in payload["players"]}
    assert {"Patrick Mahomes", "JaMarr Chase"}.issubset(names)
    assert "Pass Yds" in payload["stat_columns"]
    assert "Rec Yds" in payload["stat_columns"]
    assert players_by_name["Patrick Mahomes"]["position"] == "QB"
    assert players_by_name["Patrick Mahomes"]["age"] == 30

def test_chart_data_endpoint_for_position_includes_position_and_age(client_factory, app_caches) -> None:
    with client_factory(app_caches) as client:
        response = client.get("/api/chart-data", params={"position": "QB", "season": 2025})

    assert response.status_code == 200
    payload = response.json()
    assert payload["position"] == "QB"
    assert payload["players"][0]["name"] == "Patrick Mahomes"
    assert payload["players"][0]["position"] == "QB"
    assert payload["players"][0]["age"] == 30

def test_consistency_data_endpoint_returns_weekly_profiles(client_factory, app_caches) -> None:
    custom_caches = deepcopy(app_caches)
    custom_caches[constants.CACHE["STATISTICS"]][constants.STATS["PLAYER_WEEKLY_STATS"]] = {
        "Patrick Mahomes": [
            {"season": 2025, "week": 1, "fp_ppr": 24.8},
            {"season": 2025, "week": 2, "fp_ppr": 19.2},
        ],
        "JaMarr Chase": [
            {"season": 2025, "week": 1, "fp_ppr": 21.4},
            {"season": 2025, "week": 2, "fp_ppr": 33.9},
        ],
    }

    with client_factory(custom_caches) as client:
        response = client.get("/api/consistency-data", params={"position": "Overall", "season": 2025, "top_n": 20})

    assert response.status_code == 200
    payload = response.json()
    assert payload["season"] == 2025
    assert payload["position"] == "Overall"
    assert any(player["name"] == "Patrick Mahomes" for player in payload["players"])
    assert all("avg_fp_ppr" in player and "ceiling_fp_ppr" in player for player in payload["players"])


def test_player_trend_endpoint_returns_single_player_series(client_factory, app_caches) -> None:
    with client_factory(app_caches) as client:
        response = client.get("/api/player-trend", params={"player_name": "Patrick Mahomes", "position": "QB", "stat": "Pass Yds"})

    assert response.status_code == 200
    payload = response.json()
    assert payload["player_name"] == "Patrick Mahomes"
    assert payload["position"] == "QB"
    assert payload["stat"] == "Pass Yds"
    assert payload["available_seasons"] == [2025, 2024]
    assert payload["points"] == [
        {"season": 2024, "value": 4065.0},
        {"season": 2025, "value": 4280.0},
    ]


def test_player_trend_endpoint_rejects_unknown_stat(client_factory, app_caches) -> None:
    with client_factory(app_caches) as client:
        response = client.get("/api/player-trend", params={"player_name": "Patrick Mahomes", "position": "QB", "stat": "not_a_stat"})

    assert response.status_code == 400
    assert "Invalid stat" in response.json()["detail"]


def test_search_endpoint_rejects_short_query(client_factory, app_caches) -> None:
    with client_factory(app_caches) as client:
        response = client.get("/api/search", params={"q": "a"})

    assert response.status_code == 400
    assert "at least 2 characters" in response.json()["detail"]


@pytest.mark.parametrize("position", ["K", "DEF"])
def test_chart_data_endpoint_rejects_invalid_position(client_factory, app_caches, position: str) -> None:
    with client_factory(app_caches) as client:
        response = client.get("/api/chart-data", params={"position": position, "season": 2025})

    assert response.status_code == 400
    assert "Invalid position" in response.json()["detail"]


@pytest.mark.parametrize("top_n", [3, 201])
def test_consistency_data_endpoint_validates_top_n_range(client_factory, app_caches, top_n: int) -> None:
    with client_factory(app_caches) as client:
        response = client.get(
            "/api/consistency-data",
            params={"position": "Overall", "season": 2025, "top_n": top_n},
        )

    assert response.status_code == 400
    assert "top_n must be between 5 and 200" in response.json()["detail"]


def test_player_trend_endpoint_rejects_unknown_player(client_factory, app_caches) -> None:
    with client_factory(app_caches) as client:
        response = client.get(
            "/api/player-trend",
            params={"player_name": "Not A Real Player", "position": "QB", "stat": "Pass Yds"},
        )

    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_player_trend_endpoint_requires_stat(client_factory, app_caches) -> None:
    with client_factory(app_caches) as client:
        response = client.get(
            "/api/player-trend",
            params={"player_name": "Patrick Mahomes", "position": "QB", "stat": "   "},
        )

    assert response.status_code == 400
    assert "stat is required" in response.json()["detail"]


def test_missing_statistics_cache_maps_to_503(client_factory, app_caches) -> None:
    empty_stats_caches = deepcopy(app_caches)
    empty_stats_caches[constants.CACHE["STATISTICS"]] = {}

    with client_factory(empty_stats_caches) as client:
        response = client.get("/api/search", params={"q": "maho"})

    assert response.status_code == 503
    assert "not loaded" in response.json()["detail"].lower()

def test_app_info_uses_max_stat_columns_across_all_positions(client_factory, app_caches) -> None:
    custom_caches = deepcopy(app_caches)
    custom_caches[constants.CACHE["STATISTICS"]][constants.STATS["BY_YEAR"]] = {
        2025: {
            "WR": pd.DataFrame({"Rec": [109], "Rec Yds": [1462]}, index=pd.Index(["JaMarr Chase"], name="player_display_name")),
            "QB": pd.DataFrame({"Comp": [401],
                                "Att": [590],
                                "Pass Yds": [4280],
                                "Pass TD": [32],
                                "INT": [11]}, index=pd.Index(["Patrick Mahomes"], name="player_display_name")),
        }
    }

    with client_factory(custom_caches) as client:
        response = client.get("/api/app-info")

    assert response.status_code == 200
    payload = response.json()
    assert payload["stat_columns"] == 5

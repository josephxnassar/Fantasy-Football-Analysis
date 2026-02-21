from copy import deepcopy

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
    assert {"Patrick Mahomes", "JaMarr Chase"}.issubset(names)
    assert "Pass Yds" in payload["stat_columns"]
    assert "Rec Yds" in payload["stat_columns"]

def test_missing_statistics_cache_maps_to_503(client_factory, app_caches) -> None:
    empty_stats_caches = deepcopy(app_caches)
    empty_stats_caches[constants.CACHE["STATISTICS"]] = {}

    with client_factory(empty_stats_caches) as client:
        response = client.get("/api/search", params={"q": "maho"})

    assert response.status_code == 503
    assert "not loaded" in response.json()["detail"].lower()

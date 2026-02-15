from urllib.parse import quote

import pytest

pytestmark = pytest.mark.e2e


def test_user_can_discover_player_then_open_team_views(client_factory, app_caches) -> None:
    with client_factory(app_caches) as client:
        rankings_response = client.get("/api/rankings", params={"format": "redraft", "position": "QB"})
        assert rankings_response.status_code == 200

        qb_players = rankings_response.json()["rankings"]["QB"]
        selected_player = qb_players[0]["name"]

        search_query = selected_player.split()[0][:3]
        search_response = client.get("/api/search", params={"q": search_query})
        assert search_response.status_code == 200
        assert any(result["name"] == selected_player for result in search_response.json()["results"])

        player_response = client.get(f"/api/player/{quote(selected_player)}")
        assert player_response.status_code == 200
        player_payload = player_response.json()
        team = player_payload["team"]

        schedule_response = client.get(f"/api/schedules/{team}", params={"season": 2025})
        depth_response = client.get(f"/api/depth-charts/{team}")
        assert schedule_response.status_code == 200
        assert depth_response.status_code == 200

        depth_payload = depth_response.json()
        assert any(row["starter"] == selected_player for row in depth_payload["depth_chart"])


def test_player_profile_and_chart_data_are_consistent_for_same_season(client_factory, app_caches) -> None:
    with client_factory(app_caches) as client:
        player_response = client.get("/api/player/Patrick%20Mahomes", params={"season": 2025})
        chart_response = client.get("/api/chart-data", params={"position": "QB", "season": 2025})

    assert player_response.status_code == 200
    assert chart_response.status_code == 200

    player_payload = player_response.json()
    chart_payload = chart_response.json()
    chart_player = next(player for player in chart_payload["players"] if player["name"] == "Patrick Mahomes")

    assert player_payload["stats"]["Pass Yds"] == chart_player["stats"]["Pass Yds"]
    assert player_payload["stats"]["Pass TD"] == chart_player["stats"]["Pass TD"]
    assert chart_payload["season"] == 2025

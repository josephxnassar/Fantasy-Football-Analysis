"""Unit tests for StatisticsSourceLoader._build_import_loader_map."""

from unittest.mock import MagicMock

from backend.statistics.loaders import StatisticsSourceLoader

# normal

def test_build_import_loader_map_returns_expected_source_keys(statistics_loader: StatisticsSourceLoader) -> None:
    """_build_import_loader_map returns the expected import source keys."""
    import_loader_map = statistics_loader._build_import_loader_map({"staffma01": "00-0034860"})

    assert set(import_loader_map) == {
        "rosters",
        "player_weekly",
        "player_seasonal",
        "ff_opp_weekly",
        "nextgen_pass_weekly",
        "nextgen_rec_weekly",
        "nextgen_rush_weekly",
        "pfr_pass_weekly",
        "pfr_rush_weekly",
        "pfr_rec_weekly",
        "pfr_pass_season",
        "pfr_rush_season",
        "pfr_rec_season",
        "snap_counts",
    }

# edge

def test_build_import_loader_map_passes_ff_playerid_map_to_lambda_loaders(statistics_loader: StatisticsSourceLoader) -> None:
    """_build_import_loader_map wires the PFR and snap lambda loaders with the id map."""
    ff_playerid_map = {"staffma01": "00-0034860"}
    pfr_pass_weekly_mock = MagicMock(return_value="pass_weekly")
    pfr_rush_weekly_mock = MagicMock(return_value="rush_weekly")
    pfr_rec_weekly_mock = MagicMock(return_value="rec_weekly")
    pfr_pass_season_mock = MagicMock(return_value="pass_season")
    pfr_rush_season_mock = MagicMock(return_value="rush_season")
    pfr_rec_season_mock = MagicMock(return_value="rec_season")
    snap_counts_mock = MagicMock(return_value="snap_counts")

    statistics_loader.load_pfr_adv_pass_weekly = pfr_pass_weekly_mock
    statistics_loader.load_pfr_adv_rush_weekly = pfr_rush_weekly_mock
    statistics_loader.load_pfr_adv_rec_weekly = pfr_rec_weekly_mock
    statistics_loader.load_pfr_adv_pass_season = pfr_pass_season_mock
    statistics_loader.load_pfr_adv_rush_season = pfr_rush_season_mock
    statistics_loader.load_pfr_adv_rec_season = pfr_rec_season_mock
    statistics_loader.load_snap_counts = snap_counts_mock

    import_loader_map = statistics_loader._build_import_loader_map(ff_playerid_map)

    assert import_loader_map["pfr_pass_weekly"]() == "pass_weekly"
    assert import_loader_map["pfr_rush_weekly"]() == "rush_weekly"
    assert import_loader_map["pfr_rec_weekly"]() == "rec_weekly"
    assert import_loader_map["pfr_pass_season"]() == "pass_season"
    assert import_loader_map["pfr_rush_season"]() == "rush_season"
    assert import_loader_map["pfr_rec_season"]() == "rec_season"
    assert import_loader_map["snap_counts"]() == "snap_counts"

    pfr_pass_weekly_mock.assert_called_once_with(ff_playerid_map)
    pfr_rush_weekly_mock.assert_called_once_with(ff_playerid_map)
    pfr_rec_weekly_mock.assert_called_once_with(ff_playerid_map)
    pfr_pass_season_mock.assert_called_once_with(ff_playerid_map)
    pfr_rush_season_mock.assert_called_once_with(ff_playerid_map)
    pfr_rec_season_mock.assert_called_once_with(ff_playerid_map)
    snap_counts_mock.assert_called_once_with(ff_playerid_map)

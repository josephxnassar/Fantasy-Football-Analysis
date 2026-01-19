import pandas as pd

from pytest_mock import MockerFixture

from backend.statistics.statistics import Statistics


def test_load_key_sets_mappings_and_metadata(mocker: MockerFixture):
    rosters = pd.DataFrame({
        "player_id": ["00-0031234", "00-0035678", "00-0099999"],
        "player_name": ["Patrick Mahomes", "Travis Kelce", "Retired Guy"],
        "depth_chart_position": ["QB", "TE", "WR"],
        "age": [29, 35, 40],
        "season": [2025, 2025, 2025],
        "status": ["ACT", "ACT", "RET"],
    })

    seasonal = pd.DataFrame({
        "player_id": ["00-0031234"],
        "season": [2025],
        "season_type": ["REG"],
        "fantasy_points_ppr": [10],
    })

    mock_rosters = mocker.patch("backend.statistics.statistics.nfl.import_seasonal_rosters", return_value=rosters)
    mocker.patch("backend.statistics.statistics.nfl.import_seasonal_data", return_value=seasonal)

    stats = Statistics([2025])

    mock_rosters.assert_called_once()
    assert stats.id_to_player == {
        "00-0031234": ("Patrick Mahomes", "QB"),
        "00-0035678": ("Travis Kelce", "TE"),
        "00-0099999": ("Retired Guy", "WR"),
    }
    assert stats.player_ages == {"Patrick Mahomes": 29, "Travis Kelce": 35, "Retired Guy": 40}
    assert stats.eligible_players == {"Patrick Mahomes", "Travis Kelce"}


def test_compute_averaged_data(mocker: MockerFixture):
    raw = pd.DataFrame({
        "player_id": ["p1", "p1", "p2"],
        "season": [2024, 2025, 2025],
        "season_type": ["REG", "REG", "REG"],
        "fantasy_points_ppr": [10.0, 20.0, 30.0],
        "completions": [100, 200, 50],
    })

    mocker.patch(
        "backend.statistics.statistics.nfl.import_seasonal_rosters",
        return_value=pd.DataFrame({
            "player_id": ["p1", "p2"],
            "player_name": ["One", "Two"],
            "depth_chart_position": ["QB", "RB"],
            "age": [25, 26],
            "season": [2025, 2025],
            "status": ["ACT", "ACT"],
        }),
    )
    mocker.patch("backend.statistics.statistics.Statistics._load", return_value=raw)

    stats = Statistics([2024, 2025])

    expected = pd.DataFrame({
        "player_id": ["p1", "p2"],
        "fantasy_points_ppr": [15.0, 30.0],
        "completions": [150.0, 50.0],
    })

    pd.testing.assert_frame_equal(stats.seasonal_data.reset_index(drop=True), expected)
    assert set(stats.seasonal_data_by_year.keys()) == {2024, 2025}


def test_partition_data_creates_position_frames():
    stats = Statistics.__new__(Statistics)
    stats.id_to_player = {
        "id1": ("Player QB", "QB"),
        "id2": ("Player RB", "RB"),
    }

    data = pd.DataFrame({
        "player_id": ["id1", "id2"],
        "fantasy_points_ppr": [10, 20],
    })

    result = stats._partition_data(data)

    assert set(result.keys()) == {"QB", "RB"}
    qb_df = result["QB"]
    assert qb_df.index.name == "QB"
    assert "player_name" not in qb_df.columns
    assert qb_df.loc["Player QB", "fantasy_points_ppr"] == 10


def test_filter_df_drops_sparse_columns():
    df = pd.DataFrame({
        "keep": [1, 1, 1, 0, 1, 1, 1, 1, 1, 1],
        "drop": [1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    })

    stats = Statistics.__new__(Statistics)
    filtered = stats._filter_df(df)
    assert list(filtered.columns) == ["keep"]


def test_create_ratings_uses_regression(mocker: MockerFixture):
    df = pd.DataFrame({
        "fantasy_points": [100, 150],
        "fantasy_points_ppr": [110, 160],
        "yards": [3000, 3500],
    })

    mock_instance = mocker.Mock()
    mock_instance.fit.return_value = mock_instance
    mock_instance.get_ratings.return_value = pd.DataFrame({"rating": [0.9, 0.8]})

    mock_regression = mocker.patch("backend.statistics.statistics.Regression", return_value=mock_instance)

    stats = Statistics.__new__(Statistics)
    result = stats._create_ratings(df, "ridge")

    mock_regression.assert_called_once()
    args, kwargs = mock_regression.call_args
    assert kwargs == {}
    assert args[0].equals(df.drop(columns=["fantasy_points", "fantasy_points_ppr"]))
    assert args[1].equals(df["fantasy_points_ppr"])
    assert args[2] == "ridge"
    mock_instance.fit.assert_called_once()
    mock_instance.get_ratings.assert_called_once()
    pd.testing.assert_frame_equal(result, mock_instance.get_ratings.return_value)


def test_run_builds_cache_structure(mocker: MockerFixture):
    stats = Statistics.__new__(Statistics)
    stats.ratings_method = "ridge"
    stats.seasons = [2024]
    stats.seasonal_data = pd.DataFrame()
    stats.seasonal_data_by_year = {2024: pd.DataFrame()}
    stats.player_ages = {}
    stats.eligible_players = set()

    ratings_df = pd.DataFrame({"Rating": [1.0]}, index=["Player A"])
    renamed_df = pd.DataFrame({"Rating": [1.0]}, index=["Player A"])

    mock_partition = mocker.patch(
        "backend.statistics.statistics.Statistics._partition_data",
        side_effect=[{"QB": pd.DataFrame({"fantasy_points_ppr": [10]}, index=["Player A"])},
                     {"QB": pd.DataFrame({"fantasy_points_ppr": [10]}, index=["Player A"])}],
    )
    mock_filter = mocker.patch("backend.statistics.statistics.Statistics._filter_df", return_value=pd.DataFrame({"fantasy_points_ppr": [10]}, index=["Player A"]))
    mock_create = mocker.patch("backend.statistics.statistics.Statistics._create_ratings", return_value=ratings_df)
    mock_rename = mocker.patch("backend.statistics.statistics.Statistics._rename_columns", return_value=renamed_df)

    captured_cache = {}
    stats.set_cache = lambda val: captured_cache.update(val)

    stats.run()

    assert captured_cache["averaged"] == {"QB": renamed_df}
    assert captured_cache["by_year"] == {2024: {"QB": renamed_df}}
    assert captured_cache["available_seasons"] == [2024]
    mock_partition.assert_called()
    mock_filter.assert_called()
    mock_create.assert_called()
    mock_rename.assert_called()
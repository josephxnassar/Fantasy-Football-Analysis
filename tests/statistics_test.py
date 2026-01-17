import pandas as pd

from pytest_mock import MockerFixture

from backend.statistics.statistics import Statistics

def test_load_key(mocker: MockerFixture):
    df = pd.DataFrame({"player_id":            ["00-0031234",      "00-0035678"  ],
                       "player_name":          ["Patrick Mahomes", "Travis Kelce"],
                       "depth_chart_position": ["QB",              "TE"          ]})
    
    mock_key = mocker.patch("backend.statistics.statistics.nfl.import_seasonal_rosters", return_value = df)
    mocker.patch("backend.statistics.statistics.nfl.import_seasonal_data")
    
    stats = Statistics([2024], ["ridge"])
    mock_key.assert_called_once()
    assert stats.id_to_player == {"00-0031234": ("Patrick Mahomes", "QB"),
                                  "00-0035678": ("Travis Kelce",    "TE")}

def test_load_data(mocker: MockerFixture):
    df = pd.DataFrame({'player_id':   ['12345', '67890'], 'season':      [2024, 2024],
                       'season_type': ['REG',   'REG'  ], 'completions': [300,  275 ]})
    
    mocker.patch("backend.statistics.statistics.nfl.import_seasonal_rosters")
    mock_load_data = mocker.patch("backend.statistics.statistics.Statistics._load", return_value = df)

    stats = Statistics([2024], ["ridge"])
    mock_load_data.assert_called_once()
    pd.testing.assert_frame_equal(stats.seasonal_data, df)

def test_partition():
    stats = Statistics.__new__(Statistics)
    stats.seasons = [2024]

    stats.key = {'id1': ('Player QB', 'QB'),
                 'id2': ('Player RB', 'RB'),
                 'id3': ('Player WR', 'WR'),
                 'id4': ('Player TE', 'TE')}

    stats.seasonal_data = pd.DataFrame({'player_id':          ['id1', 'id2', 'id3', 'id4'],
                                        'completions':        [ 10,    20,    30,    40  ],
                                        'yards':              [ 100,   200,   300,   400 ],
                                        'fantasy_points_ppr': [ 15,    25,    35,    45  ]})

    result = stats._partition()
    
    for pos, df in result.items():
        assert df.index.name == pos
        assert "player_name" not in df.columns
        for player_name in df.index:
            matched = any(player_name == value[0] for value in stats.key.values())
            assert matched

def test_filter_df():
    df = pd.DataFrame({'a': [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                       'b': [1, 1, 1, 1, 1, 0, 0, 0, 0, 0],
                       'c': [1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                       'd': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]})
    
    stats = Statistics.__new__(Statistics)
    assert list(stats._filter_df(df).columns) == ['a', 'b']
    
def test_create_ratings(mocker: MockerFixture):
    df = pd.DataFrame({'fantasy_points':     [100,  150,  120 ],
                       'fantasy_points_ppr': [110,  160,  130 ],
                       'yards':              [3000, 3500, 3200],
                       'touchdowns':         [20,   25,   22  ]})

    mock_instance = mocker.Mock()
    mock_instance.fit.return_value = mock_instance
    mock_instance.get_ratings.return_value = pd.DataFrame({'player': ['Player A', 'Player B', 'Player C'],
                                                           'rating': [ 0.9,        0.85,       0.8      ]})

    mock_regression = mocker.patch("backend.statistics.statistics.Regression", return_value = mock_instance)

    stats = Statistics.__new__(Statistics)
    result = stats._create_ratings(df, "ridge")

    mock_regression.assert_called_once()
    args, kwargs = mock_regression.call_args
    assert kwargs == {}
    assert args[2] == "ridge"
    mock_instance.fit.assert_called_once()
    mock_instance.get_ratings.assert_called_once()

    expected = pd.DataFrame({'player': ['Player A', 'Player B', 'Player C'],
                             'rating': [ 0.9,        0.85,       0.8]})

    pd.testing.assert_frame_equal(result.reset_index(drop=True), expected)

def test_run(mocker: MockerFixture):
    df = pd.DataFrame({'fantasy_points':     [100,  150,  120],
                       'fantasy_points_ppr': [110,  160,  130],
                       'yards':              [3000, 3500, 3200]})

    fake_partition = {"QB": df, "RB": df}

    mock_filtered_df = pd.DataFrame({'fantasy_points':     [100, 150],
                                     'fantasy_points_ppr': [110, 160],
                                     'yards':              [3000, 3500]})

    mock_ratings_df = pd.DataFrame({'player': ['Player A', 'Player B'],
                                    'rating': [0.95, 0.90]})

    mock_partition = mocker.patch("backend.statistics.statistics.Statistics._partition", return_value = fake_partition)
    mock_filter_df = mocker.patch("backend.statistics.statistics.Statistics._filter_df", return_value = mock_filtered_df)
    mock_create_ratings = mocker.patch("backend.statistics.statistics.Statistics._create_ratings", return_value = mock_ratings_df)

    stats = Statistics.__new__(Statistics)
    stats.ratings_method = "ridge"
    stats.set_cache = lambda val: setattr(stats, "cache", val)

    stats.run()

    expected = {"QB": mock_ratings_df, "RB": mock_ratings_df}

    for pos in expected:
        pd.testing.assert_frame_equal(stats.cache[pos], expected[pos])

    mock_partition.assert_called_once()
    assert mock_filter_df.call_count == 2
    assert mock_create_ratings.call_count == 2
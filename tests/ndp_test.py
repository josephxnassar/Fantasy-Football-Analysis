import pandas as pd

from pytest_mock import MockerFixture

from backend.depth_chart.ndp import NDPDepthChart

def test_load(mocker: MockerFixture):
    df = pd.DataFrame({"week":          [ 1,         1        ],
                       "formation":     ["Offense", "Offense" ],
                       "football_name": ["Noah",    "Patrick" ],
                       "last_name":     ["Gray",    "Mahomes" ],
                       "club_code":     ["KC",      "KC"      ],
                       "depth_team":    [ 2,         1        ],
                       "position":      ["TE",      "QB"      ]})
    
    mock_depth = mocker.patch("source.depth_chart.ndp.nfl.import_depth_charts", return_value = df)

    expected_df = pd.DataFrame({"club_code":  ["KC",              "KC"           ],
                                "depth_team": [ 1,                 2             ],
                                "position":   ["QB",              "TE"           ],
                                "full_name":  ["Patrick Mahomes", "Noah Gray"    ]})

    ndp = NDPDepthChart([2024])
    mock_depth.assert_called_once()
    pd.testing.assert_frame_equal(ndp.master_depth_chart.reset_index(drop=True), expected_df)

def test_group_players_by_position():
    df = pd.DataFrame({"club_code":  ["KC",              "KC"           ],
                       "depth_team": [ 1,                 2             ],
                       "position":   ["QB",              "TE"           ],
                       "full_name":  ["Patrick Mahomes", "Noah Gray"    ]})
    
    ndp = NDPDepthChart.__new__(NDPDepthChart)
    
    position_players = {"QB": ["Patrick Mahomes"], "TE": ["Noah Gray"]}
    assert ndp._group_players_by_position(df) == position_players

def test_build_position_rows():
    position_players = {"QB": ["Patrick Mahomes"], "RB": ["Isiah Pacheco"], "WR": ["Rashee Rice"], "TE": ["Travis Kelce"]}

    ndp = NDPDepthChart.__new__(NDPDepthChart)

    expected = [{'Position': 'QB', 'Starter': 'Patrick Mahomes', '2nd': None, '3rd': None}, 
                {'Position': 'RB', 'Starter': 'Isiah Pacheco',   '2nd': None, '3rd': None},
                {'Position': 'WR', 'Starter': 'Rashee Rice',     '2nd': None, '3rd': None},
                {'Position': 'TE', 'Starter': 'Travis Kelce',    '2nd': None, '3rd': None}]
    
    assert ndp._build_position_rows(position_players) == expected

def test_run(mocker: MockerFixture):
    df = pd.DataFrame({"club_code":  ["KC",              "KC"           ],
                       "depth_team": [ 1,                 2             ],
                       "position":   ["QB",              "TE"           ],
                       "full_name":  ["Patrick Mahomes", "Noah Gray"    ]})
    
    rows = [{'Position': 'QB', 'Starter': 'Patrick Mahomes', '2nd': None, '3rd': None},
            {'Position': 'TE', 'Starter': 'Noah Gray',       '2nd': None, '3rd': None},
            {'Position': 'RB', 'Starter':  None,             '2nd': None, '3rd': None},
            {'Position': 'WR', 'Starter':  None,             '2nd': None, '3rd': None}]

    ndp = NDPDepthChart.__new__(NDPDepthChart)
    ndp.master_depth_chart = df

    ndp._group_players_by_position = mocker.Mock(return_value = {"QB": ["Patrick Mahomes"], "TE": ["Noah Gray"]}) # Something was messing up with groupby
    ndp._build_position_rows = mocker.Mock(return_value = rows)

    expected = pd.DataFrame([{'Position': 'QB', 'Starter': 'Patrick Mahomes', '2nd': None, '3rd': None},
                             {'Position': 'TE', 'Starter': 'Noah Gray',       '2nd': None, '3rd': None},
                             {'Position': 'RB', 'Starter':  None,             '2nd': None, '3rd': None},
                             {'Position': 'WR', 'Starter':  None,             '2nd': None, '3rd': None}]).set_index("Position").rename_axis("KC")

    ndp.run()

    result = ndp.cache
    
    pd.testing.assert_frame_equal(result["KC"], expected)
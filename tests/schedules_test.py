import pandas as pd

from pytest_mock import MockerFixture

from backend.schedules.schedules import Schedules

def test_load(mocker):
    df = pd.DataFrame({'game_type': ['REG', 'REG'],
                       'week':      [ 1,     2   ],
                       'away_team': ['NYG', 'DAL'],
                       'home_team': ['PHI', 'WSH']})
    
    mock_schedule = mocker.patch("backend.schedules.schedules.nfl.import_schedules", return_value = df)
    
    sched = Schedules([2024])
    mock_schedule.assert_called_once()
    pd.testing.assert_frame_equal(sched.master_schedule, df.drop(columns=['game_type']))

def test_fill_bye_weeks(mocker: MockerFixture):
    df = pd.DataFrame({'Opponent': ['DAL', 'MIA', 'BUF', 'NYJ']}, index = pd.Index([1, 2, 4, 5], name = 'week'))
        
    sched = Schedules.__new__(Schedules)
    sched.weeks = 5

    result_df = pd.DataFrame(['DAL', 'MIA', 'BYE', 'BUF', 'NYJ'], index=pd.Index([1, 2, 3, 4, 5], name = "SEA"), columns=['Opponent'])
    pd.testing.assert_frame_equal(sched._fill_bye_weeks(df, "SEA"), result_df)

def test_create_combined_schedule_only(mocker: MockerFixture):
    df = pd.DataFrame({'week':      [ 1,     1,     2,     2   ],
                       'away_team': ['NYG', 'DAL', 'PHI', 'NYG'],
                       'home_team': ['PHI', 'WAS', 'WAS', 'DAL'],
                       'game_type': ['REG', 'REG', 'REG', 'REG']})
    
    mocker.patch("backend.schedules.schedules.Schedules._load", return_value = df.drop(columns='game_type'))

    sched = Schedules([2024])
    result = sched._create_combined_schedule()

    expected = pd.DataFrame({'week':     [ 1,     1,     2,     2,     1,     1,     2,     2   ],
                             'Opponent': ['NYG', 'DAL', 'PHI', 'NYG', 'PHI', 'WAS', 'WAS', 'DAL'],
                             'Team':     ['PHI', 'WAS', 'WAS', 'DAL', 'NYG', 'DAL', 'PHI', 'NYG']})
    
    pd.testing.assert_frame_equal(result.sort_values(['week', 'Team', 'Opponent']).reset_index(drop=True), expected.sort_values(['week', 'Team', 'Opponent']).reset_index(drop=True))

def test_run(mocker: MockerFixture):
    df = pd.DataFrame({'week':     [ 1,       2,       1,       2     ],
                       'Opponent': ['Team1', 'Team2', 'Team3', 'Team4'],
                       'Team':     ['A',     'A',     'B',     'B'    ]})
    
    filled_df = pd.DataFrame({'Opponent': ['Team1', 'Team2']}, index=pd.Index([1, 2], name='Team'))
    
    mocker.patch("backend.schedules.schedules.Schedules._load", return_value = pd.DataFrame())
    mock_combined = mocker.patch("backend.schedules.schedules.Schedules._create_combined_schedule", return_value = df)
    mock_bye = mocker.patch("backend.schedules.schedules.Schedules._fill_bye_weeks", return_value = filled_df)
    mock_cache = mocker.patch("backend.schedules.schedules.Schedules.set_cache")

    sched = Schedules([2024])
    sched.run()

    assert mock_combined.called
    assert mock_bye.call_count == 2
    assert mock_cache.called

    cached = mock_cache.call_args[0][0]
    assert cached.keys() == {'A', 'B'}
    for val in cached.values():
        pd.testing.assert_frame_equal(val, filled_df)
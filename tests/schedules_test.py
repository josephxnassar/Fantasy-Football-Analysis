import pandas as pd

from pytest_mock import MockerFixture

from source.schedules.schedules import Schedules

def test_load_data(mocker):
    df = pd.DataFrame({'game_type': ['REG', 'REG'],
                       'week':      [ 1,     2   ],
                       'away_team': ['NYG', 'DAL'],
                       'home_team': ['PHI', 'WAS']})
    
    mock_schedule = mocker.patch("source.schedules.schedules.nfl.import_schedules", return_value = df)
    
    sched = Schedules([2024])
    mock_schedule.assert_called_once()
    pd.testing.assert_frame_equal(sched.master_schedule, df.drop(columns=['game_type']))

def test_fill_bye_weeks(mocker: MockerFixture):
    df = pd.DataFrame({'Opponent': ['DAL', 'MIA', 'BUF', 'NYJ']}, index = pd.Index([1, 2, 4, 5], name = 'week'))
        
    sched = Schedules.__new__(Schedules)
    sched.weeks = 5

    result_df = pd.DataFrame(['DAL', 'MIA', 'BYE', 'BUF', 'NYJ'], index=pd.Index([1, 2, 3, 4, 5], name = "SEA"), columns=['Opponent'])
    pd.testing.assert_frame_equal(sched._fill_bye_weeks(df, "SEA"), result_df)

def test_split_schedules_by_team(mocker: MockerFixture):
    df = pd.DataFrame({'week':      [ 1,     1,     2,     2   ],
                       'away_team': ['NYG', 'DAL', 'PHI', 'NYG'],
                       'home_team': ['PHI', 'WAS', 'WAS', 'DAL'],
                       'game_type': ['REG', 'REG', 'REG', 'REG']})
    
    filled_df = pd.DataFrame({'Opponent': ['Team1', 'Team2']}, index=pd.Index([1, 2], name='Team'))
    
    mocker.patch("source.schedules.schedules.Schedules._load", return_value = df.drop(columns='game_type'))
    mock_bye = mocker.patch("source.schedules.schedules.Schedules._fill_bye_weeks", return_value = filled_df)

    sched = Schedules([2024])
    result = sched._split_schedules_by_team()
    expected_teams = {'PHI', 'WAS', 'NYG', 'DAL'}

    assert result.keys() == expected_teams
    assert mock_bye.call_count == len(expected_teams)
    for team_df in result.values():
        pd.testing.assert_frame_equal(team_df, filled_df)
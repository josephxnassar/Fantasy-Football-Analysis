import logging

import pandas as pd
import nfl_data_py as nfl

from source.base_source import BaseSource

logger = logging.getLogger(__name__)

class Schedules(BaseSource):
    def __init__(self, seasons: list[int]):
        super().__init__(seasons)
        self.master_schedule = self._load()

    def _load(self) -> pd.DataFrame:
        try:
            df = nfl.import_schedules(self.seasons)
            self.weeks = df['week'].nunique()
            return df[df['game_type'] == 'REG'][['week', 'away_team', 'home_team']].replace({"LA":"LAR", "WAS":"WSH"})
        except Exception as e:
            logger.error(f"Error loading schedules: {e}")
            raise

    def _fill_bye_weeks(self, df: pd.DataFrame, team: str) -> pd.DataFrame:
        try:
            all_weeks = pd.Index(range(1, self.weeks + 1), name=team)
            return df.reindex(all_weeks, fill_value="BYE").sort_index()
        except Exception as e:
            logger.error(f"Error filling team '{team}' bye weeks: {e}")
            raise

    def _create_combined_schedule(self) -> pd.DataFrame:
        try:
            home_games = self.master_schedule.rename(columns={'away_team': 'Opponent', 'home_team': 'Team'})
            away_games = self.master_schedule.rename(columns={'home_team': 'Opponent', 'away_team': 'Team'})
            return pd.concat([home_games, away_games], ignore_index=True)
        except Exception as e:
            logger.error(f"Error creating combined schedule: {e}")
            raise

    def run(self) -> None:
        schedules = {}
        for team, group in self._create_combined_schedule().groupby('Team'):
            try:
                schedules[team] = self._fill_bye_weeks(group.drop(columns='Team').set_index('week').sort_index().rename_axis(team), team)
            except Exception as e:
                logger.error(f"Failed to process team '{team}': {e}")
        self.set_cache(schedules)

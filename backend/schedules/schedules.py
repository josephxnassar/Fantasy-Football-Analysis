"""NFL schedules processing from nflreadpy"""

import logging
from typing import Dict, List

import nflreadpy as nfl
import pandas as pd

from backend.base_source import BaseSource
from backend.util.exceptions import DataLoadError, DataProcessingError

logger = logging.getLogger(__name__)

class Schedules(BaseSource):
    """Processes NFL schedules with bye week handling"""
    
    def __init__(self, seasons: List[int]) -> None:
        super().__init__(seasons)
        self.weeks_by_season: Dict[int, int] = {}  # Set by _load()
        self.master_schedule: pd.DataFrame = self._load_schedules()

    def _load_schedules(self) -> pd.DataFrame:
        """Load schedules from nflreadpy"""
        try:
            df = nfl.load_schedules(seasons=self.seasons).to_pandas()
            reg_games = df[df['game_type'] == 'REG'][['season', 'week', 'away_team', 'home_team']].replace({"LA":"LAR", "WAS":"WSH"})
            self.weeks_by_season = reg_games.groupby('season')['week'].nunique().to_dict()
            return reg_games
        except Exception as e:
            logger.error(f"Failed to load schedules: {e}")
            raise DataLoadError(f"Failed to load schedules: {e}", source="Schedules") from e

    def _fill_bye_weeks(self, df: pd.DataFrame, total_weeks: int) -> pd.DataFrame:
        """Fill missing weeks with BYE placeholder"""
        try:
            all_weeks = pd.Index(range(1, total_weeks + 1), name="week")
            return df.reindex(all_weeks, fill_value="BYE").sort_index()
        except Exception as e:
            logger.error(f"Failed to fill bye weeks: {e}")
            raise DataProcessingError(f"Failed to fill bye weeks: {e}", source="Schedules") from e

    def _create_combined_schedule(self) -> pd.DataFrame:
        """Combine home and away games into single schedule"""
        try:
            home_games = self.master_schedule.rename(columns={'away_team': 'opponent', 'home_team': 'team'})
            home_games["home_away"] = "HOME"
            away_games = self.master_schedule.rename(columns={'home_team': 'opponent', 'away_team': 'team'})
            away_games["home_away"] = "AWAY"
            return pd.concat([home_games, away_games], ignore_index=True)
        except Exception as e:
            logger.error(f"Failed to create combined schedule: {e}")
            raise DataProcessingError(f"Failed to create combined schedule: {e}", source="Schedules") from e

    def run(self) -> None:
        """Process schedules for all teams"""
        schedules_by_year: Dict[int, Dict[str, pd.DataFrame]] = {}
        for (season, team), group in self._create_combined_schedule().groupby(['season', 'team']):
            try:
                total_weeks = int(self.weeks_by_season.get(season, 18))
                team_schedule = self._fill_bye_weeks(group.drop(columns=['team', 'season']).set_index('week').sort_index(), total_weeks)
                schedules_by_year.setdefault(int(season), {})[team] = team_schedule
            except Exception as e:
                logger.warning(f"Skipping team '{team}' season '{season}': {e}")
        self.set_cache(schedules_by_year)

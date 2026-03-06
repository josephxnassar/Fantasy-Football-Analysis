"""NFL schedules processing from nflreadpy"""

import logging
from typing import Dict, List

import nflreadpy as nfl
import pandas as pd

from backend.base_source import BaseSource
from backend.util import constants
from backend.util.exceptions import DataLoadError, DataProcessingError

logger = logging.getLogger(__name__)


class Schedules(BaseSource):
    """Processes NFL schedules with bye week handling"""
    
    def __init__(self, seasons: List[int]) -> None:
        super().__init__(seasons)
        self.weeks_by_season: Dict[int, int] = {}
        self.master_schedule: pd.DataFrame = pd.DataFrame()

    def _load_schedules(self) -> pd.DataFrame:
        """Load schedules from nflreadpy"""
        try:
            df = nfl.load_schedules(seasons=self.seasons).to_pandas()
            reg_games = (df[df['game_type'] == 'REG'][['season', 'week', 'away_team', 'home_team', 'away_score', 'home_score']].replace(constants.TEAM_ABBR_NORMALIZATION))
            self.weeks_by_season = reg_games.groupby('season')['week'].nunique().to_dict()
            return reg_games
        except Exception as e:
            logger.error("Failed to load schedules: %s", e)
            raise DataLoadError(f"Failed to load schedules: {e}", source="Schedules") from e

    def _fill_bye_weeks(self, df: pd.DataFrame, total_weeks: int) -> pd.DataFrame:
        """Fill missing weeks with BYE placeholder"""
        try:
            all_weeks = pd.Index(range(1, total_weeks + 1), name="week")
            filled = df.reindex(all_weeks).sort_index()
            filled["opponent"] = filled["opponent"].fillna("BYE")
            if "home_away" in filled.columns:
                filled.loc[filled["opponent"] == "BYE", "home_away"] = None
            return filled
        except Exception as e:
            logger.error("Failed to fill bye weeks: %s", e)
            raise DataProcessingError(f"Failed to fill bye weeks: {e}", source="Schedules") from e

    def _create_combined_schedule(self) -> pd.DataFrame:
        """Combine home and away games into single schedule"""
        try:
            home_games = self.master_schedule.rename(columns={'away_team': 'opponent', 'home_team': 'team'})
            home_games["home_away"] = "HOME"
            home_games["team_score"] = home_games["home_score"]
            home_games["opponent_score"] = home_games["away_score"]

            away_games = self.master_schedule.rename(columns={'home_team': 'opponent', 'away_team': 'team'})
            away_games["home_away"] = "AWAY"
            away_games["team_score"] = away_games["away_score"]
            away_games["opponent_score"] = away_games["home_score"]

            combined = pd.concat([home_games, away_games], ignore_index=True)
            return combined[["season", "week", "team", "opponent", "home_away", "team_score", "opponent_score"]]
        except Exception as e:
            logger.error("Failed to create combined schedule: %s", e)
            raise DataProcessingError(f"Failed to create combined schedule: {e}", source="Schedules") from e

    def run(self) -> None:
        """Process schedules for all teams"""
        self.master_schedule = self._load_schedules()
        schedules_by_year: Dict[int, Dict[str, pd.DataFrame]] = {}
        for (season, team), group in self._create_combined_schedule().groupby(['season', 'team']):
            try:
                total_weeks = int(self.weeks_by_season.get(season, 18))
                team_schedule = self._fill_bye_weeks(group.drop(columns=['team', 'season']).set_index('week').sort_index(), total_weeks)
                schedules_by_year.setdefault(int(season), {})[team] = team_schedule
            except Exception as e:
                logger.warning("Skipping team '%s' season '%s': %s", team, season, e)
        self.set_cache(schedules_by_year)

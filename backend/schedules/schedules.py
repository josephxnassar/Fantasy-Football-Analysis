"""NFL schedules processing from nflreadpy."""

import logging

import nflreadpy as nfl
import pandas as pd

from backend.base_source import BaseSource
from backend.util import constants
from backend.util.exceptions import DataLoadError, DataProcessingError

logger = logging.getLogger(__name__)


class Schedules(BaseSource):
    """Build flat team schedules with bye weeks."""

    def __init__(self, seasons: list[int]) -> None:
        super().__init__(seasons)
        self.weeks_by_season: dict[int, int] = {}

    def _load_schedules(self) -> pd.DataFrame:
        """Load regular-season schedules from nflreadpy."""
        try:
            schedule = nfl.load_schedules(seasons=self.seasons).to_pandas()
            schedule = schedule.loc[schedule["game_type"] == "REG", ["season", "week", "away_team", "home_team", "away_score", "home_score"]].replace(constants.TEAM_ABBR_NORMALIZATION)
            self.weeks_by_season = schedule.groupby("season")["week"].nunique().to_dict()
            return schedule
        except Exception as e:
            logger.error("Failed to load schedules: %s", e)
            raise DataLoadError(f"Failed to load schedules: {e}", source="Schedules") from e

    def _create_combined_schedule(self, schedule: pd.DataFrame) -> pd.DataFrame:
        """Build one team-facing schedule row for each game side."""
        try:
            home_games = schedule.rename(columns={"away_team": "opponent", "home_team": "team"})
            home_games["home_away"] = "HOME"
            home_games["team_score"] = home_games["home_score"]
            home_games["opponent_score"] = home_games["away_score"]

            away_games = schedule.rename(columns={"home_team": "opponent", "away_team": "team"})
            away_games["home_away"] = "AWAY"
            away_games["team_score"] = away_games["away_score"]
            away_games["opponent_score"] = away_games["home_score"]

            combined = pd.concat([home_games, away_games], ignore_index=True)
            return combined[["season", "week", "team", "opponent", "home_away", "team_score", "opponent_score"]]
        except Exception as e:
            logger.error("Failed to create combined schedule: %s", e)
            raise DataProcessingError(f"Failed to create combined schedule: {e}", source="Schedules") from e

    def _fill_bye_weeks(self, schedule: pd.DataFrame, total_weeks: int) -> pd.DataFrame:
        """Fill missing team weeks with a BYE row."""
        try:
            filled = schedule.reindex(pd.Index(range(1, total_weeks + 1), name="week")).sort_index()
            filled["opponent"] = filled["opponent"].fillna("BYE")
            filled.loc[filled["opponent"] == "BYE", "home_away"] = None
            return filled
        except Exception as e:
            logger.error("Failed to fill bye weeks: %s", e)
            raise DataProcessingError(f"Failed to fill bye weeks: {e}", source="Schedules") from e

    def run(self) -> None:
        """Build a flat schedule cache across all requested seasons."""
        schedule = self._load_schedules()
        combined_schedule = self._create_combined_schedule(schedule)

        flat_schedules: list[dict[str, object]] = []
        for season, season_group in combined_schedule.groupby("season", sort=False):
            total_weeks = int(self.weeks_by_season.get(season, 18))
            for team, team_group in season_group.groupby("team", sort=False):
                try:
                    team_schedule = self._fill_bye_weeks(team_group.drop(columns=["season", "team"]).set_index("week").sort_index(), total_weeks)
                    team_rows = team_schedule.reset_index()
                    team_rows["season"] = int(season)
                    team_rows["team"] = str(team)
                    flat_schedules.extend(team_rows[["season", "team", "week", "opponent", "home_away", "team_score", "opponent_score"]].to_dict("records"))
                except Exception as e:
                    logger.warning("Skipping team '%s' season '%s': %s", team, season, e)

        self.set_cache(flat_schedules)

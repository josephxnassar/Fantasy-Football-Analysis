import logging
from collections import defaultdict

import pandas as pd
import nfl_data_py as nfl

from backend.util import constants
from backend.base_source import BaseSource

logger = logging.getLogger(__name__)

class NDPDepthChart(BaseSource):
    def __init__(self, seasons: list):
        super().__init__(seasons)
        self.master_depth_chart = self._load()

    def _load(self) -> pd.DataFrame:
        try:
            dc = nfl.import_depth_charts(self.seasons)
            return dc[(dc['week'] == 1) & (dc['formation'] == 'Offense')].assign(full_name=lambda x: x['football_name'].str.cat(x['last_name'], sep=' ')).sort_values(by=['club_code', 'depth_team', 'position'])[['club_code', 'depth_team', 'position', 'full_name']].replace({"LA":"LAR", "WAS":"WSH"})
        except Exception as e:
            logger.error(f"Error loading depth charts: {e}")
            raise

    def _group_players_by_position(self, group: pd.DataFrame) -> dict[str, list[str]]:
        try:
            position_players = defaultdict(list)
            for _, row in group.iterrows():
                position_players[row['position']].append(row['full_name'])
            return position_players
        except Exception as e:
            logger.error(f"Error grouping players: {e}")
            raise

    def _build_position_rows(self, position_players: dict[str, list[str]]) -> list[dict]:
        try:
            rows = []
            for pos in constants.POSITIONS:
                rows.append({'Position': pos,
                             'Starter':  position_players[pos][0] if len(position_players[pos]) > 0 else None,
                             '2nd':      position_players[pos][1] if len(position_players[pos]) > 1 else None,
                             '3rd':      position_players[pos][2] if len(position_players[pos]) > 2 else None})
            return rows
        except Exception as e:
            logger.error(f"Error building rows: {e}")
            raise

    def run(self) -> None:
        depth_charts = {}
        for team, group in self.master_depth_chart.groupby('club_code'):
            try:
                position_players = self._group_players_by_position(group)
                rows = self._build_position_rows(position_players)
                depth_charts[team] = pd.DataFrame(rows).set_index('Position').rename_axis(team)
            except Exception as e:
                logger.error(f"Failed to process team '{team}': {e}")
        self.set_cache(depth_charts)
    
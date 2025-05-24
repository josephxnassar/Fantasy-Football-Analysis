import logging
from collections import defaultdict

import pandas as pd
import nfl_data_py as nfl

from source import constants
from .ratings import *
from source.base_source import BaseSource


logger = logging.getLogger(__name__)

RATING_METHODS = {"linear": LinearRegression,
                   "ridge": RidgeRegression}

class Statistics(BaseSource):
    def __init__(self, seasons: list, method: str = "ridge"):
        super().__init__(seasons)
        self.ratings_method = method
        self.key = self._load_key()
        self.seasonal_data = self._load()

    def _load_key(self) -> dict:
        try:
            sr = nfl.import_seasonal_rosters(self.seasons, columns=['player_id', 'player_name', 'depth_chart_position'])
            return {row.player_id: (row.player_name, row.depth_chart_position) for row in sr.itertuples(index=False)}
        except Exception as e:
            logger.error(f"Error loading key: {e}")
            raise

    def _load(self) -> pd.DataFrame:
        try:
            sd = nfl.import_seasonal_data(self.seasons)
            return sd.drop(columns=['season', 'season_type']).groupby('player_id').mean().reset_index().dropna()
        except Exception as e:
            logger.error(f"Error loading seasonal data: {e}")
            raise

    def _partition(self) -> dict:
        try:
            cols = ['player_name'] + self.seasonal_data.columns.tolist()[1:]
            position_data = defaultdict(list)
            for _, row in self.seasonal_data.iterrows():
                try:
                    player_name, position = self.key[row.player_id]
                    if position in constants.POSITIONS:
                        position_data[position].append([player_name] + row.tolist()[1:])
                except Exception as e:
                    logger.error(f"Failed to process player_id '{row.player_id}': {e}")
            return {pos: pd.DataFrame(data, columns=cols).set_index('player_name').rename_axis(pos) for pos, data in position_data.items()}
        except Exception as e:
            logger.error(f"Error partitioning data: {e}")
            raise

    def _filter_df(self, df: pd.DataFrame) -> pd.DataFrame:
        try:
            threshold = 0.1 * len(df)
            return df.loc[:, (df != 0).sum() > threshold]
        except Exception as e:
            logger.error(f"Error filtering data: {e}")
            raise

    def _create_ratings(self, df: pd.DataFrame, method: str) -> pd.DataFrame:
        try:
            y = df["fantasy_points_ppr"]
            X = df.drop(columns=["fantasy_points", "fantasy_points_ppr"])
            model = RATING_METHODS[method](X, y)
            model.fit()
            return model.get_ratings()
        except Exception as e:
            logger.error(f"Error creating ratings using '{method}': {e}")
            raise

    def run(self) -> None:
        stats = {}
        for pos, df in self._partition().items():
            try:
                filtered_df = self._filter_df(df)
                stats[pos] = self._create_ratings(filtered_df, self.ratings_method)
            except Exception as e:
                logger.error(f"Failed to process position '{pos}': {e}")
        self.set_cache(stats)

# ═══════════════════ ❖  DATABASE OPERATIONS  ❖ ═══════════════════

    def _get_keys(self) -> list:
        return constants.POSITIONS

    def _get_name(self, key) -> str:
        return f"statistics_{key}_{self.ratings_method}"
    
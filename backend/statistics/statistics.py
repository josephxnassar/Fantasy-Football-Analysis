import logging
from collections import defaultdict

import pandas as pd
import nfl_data_py as nfl

from backend.util import constants
from backend.base_source import BaseSource
from backend.statistics.ratings import *

logger = logging.getLogger(__name__)

# Column name mapping: ugly internal names -> presentable display names
COLUMN_NAME_MAP = {
    # Fantasy Points
    'fantasy_points': 'Fantasy Pts',
    'fantasy_points_ppr': 'PPR Pts',
    
    # Passing Stats
    'completions': 'Comp',
    'attempts': 'Att',
    'passing_yards': 'Pass Yds',
    'passing_tds': 'Pass TD',
    'interceptions': 'INT',
    'sacks': 'Sacks',
    'sack_yards': 'Sack Yds',
    'sack_fumbles': 'Sack Fum',
    'sack_fumbles_lost': 'Sack Fum Lost',
    'passing_air_yards': 'Air Yds',
    'passing_yards_after_catch': 'YAC',
    'passing_first_downs': 'Pass 1st',
    'passing_epa': 'Pass EPA',
    'passing_2pt_conversions': 'Pass 2PT',
    'pacr': 'PACR',
    'dakota': 'Dakota',
    
    # Rushing Stats
    'carries': 'Carries',
    'rushing_yards': 'Rush Yds',
    'rushing_tds': 'Rush TD',
    'rushing_fumbles': 'Rush Fum',
    'rushing_fumbles_lost': 'Rush Fum Lost',
    'rushing_first_downs': 'Rush 1st',
    'rushing_epa': 'Rush EPA',
    'rushing_2pt_conversions': 'Rush 2PT',
    
    # Receiving Stats
    'receptions': 'Rec',
    'targets': 'Tgt',
    'receiving_yards': 'Rec Yds',
    'receiving_tds': 'Rec TD',
    'receiving_fumbles': 'Rec Fum',
    'receiving_fumbles_lost': 'Rec Fum Lost',
    'receiving_air_yards': 'Rec Air Yds',
    'receiving_yards_after_catch': 'Rec YAC',
    'receiving_first_downs': 'Rec 1st',
    'receiving_epa': 'Rec EPA',
    'receiving_2pt_conversions': 'Rec 2PT',
    'racr': 'RACR',
    'target_share': 'Tgt Share',
    'air_yards_share': 'Air Yds Share',
    'wopr': 'WOPR',
    'special_teams_tds': 'ST TD',
    
    # Market Share Metrics
    'tgt_sh': 'Tgt %',
    'ay_sh': 'Air Yds %',
    'yac_sh': 'YAC %',
    'ry_sh': 'Rec Yds %',
    'rtd_sh': 'Rec TD %',
    'rfd_sh': 'Rec 1st %',
    'rtdfd_sh': 'TD+1st %',
    'ppr_sh': 'PPR %',
    
    # Advanced Metrics
    'yptmpa': 'Yds/TmAtt',
    'wopr_x': 'WOPR-X',
    'wopr_y': 'WOPR-Y',
    'dom': 'Dominator',
    'w8dom': 'W8 Dom',
    
    # Keep rating as is
    'rating': 'Rating'
}

class Statistics(BaseSource):
    def __init__(self, seasons: list, method: str = "ridge"):
        super().__init__(seasons)
        self.ratings_method = method
        self.id_to_player = self._load_key()
        self.seasonal_data = self._load()

    def get_keys(self) -> list:
        return constants.POSITIONS

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
                    player_name, position = self.id_to_player[row.player_id]
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
    
    def _rename_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Rename columns to presentable names using the mapping"""
        try:
            # Only rename columns that exist in both the dataframe and the mapping
            rename_map = {col: COLUMN_NAME_MAP[col] for col in df.columns if col in COLUMN_NAME_MAP}
            return df.rename(columns=rename_map)
        except Exception as e:
            logger.error(f"Error renaming columns: {e}")
            raise

    def _create_ratings(self, df: pd.DataFrame, method: str) -> pd.DataFrame:
        try:
            y = df["fantasy_points_ppr"]
            X = df.drop(columns=["fantasy_points", "fantasy_points_ppr"])
            return Regression(X, y, method).fit().get_ratings()
        except Exception as e:
            logger.error(f"Error creating ratings using '{method}': {e}")
            raise

    def run(self) -> None:
        stats = {}
        for pos, df in self._partition().items():
            try:
                filtered_df = self._filter_df(df)
                ratings_df = self._create_ratings(filtered_df, self.ratings_method)
                # Rename columns to presentable names
                stats[pos] = self._rename_columns(ratings_df)
            except Exception as e:
                logger.error(f"Failed to process position '{pos}': {e}")
        self.set_cache(stats)

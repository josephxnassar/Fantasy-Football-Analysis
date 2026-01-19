import logging
from collections import defaultdict
from typing import Dict, List, Tuple

import pandas as pd
import nfl_data_py as nfl

from backend.util import constants
from backend.base_source import BaseSource
from backend.statistics.ratings import *

logger = logging.getLogger(__name__)

class Statistics(BaseSource):
    def __init__(self, seasons: List[int], method: str = "ridge"):
        super().__init__(seasons)
        self.ratings_method: str = method
        self.id_to_player: Dict[str, Tuple[str, str]] = self._load_key()
        self.raw_seasonal_data: pd.DataFrame = self._load()  # Load once via abstract method
        self.seasonal_data: pd.DataFrame = self._compute_averaged_data()  # Averaged data for ratings
        self.seasonal_data_by_year: Dict[int, pd.DataFrame] = self._split_by_year()  # Individual season data

    def get_keys(self) -> List[str]:
        return constants.POSITIONS

    def _load_key(self) -> Dict[str, Tuple[str, str]]:
        try:
            # Load roster for all seasons to map player_id -> (name, position)
            all_rosters = nfl.import_seasonal_rosters(self.seasons)
            
            # Build player mapping from all seasons
            player_dict = {}
            age_tracker: Dict[str, Tuple[int, int]] = {}  # player_name -> (season, age)
            current_season = max(self.seasons)
            
            for row in all_rosters.itertuples(index=False):
                player_dict[row.player_id] = (row.player_name, row.depth_chart_position)
                
                # Track the most recent age we have per player (use latest season available)
                if hasattr(row, 'age') and pd.notna(row.age):
                    try:
                        age_val = int(row.age)
                    except (ValueError, TypeError):
                        age_val = None
                    if age_val and age_val > 0:
                        prev = age_tracker.get(row.player_name)
                        if not prev or row.season > prev[0]:
                            age_tracker[row.player_name] = (row.season, age_val)

            # Collapse tracker to name -> age mapping for dynasty calculations
            self.player_ages = {name: age for name, (_, age) in age_tracker.items()}
            
            logger.info(f"Loaded ages for {len(self.player_ages)} players")
            
            # Build eligibility from the latest season only (filter in-memory)
            latest_roster = all_rosters[all_rosters['season'] == current_season]
            
            self.eligible_players = set()
            for row in latest_roster.itertuples(index=False):
                if pd.notna(row.player_name) and row.status != 'RET':
                    self.eligible_players.add(row.player_name)

            return player_dict
        except Exception as e:
            logger.error(f"Error loading key: {e}")
            raise

    def _load(self) -> pd.DataFrame:
        """Load raw seasonal data once (implements abstract method from BaseSource)"""
        try:
            return nfl.import_seasonal_data(self.seasons)
        except Exception as e:
            logger.error(f"Error loading seasonal data: {e}")
            raise
    
    def _compute_averaged_data(self) -> pd.DataFrame:
        """Compute averaged data from raw seasonal data"""
        try:
            return self.raw_seasonal_data.drop(columns=['season', 'season_type']).groupby('player_id').mean().reset_index().dropna()
        except Exception as e:
            logger.error(f"Error computing averaged data: {e}")
            raise
    
    def _split_by_year(self) -> Dict[int, pd.DataFrame]:
        """Split raw data by year"""
        try:
            seasonal_dict = {}
            for season in self.seasons:
                season_data = self.raw_seasonal_data[self.raw_seasonal_data['season'] == season].copy()
                season_data = season_data.drop(columns=['season', 'season_type']).dropna()
                seasonal_dict[season] = season_data
            return seasonal_dict
        except Exception as e:
            logger.error(f"Error splitting data by year: {e}")
            raise

    def _partition_data(self, data: pd.DataFrame) -> Dict[str, pd.DataFrame]:
        """Partition data by position (works for both averaged and seasonal data)"""
        try:
            cols = ['player_name'] + data.columns.tolist()[1:]
            position_data = defaultdict(list)
            for _, row in data.iterrows():
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
            rename_map = {col: constants.COLUMN_NAME_MAP[col] for col in df.columns if col in constants.COLUMN_NAME_MAP}
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
        # Process averaged data with ratings
        stats = {}
        for pos, df in self._partition_data(self.seasonal_data).items():
            try:
                filtered_df = self._filter_df(df)
                ratings_df = self._create_ratings(filtered_df, self.ratings_method)
                stats[pos] = self._rename_columns(ratings_df)
            except Exception as e:
                logger.error(f"Failed to process position '{pos}': {e}")
        
        # Process individual season data (no ratings, just renamed columns)
        stats_by_year = {}
        for season, season_data in self.seasonal_data_by_year.items():
            season_stats = {}
            for pos, df in self._partition_data(season_data).items():
                try:
                    season_stats[pos] = self._rename_columns(df)
                except Exception as e:
                    logger.error(f"Failed to process position '{pos}' for season {season}: {e}")
            stats_by_year[season] = season_stats
        
        # Store both in cache
        self.set_cache({
            'averaged': stats,
            'by_year': stats_by_year,
            'available_seasons': self.seasons,
            'eligible_players': getattr(self, 'eligible_players', set()),
            'player_ages': self.player_ages
        })

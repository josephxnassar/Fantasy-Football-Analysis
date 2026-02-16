"""SQLite cache service for Statistics, Schedules, and ESPN depth charts."""

from __future__ import annotations

import logging
from typing import Any, Dict, Iterable, List, Optional

import pandas as pd

from backend.database.DAO.sqlite_dao import SQLiteCacheManager
from backend.util import constants
from backend.util.timing import timed

logger = logging.getLogger(__name__)

class SQLService:
    """Persist and load the three supported cache types."""

    def __init__(self) -> None:
        self.db: SQLiteCacheManager = SQLiteCacheManager()

    @timed("SQLService.has_cached_data")
    def has_cached_data(self) -> bool:
        """Return True when all required cache families exist."""
        tables = set(self.db.list_tables())
        if not tables:
            return False
        return (f"{constants.CACHE['STATISTICS']}_metadata" in tables and f"{constants.CACHE['SCHEDULES']}_metadata" in tables and any(t.startswith(f"{constants.CACHE['DEPTH_CHART']}_") for t in tables))

    @timed("SQLService.save_to_db")
    def save_to_db(self, cache: Dict[str, Any], cls_name: str) -> None:
        """Save one cache object based on its class name."""
        if cache is None:
            logger.warning("No cached data to save - call run() first.")
            return

        if cls_name == constants.CACHE["STATISTICS"]:
            self._save_statistics(cache)
            return
        if cls_name == constants.CACHE["SCHEDULES"]:
            self._save_schedules(cache)
            return
        if cls_name == constants.CACHE["DEPTH_CHART"]:
            self._save_depth_charts(cache)
            return

        logger.warning("Unsupported cache class '%s'; skipping save.", cls_name)

    @timed("SQLService.load_from_db")
    def load_from_db(self, keys: List[str], cls_name: str) -> Dict[str, Any]:
        """Load one cache object based on its class name."""
        if cls_name == constants.CACHE["STATISTICS"]:
            return self._load_statistics()
        if cls_name == constants.CACHE["SCHEDULES"]:
            return self._load_schedules()
        if cls_name == constants.CACHE["DEPTH_CHART"]:
            return self._load_depth_charts(keys)

        logger.warning("Unsupported cache class '%s'; returning empty cache.", cls_name)
        return {}

    @timed("SQLService._save_statistics")
    def _save_statistics(self, cache: Dict[str, Any]) -> None:
        prefix = constants.CACHE["STATISTICS"]

        all_players = cache.get(constants.STATS["ALL_PLAYERS"], [])
        if all_players:
            self.db.save_table(f"{prefix}_{constants.STATS['ALL_PLAYERS']}", pd.DataFrame(all_players), index=False)

        by_year = cache.get(constants.STATS["BY_YEAR"], {})
        for season, position_map in by_year.items():
            if not isinstance(position_map, dict):
                continue
            for position, df in position_map.items():
                self.db.save_table(f"{prefix}_{season}_{position}", df.reset_index(), index=False)

        weekly = cache.get(constants.STATS["PLAYER_WEEKLY_STATS"], {})
        if weekly:
            weekly_rows = [{"player_name": player_name, **week_stats} for player_name, week_list in weekly.items() for week_stats in week_list]
            if weekly_rows:
                self.db.save_table(f"{prefix}_{constants.STATS['PLAYER_WEEKLY_STATS']}", pd.DataFrame(weekly_rows), index=False)

        seasons = cache.get("available_seasons", list(by_year.keys()))
        self._save_season_metadata(prefix, seasons)

    @timed("SQLService._load_statistics")
    def _load_statistics(self) -> Dict[str, Any]:
        prefix = constants.CACHE["STATISTICS"]

        seasons = self._load_season_metadata(prefix)

        all_players_df = self._load_table_safe(f"{prefix}_{constants.STATS['ALL_PLAYERS']}")
        all_players = all_players_df.to_dict("records") if all_players_df is not None and not all_players_df.empty else []

        by_year: Dict[int, Dict[str, pd.DataFrame]] = {}
        for season in seasons:
            season_map: Dict[str, pd.DataFrame] = {}
            for position in constants.POSITIONS:
                df = self._load_table_safe(f"{prefix}_{season}_{position}")
                if df is None or df.empty:
                    continue
                season_map[position] = df.set_index("player_display_name")
            if season_map:
                by_year[int(season)] = season_map

        weekly_df = self._load_table_safe(f"{prefix}_{constants.STATS['PLAYER_WEEKLY_STATS']}")
        weekly_stats: Dict[str, List[Dict[str, Any]]] = {}
        if weekly_df is not None and not weekly_df.empty:
            for rec in weekly_df.to_dict("records"):
                player_name = rec.pop("player_name", None)
                if player_name:
                    weekly_stats.setdefault(player_name, []).append(rec)

        return {"available_seasons": seasons,
                constants.STATS["ALL_PLAYERS"]: all_players,
                constants.STATS["BY_YEAR"]: by_year,
                constants.STATS["PLAYER_WEEKLY_STATS"]: weekly_stats}

    @timed("SQLService._save_schedules")
    def _save_schedules(self, cache: Dict[str, Any]) -> None:
        prefix = constants.CACHE["SCHEDULES"]
        seasons: List[int] = []

        for season, season_map in cache.items():
            if not isinstance(season_map, dict):
                continue
            try:
                seasons.append(int(season))
            except (TypeError, ValueError):
                pass

            for team, df in season_map.items():
                self.db.save_table(f"{prefix}_{season}_{team}", df)

        self._save_season_metadata(prefix, seasons)

    @timed("SQLService._load_schedules")
    def _load_schedules(self) -> Dict[int, Dict[str, pd.DataFrame]]:
        prefix = constants.CACHE["SCHEDULES"]
        seasons = self._load_season_metadata(prefix, fallback=constants.SEASONS)
        nested: Dict[int, Dict[str, pd.DataFrame]] = {}

        for season in seasons:
            season_map: Dict[str, pd.DataFrame] = {}
            for team in constants.TEAMS:
                df = self._load_table_safe(f"{prefix}_{season}_{team}")
                if df is None or df.empty:
                    continue
                index_col = "week" if "week" in df.columns else df.columns[0]
                season_map[team] = df.set_index(index_col)
            if season_map:
                nested[int(season)] = season_map

        return nested

    @timed("SQLService._save_depth_charts")
    def _save_depth_charts(self, cache: Dict[str, Any]) -> None:
        prefix = constants.CACHE["DEPTH_CHART"]
        for team, df in cache.items():
            self.db.save_table(f"{prefix}_{team}", df)

    @timed("SQLService._load_depth_charts")
    def _load_depth_charts(self, keys: List[str]) -> Dict[str, pd.DataFrame]:
        prefix = constants.CACHE["DEPTH_CHART"]
        charts: Dict[str, pd.DataFrame] = {}

        for team in keys:
            df = self._load_table_safe(f"{prefix}_{team}")
            if df is None or df.empty:
                continue
            index_col = team if team in df.columns else df.columns[0]
            charts[team] = df.set_index(index_col)

        return charts

    def _save_season_metadata(self, prefix: str, seasons: Iterable[Any]) -> None:
        clean: List[int] = []
        for value in seasons:
            try:
                clean.append(int(value))
            except (TypeError, ValueError):
                continue
        clean = sorted(set(clean))
        if clean:
            self.db.save_table(f"{prefix}_metadata", pd.DataFrame({"available_seasons": clean}), index=False)

    def _load_season_metadata(self, prefix: str, fallback: Optional[Iterable[Any]] = None) -> List[int]:
        df = self._load_table_safe(f"{prefix}_metadata")
        raw = (df["available_seasons"].tolist() if df is not None and "available_seasons" in df.columns else list(fallback or []))
        seasons: List[int] = []
        for value in raw:
            try:
                seasons.append(int(value))
            except (TypeError, ValueError):
                continue
        return seasons

    def _load_table_safe(self, table_name: str) -> Optional[pd.DataFrame]:
        try:
            return self.db.load_table(table_name)
        except Exception as e:
            if "no such table" in str(e).lower():
                return None
            logger.error("Error loading table '%s': %s", table_name, e)
            return None

    def close(self) -> None:
        self.db.close()

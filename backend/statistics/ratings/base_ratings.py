"""Abstract base class for rating models"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

import pandas as pd

class BaseRatings(ABC):
    """Base class for all rating models"""
    
    def __init__(self, X: pd.DataFrame, y: pd.Series) -> None:
        self.X: pd.DataFrame = X
        self.y: pd.Series = y
        self.model: Any = None

    @abstractmethod
    def fit(self) -> BaseRatings:
        """Train the rating model"""
        pass

    @abstractmethod
    def get_ratings(self) -> pd.DataFrame:
        """Generate ratings from trained model"""
        pass
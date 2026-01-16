from abc import ABC, abstractmethod
import pandas as pd

class BaseRatings(ABC):
    def __init__(self, X: pd.DataFrame, y: pd.Series):
        self.X = X
        self.y = y
        self.model = None

    @abstractmethod
    def fit(self):
        pass

    @abstractmethod
    def get_ratings(self) -> pd.Series:
        pass
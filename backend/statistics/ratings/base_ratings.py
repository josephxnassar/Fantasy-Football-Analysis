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

    def evaluate(self, X_test: pd.DataFrame, y_test: pd.Series) -> float:
        if self.model is None:
            raise RuntimeError("Model has not been trained yet.")
        if hasattr(self.model, "score"):
            return self.model.score(X_test, y_test)
        else:
            raise NotImplementedError("Evaluation not implemented for this model.")
        
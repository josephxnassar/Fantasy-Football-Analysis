import logging
import pandas as pd

from sklearn.linear_model import Ridge
from sklearn.preprocessing import StandardScaler

from backend.statistics.ratings.base_ratings import BaseRatings

logger = logging.getLogger(__name__)

class Regression(BaseRatings):
    def __init__(self, X: pd.DataFrame, y: pd.Series, model_type: str, alpha: float = 1.0):
        super().__init__(X, y)
        self.model_type = model_type.lower()
        self.alpha = alpha
        self.scaler = StandardScaler()

    def fit(self):
        try:
            X_scaled = self.scaler.fit_transform(self.X)

            if self.model_type == "ridge":
                self.model = Ridge(alpha=self.alpha)
            else:
                raise ValueError(f"Unsupported model_type: {self.model_type}. Only 'ridge' is supported.")

            self.model.fit(X_scaled, self.y)
            return self
        except Exception as e:
            logger.error(f"Error training {self.model_type.title()}Regression: {e}")
            raise

    def get_ratings(self) -> pd.DataFrame:
        try:
            X_scaled = self.scaler.transform(self.X)
            self.X['rating'] = pd.Series(self.model.predict(X_scaled), index=self.X.index, name="rating")
            return self.X.sort_values(by='rating', ascending=False)
        except Exception as e:
            logger.error(f"Error calculating ratings: {e}")
            raise
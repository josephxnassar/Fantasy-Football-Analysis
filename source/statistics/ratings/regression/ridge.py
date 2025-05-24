import logging

import pandas as pd

from sklearn.linear_model import Ridge
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

from ..base_ratings import BaseRatings

logger = logging.getLogger(__name__)

class RidgeRegression(BaseRatings):
    def __init__(self, X: pd.DataFrame, y: pd.Series, alpha: float = 1.0):
        super().__init__(X, y)
        self.alpha = alpha
        self.scaler = StandardScaler()

    def fit(self):
        try:
            X_scaled = self.scaler.fit_transform(self.X)
            X_train, _, y_train, _ = train_test_split(X_scaled, self.y, test_size=0.2, shuffle=True)

            self.model = Ridge(alpha=self.alpha)
            self.model.fit(X_train, y_train)
        except Exception as e:
            logger.error(f"Error training RidgeRegression: {e}")
            raise

    def get_ratings(self) -> pd.DataFrame:
        try:
            X_scaled = self.scaler.transform(self.X)
            self.X['rating'] = pd.Series(self.model.predict(X_scaled), index=self.X.index, name="rating")
            return self.X.sort_values(by='rating', ascending=False)
        except Exception as e:
            logger.error(f"Error calculating ratings: {e}")
            raise
        
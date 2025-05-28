import logging
import pandas as pd
from sklearn.linear_model import LinearRegression, Ridge, Lasso
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

from source.statistics.ratings.base_ratings import BaseRatings

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
            X_train, _, y_train, _ = train_test_split(X_scaled, self.y, test_size=0.2, shuffle=True)

            if self.model_type == "linear":
                self.model = LinearRegression()
            elif self.model_type == "ridge":
                self.model = Ridge(alpha=self.alpha)
            elif self.model_type == "lasso":
                self.model = Lasso(alpha=self.alpha)
            else:
                raise ValueError(f"Unsupported model_type: {self.model_type}")

            self.model.fit(X_train, y_train)
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
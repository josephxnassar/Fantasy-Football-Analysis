"""Ridge regression model for player ratings"""

import logging
from typing import cast

import numpy as np
import pandas as pd
from sklearn.linear_model import Ridge
from sklearn.preprocessing import StandardScaler

from backend.statistics.ratings.base_ratings import BaseRatings
from backend.util.exceptions import DataProcessingError

logger = logging.getLogger(__name__)

class Regression(BaseRatings):
    """Ridge regression rating model"""
    
    def __init__(self, X: pd.DataFrame, y: pd.Series, model_type: str, alpha: float = 1.0) -> None:
        """Initialize with features, target, model type, and regularization strength"""
        super().__init__(X, y)
        self.model_type: str = model_type.lower()
        self.alpha: float = alpha
        self.scaler: StandardScaler = StandardScaler()

    def fit(self) -> "Regression":
        """Train the regression model"""
        try:
            X_clean = self.X.dropna(axis=1, how='all')
            X_clean = X_clean.fillna(0)
            
            X_scaled = self.scaler.fit_transform(X_clean)

            if self.model_type == "ridge":
                self.model = Ridge(alpha=self.alpha, random_state=42)
            else:
                raise ValueError(f"Unsupported model_type: {self.model_type}. Only 'ridge' is supported.")

            self.model.fit(X_scaled, self.y)
            self.X_clean = X_clean
            return self
        except Exception as e:
            logger.error(f"Failed to train {self.model_type.title()}Regression: {e}")
            raise DataProcessingError(f"Failed to train {self.model_type.title()}Regression: {e}", source="Regression") from e

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """Predict ratings for new rows using trained feature columns."""
        try:
            X_aligned = X.reindex(columns=self.X_clean.columns, fill_value=0).fillna(0)
            X_scaled = self.scaler.transform(X_aligned)
            return cast(np.ndarray, self.model.predict(X_scaled))
        except Exception as e:
            logger.error(f"Failed to predict ratings: {e}")
            raise DataProcessingError(f"Failed to predict ratings: {e}", source="Regression") from e

    def get_ratings(self) -> pd.DataFrame:
        """Generate ratings from trained model"""
        try:
            X_scaled = self.scaler.transform(self.X_clean)
            rated = self.X_clean.copy()
            rated["rating"] = pd.Series(self.model.predict(X_scaled), index=rated.index, name="rating")
            return rated.sort_values(by="rating", ascending=False)
        except Exception as e:
            logger.error(f"Failed to calculate ratings: {e}")
            raise DataProcessingError(f"Failed to calculate ratings: {e}", source="Regression") from e

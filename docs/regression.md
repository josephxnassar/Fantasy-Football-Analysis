# `RidgeRegression` Class

The [`RidgeRegression`](../source/ratings/regression/ridge.py) class performs ridge regression using scikit-learn's `Ridge` model and computes a rating for each instance in the dataset based on the model’s predictions.

---

## Table of Contents

- [Initialization](#initialization)
- [Methods](#methods)  
  - [`fit() -> None`](#fit---none)  
  - [`get_ratings() -> pddataframe`](#get_ratings---pddataframe)
- [Example Usage](#example-usage)

---

## Initialization

```python
RidgeRegression(X: pd.DataFrame, y: pd.Series, alpha: float = 1.0)
```

### Parameters:
- `X` (`pd.DataFrame`): The input feature matrix.
- `y` (`pd.Series`): The target variable.
- `alpha` (`float`, optional): Regularization strength; must be a positive float. Default is `1.0`.

---

## Methods

### `fit() -> None`

Scales the feature matrix using `StandardScaler`, splits it into a training subset (80%) and discards the rest, then trains a `Ridge` regression model on this data.

#### Raises:
- Logs and raises an exception if training fails.

---

### `get_ratings() -> pd.DataFrame`

Applies the trained model to the full feature matrix, adds a `rating` column to the `X` DataFrame containing the predicted values, and returns the DataFrame sorted in descending order of ratings.

#### Returns:
- `pd.DataFrame`: The feature DataFrame with an additional `rating` column.

#### Raises:
- Logs and raises an exception if prediction fails.

---

## Example Usage

```python
from source.ratings.regression.ridge import RidgeRegression
import xlwings as xw

model = RidgeRegression(X, y, alpha=0.5)
model.fit()

wb = xw.Book("output_file.xlsm")
sheet = wb.sheets["output_sheet"]
sheet.cells.clear()
sheet.range("B2").value = model.get_ratings()
wb.close()
```

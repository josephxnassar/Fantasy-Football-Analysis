# NFL Data Analysis Tool

This project provides a suite of tools to collect, process, and analyze NFL player depth charts and statistics from multiple sources. It integrates data from **nfl_data_py**, ESPN, and performs rating calculations via ridge regression. It also provides the ability to export processed data to Excel.

---

## 📂 Modules

### 1. [`Statistics`](./source/statistics/statistics.py)
Processes NFL seasonal data by organizing into position and running a regression algorithm.

### 2. [`Schedules`](./source/schedules/schedules.py)
Processes NFL schedule data by inserting bye weeks where games are missing from the schedule.

### 3. [`NDPDepthChart`](./source/depth_chart/ndp.py)
Retrieves offensive player depth charts from `nfl_data_py`.  

### 4. [`ESPNDepthChart`](./source/depth_chart/espn.py)
Scrapes player depth chart information directly from ESPN’s website.  

---

## ▶️ Running the Program

To successfully run the project, follow these steps:

### 1. 📦 Install Dependencies
Install required Python packages using `pip`:

```bash
pip install -r requirements.txt
```

Ensure the following are included with the correct versions stated inside requirements.txt:
- `pandas`
- `xlwings`
- `scikit-learn`
- `beautifulsoup4`
- `requests`
- `nfl_data_py`

Additionally, `xlwings` may require Microsoft Excel to be installed locally.

### 2. 🧩 Structure the Codebase

Your codebase should be structured something like:

```
source/
├── database/
├────── sqlite.py
├── depth_chart/
├────── ndpdepthchart.py
├────── espndepthchart.py
├── output/
├────── excel.py
├── schedules/
├────── schedules.py
├── statistics/
├────── statistics.py
main.py
```

### 3. 🚀 Example Execution

To pull and output depth charts from ESPN:

```python
from source.depth_chart.espn import ESPNDepthChart
from source.output.excel import Excel

espn = ESPNDepthChart()
excel = Excel("output_file.xlsm")
excel.output_dfs(espn.run(), "output_sheet")
excel.close()
```

To calculate nnd sort statistics by rating:

```python
from source.statistics.statistics import Statistics
from source.output.excel import Excel

stats = Statistics([2024])
excel = Excel("output_file.xlsm")
excel.output_dfs(stats.run(), "output_sheet")
excel.close()
```

---

## 📘 Documentation

Each module's documentation can be found in the respective Markdown files:

- [`statistics.md`](./docs/statistics.md)
- [`schedules.md`](./docs/schedules.md)
- [`ndpdepthchart.md`](./docs/ndp.md)
- [`espndepthchart.md`](./docs/espn.md)

---

## 👨‍💻 Author

Created by Joseph Nassar, 2025  

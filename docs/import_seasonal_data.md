# `nfl_data_py` – `import_seasonal_data`

The `import_seasonal_data()` function from the `nfl_data_py` library provides season-level statistics for NFL players, primarily focused on receiving performance and advanced analytics. 

## Receiving Market Share Metrics

| Column       | Description                                                                 |
|--------------|-----------------------------------------------------------------------------|
| `tgt_sh`     | Target share — percentage of team pass attempts targeted at the player.     |
| `ay_sh`      | Air yards share — percentage of team total air yards attributed to player.  |
| `yac_sh`     | Yards after catch share — percentage of team total YAC from the player.     |
| `ry_sh`      | Receiving yards share — share of team receiving yards by the player.        |
| `rtd_sh`     | Receiving touchdowns share — percentage of team receiving TDs.              |
| `rfd_sh`     | Receiving first downs share — share of team receiving first downs.          |
| `rtdfd_sh`   | Combined share of receiving touchdowns and first downs.                     |
| `ppr_sh`     | PPR fantasy points share — player's share of team PPR fantasy points.       |

---

## Advanced & Composite Efficiency Metrics

| Column       | Description                                                                 |
|--------------|-----------------------------------------------------------------------------|
| `racr`       | Receiver Air Conversion Ratio — ratio of receiving yards to air yards.      |
| `yptmpa`     | Yards per team pass attempt — receiving yards divided by team pass attempts.|
| `wopr_x`     | Air yards share weight used in WOPR calculation.                            |
| `wopr_y`     | Target share weight used in WOPR calculation.                               |
| `wopr`       | Weighted Opportunity Rating — combines target and air yards share.          |
| `dakota`     | Composite metric of WOPR and YPTMPA — overall efficiency / usage indicator. |
| `dom`        | Dominator rating — sum of share of receiving yards and touchdowns.          |
| `w8dom`      | Weighted dominator — emphasizes yards more heavily than touchdowns.         |

---
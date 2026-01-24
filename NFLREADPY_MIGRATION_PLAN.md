# nflreadpy Migration Plan

**Date:** January 23, 2026  
**Current Library:** `nfl_data_py` (archived/discontinued)  
**Target Library:** `nflreadpy` (active, maintained)

---

## Executive Summary

**Recommendation: Create a migration branch** (`migrate/nflreadpy`)

- Same project purpose, just updating the data source library
- Preserve git history and enable easy comparison
- Can test thoroughly before merging to main
- Reversible if issues arise

---

## Key Findings from nflreadpy Documentation

### 1. **API Compatibility**
✅ nflreadpy is a **Python port of nflreadr** (the R package)  
✅ Very similar API to nfl_data_py  
✅ Designed for modern Python conventions

### 2. **Major Differences**

| Aspect | nfl_data_py | nflreadpy |
|--------|-------------|-----------|
| **DataFrame Library** | pandas | **Polars** (faster) |
| **Conversion** | N/A | `.to_pandas()` method available |
| **Package Manager** | pip + venv | **uv recommended** (handles venv) |
| **Caching** | Limited | Built-in intelligent caching |
| **Maintenance** | ❌ Archived | ✅ Active development |

### 3. **Function Mappings**

Your current code uses these 3 main functions:

| Current (nfl_data_py) | New (nflreadpy) | Notes |
|----------------------|-----------------|-------|
| `nfl.import_seasonal_data(seasons)` | `nfl.load_player_stats(seasons)` | Returns Polars, use `.to_pandas()` |
| `nfl.import_schedules(seasons)` | `nfl.load_schedules(seasons)` | Returns Polars |
| `nfl.import_seasonal_rosters(seasons)` | `nfl.load_rosters(seasons)` | Returns Polars |

### 4. **Installation with uv** (Recommended)

nflreadpy docs strongly recommend using `uv`:

```bash
# Install nflreadpy
uv add nflreadpy

# uv automatically handles:
# - Virtual environment creation
# - Dependency resolution
# - Lock file generation (uv.lock)
# - Faster installs than pip
```

**Benefits of uv:**
- No manual venv activation needed
- Much faster than pip
- Better dependency resolution
- Creates `pyproject.toml` and `uv.lock` for reproducibility
- Becoming the modern Python standard

---

## Migration Strategy

### **Phase 1: Research & Validation** (1-2 hours)

1. ✅ Analyze nflreadpy documentation (DONE)
2. 🔄 Run `nflreadpy_analysis.py` script to:
   - Test actual API calls
   - Compare DataFrame structures
   - Identify column name differences
   - Document any breaking changes

### **Phase 2: Branch Setup** (30 mins)

```bash
# Create migration branch
git checkout -b migrate/nflreadpy

# Replace requirements.txt with pyproject.toml for uv
# Update dev-startup.ps1 to use uv commands
```

### **Phase 3: Code Changes** (2-4 hours)

**Files to Update:**

1. **`backend/statistics/statistics.py`**
   ```python
   # OLD
   import nfl_data_py as nfl
   df = nfl.import_seasonal_data(self.seasons)
   
   # NEW
   import nflreadpy as nfl
   df = nfl.load_player_stats(seasons=self.seasons).to_pandas()
   ```

2. **`backend/schedules/schedules.py`**
   ```python
   # OLD
   df = nfl.import_schedules(self.seasons)
   
   # NEW
   df = nfl.load_schedules(seasons=self.seasons).to_pandas()
   ```

3. **`backend/util/constants.py`**
   - May need updates if column names differ

4. **`requirements.txt` → `pyproject.toml`**
   - Migrate to modern uv-based dependency management

5. **`dev-startup.ps1`**
   - Replace venv + pip commands with uv commands

### **Phase 4: Testing** (2-3 hours)

1. Run `refresh_data.py` to verify data collection
2. Test API endpoints return same structure
3. Verify frontend functionality
4. Check data quality (sample players, schedules)
5. Run existing unit tests

### **Phase 5: Documentation** (1 hour)

1. Update README.md with new setup instructions
2. Update docs/ files if needed
3. Add migration notes to CHANGELOG

### **Phase 6: Merge & Deploy**

1. Merge `migrate/nflreadpy` → `main`
2. Keep old branch as reference (optional)
3. Update any CI/CD pipelines

---

## Code Changes Breakdown

### **Minimal Changes Needed**

✅ **Only 3 files use nfl_data_py:**
- `backend/statistics/statistics.py`
- `backend/schedules/schedules.py`  
- (depth chart uses ESPN scraping, no change)

✅ **Import updates:**
```python
# Change this everywhere
import nfl_data_py as nfl

# To this
import nflreadpy as nfl
```

✅ **Function call updates:**
```python
# Add .to_pandas() to maintain pandas compatibility
df = nfl.load_player_stats(seasons).to_pandas()
df = nfl.load_schedules(seasons).to_pandas()
df = nfl.load_rosters(seasons).to_pandas()
```

### **Potential Issues to Watch For**

⚠️ **Column Name Differences**
- Run the analysis script to identify any differences
- Update `COLUMN_NAME_MAP` in `constants.py` if needed

⚠️ **Default Parameter Values**
- nflreadpy may have different defaults
- Explicitly specify all parameters

⚠️ **Data Type Changes**
- Polars → Pandas conversion may change dtypes slightly
- Verify numeric columns remain numeric

---

## Benefits of Migration

✅ **Active Maintenance** - nflreadpy is actively developed  
✅ **Better Performance** - Polars is faster than pandas  
✅ **Modern Tooling** - uv is the new Python standard  
✅ **Better Caching** - Built-in intelligent caching  
✅ **Additional Data** - Access to more nflverse datasets  
✅ **Future-Proof** - Won't break when nfl_data_py stops working

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Column names differ | Medium | Medium | Run analysis script first |
| Data quality differs | Low | High | Compare sample data |
| Performance regression | Very Low | Low | Polars is faster |
| Breaking API changes | Low | Medium | Test thoroughly on branch |

**Overall Risk: LOW** ✅

---

## Next Steps

**IMMEDIATE (Now):**
1. Install nflreadpy locally: `uv add nflreadpy`
2. Run `python nflreadpy_analysis.py` to generate comparison data
3. Review the JSON output files for differences

**SHORT-TERM (This week):**
1. Create `migrate/nflreadpy` branch
2. Set up uv-based dependency management
3. Update the 3 core data loading files
4. Test data collection and API endpoints

**BEFORE MERGE:**
1. Verify all tests pass
2. Compare data quality with production
3. Update all documentation
4. Get approval/review

---

## Questions to Answer from Analysis Script

After running `nflreadpy_analysis.py`, check:

1. ✅ Are column names identical between libraries?
2. ✅ Are data types compatible?
3. ✅ Does `.to_pandas()` work seamlessly?
4. ✅ Are there any missing columns we rely on?
5. ✅ Do the DataFrames have the same structure?

---

## Resources

- **nflreadpy GitHub:** https://github.com/nflverse/nflreadpy
- **nflreadpy Docs:** https://nflreadpy.nflverse.com/
- **uv Documentation:** https://docs.astral.sh/uv/
- **Analysis Script:** `nflreadpy_analysis.py`

---

## Timeline Estimate

| Phase | Duration | When |
|-------|----------|------|
| Research & validation | 1-2 hours | Now |
| Branch setup | 30 mins | Now |
| Code changes | 2-4 hours | This week |
| Testing | 2-3 hours | This week |
| Documentation | 1 hour | This week |
| Review & merge | 1 hour | Next week |

**Total: ~8-12 hours over 1-2 weeks**

---

## Decision: Branch vs New Repo

✅ **BRANCH RECOMMENDED**

**Why:**
- Same project, different data source
- Preserves history
- Easier to compare
- Can revert if needed
- One codebase to maintain

**When you'd want a new repo:**
- ❌ Fundamentally different product
- ❌ Need to support both long-term
- ❌ Major architecture changes

**This is a library upgrade, not a new project.**

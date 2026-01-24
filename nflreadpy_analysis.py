"""
nflreadpy Analysis Script
=========================
Comprehensive testing and comparison script to understand nflreadpy's API
and compare it with the current nfl_data_py implementation.

This script will:
1. Test all relevant nflreadpy functions
2. Inspect DataFrame structures and column names
3. Compare with current nfl_data_py data structures
4. Document any differences for migration planning
"""

import sys
from datetime import datetime
from pathlib import Path
import json

try:
    import nflreadpy as nfl
    import polars as pl
    NFLREADPY_AVAILABLE = True
except ImportError:
    NFLREADPY_AVAILABLE = False
    print("WARNING: nflreadpy not installed. Install with: uv add nflreadpy")
    print("Continuing with limited functionality...")

try:
    import nfl_data_py as nfl_legacy
    import pandas as pd
    NFL_DATA_PY_AVAILABLE = True
except ImportError:
    NFL_DATA_PY_AVAILABLE = False
    print("WARNING: nfl_data_py not installed.")


# Configuration
TEST_SEASONS = [2024]  # Test with recent season
CURRENT_SEASON = 2025
OUTPUT_DIR = Path("nflreadpy_analysis_results")
OUTPUT_DIR.mkdir(exist_ok=True)


def save_results(filename: str, data: dict):
    """Save results to JSON file."""
    filepath = OUTPUT_DIR / filename
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, default=str)
    print(f"  ✓ Saved to {filepath}")


def test_player_stats():
    """Test load_player_stats() - equivalent to import_seasonal_data()."""
    print("\n" + "="*80)
    print("TEST: Player Statistics (Seasonal Data)")
    print("="*80)
    
    results = {
        "function": "load_player_stats()",
        "nfl_data_py_equivalent": "import_seasonal_data()",
        "timestamp": datetime.now().isoformat(),
        "seasons_tested": TEST_SEASONS
    }
    
    if NFLREADPY_AVAILABLE:
        print("\n[nflreadpy] Testing load_player_stats()...")
        try:
            # Test with single season
            df = nfl.load_player_stats(seasons=TEST_SEASONS[0])
            
            results["nflreadpy"] = {
                "success": True,
                "dataframe_type": str(type(df)),
                "rows": len(df),
                "columns": len(df.columns),
                "column_names": df.columns,
                "column_dtypes": {col: str(df[col].dtype) for col in df.columns},
                "sample_data": df.head(5).to_dicts()
            }
            
            print(f"  ✓ Success! Loaded {len(df):,} rows × {len(df.columns)} columns")
            print(f"  - DataFrame type: {type(df)}")
            print(f"  - Columns: {', '.join(df.columns[:10])}...")
            
            # Check for player identification columns
            id_cols = [col for col in df.columns if 'player' in col.lower() or 'id' in col.lower()]
            print(f"  - Player ID columns: {id_cols}")
            
        except Exception as e:
            results["nflreadpy"] = {"success": False, "error": str(e)}
            print(f"  ✗ Error: {e}")
    
    if NFL_DATA_PY_AVAILABLE:
        print("\n[nfl_data_py] Testing import_seasonal_data()...")
        try:
            df = nfl_legacy.import_seasonal_data(TEST_SEASONS)
            
            results["nfl_data_py"] = {
                "success": True,
                "dataframe_type": str(type(df)),
                "rows": len(df),
                "columns": len(df.columns),
                "column_names": list(df.columns),
                "column_dtypes": {col: str(df[col].dtype) for col in df.columns},
                "sample_data": df.head(5).to_dict('records')
            }
            
            print(f"  ✓ Success! Loaded {len(df):,} rows × {len(df.columns)} columns")
            print(f"  - DataFrame type: {type(df)}")
            print(f"  - Columns: {', '.join(df.columns[:10].tolist())}...")
            
        except Exception as e:
            results["nfl_data_py"] = {"success": False, "error": str(e)}
            print(f"  ✗ Error: {e}")
    
    # Compare column names
    if NFLREADPY_AVAILABLE and NFL_DATA_PY_AVAILABLE:
        if results.get("nflreadpy", {}).get("success") and results.get("nfl_data_py", {}).get("success"):
            nflreadpy_cols = set(results["nflreadpy"]["column_names"])
            legacy_cols = set(results["nfl_data_py"]["column_names"])
            
            results["comparison"] = {
                "identical_columns": nflreadpy_cols == legacy_cols,
                "columns_only_in_nflreadpy": list(nflreadpy_cols - legacy_cols),
                "columns_only_in_nfl_data_py": list(legacy_cols - nflreadpy_cols),
                "common_columns": list(nflreadpy_cols & legacy_cols)
            }
            
            print("\n[Comparison]")
            print(f"  - Identical columns: {results['comparison']['identical_columns']}")
            print(f"  - Columns only in nflreadpy: {len(results['comparison']['columns_only_in_nflreadpy'])}")
            print(f"  - Columns only in nfl_data_py: {len(results['comparison']['columns_only_in_nfl_data_py'])}")
            print(f"  - Common columns: {len(results['comparison']['common_columns'])}")
    
    save_results("player_stats_analysis.json", results)
    return results


def test_schedules():
    """Test load_schedules() - equivalent to import_schedules()."""
    print("\n" + "="*80)
    print("TEST: Schedules")
    print("="*80)
    
    results = {
        "function": "load_schedules()",
        "nfl_data_py_equivalent": "import_schedules()",
        "timestamp": datetime.now().isoformat(),
        "seasons_tested": [CURRENT_SEASON]
    }
    
    if NFLREADPY_AVAILABLE:
        print("\n[nflreadpy] Testing load_schedules()...")
        try:
            df = nfl.load_schedules(seasons=CURRENT_SEASON)
            
            results["nflreadpy"] = {
                "success": True,
                "dataframe_type": str(type(df)),
                "rows": len(df),
                "columns": len(df.columns),
                "column_names": df.columns,
                "column_dtypes": {col: str(df[col].dtype) for col in df.columns},
                "sample_data": df.head(5).to_dicts()
            }
            
            print(f"  ✓ Success! Loaded {len(df):,} rows × {len(df.columns)} columns")
            print(f"  - Columns: {', '.join(df.columns[:10])}...")
            
            # Check for key columns
            key_cols = ['week', 'away_team', 'home_team', 'game_type']
            available = [col for col in key_cols if col in df.columns]
            print(f"  - Key columns available: {available}")
            
        except Exception as e:
            results["nflreadpy"] = {"success": False, "error": str(e)}
            print(f"  ✗ Error: {e}")
    
    if NFL_DATA_PY_AVAILABLE:
        print("\n[nfl_data_py] Testing import_schedules()...")
        try:
            df = nfl_legacy.import_schedules([CURRENT_SEASON])
            
            results["nfl_data_py"] = {
                "success": True,
                "dataframe_type": str(type(df)),
                "rows": len(df),
                "columns": len(df.columns),
                "column_names": list(df.columns),
                "column_dtypes": {col: str(df[col].dtype) for col in df.columns},
                "sample_data": df.head(5).to_dict('records')
            }
            
            print(f"  ✓ Success! Loaded {len(df):,} rows × {len(df.columns)} columns")
            print(f"  - Columns: {', '.join(df.columns[:10].tolist())}...")
            
        except Exception as e:
            results["nfl_data_py"] = {"success": False, "error": str(e)}
            print(f"  ✗ Error: {e}")
    
    # Compare
    if NFLREADPY_AVAILABLE and NFL_DATA_PY_AVAILABLE:
        if results.get("nflreadpy", {}).get("success") and results.get("nfl_data_py", {}).get("success"):
            nflreadpy_cols = set(results["nflreadpy"]["column_names"])
            legacy_cols = set(results["nfl_data_py"]["column_names"])
            
            results["comparison"] = {
                "identical_columns": nflreadpy_cols == legacy_cols,
                "columns_only_in_nflreadpy": list(nflreadpy_cols - legacy_cols),
                "columns_only_in_nfl_data_py": list(legacy_cols - nflreadpy_cols),
                "common_columns": list(nflreadpy_cols & legacy_cols)
            }
            
            print("\n[Comparison]")
            print(f"  - Identical columns: {results['comparison']['identical_columns']}")
    
    save_results("schedules_analysis.json", results)
    return results


def test_rosters():
    """Test load_rosters() - equivalent to import_seasonal_rosters()."""
    print("\n" + "="*80)
    print("TEST: Rosters")
    print("="*80)
    
    results = {
        "function": "load_rosters()",
        "nfl_data_py_equivalent": "import_seasonal_rosters()",
        "timestamp": datetime.now().isoformat(),
        "seasons_tested": TEST_SEASONS
    }
    
    if NFLREADPY_AVAILABLE:
        print("\n[nflreadpy] Testing load_rosters()...")
        try:
            df = nfl.load_rosters(seasons=TEST_SEASONS[0])
            
            results["nflreadpy"] = {
                "success": True,
                "dataframe_type": str(type(df)),
                "rows": len(df),
                "columns": len(df.columns),
                "column_names": df.columns,
                "column_dtypes": {col: str(df[col].dtype) for col in df.columns},
                "sample_data": df.head(5).to_dicts()
            }
            
            print(f"  ✓ Success! Loaded {len(df):,} rows × {len(df.columns)} columns")
            print(f"  - Columns: {', '.join(df.columns[:10])}...")
            
            # Check for key columns
            key_cols = ['player_id', 'player_name', 'position', 'depth_chart_position', 'age', 'season', 'status']
            available = [col for col in key_cols if col in df.columns]
            print(f"  - Key columns available: {available}")
            
        except Exception as e:
            results["nflreadpy"] = {"success": False, "error": str(e)}
            print(f"  ✗ Error: {e}")
    
    if NFL_DATA_PY_AVAILABLE:
        print("\n[nfl_data_py] Testing import_seasonal_rosters()...")
        try:
            df = nfl_legacy.import_seasonal_rosters(TEST_SEASONS)
            
            results["nfl_data_py"] = {
                "success": True,
                "dataframe_type": str(type(df)),
                "rows": len(df),
                "columns": len(df.columns),
                "column_names": list(df.columns),
                "column_dtypes": {col: str(df[col].dtype) for col in df.columns},
                "sample_data": df.head(5).to_dict('records')
            }
            
            print(f"  ✓ Success! Loaded {len(df):,} rows × {len(df.columns)} columns")
            print(f"  - Columns: {', '.join(df.columns[:10].tolist())}...")
            
        except Exception as e:
            results["nfl_data_py"] = {"success": False, "error": str(e)}
            print(f"  ✗ Error: {e}")
    
    # Compare
    if NFLREADPY_AVAILABLE and NFL_DATA_PY_AVAILABLE:
        if results.get("nflreadpy", {}).get("success") and results.get("nfl_data_py", {}).get("success"):
            nflreadpy_cols = set(results["nflreadpy"]["column_names"])
            legacy_cols = set(results["nfl_data_py"]["column_names"])
            
            results["comparison"] = {
                "identical_columns": nflreadpy_cols == legacy_cols,
                "columns_only_in_nflreadpy": list(nflreadpy_cols - legacy_cols),
                "columns_only_in_nfl_data_py": list(legacy_cols - nflreadpy_cols),
                "common_columns": list(nflreadpy_cols & legacy_cols)
            }
            
            print("\n[Comparison]")
            print(f"  - Identical columns: {results['comparison']['identical_columns']}")
    
    save_results("rosters_analysis.json", results)
    return results


def test_polars_pandas_conversion():
    """Test Polars to Pandas conversion for compatibility."""
    print("\n" + "="*80)
    print("TEST: Polars ↔ Pandas Conversion")
    print("="*80)
    
    if not NFLREADPY_AVAILABLE:
        print("  ✗ Skipped: nflreadpy not available")
        return None
    
    results = {
        "test": "polars_pandas_conversion",
        "timestamp": datetime.now().isoformat()
    }
    
    print("\n[Testing conversion workflow]")
    try:
        # Load data with nflreadpy (Polars)
        print("  1. Loading data with nflreadpy (returns Polars DataFrame)...")
        df_polars = nfl.load_schedules(seasons=CURRENT_SEASON)
        print(f"     ✓ Loaded: {type(df_polars)}")
        
        # Convert to pandas
        print("  2. Converting to pandas...")
        df_pandas = df_polars.to_pandas()
        print(f"     ✓ Converted: {type(df_pandas)}")
        
        # Verify columns match
        print("  3. Verifying column names...")
        polars_cols = set(df_polars.columns)
        pandas_cols = set(df_pandas.columns)
        assert polars_cols == pandas_cols, "Column mismatch!"
        print(f"     ✓ Columns match: {len(polars_cols)} columns")
        
        # Verify data types are reasonable
        print("  4. Checking data types...")
        print(f"     - Polars dtypes sample: {list(df_polars.dtypes)[:5]}")
        print(f"     - Pandas dtypes sample: {list(df_pandas.dtypes)[:5]}")
        
        results["success"] = True
        results["polars_type"] = str(type(df_polars))
        results["pandas_type"] = str(type(df_pandas))
        results["columns_match"] = True
        results["conversion_notes"] = "Seamless conversion with .to_pandas()"
        
        print("\n  ✓ Conversion successful! Use .to_pandas() to convert Polars → Pandas")
        
    except Exception as e:
        results["success"] = False
        results["error"] = str(e)
        print(f"  ✗ Error: {e}")
    
    save_results("polars_pandas_conversion.json", results)
    return results


def test_additional_functions():
    """Test other useful nflreadpy functions."""
    print("\n" + "="*80)
    print("TEST: Additional nflreadpy Functions")
    print("="*80)
    
    if not NFLREADPY_AVAILABLE:
        print("  ✗ Skipped: nflreadpy not available")
        return None
    
    results = {
        "test": "additional_functions",
        "timestamp": datetime.now().isoformat(),
        "functions": {}
    }
    
    # Test get_current_season()
    print("\n[get_current_season()]")
    try:
        current_season = nfl.get_current_season()
        roster_season = nfl.get_current_season(roster=True)
        print(f"  ✓ Current season: {current_season}")
        print(f"  ✓ Current roster year: {roster_season}")
        results["functions"]["get_current_season"] = {
            "success": True,
            "current_season": current_season,
            "roster_season": roster_season
        }
    except Exception as e:
        print(f"  ✗ Error: {e}")
        results["functions"]["get_current_season"] = {"success": False, "error": str(e)}
    
    # Test get_current_week()
    print("\n[get_current_week()]")
    try:
        current_week = nfl.get_current_week()
        print(f"  ✓ Current week: {current_week}")
        results["functions"]["get_current_week"] = {
            "success": True,
            "current_week": current_week
        }
    except Exception as e:
        print(f"  ✗ Error: {e}")
        results["functions"]["get_current_week"] = {"success": False, "error": str(e)}
    
    # Test load_depth_charts() - bonus data not in nfl_data_py
    print("\n[load_depth_charts()]")
    try:
        df = nfl.load_depth_charts(seasons=CURRENT_SEASON)
        print(f"  ✓ Loaded depth charts: {len(df):,} rows × {len(df.columns)} columns")
        print(f"  - Columns: {', '.join(df.columns[:10])}...")
        results["functions"]["load_depth_charts"] = {
            "success": True,
            "rows": len(df),
            "columns": len(df.columns),
            "column_names": df.columns
        }
    except Exception as e:
        print(f"  ✗ Error: {e}")
        results["functions"]["load_depth_charts"] = {"success": False, "error": str(e)}
    
    save_results("additional_functions.json", results)
    return results


def generate_migration_summary():
    """Generate a migration summary report."""
    print("\n" + "="*80)
    print("MIGRATION SUMMARY")
    print("="*80)
    
    summary = {
        "timestamp": datetime.now().isoformat(),
        "nflreadpy_available": NFLREADPY_AVAILABLE,
        "nfl_data_py_available": NFL_DATA_PY_AVAILABLE,
        "function_mappings": {
            "import_seasonal_data()": {
                "nflreadpy_equivalent": "load_player_stats()",
                "notes": "Returns Polars DataFrame; use .to_pandas() for pandas"
            },
            "import_schedules()": {
                "nflreadpy_equivalent": "load_schedules()",
                "notes": "Returns Polars DataFrame"
            },
            "import_seasonal_rosters()": {
                "nflreadpy_equivalent": "load_rosters()",
                "notes": "Returns Polars DataFrame"
            }
        },
        "key_differences": [
            "nflreadpy returns Polars DataFrames instead of pandas",
            "Use .to_pandas() method for compatibility with existing code",
            "nflreadpy has additional functions like load_depth_charts()",
            "API is similar but may have different parameter names/defaults"
        ],
        "recommended_approach": [
            "1. Create migrate/nflreadpy branch",
            "2. Update imports: nfl_data_py → nflreadpy",
            "3. Update function calls per mapping above",
            "4. Add .to_pandas() conversions where needed",
            "5. Update any column name mappings if different",
            "6. Test thoroughly before merging"
        ]
    }
    
    print("\n[Function Mappings]")
    for old_func, mapping in summary["function_mappings"].items():
        print(f"  {old_func:<30} → {mapping['nflreadpy_equivalent']}")
        print(f"  {'':30}   Note: {mapping['notes']}")
    
    print("\n[Key Differences]")
    for diff in summary["key_differences"]:
        print(f"  - {diff}")
    
    print("\n[Recommended Migration Steps]")
    for step in summary["recommended_approach"]:
        print(f"  {step}")
    
    save_results("migration_summary.json", summary)
    return summary


def main():
    """Run all tests."""
    print("\n" + "="*80)
    print(" nflreadpy Analysis Script")
    print("="*80)
    print(f"\nOutput directory: {OUTPUT_DIR.absolute()}")
    
    if not NFLREADPY_AVAILABLE:
        print("\n⚠️  nflreadpy is not installed!")
        print("    Install with: uv add nflreadpy")
        print("    or: pip install nflreadpy")
        print("\nContinuing with limited functionality...")
    
    if not NFL_DATA_PY_AVAILABLE:
        print("\n⚠️  nfl_data_py is not installed for comparison")
        print("    Comparison features will be skipped")
    
    # Run all tests
    test_player_stats()
    test_schedules()
    test_rosters()
    test_polars_pandas_conversion()
    test_additional_functions()
    generate_migration_summary()
    
    print("\n" + "="*80)
    print(" Analysis Complete!")
    print("="*80)
    print(f"\nResults saved to: {OUTPUT_DIR.absolute()}")
    print("\nReview the JSON files for detailed comparison data.")
    print("\nNext steps:")
    print("  1. Review migration_summary.json for high-level guidance")
    print("  2. Check *_analysis.json files for column comparisons")
    print("  3. Decide on branch vs new repo approach")
    print("  4. Begin migration on a feature branch")


if __name__ == "__main__":
    main()

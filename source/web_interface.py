import logging
from flask import Flask, render_template, jsonify, request
from source.app import App
from source.util import constants
import pandas as pd
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Initialize the app with data
app_data = App()
app_data.load()

@app.route('/')
def index():
    """Main page that lists all available data tables"""
    tables = list(app_data.caches.keys())
    return render_template('index.html', 
                         tables=tables,
                         current_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

import json
import os

def _save_debug_data(data, filename):
    """Helper to save debug data to a file"""
    debug_dir = os.path.join(os.path.dirname(__file__), '..', 'debug_data')
    os.makedirs(debug_dir, exist_ok=True)
    path = os.path.join(debug_dir, filename)
    
    try:
        if hasattr(data, 'to_dict'):
            data = data.to_dict()
        with open(path, 'w') as f:
            if isinstance(data, (dict, list)):
                json.dump(data, f, indent=2, default=str)
            else:
                f.write(str(data))
        print(f"Debug data saved to {path}")
    except Exception as e:
        print(f"Error saving debug data: {e}")

def _process_position_players(depth_chart_df, position, depth_levels, team_players, positions):
    """Helper method to process players at a specific position"""
    # Process each depth level
    for depth, depth_col in enumerate(depth_levels, 1):
        if depth_col not in depth_chart_df.columns:
            continue
            
        try:
            # Get the player info for this position and depth
            player_info = depth_chart_df.at[position, depth_col]
            
            # Skip if no player at this depth
            if pd.isna(player_info):
                continue
                
            # Convert to string and clean up
            if hasattr(player_info, 'item'):  # Handle numpy types
                player_info = player_info.item()
                
            player_str = str(player_info).strip()
            if not player_str or player_str.lower() in ['-', 'nan', 'none']:
                continue
                
            # Extract player name and number (handle format like "8 Jayden Daniels")
            player_parts = player_str.split(' ', 1)
            if len(player_parts) > 1 and player_parts[0].isdigit():
                player_number = player_parts[0]
                player_name = player_parts[1].strip()
            else:
                player_number = None
                player_name = player_str.strip()
            
            # For WR positions, use 'WR' as the position instead of 'WR1', 'WR2', etc.
            display_position = position[:2] if position.startswith('WR') and len(position) > 2 else position
            
            # Create player data
            player_data = {
                'position': display_position,
                'full_name': player_name,
                'jersey_number': player_number,
                'depth_team': depth,
                'source': 'ESPN',
                'source_display': 'ESPN'
            }
            
            team_players.append(player_data)
            positions.add(display_position)
            
            print(f"  {depth_col}: {player_name} ({player_number or 'No #'})")
            
        except Exception as e:
            print(f"Error processing {position} {depth_col}: {e}")


def _process_espn_depth_chart(team_data, team):
    """Process ESPN depth chart data for a single team
    
    Args:
        team_data: Dictionary containing depth chart data for all teams
        team: Team abbreviation (e.g., 'BUF')
        
    Returns:
        tuple: (list of player dictionaries, set of positions)
    """
    team_players = []
    positions = set()
    
    print(f"\n{'='*80}")
    print(f"Processing ESPN data for team: {team}")
    
    # Get the team's depth chart DataFrame
    depth_chart_df = team_data.get(team)
    if depth_chart_df is None:
        print(f"No depth chart data found for team {team}")
        return team_players, positions
    
    if not hasattr(depth_chart_df, 'head'):
        print(f"Expected a DataFrame for team {team}, got {type(depth_chart_df)}")
        return team_players, positions
    
    print(f"Depth chart columns: {depth_chart_df.columns.tolist()}")
    print(f"Positions: {depth_chart_df.index.tolist()}")
    
    # Define depth levels to process
    depth_levels = ['Starter', '2nd', '3rd', '4th']
    
    # Create a list to store (position_index, position_name) tuples
    positions_to_process = []
    
    # Create a list of all position indices and their names
    position_indices = list(depth_chart_df.index)
    
    # Process each position in the index exactly as it appears
    for i, pos in enumerate(position_indices):
        pos_str = str(pos).strip()
        if not pos_str or pos_str.lower() == 'nan':
            continue
            
        # For duplicate positions, append a number to make them unique for processing
        # but still store the original position name for display
        position_count = position_indices[:i+1].count(pos)
        display_pos = f"{pos_str}{position_count}" if position_count > 1 else pos_str
        
        positions_to_process.append((i, pos_str, display_pos))
    
    # Now process each position
    for pos_idx, orig_pos, display_pos in positions_to_process:
        print(f"\nProcessing position: {display_pos} (index: {pos_idx})")
        
        # Get the row for this position
        try:
            row = depth_chart_df.iloc[pos_idx] if isinstance(depth_chart_df, pd.DataFrame) else depth_chart_df
        except IndexError:
            print(f"  Warning: Position index {pos_idx} out of range")
            continue
            
        # Process each depth level
        for depth, depth_col in enumerate(depth_levels, 1):
            if depth_col not in depth_chart_df.columns:
                continue
                
            try:
                # Use the row we already have
                row = depth_chart_df.iloc[pos_idx] if isinstance(depth_chart_df, pd.DataFrame) else depth_chart_df
                
                # Get player info for this depth
                if depth_col not in row:
                    continue
                    
                player_info = row[depth_col]
                
                # Skip if no player at this depth
                if pd.isna(player_info) or player_info == '':
                    continue
                    
                # Convert to string and clean up
                if hasattr(player_info, 'item'):  # Handle numpy types
                    player_info = player_info.item()
                    
                player_str = str(player_info).strip()
                if not player_str or player_str.lower() in ['-', 'nan', 'none']:
                    continue
                
                # Extract player name and number
                player_parts = player_str.split(' ', 1)
                if len(player_parts) > 1 and player_parts[0].isdigit():
                    player_number = player_parts[0]
                    player_name = player_parts[1].strip()
                else:
                    player_number = None
                    player_name = player_str.strip()
                
                # For display, use WR instead of WR1, WR2, etc.
                display_position = display_pos[:2] if display_pos.startswith('WR') and len(display_pos) > 2 else display_pos
                
                # Create player data
                player_data = {
                    'position': display_position,
                    'full_name': player_name,
                    'jersey_number': player_number,
                    'depth_team': depth,
                    'source': 'ESPN',
                    'source_display': 'ESPN'
                }
                
                team_players.append(player_data)
                positions.add(display_position)
                
                print(f"  {depth_col}: {player_name} ({player_number or 'No #'})")
                
            except Exception as e:
                print(f"Error processing {display_pos} {depth_col}: {e}")
                continue
    
    print(f"\nSuccessfully processed {len(team_players)} players for {team}")
    print(f"Positions found: {positions}")
    print("="*80)
    return team_players, positions




def _process_depth_chart_data(depth_data, source_name):
    """Helper function to process depth chart data from ESPN"""
    teams_data = {}
    all_positions = set()
    
    if not isinstance(depth_data, dict):
        print(f"{source_name}: Unexpected depth data format: {type(depth_data)}")
        return teams_data, all_positions
    
    for team, df in depth_data.items():
        try:
            if df is None or df.empty:
                print(f"{source_name}: No data available for team: {team}")
                continue
            
            # Skip if we already have data for this team from a higher priority source
            team_str = str(team)
            if team_str in teams_data:
                print(f"{source_name}: Skipping {team_str} - already processed")
                continue
            
            # Print debug info about the data
            print(f"\nProcessing {source_name} data for team: {team_str}")
            print(f"Columns: {df.columns.tolist()}")
            print(f"Sample data:\n{df.head()}")
            
            try:
                team_players, positions = _process_espn_depth_chart(depth_data, team_str)
                print(f"Processed {len(team_players)} players for {team_str}")
                if team_players:  # Only add if we have players
                    teams_data[team_str] = team_players
                    all_positions.update(positions)
                    print(f"Added {len(team_players)} players for {team_str}")
                else:
                    print(f"No players found for {team_str}")
                    
            except Exception as e:
                print(f"{source_name}: Error processing team {team}: {e}")
                import traceback
                traceback.print_exc()
                continue
                
        except Exception as e:
            print(f"{source_name}: Error initializing processing for team {team}: {e}")
            import traceback
            traceback.print_exc()
            continue
    
    return teams_data, all_positions

@app.route('/depth_chart')
def depth_chart():
    """Display depth chart for all teams using ESPN data"""
    try:
        # Initialize empty data structures
        all_teams_data = {}
        all_positions = set()
        team_sources = {}  # Track data source for each team
        
        # Process ESPN data
        if 'ESPNDepthChart' in app_data.caches and app_data.caches['ESPNDepthChart'] is not None:
            print("Processing ESPN depth chart data...")
            if isinstance(app_data.caches['ESPNDepthChart'], dict):
                espn_teams, espn_positions = _process_depth_chart_data(
                    app_data.caches['ESPNDepthChart'], 'ESPN')
                
                # Add all ESPN teams to our data
                for team, players in espn_teams.items():
                    all_teams_data[team] = players
                    team_sources[team] = 'ESPN'
                
                all_positions.update(espn_positions)
                print(f"Successfully processed ESPN data for {len(espn_teams)} teams")
        
        if not all_teams_data:
            print("No depth chart data available from any source")
            return render_template('depth_chart.html',
                                teams_data={}, 
                                positions=[], 
                                team_names=[],
                                team_sources={},
                                current_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        
        # Convert positions to a sorted list
        positions = sorted(list(all_positions))
        
        # Sort team names alphabetically
        team_names = sorted(list(all_teams_data.keys()))
        
        # Debug output
        print("\nData sources by team:")
        for team, source in team_sources.items():
            print(f"{team}: {source}")
        
        return render_template('depth_chart.html',
                            teams_data=all_teams_data,
                            positions=positions,
                            team_names=team_names,
                            team_sources=team_sources,
                            current_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    
    except Exception as e:
        print(f"Unexpected error in depth_chart: {e}")
        import traceback
        traceback.print_exc()
        return render_template('depth_chart.html',
                            teams_data={}, 
                            positions=[], 
                            team_names=[],
                            team_sources={},
                            current_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

@app.route('/statistics')
def statistics():
    """Display player statistics"""
    if 'Statistics' not in app_data.caches:
        return "Statistics data not available", 404
    
    stats_data = app_data.caches['Statistics']
    
    # Convert statistics data to a format suitable for display
    positions_data = {}
    for pos, df in stats_data.items():
        if df is not None and not df.empty:
            # Reset index and convert to dictionary
            df_display = df.reset_index()
            
            # Convert all data to strings to handle any non-serializable types
            df_display = df_display.astype(str)
            
            # Convert to list of dictionaries for the template
            positions_data[pos] = df_display.to_dict('records')
    
    # Get available positions for the tabs
    available_positions = list(positions_data.keys())
    
    return render_template('statistics.html',
                         positions_data=positions_data,
                         available_positions=available_positions,
                         current_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

@app.route('/schedules')
def schedules():
    """Display team schedules"""
    if 'Schedules' not in app_data.caches:
        return "Schedule data not available", 404
    
    schedule_data = app_data.caches['Schedules']
    
    # Convert schedule data to a format suitable for display
    teams_schedule = {}
    for team, df in schedule_data.items():
        teams_schedule[team] = df.reset_index().to_dict('records')
    
    return render_template('schedules.html',
                         teams_schedule=teams_schedule,
                         current_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

@app.route('/table/<table_name>')
def show_table(table_name):
    """Generic table view for other data"""
    if table_name not in app_data.caches:
        return f"Table {table_name} not found", 404
    
    data = app_data.caches[table_name]
    
    # Handle different data structures
    if hasattr(data, 'to_dict'):
        records = data.to_dict('records')
        headers = list(data.columns) if hasattr(data, 'columns') else []
    elif isinstance(data, dict) and data:
        # For dictionary of DataFrames, combine them
        all_records = []
        for key, df in data.items():
            if hasattr(df, 'to_dict'):
                df_records = df.reset_index().to_dict('records')
                for record in df_records:
                    record['_source'] = str(key)
                all_records.extend(df_records)
        
        if all_records:
            headers = list(all_records[0].keys())
            # Move _source to the beginning if it exists
            if '_source' in headers:
                headers.remove('_source')
                headers.insert(0, '_source')
            records = all_records
        else:
            records = []
            headers = []
    else:
        records = []
        headers = []
    
    return render_template('table.html',
                         table_name=table_name,
                         headers=headers,
                         data=records,
                         current_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

@app.route('/api/<endpoint>')
def api_endpoint(endpoint):
    """Generic API endpoint for data"""
    if endpoint not in app_data.caches:
        return jsonify({"error": f"{endpoint} data not found"}), 404
    
    data = app_data.caches[endpoint]
    
    if hasattr(data, 'to_dict'):
        return jsonify(data.reset_index().to_dict('records'))
    elif isinstance(data, dict):
        result = {}
        for key, df in data.items():
            result[key] = df.reset_index().to_dict('records')
        return jsonify(result)
    
    return jsonify([])

def run_web_interface(host='0.0.0.0', port=8080, debug=True):
    """Run the Flask web server"""
    app.run(host=host, port=port, debug=debug)

if __name__ == '__main__':
    run_web_interface()

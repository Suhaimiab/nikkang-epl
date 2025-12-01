"""
Weekly Prediction Results - Gameweek by Gameweek
Nikkang KK EPL Prediction Competition
Detailed breakdown of predictions vs results for each gameweek
"""

import streamlit as st
import pandas as pd
from pathlib import Path
from datetime import datetime
import json
import io
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')

# Add utils to path
import sys
sys.path.append(str(Path(__file__).parent.parent))

from utils.data_manager import DataManager
from utils.auth import check_password

# Page config
st.set_page_config(
    page_title="Weekly Results - Nikkang KK",
    page_icon="📊",
    layout="wide"
)

def generate_weekly_results_png(table_data, week_matches, week_results, selected_week, gotw_index, get_team_abbrev_func, champions=None, champ_pts=0, champ_kk=0):
    """Generate a styled PNG image of weekly results with actual scores and winner info"""
    n_participants = len(table_data)
    n_matches = len(week_matches)
    
    # Calculate figure size - add extra height for results row and winner banner
    fig_width = max(14, 2.5 + n_matches * 1.0)
    fig_height = max(6, n_participants * 0.5 + 4.0)
    
    fig, ax = plt.subplots(figsize=(fig_width, fig_height))
    ax.axis('off')
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    
    # Colors
    header_bg = '#1a1a2e'
    green = '#28a745'
    yellow = '#ffc107'
    red = '#dc3545'
    purple = '#9b59b6'
    gold = '#ffd700'
    silver = '#c0c0c0'
    bronze = '#cd7f32'
    result_bg = '#2c3e50'
    
    # Title (no emojis - matplotlib font doesn't support them)
    ax.text(0.5, 0.97, f"Gameweek {selected_week} Results", ha='center', va='top', fontsize=14, fontweight='bold', color='#1a1a2e')
    ax.text(0.5, 0.93, "Nikkang KK EPL Prediction League", ha='center', va='top', fontsize=9, color='#6c757d')
    
    # Winner banner (if champions provided)
    banner_height = 0
    if champions:
        banner_height = 0.05
        if len(champions) == 1:
            champ_text = f"CHAMPION: {champions[0]} ({champ_pts} pts, {champ_kk} KK)"
        else:
            champ_text = f"JOINT CHAMPIONS: {' & '.join(champions)} ({champ_pts} pts, {champ_kk} KK)"
        
        # Draw gold banner
        banner_y = 0.86
        rect = plt.Rectangle((0.1, banner_y), 0.8, 0.04, facecolor=gold, edgecolor='#b8860b', linewidth=1, zorder=5)
        ax.add_patch(rect)
        ax.text(0.5, banner_y + 0.02, champ_text, ha='center', va='center', fontsize=8, fontweight='bold', color='#1a1a2e', zorder=6)
    
    # Table dimensions - account for banner
    table_top = 0.84 - banner_height
    n_cols = 2 + n_matches + 2  # Rank, Name, Matches..., PTS, KK
    row_height = 0.68 / (n_participants + 3)  # +3 for header, results row, spacing
    col_widths = [0.04, 0.12] + [0.07] * n_matches + [0.06, 0.05]
    total_width = sum(col_widths)
    col_widths = [w / total_width * 0.96 for w in col_widths]
    left_margin = 0.02
    
    # Get x positions
    x_positions = [left_margin]
    for w in col_widths[:-1]:
        x_positions.append(x_positions[-1] + w)
    
    # Draw header row (Team matchups)
    headers = ['#', 'Name']
    for idx, match in enumerate(week_matches):
        home = get_team_abbrev_func(match.get('home', 'TBC'))
        away = get_team_abbrev_func(match.get('away', 'TBC'))
        gotw_mark = "*" if idx == gotw_index else ""
        headers.append(f"{home}v{away}{gotw_mark}")
    headers.extend(['PTS', 'KK'])
    
    for j, header in enumerate(headers):
        x = x_positions[j]
        w = col_widths[j]
        rect = plt.Rectangle((x, table_top - row_height), w, row_height, 
                            facecolor=header_bg, edgecolor='#2a2a4e', linewidth=0.5)
        ax.add_patch(rect)
        ax.text(x + w/2, table_top - row_height/2, header, 
               ha='center', va='center', fontsize=6, fontweight='bold', color='white')
    
    # Draw ACTUAL RESULTS row (new row showing what actually happened)
    results_y = table_top - 2 * row_height
    
    # Results row label
    rect = plt.Rectangle((x_positions[0], results_y), col_widths[0] + col_widths[1], row_height, 
                        facecolor=result_bg, edgecolor='#1a252f', linewidth=0.5)
    ax.add_patch(rect)
    ax.text(x_positions[0] + (col_widths[0] + col_widths[1])/2, results_y + row_height/2, "RESULT", 
           ha='center', va='center', fontsize=6, fontweight='bold', color='#ffd700')
    
    # Actual scores for each match
    for j in range(n_matches):
        col_idx = 2 + j
        x = x_positions[col_idx]
        w = col_widths[col_idx]
        
        # Get actual result
        if j < len(week_results) and week_results[j]:
            res = week_results[j]
            res_home = res.get('home', res.get('home_score', '-'))
            res_away = res.get('away', res.get('away_score', '-'))
            result_text = f"{res_home}-{res_away}"
        else:
            result_text = "-"
        
        rect = plt.Rectangle((x, results_y), w, row_height, 
                            facecolor=result_bg, edgecolor='#1a252f', linewidth=0.5)
        ax.add_patch(rect)
        ax.text(x + w/2, results_y + row_height/2, result_text, 
               ha='center', va='center', fontsize=7, fontweight='bold', color='#ffd700')
    
    # Empty cells for PTS and KK columns in results row
    for col_idx in [2 + n_matches, 2 + n_matches + 1]:
        rect = plt.Rectangle((x_positions[col_idx], results_y), col_widths[col_idx], row_height, 
                            facecolor=result_bg, edgecolor='#1a252f', linewidth=0.5)
        ax.add_patch(rect)
    
    # Draw participant data rows
    for i, row in enumerate(table_data):
        y = table_top - (i + 3) * row_height  # +3 to account for header and results row
        
        # Rank cell
        if row['rank'] == 1:
            rank_bg = gold
            rank_text = '#333'
        elif row['rank'] == 2:
            rank_bg = silver
            rank_text = '#333'
        elif row['rank'] == 3:
            rank_bg = bronze
            rank_text = 'white'
        else:
            rank_bg = 'white'
            rank_text = '#333'
        
        rect = plt.Rectangle((x_positions[0], y), col_widths[0], row_height, 
                            facecolor=rank_bg, edgecolor='#e0e0e0', linewidth=0.5)
        ax.add_patch(rect)
        ax.text(x_positions[0] + col_widths[0]/2, y + row_height/2, str(row['rank']), 
               ha='center', va='center', fontsize=7, fontweight='bold', color=rank_text)
        
        # Name cell
        rect = plt.Rectangle((x_positions[1], y), col_widths[1], row_height, 
                            facecolor='white', edgecolor='#e0e0e0', linewidth=0.5)
        ax.add_patch(rect)
        ax.text(x_positions[1] + col_widths[1]/2, y + row_height/2, row['name'][:12], 
               ha='center', va='center', fontsize=6, fontweight='bold', color='#333')
        
        # Prediction cells
        for j, pred in enumerate(row['predictions']):
            col_idx = 2 + j
            x = x_positions[col_idx]
            w = col_widths[col_idx]
            
            if pred['is_exact']:
                cell_bg = purple if pred['is_gotw'] else green
            elif pred['is_correct']:
                cell_bg = purple if pred['is_gotw'] else yellow
            else:
                cell_bg = red
            
            cell_text = 'white' if cell_bg in [green, red, purple] else '#333'
            
            rect = plt.Rectangle((x, y), w, row_height, 
                                facecolor=cell_bg, edgecolor='#e0e0e0', linewidth=0.5)
            ax.add_patch(rect)
            ax.text(x + w/2, y + row_height/2, f"{pred['pred_home']}-{pred['pred_away']}", 
                   ha='center', va='center', fontsize=6, fontweight='bold', color=cell_text)
        
        # PTS cell
        pts_idx = 2 + n_matches
        rect = plt.Rectangle((x_positions[pts_idx], y), col_widths[pts_idx], row_height, 
                            facecolor='#17a2b8', edgecolor='#e0e0e0', linewidth=0.5)
        ax.add_patch(rect)
        ax.text(x_positions[pts_idx] + col_widths[pts_idx]/2, y + row_height/2, str(row['total_points']), 
               ha='center', va='center', fontsize=7, fontweight='bold', color='white')
        
        # KK cell
        kk_idx = 2 + n_matches + 1
        rect = plt.Rectangle((x_positions[kk_idx], y), col_widths[kk_idx], row_height, 
                            facecolor=green, edgecolor='#e0e0e0', linewidth=0.5)
        ax.add_patch(rect)
        ax.text(x_positions[kk_idx] + col_widths[kk_idx]/2, y + row_height/2, str(row['kk_count']), 
               ha='center', va='center', fontsize=7, fontweight='bold', color='white')
    
    # Legend
    legend_y = table_top - (n_participants + 4) * row_height
    legend_items = [
        (green, 'Exact (KK) = 6pts'),
        (yellow, 'Correct = 3pts'),
        (red, 'Wrong = 0pts'),
        (purple, 'GOTW = 10/5pts')
    ]
    legend_x = 0.15
    for color, label in legend_items:
        rect = plt.Rectangle((legend_x, legend_y), 0.02, 0.02, facecolor=color, edgecolor='#333', linewidth=0.5)
        ax.add_patch(rect)
        ax.text(legend_x + 0.025, legend_y + 0.01, label, ha='left', va='center', fontsize=6, color='#333')
        legend_x += 0.18
    
    # Footer
    ax.text(0.5, 0.02, f"Generated: {datetime.now().strftime('%d %b %Y %H:%M')}", 
           ha='center', va='bottom', fontsize=7, color='#6c757d', style='italic')
    
    plt.tight_layout()
    
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=150, bbox_inches='tight', 
                facecolor='white', edgecolor='none', pad_inches=0.1)
    buf.seek(0)
    plt.close(fig)
    
    return buf.getvalue()

# Custom CSS for the results table
st.markdown("""
<style>
    /* Main header styling */
    .week-header {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 10px;
        text-align: center;
        margin-bottom: 1.5rem;
    }
    
    .week-header h1 {
        margin: 0;
        font-size: 2rem;
        color: #00d4ff;
    }
    
    .week-header p {
        margin: 0.5rem 0 0 0;
        color: #aaa;
    }
    
    /* Results table styling */
    .results-table {
        width: 100%;
        border-collapse: collapse;
        font-size: 0.85rem;
        background: white;
        border-radius: 10px;
        overflow: hidden;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    .results-table th {
        background: #1a1a2e;
        color: white;
        padding: 10px 8px;
        text-align: center;
        font-weight: 600;
        border: 1px solid #2a2a4e;
    }
    
    .results-table td {
        padding: 8px 6px;
        text-align: center;
        border: 1px solid #e0e0e0;
    }
    
    .results-table tr:nth-child(even) {
        background: #f8f9fa;
    }
    
    .results-table tr:hover {
        background: #e8f4f8;
    }
    
    /* Score cells */
    .exact-score {
        background: #28a745 !important;
        color: white;
        font-weight: bold;
    }
    
    .correct-result {
        background: #ffc107 !important;
        color: #333;
        font-weight: bold;
    }
    
    .wrong {
        background: #dc3545 !important;
        color: white;
    }
    
    .gotw-cell {
        background: #9b59b6 !important;
        color: white;
        font-weight: bold;
    }
    
    /* Points column */
    .points-col {
        background: #17a2b8 !important;
        color: white;
        font-weight: bold;
        font-size: 1rem;
    }
    
    /* KK column */
    .kk-col {
        background: #28a745 !important;
        color: white;
        font-weight: bold;
    }
    
    /* Rank badges */
    .rank-1 { background: gold; color: #333; }
    .rank-2 { background: silver; color: #333; }
    .rank-3 { background: #cd7f32; color: white; }
    
    /* Match header */
    .match-header {
        font-size: 0.75rem;
        line-height: 1.2;
    }
    
    .match-teams {
        font-weight: bold;
        color: #1a1a2e;
    }
    
    .match-score {
        color: #dc3545;
        font-weight: bold;
    }
    
    /* Champion banner */
    .champion-banner {
        background: linear-gradient(135deg, #ffd700 0%, #ffed4a 100%);
        color: #1a1a2e;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        margin: 1rem 0;
        font-weight: bold;
        font-size: 1.2rem;
    }
    
    /* Legend */
    .legend {
        display: flex;
        gap: 1rem;
        flex-wrap: wrap;
        margin: 1rem 0;
        padding: 1rem;
        background: #f8f9fa;
        border-radius: 8px;
    }
    
    .legend-item {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        font-size: 0.85rem;
    }
    
    .legend-box {
        width: 20px;
        height: 20px;
        border-radius: 4px;
    }
</style>
""", unsafe_allow_html=True)

# Authentication - optional for viewing
# if not check_password():
#     st.stop()

# Logo in sidebar
if Path("nikkang_logo.png").exists():
    st.sidebar.image("nikkang_logo.png", width='stretch')
    st.sidebar.markdown("---")

# Initialize data manager
dm = DataManager()

# Team abbreviation mapping
TEAM_ABBREV = {
    'Arsenal': 'ARS', 'Aston Villa': 'AVL', 'Bournemouth': 'BOU', 'Brentford': 'BRE',
    'Brighton': 'BHA', 'Chelsea': 'CHE', 'Crystal Palace': 'CRY', 'Everton': 'EVE',
    'Fulham': 'FUL', 'Ipswich Town': 'IPS', 'Ipswich': 'IPS', 'Leicester City': 'LEI',
    'Leicester': 'LEI', 'Liverpool': 'LIV', 'Man City': 'MCI', 'Manchester City': 'MCI',
    'Man United': 'MUN', 'Manchester United': 'MUN', 'Newcastle': 'NEW', 'Newcastle United': 'NEW',
    "Nott'm Forest": 'NFO', 'Nottingham Forest': 'NFO', 'Southampton': 'SOU', 'Tottenham': 'TOT',
    'Spurs': 'TOT', 'West Ham': 'WHU', 'West Ham United': 'WHU', 'Wolves': 'WOL',
    'Wolverhampton': 'WOL', 'Burnley': 'BUR', 'Luton': 'LUT', 'Luton Town': 'LUT',
    'Sheffield United': 'SHU', 'Sheffield Utd': 'SHU', 'Leeds': 'LEE', 'Leeds United': 'LEE',
    'Sunderland': 'SUN'
}

def get_team_abbrev(team_name):
    """Get proper 3-letter abbreviation for team"""
    if not team_name:
        return 'TBC'
    # Check exact match first
    if team_name in TEAM_ABBREV:
        return TEAM_ABBREV[team_name]
    # Check partial match
    for full_name, abbrev in TEAM_ABBREV.items():
        if full_name.lower() in team_name.lower() or team_name.lower() in full_name.lower():
            return abbrev
    # Fallback to first 3 chars
    return team_name[:3].upper()

# Team abbreviations mapping
TEAM_ABBREV = {
    'Arsenal': 'ARS',
    'Aston Villa': 'AVL',
    'Bournemouth': 'BOU',
    'Brentford': 'BRE',
    'Brighton': 'BHA',
    'Chelsea': 'CHE',
    'Crystal Palace': 'CRY',
    'Everton': 'EVE',
    'Fulham': 'FUL',
    'Ipswich Town': 'IPS',
    'Ipswich': 'IPS',
    'Leicester City': 'LEI',
    'Leicester': 'LEI',
    'Liverpool': 'LIV',
    'Man City': 'MCI',
    'Manchester City': 'MCI',
    'Man United': 'MUN',
    'Manchester United': 'MUN',
    'Newcastle': 'NEW',
    'Newcastle United': 'NEW',
    "Nott'm Forest": 'NFO',
    'Nottingham Forest': 'NFO',
    'Southampton': 'SOU',
    'Tottenham': 'TOT',
    'Spurs': 'TOT',
    'West Ham': 'WHU',
    'Wolves': 'WOL',
    'Wolverhampton': 'WOL',
    'Burnley': 'BUR',
    'Luton': 'LUT',
    'Luton Town': 'LUT',
    'Sheffield United': 'SHU',
    'Sheffield Utd': 'SHU',
    'Sunderland': 'SUN',
    'Leeds': 'LEE',
    'Leeds United': 'LEE',
}

def get_team_abbrev(team_name):
    """Get proper 3-letter abbreviation for team"""
    if not team_name:
        return 'TBC'
    # Check exact match first
    if team_name in TEAM_ABBREV:
        return TEAM_ABBREV[team_name]
    # Check partial match
    for full_name, abbrev in TEAM_ABBREV.items():
        if full_name.lower() in team_name.lower() or team_name.lower() in full_name.lower():
            return abbrev
    # Fallback to first 3 letters
    return team_name[:3].upper()

# Header
st.markdown('<div style="background:linear-gradient(135deg,#1a1a2e 0%,#16213e 100%);color:white;padding:1.5rem;border-radius:10px;text-align:center;margin-bottom:1.5rem;"><h1 style="margin:0;font-size:2rem;color:#00d4ff;">📊 Weekly Prediction Results</h1><p style="margin:0.5rem 0 0 0;color:#aaa;">Detailed breakdown of predictions vs actual results</p></div>', unsafe_allow_html=True)

# Load data
participants = dm.get_all_participants()
matches_data = dm.load_matches()
predictions_data = dm.load_predictions()
results_data = dm.load_results()

# Week selector
available_weeks = sorted([int(w) for w in matches_data.keys() if matches_data.get(w)], reverse=True)

if not available_weeks:
    st.warning("No match data available yet.")
    st.stop()

# Filter to weeks 11 onwards
available_weeks = [w for w in available_weeks if w >= 11]

if not available_weeks:
    st.info("Weekly results are available from Week 11 onwards.")
    st.stop()

selected_week = st.selectbox(
    "🗓️ Select Gameweek:",
    available_weeks,
    format_func=lambda x: f"Gameweek {x}"
)

st.markdown("---")

# Get data for selected week
week_str = str(selected_week)
week_matches = matches_data.get(week_str, [])
week_results = results_data.get(week_str, [])
week_predictions = predictions_data.get(week_str, {})

if not week_matches:
    st.warning(f"No matches found for Gameweek {selected_week}")
    st.stop()

if not week_results:
    st.info(f"Results not yet available for Gameweek {selected_week}")
    st.stop()

# Find GOTW match index
gotw_index = None
for idx, match in enumerate(week_matches):
    if match.get('gotw', False):
        gotw_index = idx
        break

# Build results table data
table_data = []

for p in participants:
    if p.get('status') != 'active':
        continue
    
    p_id = p.get('id')
    p_name = p.get('display_name') or p.get('name', 'Unknown')
    
    # Get predictions for this participant
    p_preds = week_predictions.get(p_id, [])
    
    if not p_preds:
        continue
    
    row = {
        'name': p_name,
        'predictions': [],
        'points_per_match': [],
        'total_points': 0,
        'kk_count': 0,
        'gotw_kk': 0
    }
    
    for idx, match in enumerate(week_matches):
        # Get prediction
        if idx < len(p_preds):
            pred = p_preds[idx]
            if isinstance(pred, dict):
                pred_home = pred.get('home', pred.get('home_score', '-'))
                pred_away = pred.get('away', pred.get('away_score', '-'))
            else:
                pred_home = '-'
                pred_away = '-'
        else:
            pred_home = '-'
            pred_away = '-'
        
        # Get actual result
        if idx < len(week_results):
            result = week_results[idx]
            if isinstance(result, dict):
                actual_home = result.get('home', result.get('home_score', '-'))
                actual_away = result.get('away', result.get('away_score', '-'))
            else:
                actual_home = '-'
                actual_away = '-'
        else:
            actual_home = '-'
            actual_away = '-'
        
        # Calculate points
        is_gotw = (idx == gotw_index)
        points = 0
        is_exact = False
        is_correct = False
        
        try:
            pred_h = int(pred_home) if pred_home != '-' else -1
            pred_a = int(pred_away) if pred_away != '-' else -1
            act_h = int(actual_home) if actual_home != '-' else -2
            act_a = int(actual_away) if actual_away != '-' else -2
            
            if pred_h == act_h and pred_a == act_a:
                # Exact score
                is_exact = True
                points = 10 if is_gotw else 6
                row['kk_count'] += 1
                if is_gotw:
                    row['gotw_kk'] = 1
            else:
                # Check correct result
                pred_result = 'H' if pred_h > pred_a else ('A' if pred_a > pred_h else 'D')
                act_result = 'H' if act_h > act_a else ('A' if act_a > act_h else 'D')
                
                if pred_result == act_result:
                    is_correct = True
                    points = 5 if is_gotw else 3
        except:
            pass
        
        row['predictions'].append({
            'pred_home': pred_home,
            'pred_away': pred_away,
            'actual_home': actual_home,
            'actual_away': actual_away,
            'points': points,
            'is_exact': is_exact,
            'is_correct': is_correct,
            'is_gotw': is_gotw
        })
        row['points_per_match'].append(points)
        row['total_points'] += points
    
    table_data.append(row)

# Sort by total points (descending), then by KK count (descending)
table_data.sort(key=lambda x: (-x['total_points'], -x['kk_count']))

# Add rank - handle ties properly
prev_pts, prev_kk, prev_rank = None, None, 0
for idx, row in enumerate(table_data):
    if row['total_points'] == prev_pts and row['kk_count'] == prev_kk:
        # Same points AND KK = same rank (joint position)
        row['rank'] = prev_rank
    else:
        row['rank'] = idx + 1
        prev_rank = idx + 1
    prev_pts = row['total_points']
    prev_kk = row['kk_count']

# Find champion(s) - must have same points AND same KK to be joint winners
champions = []
if table_data:
    max_points = table_data[0]['total_points']
    max_kk_at_top = table_data[0]['kk_count']
    
    for r in table_data:
        if r['total_points'] == max_points and r['kk_count'] == max_kk_at_top:
            champions.append(r['name'])
        elif r['total_points'] < max_points:
            break  # No need to check further

# Display champion banner
if table_data and champions:
    if len(champions) == 1:
        champ_text = champions[0]
        banner_text = f"🏆 GAMEWEEK {selected_week} CHAMPION: {champ_text} 🏆"
    else:
        champ_text = ", ".join(champions)
        banner_text = f"🏆 GAMEWEEK {selected_week} JOINT CHAMPIONS: {champ_text} 🏆"
    st.markdown(f'<div style="background:linear-gradient(135deg,#ffd700 0%,#ffed4a 100%);color:#1a1a2e;padding:1rem;border-radius:10px;text-align:center;margin:1rem 0;font-weight:bold;font-size:1.2rem;">{banner_text}</div>', unsafe_allow_html=True)

# Legend
st.markdown('<div style="display:flex;gap:1rem;flex-wrap:wrap;margin:1rem 0;padding:1rem;background:#f8f9fa;border-radius:8px;"><div style="display:flex;align-items:center;gap:0.5rem;font-size:0.85rem;"><div style="width:20px;height:20px;border-radius:4px;background:#28a745;"></div><span>Exact Score (KK) = 6 pts</span></div><div style="display:flex;align-items:center;gap:0.5rem;font-size:0.85rem;"><div style="width:20px;height:20px;border-radius:4px;background:#ffc107;"></div><span>Correct Result = 3 pts</span></div><div style="display:flex;align-items:center;gap:0.5rem;font-size:0.85rem;"><div style="width:20px;height:20px;border-radius:4px;background:#dc3545;"></div><span>Wrong = 0 pts</span></div><div style="display:flex;align-items:center;gap:0.5rem;font-size:0.85rem;"><div style="width:20px;height:20px;border-radius:4px;background:#9b59b6;"></div><span>GOTW = 10/5 pts</span></div></div>', unsafe_allow_html=True)

# Build HTML table
html_table = '<table style="width:100%;border-collapse:collapse;font-size:0.85rem;background:white;border-radius:10px;overflow:hidden;box-shadow:0 4px 6px rgba(0,0,0,0.1);"><thead><tr>'
html_table += '<th style="width:30px;background:#1a1a2e;color:white;padding:10px 8px;text-align:center;border:1px solid #2a2a4e;">#</th>'
html_table += '<th style="width:100px;background:#1a1a2e;color:white;padding:10px 8px;text-align:center;border:1px solid #2a2a4e;">Name</th>'

# Match headers
for idx, match in enumerate(week_matches):
    home_team = get_team_abbrev(match.get('home', 'TBC'))
    away_team = get_team_abbrev(match.get('away', 'TBC'))
    
    # Get actual result for header
    if idx < len(week_results):
        result = week_results[idx]
        if isinstance(result, dict):
            r_home = result.get('home', result.get('home_score', '-'))
            r_away = result.get('away', result.get('away_score', '-'))
        else:
            r_home = '-'
            r_away = '-'
    else:
        r_home = '-'
        r_away = '-'
    
    gotw_marker = " ⭐" if idx == gotw_index else ""
    
    html_table += f'<th style="font-size:0.75rem;line-height:1.2;background:#1a1a2e;color:white;padding:10px 8px;text-align:center;border:1px solid #2a2a4e;"><div style="font-weight:bold;color:#00d4ff;">{home_team} v {away_team}</div><div style="color:#ff6b6b;font-weight:bold;">{r_home} - {r_away}{gotw_marker}</div></th>'

html_table += '<th style="width:50px;background:#1a1a2e;color:white;padding:10px 8px;text-align:center;border:1px solid #2a2a4e;">PTS</th>'
html_table += '<th style="width:40px;background:#1a1a2e;color:white;padding:10px 8px;text-align:center;border:1px solid #2a2a4e;">KK</th>'
html_table += '</tr></thead><tbody>'

# Data rows
for row in table_data:
    # Rank cell styling
    if row['rank'] == 1:
        rank_style = "background:gold;color:#333;font-weight:bold;padding:8px 6px;text-align:center;border:1px solid #e0e0e0;"
    elif row['rank'] == 2:
        rank_style = "background:silver;color:#333;font-weight:bold;padding:8px 6px;text-align:center;border:1px solid #e0e0e0;"
    elif row['rank'] == 3:
        rank_style = "background:#cd7f32;color:white;font-weight:bold;padding:8px 6px;text-align:center;border:1px solid #e0e0e0;"
    else:
        rank_style = "font-weight:bold;padding:8px 6px;text-align:center;border:1px solid #e0e0e0;"
    
    html_table += f'<tr><td style="{rank_style}">{row["rank"]}</td>'
    html_table += f'<td style="text-align:left;padding:8px 10px;font-weight:500;border:1px solid #e0e0e0;">{row["name"]}</td>'
    
    for pred in row['predictions']:
        # Inline styles for each cell type
        if pred['is_exact']:
            if pred['is_gotw']:
                cell_style = "background:#9b59b6;color:white;font-weight:bold;padding:8px 6px;text-align:center;border:1px solid #e0e0e0;"
            else:
                cell_style = "background:#28a745;color:white;font-weight:bold;padding:8px 6px;text-align:center;border:1px solid #e0e0e0;"
        elif pred['is_correct']:
            if pred['is_gotw']:
                cell_style = "background:#8e44ad;color:white;font-weight:bold;padding:8px 6px;text-align:center;border:1px solid #e0e0e0;"
            else:
                cell_style = "background:#ffc107;color:#333;font-weight:bold;padding:8px 6px;text-align:center;border:1px solid #e0e0e0;"
        else:
            cell_style = "background:#dc3545;color:white;padding:8px 6px;text-align:center;border:1px solid #e0e0e0;"
        
        html_table += f'<td style="{cell_style}">{pred["pred_home"]}-{pred["pred_away"]}<br><small>({pred["points"]})</small></td>'
    
    html_table += f'<td style="background:#17a2b8;color:white;font-weight:bold;font-size:1rem;padding:8px 6px;text-align:center;border:1px solid #e0e0e0;">{row["total_points"]}</td>'
    html_table += f'<td style="background:#28a745;color:white;font-weight:bold;padding:8px 6px;text-align:center;border:1px solid #e0e0e0;">{row["kk_count"]}</td></tr>'

html_table += '</tbody></table>'

st.markdown(html_table, unsafe_allow_html=True)

# Download as PNG button
col_dl1, col_dl2, col_dl3 = st.columns([1, 1, 2])
with col_dl1:
    if table_data:
        # Get champion points and KK for the PNG
        champ_pts = table_data[0]['total_points'] if table_data else 0
        champ_kk = table_data[0]['kk_count'] if table_data else 0
        png_bytes = generate_weekly_results_png(
            table_data, week_matches, week_results, selected_week, gotw_index, get_team_abbrev,
            champions=champions, champ_pts=champ_pts, champ_kk=champ_kk
        )
        st.download_button(
            label="📥 Download as PNG",
            data=png_bytes,
            file_name=f"nikkang_week{selected_week}_{datetime.now().strftime('%Y%m%d')}.png",
            mime="image/png",
            key="download_weekly_png"
        )

# Summary stats
st.markdown("---")
st.markdown("### 📈 Gameweek Statistics")

col1, col2, col3, col4 = st.columns(4)

with col1:
    total_participants = len(table_data)
    st.metric("Participants", total_participants)

with col2:
    if table_data:
        avg_points = sum(r['total_points'] for r in table_data) / len(table_data)
        st.metric("Avg Points", f"{avg_points:.1f}")
    else:
        st.metric("Avg Points", "0")

with col3:
    if table_data:
        total_kk = sum(r['kk_count'] for r in table_data)
        st.metric("Total KK", total_kk)
    else:
        st.metric("Total KK", "0")

with col4:
    if table_data:
        max_pts = table_data[0]['total_points']
        st.metric("Highest Score", max_pts)
    else:
        st.metric("Highest Score", "0")

# Top 3 section
if len(table_data) >= 3:
    st.markdown("### 🏆 Top 3 This Week")
    
    col1, col2, col3 = st.columns(3)
    
    medals = ["🥇", "🥈", "🥉"]
    colors = ["#ffd700", "#c0c0c0", "#cd7f32"]
    
    for i, col in enumerate([col1, col2, col3]):
        with col:
            if i < len(table_data):
                row = table_data[i]
                st.markdown(f'<div style="background:{colors[i]};padding:1rem;border-radius:10px;text-align:center;"><div style="font-size:2rem;">{medals[i]}</div><div style="font-weight:bold;font-size:1.1rem;color:#333;">{row["name"]}</div><div style="font-size:1.5rem;font-weight:bold;color:#1a1a2e;">{row["total_points"]} pts</div><div style="color:#555;">KK: {row["kk_count"]}</div></div>', unsafe_allow_html=True)

# Week navigation
st.markdown("---")
col1, col2, col3 = st.columns([1, 2, 1])

with col1:
    prev_week = selected_week - 1
    if prev_week >= 11 and prev_week in available_weeks:
        if st.button(f"⬅️ Week {prev_week}"):
            st.query_params["week"] = prev_week
            st.rerun()

with col3:
    next_week = selected_week + 1
    if next_week in available_weeks:
        if st.button(f"Week {next_week} ➡️"):
            st.query_params["week"] = next_week
            st.rerun()

# Footer
st.markdown("---")
st.caption(f"Nikkang KK EPL Prediction Competition 2025-26 • Gameweek {selected_week}")

"""
Prediction Matrix - View All Predictions
Nikkang KK EPL Prediction Competition
See what everyone has predicted for each match
COMPLETE FIXED VERSION
"""

import streamlit as st
import pandas as pd
from pathlib import Path
from datetime import datetime
import sys

sys.path.append(str(Path(__file__).parent.parent))

from utils.data_manager import DataManager
from utils.sync_ui import add_sync_buttons_sidebar, validate_week

# Page config
st.set_page_config(
    page_title="Prediction Matrix - Nikkang KK",
    page_icon="📋",
    layout="wide"
)

# Initialize data manager and sync
dm = DataManager()
current_week = validate_week(dm)
add_sync_buttons_sidebar(dm)

# Import branding
try:
    from utils.branding import inject_custom_css
    inject_custom_css()
except:
    pass

# Custom CSS
st.markdown("""
<style>
    .matrix-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 10px;
        text-align: center;
        margin-bottom: 1.5rem;
    }
    .prediction-cell {
        padding: 0.5rem;
        text-align: center;
        border-radius: 5px;
        font-weight: bold;
    }
    .prediction-locked {
        background: #f8f9fa;
        color: #6c757d;
    }
    .prediction-submitted {
        background: #d4edda;
        color: #155724;
    }
    .prediction-pending {
        background: #fff3cd;
        color: #856404;
    }
    .gotw-match {
        border: 2px solid #ffc107;
        background: #fff9e6;
    }
    .stats-card {
        background: white;
        border-radius: 10px;
        padding: 1rem;
        text-align: center;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

# Logo in sidebar
if Path("nikkang_logo.png").exists():
    st.sidebar.image("nikkang_logo.png", use_column_width=True)
    st.sidebar.markdown("---")

# Header
st.markdown("""
<div class="matrix-header">
    <h1 style="margin: 0; font-size: 2rem;">📋 Prediction Matrix</h1>
    <p style="margin: 0.5rem 0 0 0; opacity: 0.9;">See what everyone has predicted</p>
</div>
""", unsafe_allow_html=True)

# Load data
participants = dm.get_all_participants()
matches_data = dm.load_matches()
predictions_data = dm.load_predictions()

# Get available weeks
available_weeks = sorted([int(w) for w in matches_data.keys() if matches_data.get(w)], reverse=True)

if not available_weeks:
    st.warning("No matches set up yet.")
    st.stop()

# Put current week at top
weeks_sorted = sorted(available_weeks, reverse=True)
if current_week in weeks_sorted:
    weeks_sorted.remove(current_week)
    weeks_sorted.insert(0, current_week)

# Week selector
selected_week = st.selectbox(
    "🗓️ Select Gameweek:",
    weeks_sorted,
    format_func=lambda x: f"Gameweek {x}{' (Current)' if x == current_week else ''}"
)

st.markdown("---")

# Get data for selected week
week_str = str(selected_week)
week_matches = matches_data.get(week_str, [])
week_predictions = predictions_data.get(week_str, {})

if not week_matches:
    st.warning(f"No matches found for Gameweek {selected_week}")
    st.stop()

# Count participants with predictions
participants_with_predictions = 0
for p in participants:
    if not isinstance(p, dict):
        continue
    p_id = p.get('id', '')
    if p_id in week_predictions and week_predictions[p_id]:
        participants_with_predictions += 1

# Summary stats
st.markdown("### 📊 Summary")

col1, col2, col3, col4 = st.columns(4)

with col1:
    total_participants = len([p for p in participants if isinstance(p, dict)])
    st.metric("Total Participants", total_participants)

with col2:
    st.metric("Predictions Submitted", participants_with_predictions)

with col3:
    completion_rate = (participants_with_predictions / total_participants * 100) if total_participants > 0 else 0
    st.metric("Completion Rate", f"{completion_rate:.0f}%")

with col4:
    st.metric("Matches This Week", len(week_matches))

st.markdown("---")

# Build prediction matrix
st.markdown("### 📋 Prediction Matrix")

# Create matrix data
matrix_data = []

for p in participants:
    # SAFETY CHECK - Skip if not a dict
    if not isinstance(p, dict):
        continue
    
    p_id = p.get('id', '')
    p_name = p.get('display_name') or p.get('name', 'Unknown')
    
    # Get predictions for this participant
    p_preds = week_predictions.get(p_id, [])
    
    row = {'Name': p_name}
    
    # Add each match prediction
    for idx, match in enumerate(week_matches):
        home = match.get('home', 'TBC')
        away = match.get('away', 'TBC')
        is_gotw = match.get('gotw', False)
        
        match_label = f"{home[:3].upper()} v {away[:3].upper()}"
        if is_gotw:
            match_label += " ⭐"
        
        # Get prediction for this match
        if idx < len(p_preds) and p_preds[idx]:
            pred = p_preds[idx]
            if isinstance(pred, dict):
                pred_home = pred.get('home', pred.get('home_score', '-'))
                pred_away = pred.get('away', pred.get('away_score', '-'))
                row[match_label] = f"{pred_home}-{pred_away}"
            else:
                row[match_label] = "-"
        else:
            row[match_label] = "-"
    
    matrix_data.append(row)

# Display as DataFrame
if matrix_data:
    df = pd.DataFrame(matrix_data)
    st.dataframe(df, use_container_width=True, hide_index=True)
else:
    st.info("No predictions submitted yet for this gameweek.")

st.markdown("---")

# Match-by-match breakdown
st.markdown("### 🎯 Match-by-Match Breakdown")

for idx, match in enumerate(week_matches):
    home = match.get('home', 'TBC')
    away = match.get('away', 'TBC')
    is_gotw = match.get('gotw', False)
    match_date = match.get('date', '')
    match_time = match.get('time', '')
    
    # Match header
    gotw_badge = "⭐ GAME OF THE WEEK" if is_gotw else ""
    
    with st.expander(f"Match {idx + 1}: {home} vs {away} {gotw_badge}"):
        st.markdown(f"**Date:** {match_date} {match_time}")
        
        if is_gotw:
            st.info("💰 Double points for this match! (10/5 pts)")
        
        # Collect predictions for this match
        match_predictions = []
        
        for p in participants:
            # SAFETY CHECK
            if not isinstance(p, dict):
                continue
            
            p_id = p.get('id', '')
            p_name = p.get('display_name') or p.get('name', 'Unknown')
            
            p_preds = week_predictions.get(p_id, [])
            
            if idx < len(p_preds) and p_preds[idx]:
                pred = p_preds[idx]
                if isinstance(pred, dict):
                    pred_home = pred.get('home', pred.get('home_score', '-'))
                    pred_away = pred.get('away', pred.get('away_score', '-'))
                    match_predictions.append({
                        'Participant': p_name,
                        'Prediction': f"{pred_home} - {pred_away}"
                    })
        
        if match_predictions:
            pred_df = pd.DataFrame(match_predictions)
            st.dataframe(pred_df, use_container_width=True, hide_index=True)
            
            # Show popular predictions
            predictions_count = {}
            for mp in match_predictions:
                pred = mp['Prediction']
                predictions_count[pred] = predictions_count.get(pred, 0) + 1
            
            if predictions_count:
                most_popular = max(predictions_count.items(), key=lambda x: x[1])
                st.markdown(f"**Most popular prediction:** {most_popular[0]} ({most_popular[1]} participants)")
        else:
            st.info("No predictions submitted for this match yet.")

st.markdown("---")

# Popular predictions summary
st.markdown("### 🔥 Most Popular Predictions")

all_predictions = {}

for idx, match in enumerate(week_matches):
    home = match.get('home', 'TBC')
    away = match.get('away', 'TBC')
    match_key = f"{home} v {away}"
    
    predictions_count = {}
    
    for p in participants:
        # SAFETY CHECK
        if not isinstance(p, dict):
            continue
        
        p_id = p.get('id', '')
        p_preds = week_predictions.get(p_id, [])
        
        if idx < len(p_preds) and p_preds[idx]:
            pred = p_preds[idx]
            if isinstance(pred, dict):
                pred_home = pred.get('home', pred.get('home_score', '-'))
                pred_away = pred.get('away', pred.get('away_score', '-'))
                pred_str = f"{pred_home}-{pred_away}"
                predictions_count[pred_str] = predictions_count.get(pred_str, 0) + 1
    
    if predictions_count:
        most_popular = max(predictions_count.items(), key=lambda x: x[1])
        all_predictions[match_key] = f"{most_popular[0]} ({most_popular[1]} picks)"

if all_predictions:
    pop_df = pd.DataFrame([
        {'Match': k, 'Most Popular': v} 
        for k, v in all_predictions.items()
    ])
    st.dataframe(pop_df, use_container_width=True, hide_index=True)
else:
    st.info("No predictions data available.")

# Footer
st.markdown("---")
st.caption(f"Nikkang KK EPL Prediction Competition 2025-26 • Gameweek {selected_week}")

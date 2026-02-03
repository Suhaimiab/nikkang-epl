"""
Make Predictions Page - FIXED VERSION
Nikkang KK EPL Prediction Competition

FIXES:
- Predictions now reload correctly when week changes
- Changes are properly reflected when you come back
- No more stale data showing wrong scores
- CURRENT WEEK AT TOP OF SELECTOR
"""

import streamlit as st
from pathlib import Path
import sys
from utils.prediction_tracker import PredictionTracker

from utils.data_manager import DataManager
from utils.sync_ui import add_sync_buttons_sidebar, validate_week

# Add utils to path
sys.path.append(str(Path(__file__).parent.parent))

from utils.participant_auth import (
    require_participant_auth,
    participant_info_sidebar,
    get_current_participant_id,
    get_current_participant_name
)
from utils.data_manager import DataManager

# Page config
st.set_page_config(
    page_title="Make Predictions - Nikkang KK",
    page_icon="🎯",
    layout="wide"
)

dm = DataManager()
current_week = validate_week(dm)
add_sync_buttons_sidebar(dm)

# REQUIRE AUTHENTICATION
require_participant_auth()

# Show participant info in sidebar
participant_info_sidebar()

# Logo
if Path("nikkang_logo.png").exists():
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.image("nikkang_logo.png", width=200)

# Get current participant
participant_id = get_current_participant_id()
participant_name = get_current_participant_name()

# Welcome message
st.title("🎯 Make Your Predictions")
st.markdown(f"### Welcome, {participant_name}!")
st.markdown("---")

# Initialize data manager
dm = DataManager()

st.info("🎯 **Prediction system**: Select gameweek, enter predictions, and submit!")

# Get available weeks
weeks = dm.get_weeks()

if not weeks:
    st.info("No gameweeks available yet. Check back soon!")
    st.stop()

# Get current week
current_week = dm.get_current_week()

# Sort weeks with current week at top
weeks_sorted = sorted(weeks)
if current_week in weeks_sorted:
    weeks_sorted.remove(current_week)
    weeks_sorted = [current_week] + weeks_sorted

# IMPORTANT: Select week FIRST with current week at top
selected_week = st.selectbox(
    "Select Gameweek:", 
    options=weeks_sorted,
    format_func=lambda x: f"Week {x} {'✅ (Current)' if x == current_week else ''}",
    help="Current week is shown at the top",
    key="week_selector"
)

# NOW load predictions for the selected week
# This ensures fresh data every time week changes
all_predictions = dm.load_predictions()
week_key = str(selected_week)
week_predictions = all_predictions.get(week_key, {})
my_predictions = week_predictions.get(participant_id, [])

# Get matches for this week
matches = dm.get_matches_by_week(selected_week)

if not matches:
    st.warning("No matches available for this week yet.")
    st.stop()

# Display prediction form
st.markdown(f"### Gameweek {selected_week} - {len(matches)} Matches")

# Show if already predicted
if my_predictions:
    st.success(f"✅ You have already made predictions for Week {selected_week}. You can update them below.")
else:
    st.info(f"📝 Make your predictions for Week {selected_week} below.")

with st.form(f"predictions_week_{selected_week}"):
    predictions = []
    
    for idx, match in enumerate(matches):
        st.markdown(f"**Match {idx+1}**: {match.get('home', 'TBC')} vs {match.get('away', 'TBC')}")
        
        # Show GOTW badge
        if match.get('gotw', False):
            st.markdown("⭐ **GAME OF THE WEEK** - Double Points!")
        
        # Get existing prediction if any
        existing_pred = {}
        if idx < len(my_predictions):
            existing_pred = my_predictions[idx]
        
        # CRITICAL FIX: Default to 0 if no prediction exists
        default_home = existing_pred.get('home', 0) if existing_pred else 0
        default_away = existing_pred.get('away', 0) if existing_pred else 0
        
        col1, col2, col3 = st.columns([2, 1, 2])
        
        with col1:
            st.markdown(f"**{match.get('home', 'TBC')}**")
        
        with col2:
            home_score = st.number_input(
                "H", 
                min_value=0, 
                max_value=20, 
                value=int(default_home),  # Ensure it's an int
                key=f"home_{selected_week}_{idx}",  # Unique key per week
                label_visibility="collapsed"
            )
            st.markdown("**-**")
            away_score = st.number_input(
                "A", 
                min_value=0, 
                max_value=20, 
                value=int(default_away),  # Ensure it's an int
                key=f"away_{selected_week}_{idx}",  # Unique key per week
                label_visibility="collapsed"
            )
        
        with col3:
            st.markdown(f"**{match.get('away', 'TBC')}**")
        
        # Store prediction
        predictions.append({
            'home': int(home_score),
            'away': int(away_score)
        })
        
        st.markdown("---")
    
    # Submit button
    submitted = st.form_submit_button(
        "💾 Save Predictions", 
        width='stretch', 
        type="primary"
    )
    
    if submitted:
        # Save predictions
        # Reload to ensure we have latest data
        all_predictions = dm.load_predictions()
        
        if week_key not in all_predictions:
            all_predictions[week_key] = {}
        
        # Save as list format
        all_predictions[week_key][participant_id] = predictions
        
        # Save to file
        success = dm.save_predictions(all_predictions)
        
        if success:
            # Use prediction tracker for timestamp
            tracker = PredictionTracker(dm)
            is_late, submit_time = tracker.save_prediction_with_timestamp(
                week=selected_week,
                participant_id=participant_id,
                predictions=predictions
            )
            
            if is_late:
                st.warning(f"⚠️ Late submission (after deadline) - will score 0 points")
                st.caption(f"Submitted at: {submit_time}")
            else:
                st.success(f"✅ Predictions saved successfully for Week {selected_week}!")
                st.caption(f"Submitted at: {submit_time}")
            
            st.balloons()
            
            # Force reload
            st.rerun()
        else:
            st.error("❌ Error saving predictions. Please try again.")

# Show prediction summary
st.markdown("---")
st.markdown("### 📊 Your Prediction Summary")

# Show current week's predictions
if my_predictions:
    st.markdown(f"#### Week {selected_week} Predictions:")
    
    for idx, match in enumerate(matches):
        if idx < len(my_predictions):
            pred = my_predictions[idx]
            home_score = pred.get('home', 0)
            away_score = pred.get('away', 0)
            
            st.caption(
                f"**{match.get('home', 'TBC')}** {home_score} - {away_score} **{match.get('away', 'TBC')}**"
            )
else:
    st.info("No predictions made for this week yet.")

# Show prediction history
st.markdown("---")
st.markdown("### 📅 Your Prediction History")

all_predictions = dm.load_predictions()
my_weeks = []

for week_str, week_data in all_predictions.items():
    if week_str.isdigit() and participant_id in week_data:
        my_weeks.append(int(week_str))

if my_weeks:
    my_weeks.sort()
    st.success(
        f"✅ You have made predictions for {len(my_weeks)} gameweeks: "
        f"{', '.join(f'Week {w}' for w in my_weeks)}"
    )
    
    # Show weeks in expandable sections
    with st.expander("📋 View All Your Predictions"):
        for week_num in sorted(my_weeks, reverse=True):
            week_key = str(week_num)
            week_preds = all_predictions[week_key][participant_id]
            week_matches = dm.get_matches_by_week(week_num)
            
            st.markdown(f"**Week {week_num}:**")
            
            for idx, match in enumerate(week_matches):
                if idx < len(week_preds):
                    pred = week_preds[idx]
                    st.caption(
                        f"{match.get('home', 'TBC')} {pred.get('home', 0)} - "
                        f"{pred.get('away', 0)} {match.get('away', 'TBC')}"
                    )
            st.markdown("---")
else:
    st.info("You haven't made any predictions yet. Get started above!")

# Footer
st.markdown("---")
st.caption("Nikkang KK EPL Prediction Competition 2025-26")
st.caption("💡 Tip: You can update your predictions anytime before the deadline!")

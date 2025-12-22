"""
Make Predictions Page - WITH AUTHENTICATION
Nikkang KK EPL Prediction Competition

Requires participant login before making predictions
"""

import streamlit as st
from pathlib import Path
import sys
from utils.prediction_tracker import PredictionTracker

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

# REQUIRE AUTHENTICATION - This will show login form if not logged in
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

# Rest of your predictions page code here...
# (I'll show the key parts that need to use participant_id)

st.info("🎯 **Prediction system**: Select gameweek, enter predictions, and submit!")

# Example: Get participant's existing predictions
st.markdown("### Your Predictions")

weeks = dm.get_weeks()

if weeks:
    selected_week = st.selectbox("Select Gameweek:", weeks, format_func=lambda x: f"Week {x}")
    
    # Load participant's predictions for this week
    all_predictions = dm.load_predictions()
    week_predictions = all_predictions.get(str(selected_week), {})
    my_predictions = week_predictions.get(participant_id, [])
    
    # Get matches for this week
    matches = dm.get_matches_by_week(selected_week)
    
    if matches:
        st.markdown(f"#### Gameweek {selected_week} - {len(matches)} Matches")
        
        # Display prediction form
        with st.form(f"predictions_week_{selected_week}"):
            predictions = []
            
            for idx, match in enumerate(matches):
                st.markdown(f"**Match {idx+1}**: {match.get('home', 'TBC')} vs {match.get('away', 'TBC')}")
                
                # Show GOTW badge
                if match.get('gotw', False):
                    st.markdown("⭐ **GAME OF THE WEEK** - Double Points!")
                
                col1, col2, col3 = st.columns([2, 1, 2])
                
                # Get existing prediction if any
                existing_pred = my_predictions[idx] if idx < len(my_predictions) else {}
                
                with col1:
                    st.markdown(f"**{match.get('home', 'TBC')}**")
                with col2:
                    home_score = st.number_input(
                        "H", 
                        min_value=0, 
                        max_value=20, 
                        value=existing_pred.get('home', 0) if existing_pred else 0,
                        key=f"home_{idx}",
                        label_visibility="collapsed"
                    )
                    st.markdown("**-**")
                    away_score = st.number_input(
                        "A", 
                        min_value=0, 
                        max_value=20, 
                        value=existing_pred.get('away', 0) if existing_pred else 0,
                        key=f"away_{idx}",
                        label_visibility="collapsed"
                    )
                with col3:
                    st.markdown(f"**{match.get('away', 'TBC')}**")
                
                predictions.append({
                    'home': home_score,
                    'away': away_score
                })
                
                st.markdown("---")
            
            # Submit button
            submitted = st.form_submit_button("💾 Save Predictions", use_container_width=True, type="primary")
            
            if submitted:
                # Save predictions
                if str(selected_week) not in all_predictions:
                    all_predictions[str(selected_week)] = {}
                
                all_predictions[str(selected_week)][participant_id] = predictions
                
                # NEW:
                tracker = PredictionTracker(dm)
                is_late, time = tracker.save_prediction_with_timestamp(
                    week=selected_week,
                    participant_id=participant_id,
                    predictions=new_predictions
                )

                if is_late:
                    st.warning("Late submission - will score 0 points")
                else:
                    st.success("Saved on time!")
    else:
        st.warning("No matches available for this week yet.")
else:
    st.info("No gameweeks available yet. Check back soon!")

# Show prediction history
st.markdown("---")
st.markdown("### 📊 Your Prediction History")

all_predictions = dm.load_predictions()
my_weeks = []

for week_str, week_data in all_predictions.items():
    if week_str.isdigit() and participant_id in week_data:
        my_weeks.append(int(week_str))

if my_weeks:
    my_weeks.sort()
    st.success(f"✅ You have made predictions for {len(my_weeks)} gameweeks: {', '.join(f'Week {w}' for w in my_weeks)}")
else:
    st.info("You haven't made any predictions yet. Get started above!")

# Footer
st.markdown("---")
st.caption("Nikkang KK EPL Prediction Competition 2025-26")

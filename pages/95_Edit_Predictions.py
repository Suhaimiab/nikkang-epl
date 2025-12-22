"""
Admin: Edit Predictions
Manually edit predictions and mark late/no submissions with X
"""

import streamlit as st
import json
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent.parent))

from utils.auth import check_password
from utils.data_manager import DataManager

# Page config
st.set_page_config(
    page_title="Edit Predictions - Admin",
    page_icon="✏️",
    layout="wide"
)

# Require admin auth
if not check_password():
    st.stop()

# Logo
if Path("nikkang_logo.png").exists():
    st.sidebar.image("nikkang_logo.png", use_container_width=True)
    st.sidebar.markdown("---")

st.title("✏️ Edit Predictions")
st.markdown("### Manually Edit or Add Predictions")

st.info("💡 **Mark Late/No Submission:** Enter **X** in both Home and Away fields → Will score 0 points")

st.markdown("---")

# Initialize data manager
dm = DataManager()

# Load data
participants = dm.get_all_participants()
predictions = dm.load_predictions()
matches = dm.load_matches()

if not participants:
    st.warning("No participants found. Please register participants first.")
    st.stop()

# Select participant
st.subheader("1️⃣ Select Participant")
participant_options = {f"{p.get('display_name', p.get('name', 'Unknown'))} ({p.get('name', 'Unknown')})": p.get('id') for p in participants}
selected_name = st.selectbox("Participant:", sorted(participant_options.keys()))
participant_id = participant_options[selected_name]

# Get participant info
participant = next((p for p in participants if p.get('id') == participant_id), None)
display_name = participant.get('display_name', 'Unknown') if participant else 'Unknown'

st.markdown("---")

# Select week
st.subheader("2️⃣ Select Gameweek")
available_weeks = sorted([int(w) for w in matches.keys() if w.isdigit()])

if not available_weeks:
    st.warning("No gameweeks with matches found.")
    st.stop()

selected_week = st.selectbox("Gameweek:", available_weeks, format_func=lambda x: f"Week {x}")

st.markdown("---")

# Get matches for selected week
week_matches = matches.get(str(selected_week), [])

if not week_matches:
    st.warning(f"No matches found for Week {selected_week}")
    st.stop()

# Get existing predictions
week_str = str(selected_week)
existing_predictions = predictions.get(week_str, {}).get(participant_id, [])

# Ensure predictions list matches number of matches
while len(existing_predictions) < len(week_matches):
    existing_predictions.append({'home': 0, 'away': 0})

st.subheader(f"3️⃣ Edit Predictions: {display_name} - Week {selected_week}")
st.caption(f"Editing {len(week_matches)} matches")

# Show current predictions summary
if existing_predictions:
    late_count = sum(1 for p in existing_predictions if p.get('late', False))
    if late_count > 0:
        st.warning(f"⚠️ Currently {late_count} match(es) marked as late/no submission")

st.markdown("---")

# Create form for editing
new_predictions = []

for idx, match in enumerate(week_matches):
    home_team = match.get('home', 'TBC')
    away_team = match.get('away', 'TBC')
    is_gotw = match.get('gotw', False)
    
    # Get existing prediction
    existing = existing_predictions[idx] if idx < len(existing_predictions) else {'home': 0, 'away': 0}
    
    # Check if existing is marked as late (X)
    is_late = existing.get('late', False)
    default_home = 'X' if is_late else str(existing.get('home', 0))
    default_away = 'X' if is_late else str(existing.get('away', 0))
    
    # Match header
    col_header1, col_header2 = st.columns([3, 1])
    with col_header1:
        st.markdown(f"**Match {idx+1}:** {home_team} vs {away_team}")
    with col_header2:
        if is_gotw:
            st.markdown("⭐ **GOTW** (Double Points)")
        if is_late:
            st.markdown("❌ *Late/No Sub*")
    
    # Input fields
    col1, col2, col3 = st.columns([2, 1, 2])
    
    with col1:
        st.caption(home_team)
    
    with col2:
        home_input = st.text_input(
            "Home",
            value=default_home,
            key=f"home_{idx}",
            label_visibility="collapsed",
            max_chars=2,
            help="Enter score (0-20) or X for late/no submission"
        )
        
        st.caption("vs")
        
        away_input = st.text_input(
            "Away",
            value=default_away,
            key=f"away_{idx}",
            label_visibility="collapsed",
            max_chars=2,
            help="Enter score (0-20) or X for late/no submission"
        )
    
    with col3:
        st.caption(away_team)
    
    # Process input
    home_input = home_input.strip().upper()
    away_input = away_input.strip().upper()
    
    # Check if marked as late (X)
    if home_input == 'X' and away_input == 'X':
        new_predictions.append({
            'home': 0,
            'away': 0,
            'late': True  # Mark as late submission
        })
        st.caption("⚠️ This match will score **0 points** (Late/No Submission)")
    elif home_input == 'X' or away_input == 'X':
        st.error(f"❌ Match {idx+1}: Both fields must be 'X' to mark as late, or both must be numbers")
        new_predictions.append(existing)
    else:
        # Try to convert to int
        try:
            home_score = int(home_input) if home_input else 0
            away_score = int(away_input) if away_input else 0
            new_predictions.append({
                'home': max(0, min(20, home_score)),  # Clamp between 0-20
                'away': max(0, min(20, away_score)),
                'late': False
            })
        except ValueError:
            st.error(f"❌ Match {idx+1}: Invalid input. Use numbers (0-20) or 'X' for late")
            new_predictions.append(existing)
    
    st.markdown("---")

# Optional note
note = st.text_area(
    "Optional Note:",
    placeholder="e.g., Late WhatsApp submission, No submission received, etc.",
    height=60
)

st.markdown("---")

# Submit buttons
col1, col2, col3 = st.columns(3)

with col1:
    save_button = st.button("💾 Save Predictions", use_container_width=True, type="primary")

with col2:
    preview_button = st.button("👀 Preview", use_container_width=True)

with col3:
    cancel_button = st.button("❌ Cancel", use_container_width=True)

# Handle form submission
if save_button:
    # Save predictions
    if week_str not in predictions:
        predictions[week_str] = {}
    
    predictions[week_str][participant_id] = new_predictions
    
    # Save to file
    if dm.save_predictions(predictions):
        st.success(f"✅ Predictions saved for {display_name} - Week {selected_week}")
        if note:
            st.info(f"📝 Note: {note}")
        st.balloons()
        
        # Show summary
        late_count = sum(1 for p in new_predictions if p.get('late', False))
        normal_count = len(new_predictions) - late_count
        
        st.markdown("### Summary:")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Normal Predictions", normal_count)
        with col2:
            st.metric("Late/No Submission (X-X)", late_count)
        
        if late_count > 0:
            st.warning(f"⚠️ {late_count} match(es) marked as late/no submission (will score 0 points)")
    else:
        st.error("❌ Error saving predictions")

elif preview_button:
    st.markdown("### 👀 Preview:")
    
    late_count = 0
    normal_count = 0
    
    for idx, (match, pred) in enumerate(zip(week_matches, new_predictions)):
        home_team = match.get('home', 'TBC')
        away_team = match.get('away', 'TBC')
        is_late = pred.get('late', False)
        is_gotw = match.get('gotw', False)
        
        gotw_mark = " ⭐" if is_gotw else ""
        
        if is_late:
            st.markdown(f"**Match {idx+1}:** {home_team} **X-X** {away_team}{gotw_mark} → ❌ *Late/No Sub (0 pts)*")
            late_count += 1
        else:
            home_score = pred.get('home', 0)
            away_score = pred.get('away', 0)
            st.markdown(f"**Match {idx+1}:** {home_team} **{home_score}-{away_score}** {away_team}{gotw_mark}")
            normal_count += 1
    
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Normal", normal_count)
    with col2:
        st.metric("Late/No Sub", late_count)

elif cancel_button:
    st.info("❌ Cancelled. No changes made.")

# Show current predictions
st.markdown("---")
st.markdown("### Current Predictions in Database:")

if existing_predictions:
    cols = st.columns(5)
    for idx, (match, pred) in enumerate(zip(week_matches, existing_predictions)):
        col_idx = idx % 5
        with cols[col_idx]:
            home_team = match.get('home', 'TBC')
            away_team = match.get('away', 'TBC')
            is_late = pred.get('late', False)
            
            if is_late:
                st.caption(f"**M{idx+1}:** {home_team[:3]}v{away_team[:3]}")
                st.error("X-X (Late)")
            else:
                home_score = pred.get('home', 0)
                away_score = pred.get('away', 0)
                st.caption(f"**M{idx+1}:** {home_team[:3]}v{away_team[:3]}")
                st.success(f"{home_score}-{away_score}")
else:
    st.caption("No predictions yet for this week")

# Footer
st.markdown("---")
st.caption("💡 **Remember:** After editing, check Weekly Results to verify scoring!")
st.caption("⚠️ Predictions marked with X-X will score 0 points regardless of the actual result")

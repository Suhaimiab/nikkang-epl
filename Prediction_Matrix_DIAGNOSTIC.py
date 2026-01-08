"""
Prediction Matrix - DIAGNOSTIC VERSION
Shows exactly what's happening and why nothing displays
"""

import streamlit as st
import pandas as pd
import json
from datetime import datetime
from pathlib import Path

st.set_page_config(
    page_title="Prediction Matrix - Diagnostic",
    page_icon="🔍",
    layout="wide"
)

st.title("🔍 Prediction Matrix - Diagnostic Mode")
st.markdown("---")

# Load functions
def load_settings():
    settings_file = Path("nikkang_data/settings.json")
    if settings_file.exists():
        try:
            with open(settings_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            return {"error": str(e)}
    return {"error": "File not found"}

def load_matches():
    matches_file = Path("nikkang_data/matches.json")
    if matches_file.exists():
        try:
            with open(matches_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            return {"error": str(e)}
    return {"error": "File not found"}

def load_predictions():
    predictions_file = Path("nikkang_data/predictions.json")
    if predictions_file.exists():
        try:
            with open(predictions_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            return {"error": str(e)}
    return {"error": "File not found"}

def load_participants():
    participants_file = Path("nikkang_data/participants.json")
    if participants_file.exists():
        try:
            with open(participants_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            return {"error": str(e)}
    return {"error": "File not found"}

# Load all data
st.markdown("## 📂 Data Files Check")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### Settings")
    settings = load_settings()
    if "error" in settings:
        st.error(f"❌ Error: {settings['error']}")
    else:
        st.success("✅ Loaded")
        st.json(settings)
        current_week = settings.get("current_week", "NOT SET")
        st.metric("Current Week", current_week)

with col2:
    st.markdown("### Matches")
    matches = load_matches()
    if "error" in matches:
        st.error(f"❌ Error: {matches['error']}")
    else:
        st.success(f"✅ Loaded - {len(matches)} weeks")
        st.write(f"Available weeks: {list(matches.keys())}")
        
        # Check current week
        current_week = settings.get("current_week", 1)
        if str(current_week) in matches:
            st.success(f"✅ Week {current_week} has {len(matches[str(current_week)])} matches")
        else:
            st.error(f"❌ Week {current_week} NOT found in matches!")

st.markdown("---")

col3, col4 = st.columns(2)

with col3:
    st.markdown("### Predictions")
    predictions = load_predictions()
    if "error" in predictions:
        st.error(f"❌ Error: {predictions['error']}")
    else:
        st.success(f"✅ Loaded - {len(predictions)} participants")
        
        # Check current week predictions
        current_week = settings.get("current_week", 1)
        count = 0
        for participant_id, pred_data in predictions.items():
            if str(current_week) in pred_data:
                count += 1
        
        if count > 0:
            st.success(f"✅ {count} participants have predictions for Week {current_week}")
        else:
            st.error(f"❌ NO predictions for Week {current_week}")
        
        # Show sample
        if predictions:
            st.write("Sample prediction structure:")
            sample_id = list(predictions.keys())[0]
            st.json({sample_id: predictions[sample_id]})

with col4:
    st.markdown("### Participants")
    participants = load_participants()
    if "error" in participants:
        st.error(f"❌ Error: {participants['error']}")
    else:
        st.success(f"✅ Loaded - {len(participants)} participants")
        
        # Show sample
        if participants:
            st.write("Sample participant:")
            sample_id = list(participants.keys())[0]
            st.json({sample_id: participants[sample_id]})

st.markdown("---")

# Now try to build the matrix
st.markdown("## 🔨 Building Matrix")

current_week = settings.get("current_week", 1)
st.info(f"Attempting to build matrix for Week {current_week}")

# Get matches for current week
week_matches = matches.get(str(current_week), [])
st.write(f"**Matches found:** {len(week_matches)}")

if not week_matches:
    st.error(f"❌ PROBLEM: No matches for Week {current_week}")
    st.stop()
else:
    st.success(f"✅ {len(week_matches)} matches found")
    with st.expander("View Matches"):
        st.json(week_matches)

# Get predictions for current week
week_predictions = {}
for participant_id, participant_data in participants.items():
    participant_name = participant_data.get('display_name', participant_data.get('name', 'Unknown'))
    
    if participant_id in predictions:
        participant_preds = predictions[participant_id]
        if str(current_week) in participant_preds:
            week_predictions[participant_name] = participant_preds[str(current_week)]

st.write(f"**Predictions found:** {len(week_predictions)} participants")

if not week_predictions:
    st.error(f"❌ PROBLEM: No predictions submitted for Week {current_week}")
    st.info("Possible causes:")
    st.markdown("""
    1. No one has made predictions yet
    2. Predictions are under different week number
    3. Current week setting is wrong
    4. Data structure mismatch
    """)
    
    # Show what weeks DO have predictions
    all_pred_weeks = set()
    for participant_id, pred_data in predictions.items():
        all_pred_weeks.update(pred_data.keys())
    
    if all_pred_weeks:
        st.warning(f"Predictions exist for weeks: {sorted(all_pred_weeks)}")
        st.info(f"Current week is set to: {current_week}")
        st.error("🔧 **FIX:** Update current_week in settings.json to match available predictions")
    
    st.stop()
else:
    st.success(f"✅ {len(week_predictions)} participants have predictions")
    with st.expander("View Prediction Summary"):
        for name, pred in week_predictions.items():
            st.write(f"**{name}:** {len(pred.get('predictions', []))} predictions")

# Build matrix
st.markdown("---")
st.markdown("## 📊 Matrix Preview")

matrix_data = []

for idx, match in enumerate(week_matches, 1):
    home = match.get('home', 'Unknown')
    away = match.get('away', 'Unknown')
    is_gotw = match.get('gotw', False)
    
    row = {
        'Match': idx,
        'Home': home,
        'Away': away,
        'GOTW': '⭐' if is_gotw else ''
    }
    
    for participant_name in sorted(week_predictions.keys()):
        preds = week_predictions[participant_name].get('predictions', [])
        
        if idx <= len(preds):
            pred = preds[idx - 1]
            home_score = pred.get('home_score', '-')
            away_score = pred.get('away_score', '-')
            row[participant_name] = f"{home_score}-{away_score}"
        else:
            row[participant_name] = "-"
    
    matrix_data.append(row)

df = pd.DataFrame(matrix_data)

st.success(f"✅ Matrix built successfully! {len(df)} rows, {len(df.columns)} columns")
st.dataframe(df, width='stretch')

st.markdown("---")
st.markdown("## 🎯 Conclusion")

if len(df) > 0:
    st.success("✅ **MATRIX WORKS!** The data is loading correctly.")
    st.info("The issue is likely in the main page code, not the data.")
    st.markdown("""
    ### Next Steps:
    1. Copy this working code to your main page
    2. Or check for errors in your main page console
    3. Verify file paths are correct
    """)
else:
    st.error("❌ Something is still wrong")
    st.info("Check the diagnostics above to see what's missing")

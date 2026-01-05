"""
Prediction Matrix - Public Version
Based on exact structure from Prediction Lock
Format: predictions[week][user_id] = [array of predictions]
"""

import streamlit as st
import pandas as pd
import json
from datetime import datetime
from pathlib import Path
import sys

# Add utils to path
sys.path.append(str(Path(__file__).parent.parent))

from utils.data_manager import DataManager

# Page config
st.set_page_config(
    page_title="Prediction Matrix - Nikkang KK EPL",
    page_icon="📊",
    layout="wide"
)

# Import branding
try:
    from utils.branding import inject_custom_css
    inject_custom_css()
except:
    pass

# Initialize data manager
dm = DataManager()

# Settings file
SETTINGS_FILE = Path("nikkang_data/settings.json")

def load_settings():
    """Load settings from JSON file"""
    if SETTINGS_FILE.exists():
        try:
            with open(SETTINGS_FILE, 'r') as f:
                return json.load(f)
        except:
            return {"current_week": 1}
    return {"current_week": 1}

st.title("📊 Prediction Matrix - Current Week")
st.markdown("View all participant predictions for the **current week only**")
st.info("🔓 **Open Access:** All participants can view the latest predictions")
st.markdown("---")

# Load settings and data
settings = load_settings()
current_week = settings.get("current_week", 1)

# Display current week
col1, col2 = st.columns([3, 1])

with col1:
    st.markdown(f"### 📅 Current Week: **Week {current_week}**")
    st.caption("Showing latest predictions for the current gameweek only")

with col2:
    auto_refresh = st.checkbox("🔄 Auto-refresh", value=False)

if auto_refresh:
    import time
    time.sleep(30)
    st.rerun()

st.markdown("---")

# Get matches for current week
matches = dm.get_matches_by_week(current_week)
participants = dm.get_all_participants()
all_predictions = dm.load_predictions()

# Get predictions for this specific week
# Format: {"21": {"USER_ID": [{"home": 2, "away": 1}, ...], ...}}
week_predictions = all_predictions.get(str(current_week), {})

if not matches:
    st.warning(f"⚠️ No matches configured for Week {current_week}")
    st.info("Please contact admin to add matches for this week.")
    st.stop()

if not participants:
    st.warning("⚠️ No participants registered yet")
    st.stop()

if not week_predictions:
    st.info(f"📭 No predictions submitted yet for Week {current_week}")
    st.markdown("### Be the first to predict!")
    
    if st.button("🎯 Make Your Predictions", type="primary"):
        st.switch_page("pages/3_Predictions.py")
    st.stop()

# Count how many participants have predictions
participants_with_predictions = len([p for p in participants if p.get('id', '') in week_predictions])

st.success(f"✅ **{participants_with_predictions} participants** have submitted predictions for Week {current_week}")

# Build matrix - rows are MATCHES, columns are PARTICIPANTS
st.markdown(f"### 🎯 Current Predictions - Week {current_week}")
st.caption(f"📅 Updated: {datetime.now().strftime('%d %B %Y %H:%M')}")

matrix_data = []

for idx, match in enumerate(matches):
    home = match.get('home', match.get('home_team', ''))
    away = match.get('away', match.get('away_team', ''))
    is_gotw = match.get('gotw', False)
    
    row = {
        'Match': idx + 1,
        'Home': home,
        'Away': away,
        'GOTW': '⭐' if is_gotw else ''
    }
    
    # Add each participant's prediction for this match
    for p in participants:
        uid = p.get('id', '')
        participant_name = p.get('display_name') or p.get('name', 'Unknown')
        
        # Get this user's predictions for current week
        user_week_preds = week_predictions.get(uid, [])
        
        # Get prediction for this specific match (by index)
        if idx < len(user_week_preds):
            pred = user_week_preds[idx]
            if isinstance(pred, dict):
                pred_home = pred.get('home', pred.get('home_score', '?'))
                pred_away = pred.get('away', pred.get('away_score', '?'))
                row[participant_name] = f"{pred_home}-{pred_away}"
            else:
                row[participant_name] = "-"
        else:
            row[participant_name] = "-"
    
    matrix_data.append(row)

# Create DataFrame
df = pd.DataFrame(matrix_data)

# Display stats
st.markdown(f"#### 📈 Week {current_week} Statistics")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Matches", len(matches))

with col2:
    st.metric("Participants", participants_with_predictions)

with col3:
    gotw_count = sum(1 for m in matches if m.get('gotw', False))
    st.metric("GOTW Matches", gotw_count)

with col4:
    # Calculate completion rate
    total_possible = participants_with_predictions * len(matches)
    total_made = sum(
        len([p for p in week_predictions.get(uid, []) if p])
        for uid in [p.get('id', '') for p in participants]
        if uid in week_predictions
    )
    completion_rate = (total_made / total_possible * 100) if total_possible > 0 else 0
    st.metric("Completion", f"{completion_rate:.0f}%")

st.markdown("---")

# Display matrix
st.info("💡 **Tip:** Scroll horizontally to see all participants. GOTW (⭐) matches earn double points!")

st.dataframe(
    df,
    use_container_width=True,
    hide_index=True,
    column_config={
        "Match": st.column_config.NumberColumn("Match #", width="small"),
        "Home": st.column_config.TextColumn("Home Team", width="medium"),
        "Away": st.column_config.TextColumn("Away Team", width="medium"),
        "GOTW": st.column_config.TextColumn("GOTW", width="small"),
    },
    height=600
)

st.markdown("---")

# Download options
st.markdown("### 📥 Download Options")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("#### 📄 CSV")
    csv = df.to_csv(index=False)
    st.download_button(
        label="⬇️ Download CSV",
        data=csv,
        file_name=f"predictions_week_{current_week}_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv",
        use_container_width=True
    )

with col2:
    st.markdown("#### 🌐 HTML")
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Predictions Week {current_week}</title>
        <style>
            body {{ font-family: Arial; padding: 20px; background: #f5f5f5; }}
            h1 {{ color: #2E7D32; text-align: center; }}
            table {{ border-collapse: collapse; width: 100%; background: white; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
            th {{ background: #2E7D32; color: white; padding: 12px; text-align: center; }}
            td {{ padding: 10px; border: 1px solid #ddd; text-align: center; }}
            tr:nth-child(even) {{ background: #f9f9f9; }}
            tr:hover {{ background: #f0f0f0; }}
            .gotw {{ color: #FFA000; font-weight: bold; }}
        </style>
    </head>
    <body>
        <h1>🏆 Nikkang KK - Week {current_week} Predictions</h1>
        <p style="text-align: center; color: #666;">Generated: {datetime.now().strftime('%d %B %Y %H:%M')}</p>
        {df.to_html(index=False, escape=False)}
        <p style="text-align: center; color: #666; margin-top: 20px;">⭐ = Game of the Week (Double Points)</p>
    </body>
    </html>
    """
    
    st.download_button(
        label="⬇️ Download HTML",
        data=html,
        file_name=f"predictions_week_{current_week}.html",
        mime="text/html",
        use_container_width=True
    )

with col3:
    st.markdown("#### 📸 Screenshot")
    st.info("""
    **Use browser screenshot:**
    - Windows: Win+Shift+S
    - Mac: Cmd+Shift+4
    - Mobile: Power+Vol Down
    """)

st.markdown("---")

# Analysis
st.markdown("### 📊 Prediction Analysis")

col1, col2 = st.columns(2)

with col1:
    st.markdown("#### 🔥 Most Popular Predictions")
    
    popular = []
    for idx, match in enumerate(matches[:5]):
        home = match.get('home', match.get('home_team', ''))
        away = match.get('away', match.get('away_team', ''))
        
        # Count predictions for this match
        pred_counts = {}
        for uid, user_preds in week_predictions.items():
            if idx < len(user_preds):
                pred = user_preds[idx]
                if isinstance(pred, dict):
                    score = f"{pred.get('home', '?')}-{pred.get('away', '?')}"
                    pred_counts[score] = pred_counts.get(score, 0) + 1
        
        if pred_counts:
            most_pop = max(pred_counts.items(), key=lambda x: x[1])
            popular.append({
                'Match': f"{home} vs {away}",
                'Score': most_pop[0],
                'Votes': f"{most_pop[1]} ({most_pop[1]/len(week_predictions)*100:.0f}%)"
            })
    
    if popular:
        st.dataframe(pd.DataFrame(popular), hide_index=True, use_container_width=True)
        st.caption("💡 Most predicted scores for the top 5 matches")

with col2:
    st.markdown("#### 🎲 Prediction Diversity")
    
    diversity = []
    for idx, match in enumerate(matches[:5]):
        home = match.get('home', match.get('home_team', ''))
        away = match.get('away', match.get('away_team', ''))
        
        # Count unique predictions
        unique_preds = set()
        for uid, user_preds in week_predictions.items():
            if idx < len(user_preds):
                pred = user_preds[idx]
                if isinstance(pred, dict):
                    score = f"{pred.get('home', '?')}-{pred.get('away', '?')}"
                    unique_preds.add(score)
        
        diversity.append({
            'Match': f"{home} vs {away}",
            'Unique': len(unique_preds),
            'Diversity': f"{(len(unique_preds)/len(week_predictions)*100):.0f}%" if week_predictions else "0%"
        })
    
    if diversity:
        st.dataframe(pd.DataFrame(diversity), hide_index=True, use_container_width=True)
        st.caption("💡 Higher diversity = more strategic differences")

st.markdown("---")

# Quick actions
st.markdown("### ⚡ Quick Actions")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("🎯 Make/Edit Predictions", use_container_width=True, type="primary"):
        st.switch_page("pages/3_Predictions.py")

with col2:
    if st.button("📊 View Leaderboard", use_container_width=True):
        st.switch_page("pages/5_Leaderboard.py")

with col3:
    if st.button("🔄 Refresh Data", use_container_width=True):
        st.rerun()

# Footer
st.markdown("---")
st.markdown(f"""
<div style='text-align: center; color: #666; font-size: 12px;'>
    <p>📊 Prediction Matrix - Current Week Only | Nikkang KK EPL</p>
    <p>⭐ GOTW = Double Points | Week {current_week} | 🔓 Open to all participants</p>
    <p>Last updated: {datetime.now().strftime('%d %B %Y %H:%M')}</p>
</div>
""", unsafe_allow_html=True)

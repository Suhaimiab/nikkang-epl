"""
Manual Score Entry
Nikkang KK EPL Prediction Competition
Enter historical scores for weeks where predictions weren't tracked in the system
"""

import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime
from utils.auth import require_admin
from utils.data_manager import DataManager

# Require admin authentication
if not require_admin("Manual Score Entry"):
    st.stop()

st.set_page_config(page_title="Manual Scores", page_icon="📝", layout="wide")

st.title("📝 Manual Score Entry")
st.markdown("Enter historical points and KK counts for weeks not tracked in the system")

dm = DataManager()

# File path for manual scores
MANUAL_SCORES_FILE = "nikkang_data/manual_scores.json"

def load_manual_scores():
    """Load manual scores from file"""
    try:
        if os.path.exists(MANUAL_SCORES_FILE):
            with open(MANUAL_SCORES_FILE, 'r') as f:
                return json.load(f)
    except:
        pass
    return {}

def save_manual_scores(data):
    """Save manual scores to file"""
    try:
        os.makedirs(os.path.dirname(MANUAL_SCORES_FILE), exist_ok=True)
        with open(MANUAL_SCORES_FILE, 'w') as f:
            json.dump(data, f, indent=2)
        return True
    except Exception as e:
        st.error(f"Error saving: {e}")
        return False

# Load data
participants = dm.load_participants()
manual_scores = load_manual_scores()

if not participants:
    st.warning("No participants registered yet!")
    st.stop()

# Convert participants to list
participant_list = []
for pid, p in participants.items():
    participant_list.append({
        'id': pid,
        'name': p.get('name', 'Unknown'),
        'nickname': p.get('display_name') or p.get('nickname') or p.get('name', 'Unknown')
    })

# Sort by name
participant_list.sort(key=lambda x: x['name'])

st.markdown("---")

# Tabs for different entry modes
tab1, tab2, tab3 = st.tabs(["📊 Enter Scores by Week", "👤 Enter Scores by Participant", "📋 View All Manual Scores"])

# =============================================================================
# TAB 1: Enter by Week
# =============================================================================
with tab1:
    st.markdown("### Enter Scores for a Specific Week")
    
    col1, col2 = st.columns(2)
    
    with col1:
        selected_week = st.selectbox(
            "Select Week:",
            range(1, 39),
            index=10,  # Default to Week 11
            format_func=lambda x: f"Week {x}",
            key="week_select"
        )
    
    with col2:
        st.info(f"📌 Entering scores for **Week {selected_week}**")
    
    week_key = str(selected_week)
    
    # Get existing scores for this week
    week_scores = manual_scores.get(week_key, {})
    
    st.markdown("#### Enter Points and KK for Each Participant")
    
    # Create a form for batch entry
    with st.form(f"week_{selected_week}_scores"):
        
        # Table header
        cols = st.columns([3, 2, 2])
        cols[0].markdown("**Participant**")
        cols[1].markdown("**Points**")
        cols[2].markdown("**KK Count**")
        
        st.markdown("---")
        
        # Entry rows for each participant
        entries = {}
        for p in participant_list:
            pid = p['id']
            existing = week_scores.get(pid, {})
            
            cols = st.columns([3, 2, 2])
            
            with cols[0]:
                st.markdown(f"**{p['nickname']}**")
                st.caption(p['name'])
            
            with cols[1]:
                points = st.number_input(
                    f"Points {pid}",
                    min_value=0,
                    max_value=100,
                    value=existing.get('points', 0),
                    key=f"pts_{week_key}_{pid}",
                    label_visibility="collapsed"
                )
            
            with cols[2]:
                kk = st.number_input(
                    f"KK {pid}",
                    min_value=0,
                    max_value=10,
                    value=existing.get('kk', 0),
                    key=f"kk_{week_key}_{pid}",
                    label_visibility="collapsed"
                )
            
            entries[pid] = {'points': points, 'kk': kk}
        
        st.markdown("---")
        
        submitted = st.form_submit_button("💾 Save Week Scores", type="primary")
        
        if submitted:
            # Save to manual_scores
            if week_key not in manual_scores:
                manual_scores[week_key] = {}
            
            # Only save non-zero entries
            for pid, scores in entries.items():
                if scores['points'] > 0 or scores['kk'] > 0:
                    manual_scores[week_key][pid] = scores
                elif pid in manual_scores[week_key]:
                    # Remove if set to zero
                    del manual_scores[week_key][pid]
            
            if save_manual_scores(manual_scores):
                st.success(f"✅ Saved scores for Week {selected_week}!")
                st.rerun()

# =============================================================================
# TAB 2: Enter by Participant
# =============================================================================
with tab2:
    st.markdown("### Enter Scores for a Specific Participant")
    
    selected_participant = st.selectbox(
        "Select Participant:",
        participant_list,
        format_func=lambda x: f"{x['nickname']} ({x['name']})",
        key="participant_select"
    )
    
    if selected_participant:
        pid = selected_participant['id']
        
        st.markdown(f"#### Scores for **{selected_participant['nickname']}**")
        
        # Get all weeks with manual scores for this participant
        participant_scores = {}
        for week_key, week_data in manual_scores.items():
            if pid in week_data:
                participant_scores[week_key] = week_data[pid]
        
        # Allow entry for multiple weeks
        st.markdown("##### Enter scores for weeks 11-13 (or any historical week):")
        
        with st.form(f"participant_{pid}_scores"):
            week_entries = {}
            
            # Show weeks 11, 12, 13 by default (common historical weeks)
            for week_num in [11, 12, 13]:
                week_key = str(week_num)
                existing = participant_scores.get(week_key, {})
                
                st.markdown(f"**Week {week_num}**")
                cols = st.columns([2, 2, 4])
                
                with cols[0]:
                    points = st.number_input(
                        f"Points W{week_num}",
                        min_value=0,
                        max_value=100,
                        value=existing.get('points', 0),
                        key=f"p_pts_{pid}_{week_key}",
                        label_visibility="collapsed",
                        help="Points"
                    )
                    st.caption("Points")
                
                with cols[1]:
                    kk = st.number_input(
                        f"KK W{week_num}",
                        min_value=0,
                        max_value=10,
                        value=existing.get('kk', 0),
                        key=f"p_kk_{pid}_{week_key}",
                        label_visibility="collapsed",
                        help="KK Count"
                    )
                    st.caption("KK")
                
                week_entries[week_key] = {'points': points, 'kk': kk}
                st.markdown("---")
            
            # Option to add other weeks
            st.markdown("**Add Other Week (Optional)**")
            cols = st.columns([1, 2, 2])
            
            with cols[0]:
                other_week = st.number_input("Week", min_value=1, max_value=38, value=1, key=f"other_week_{pid}")
            with cols[1]:
                other_points = st.number_input("Points", min_value=0, max_value=100, value=0, key=f"other_pts_{pid}")
            with cols[2]:
                other_kk = st.number_input("KK", min_value=0, max_value=10, value=0, key=f"other_kk_{pid}")
            
            if other_points > 0 or other_kk > 0:
                week_entries[str(other_week)] = {'points': other_points, 'kk': other_kk}
            
            submitted = st.form_submit_button("💾 Save Participant Scores", type="primary")
            
            if submitted:
                # Save to manual_scores
                for week_key, scores in week_entries.items():
                    if week_key not in manual_scores:
                        manual_scores[week_key] = {}
                    
                    if scores['points'] > 0 or scores['kk'] > 0:
                        manual_scores[week_key][pid] = scores
                    elif pid in manual_scores.get(week_key, {}):
                        del manual_scores[week_key][pid]
                
                if save_manual_scores(manual_scores):
                    st.success(f"✅ Saved scores for {selected_participant['nickname']}!")
                    st.rerun()

# =============================================================================
# TAB 3: View All Manual Scores
# =============================================================================
with tab3:
    st.markdown("### All Manual Scores")
    
    if not manual_scores:
        st.info("No manual scores entered yet.")
    else:
        # Create summary DataFrame
        summary_data = []
        
        for p in participant_list:
            pid = p['id']
            row = {
                'Nickname': p['nickname'],
                'Name': p['name']
            }
            
            total_points = 0
            total_kk = 0
            
            # Get scores for each week
            for week_num in range(1, 39):
                week_key = str(week_num)
                if week_key in manual_scores and pid in manual_scores[week_key]:
                    scores = manual_scores[week_key][pid]
                    pts = scores.get('points', 0)
                    kk = scores.get('kk', 0)
                    row[f'W{week_num}'] = f"{pts}pts/{kk}KK" if pts > 0 or kk > 0 else "-"
                    total_points += pts
                    total_kk += kk
                else:
                    row[f'W{week_num}'] = "-"
            
            row['Total Pts'] = total_points
            row['Total KK'] = total_kk
            
            if total_points > 0 or total_kk > 0:
                summary_data.append(row)
        
        if summary_data:
            df = pd.DataFrame(summary_data)
            
            # Only show columns with data
            cols_to_show = ['Nickname', 'Name']
            for week_num in range(1, 39):
                col = f'W{week_num}'
                if col in df.columns and (df[col] != '-').any():
                    cols_to_show.append(col)
            cols_to_show.extend(['Total Pts', 'Total KK'])
            
            df_display = df[cols_to_show]
            
            st.dataframe(df_display, use_container_width=True, hide_index=True)
            
            # Summary stats
            st.markdown("---")
            st.markdown("#### Summary")
            
            total_entries = sum(1 for w in manual_scores.values() for _ in w)
            weeks_with_data = len([w for w in manual_scores if manual_scores[w]])
            
            col1, col2, col3 = st.columns(3)
            col1.metric("Weeks with Manual Scores", weeks_with_data)
            col2.metric("Total Entries", total_entries)
            col3.metric("Participants with Scores", len(summary_data))
            
            # Download option
            st.markdown("---")
            st.download_button(
                "📥 Download Manual Scores (JSON)",
                data=json.dumps(manual_scores, indent=2),
                file_name=f"manual_scores_{datetime.now().strftime('%Y%m%d')}.json",
                mime="application/json"
            )
        else:
            st.info("No manual scores entered yet.")

# =============================================================================
# Sidebar: Quick Stats & Help
# =============================================================================
with st.sidebar:
    st.markdown("### 📊 Quick Stats")
    
    weeks_with_manual = len([w for w in manual_scores if manual_scores[w]])
    st.metric("Weeks with Manual Data", weeks_with_manual)
    
    st.markdown("---")
    st.markdown("### ℹ️ How This Works")
    st.markdown("""
    1. **Enter scores** for weeks 11-13 (or any historical week)
    2. **Points & KK** are stored separately from system-calculated scores
    3. **Leaderboard** will combine:
       - Stage 1 locked scores
       - Manual scores (weeks 11-13)
       - System-calculated scores (week 14+)
    """)
    
    st.markdown("---")
    st.markdown("### ⚠️ Important")
    st.markdown("""
    - Manual scores override system calculations for those weeks
    - Use this for weeks where predictions weren't tracked
    - Always verify totals before locking stages
    """)

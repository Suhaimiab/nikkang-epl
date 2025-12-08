"""
Manual Scores Entry - Admin Page
Enter bonus/penalty points for participants
ORGANIZED BY WEEK with sorted names
"""

import streamlit as st
import pandas as pd
from pathlib import Path
from datetime import datetime
import sys
import json

# Add utils to path
sys.path.append(str(Path(__file__).parent.parent))

from utils.data_manager import DataManager
from utils.auth import check_password

# Page config
st.set_page_config(
    page_title="Manual Scores - Nikkang KK",
    page_icon="✏️",
    layout="wide"
)

# Import branding
try:
    from utils.branding import inject_custom_css
    inject_custom_css()
except:
    pass

# Authentication
if not check_password():
    st.stop()

# Logo in sidebar
if Path("nikkang_logo.png").exists():
    st.sidebar.markdown('<div style="padding-top: 0.5rem;"></div>', unsafe_allow_html=True)
    st.sidebar.markdown('<div class="sidebar-logo-container">', unsafe_allow_html=True)
    st.sidebar.image("nikkang_logo.png", use_container_width=True)
    st.sidebar.markdown('</div>', unsafe_allow_html=True)
    st.sidebar.markdown("---")

# Header
st.markdown("""
<div style="text-align: center; padding: 1.5rem 0;">
    <h1 style="color: #667eea; font-size: 2.5rem; margin: 0;">✏️ Manual Scores</h1>
    <p style="color: #6c757d; font-size: 1.2rem; margin: 0.5rem 0 0 0;">
        Enter bonus points or penalties for participants (organized by week)
    </p>
</div>
""", unsafe_allow_html=True)

# Initialize data manager
dm = DataManager()

# Manual scores file
MANUAL_SCORES_FILE = Path("nikkang_data/manual_scores.json")

def load_manual_scores():
    """Load manual scores from JSON"""
    if MANUAL_SCORES_FILE.exists():
        try:
            with open(MANUAL_SCORES_FILE, 'r') as f:
                return json.load(f)
        except:
            pass
    return {}

def save_manual_scores(data):
    """Save manual scores to JSON"""
    try:
        MANUAL_SCORES_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(MANUAL_SCORES_FILE, 'w') as f:
            json.dump(data, f, indent=2)
        return True
    except:
        return False

# Load data
manual_scores = load_manual_scores()
participants = dm.get_all_participants()

# Sort participants by nickname
participants_sorted = sorted(
    participants,
    key=lambda p: (p.get('display_name') or p.get('nickname') or p.get('name', '')).lower()
)

st.info("""
**Manual Scores** are bonus points or penalties assigned by week.

**Common uses:**
- 🎯 Weekly GOTW bonuses
- 🏆 Weekly performance awards
- ⚡ Special achievement rewards
- ⚠️ Penalties (enter negative points)

**Organization:** Enter scores week by week, with participants listed alphabetically.
""")

st.markdown("---")

# Get current week
current_week = dm.get_current_week()

# Select week
st.markdown("### 📅 Select Week")
col1, col2 = st.columns([2, 1])

with col1:
    selected_week = st.number_input(
        "Week Number:",
        min_value=1,
        max_value=38,
        value=current_week,
        help="Select week to enter manual scores"
    )

with col2:
    st.markdown("<br>", unsafe_allow_html=True)
    if selected_week == current_week:
        st.success(f"📍 Current Week")
    elif selected_week < current_week:
        st.info(f"📜 Past Week")
    else:
        st.warning(f"🔮 Future Week")

st.markdown("---")

# Tabs
tab1, tab2, tab3 = st.tabs(["✏️ Enter Scores", "📊 View All Scores", "📋 Summary"])

# ============================================================================
# TAB 1: ENTER SCORES BY WEEK
# ============================================================================
with tab1:
    st.markdown(f"### ✏️ Enter Manual Scores - Week {selected_week}")
    
    if not participants_sorted:
        st.warning("No participants registered yet")
    else:
        st.info(f"Entering scores for **Week {selected_week}** - Participants sorted alphabetically")
        
        # Show form with all participants
        with st.form(f"week_{selected_week}_scores"):
            st.markdown("#### 👥 All Participants (Sorted by Nickname)")
            
            # Collect inputs for all participants
            participant_scores = {}
            
            for idx, p in enumerate(participants_sorted):
                pid = p.get('id', '')
                nickname = p.get('display_name') or p.get('nickname') or p.get('name', 'Unknown')
                
                # Check if already has score for this week
                existing_score = 0
                existing_reason = ""
                user_scores = manual_scores.get(pid, {})
                
                for entry_id, entry in user_scores.items():
                    if entry.get('week') == selected_week:
                        existing_score = entry.get('points', 0)
                        existing_reason = entry.get('reason', '')
                        break
                
                # Display participant with input
                st.markdown(f"**{idx + 1}. {nickname}**")
                
                col1, col2 = st.columns([1, 3])
                
                with col1:
                    points = st.number_input(
                        "Points",
                        min_value=-50,
                        max_value=50,
                        value=existing_score,
                        key=f"pts_w{selected_week}_{pid}",
                        help="Enter 0 for no change"
                    )
                
                with col2:
                    reason = st.text_input(
                        "Reason (if points given)",
                        value=existing_reason,
                        placeholder="e.g., 'GOTW bonus', 'Perfect week', 'Penalty'",
                        key=f"reason_w{selected_week}_{pid}"
                    )
                
                if points != 0:
                    participant_scores[pid] = {
                        'nickname': nickname,
                        'points': points,
                        'reason': reason if reason else f"Week {selected_week} adjustment"
                    }
                
                st.markdown("---")
            
            # Submit button
            col1, col2 = st.columns(2)
            
            with col1:
                save_btn = st.form_submit_button(
                    f"💾 Save All Scores for Week {selected_week}",
                    use_container_width=True,
                    type="primary"
                )
            
            with col2:
                clear_btn = st.form_submit_button(
                    f"🗑️ Clear Week {selected_week}",
                    use_container_width=True
                )
            
            if save_btn:
                if not participant_scores:
                    st.warning("No scores entered (all are 0)")
                else:
                    # Save scores
                    saved_count = 0
                    
                    for pid, score_data in participant_scores.items():
                        # Generate entry ID
                        entry_id = f"week_{selected_week}_{pid}"
                        
                        # Create entry
                        entry = {
                            'points': score_data['points'],
                            'reason': score_data['reason'],
                            'week': selected_week,
                            'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                            'admin': 'Admin'
                        }
                        
                        # Add to manual scores
                        if pid not in manual_scores:
                            manual_scores[pid] = {}
                        
                        manual_scores[pid][entry_id] = entry
                        saved_count += 1
                    
                    # Save to file
                    if save_manual_scores(manual_scores):
                        st.success(f"✅ Saved {saved_count} scores for Week {selected_week}!")
                        st.rerun()
                    else:
                        st.error("Failed to save manual scores")
            
            if clear_btn:
                # Remove all scores for this week
                cleared_count = 0
                
                for pid in list(manual_scores.keys()):
                    user_scores = manual_scores[pid]
                    # Remove entries for this week
                    entries_to_remove = [
                        entry_id for entry_id, entry in user_scores.items()
                        if entry.get('week') == selected_week
                    ]
                    
                    for entry_id in entries_to_remove:
                        del user_scores[entry_id]
                        cleared_count += 1
                    
                    # Clean up empty user entries
                    if not user_scores:
                        del manual_scores[pid]
                
                if save_manual_scores(manual_scores):
                    st.success(f"✅ Cleared {cleared_count} entries for Week {selected_week}")
                    st.rerun()

# ============================================================================
# TAB 2: VIEW ALL SCORES
# ============================================================================
with tab2:
    st.markdown("### 📊 All Manual Scores")
    
    if not manual_scores:
        st.info("No manual scores entered yet")
    else:
        # Build table grouped by week
        all_entries = []
        
        for uid, user_entries in manual_scores.items():
            # Find participant
            participant = next((p for p in participants_sorted if p.get('id') == uid), None)
            if not participant:
                continue
            
            nickname = participant.get('display_name') or participant.get('nickname') or participant.get('name', 'Unknown')
            
            for entry_id, entry in user_entries.items():
                all_entries.append({
                    'Week': entry.get('week') or 0,
                    'Participant': nickname,
                    'Points': entry.get('points', 0),
                    'Reason': entry.get('reason', 'N/A'),
                    'Date': entry.get('date', 'N/A')
                })
        
        if all_entries:
            df = pd.DataFrame(all_entries)
            
            # Sort by week (descending), then participant name
            df = df.sort_values(['Week', 'Participant'], ascending=[False, True])
            
            st.dataframe(df, use_container_width=True, hide_index=True)
            
            # Summary stats
            st.markdown("---")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Entries", len(all_entries))
            
            with col2:
                weeks_with_scores = len(df['Week'].unique())
                st.metric("Weeks with Scores", weeks_with_scores)
            
            with col3:
                total_positive = sum(e['Points'] for e in all_entries if e['Points'] > 0)
                st.metric("Total Bonuses", f"+{total_positive}")
            
            with col4:
                total_negative = sum(e['Points'] for e in all_entries if e['Points'] < 0)
                st.metric("Total Penalties", total_negative)
        else:
            st.info("No manual scores to display")

# ============================================================================
# TAB 3: SUMMARY BY WEEK
# ============================================================================
with tab3:
    st.markdown("### 📋 Summary by Week")
    
    if not participants_sorted:
        st.warning("No participants registered")
    elif not manual_scores:
        st.info("No manual scores entered yet")
    else:
        # Group by week
        week_summary = {}
        
        for uid, user_entries in manual_scores.items():
            participant = next((p for p in participants_sorted if p.get('id') == uid), None)
            if not participant:
                continue
            
            nickname = participant.get('display_name') or participant.get('nickname') or participant.get('name', 'Unknown')
            
            for entry_id, entry in user_entries.items():
                week = entry.get('week') or 0
                points = entry.get('points', 0)
                
                if week not in week_summary:
                    week_summary[week] = {
                        'participants': [],
                        'total_points': 0,
                        'bonuses': 0,
                        'penalties': 0
                    }
                
                week_summary[week]['participants'].append({
                    'name': nickname,
                    'points': points,
                    'reason': entry.get('reason', 'N/A')
                })
                week_summary[week]['total_points'] += points
                
                if points > 0:
                    week_summary[week]['bonuses'] += points
                else:
                    week_summary[week]['penalties'] += points
        
        # Display by week
        for week in sorted(week_summary.keys(), reverse=True):
            data = week_summary[week]
            
            with st.expander(f"📅 Week {week} - {len(data['participants'])} participants - {data['total_points']} pts total", expanded=(week == selected_week)):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Participants", len(data['participants']))
                with col2:
                    st.metric("Bonuses", f"+{data['bonuses']}")
                with col3:
                    st.metric("Penalties", data['penalties'])
                
                st.markdown("---")
                
                # Sort participants by name
                sorted_participants = sorted(data['participants'], key=lambda x: x['name'].lower())
                
                for p in sorted_participants:
                    emoji = "➕" if p['points'] > 0 else "➖"
                    st.markdown(f"{emoji} **{p['name']}**: {p['points']} pts - _{p['reason']}_")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; padding: 1rem 0; color: #6c757d; font-size: 0.9rem;">
    <p><strong>Nikkang KK EPL Prediction League</strong> - Manual Scores by Week</p>
    <p>💡 Enter scores week by week for easy organization</p>
</div>
""", unsafe_allow_html=True)

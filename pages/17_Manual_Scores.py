"""
Manual Scores Entry - Admin Page
Enter bonus/penalty points for participants
SORTED BY NICKNAME
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
        Enter bonus points or penalties for participants
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

def get_participant_manual_total(uid):
    """Get total manual points for a participant"""
    scores = load_manual_scores()
    user_scores = scores.get(uid, {})
    return sum(entry.get('points', 0) for entry in user_scores.values())

# Load data
manual_scores = load_manual_scores()
participants = dm.get_all_participants()

# Sort participants by nickname/display name
participants_sorted = sorted(
    participants, 
    key=lambda p: (p.get('display_name') or p.get('nickname') or p.get('name', '')).lower()
)

st.info("""
**Manual Scores** are bonus points or penalties you can assign to participants.

**Common uses:**
- 🎯 Bonus for exact GOTW predictions
- 🏆 Stage winner bonuses
- ⚡ Special achievement rewards
- ⚠️ Penalties (enter negative points)
- 📝 Administrative adjustments

**Note:** These points are added to the regular prediction points on the leaderboard.
""")

st.markdown("---")

# Tabs
tab1, tab2, tab3 = st.tabs(["✏️ Enter Scores", "📊 View All Scores", "📋 Summary"])

# ============================================================================
# TAB 1: ENTER MANUAL SCORES
# ============================================================================
with tab1:
    st.markdown("### ✏️ Enter Manual Scores")
    
    if not participants_sorted:
        st.warning("No participants registered yet")
    else:
        # Select participant
        st.markdown("#### 👤 Select Participant")
        
        # Build sorted participant list
        participant_options = {}
        for p in participants_sorted:
            nickname = p.get('display_name') or p.get('nickname') or p.get('name', 'Unknown')
            pid = p.get('id', '')
            participant_options[f"{nickname}"] = pid
        
        selected_participant_name = st.selectbox(
            "Participant (sorted by nickname):",
            options=list(participant_options.keys()),
            key="select_participant"
        )
        
        selected_participant_id = participant_options.get(selected_participant_name, '')
        
        # Show current manual scores for this participant
        st.markdown("---")
        st.markdown("#### 📝 Current Manual Scores")
        
        user_scores = manual_scores.get(selected_participant_id, {})
        
        if user_scores:
            current_total = sum(entry.get('points', 0) for entry in user_scores.values())
            
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(f"**{selected_participant_name}** has {len(user_scores)} manual score entries")
            with col2:
                st.metric("Total Manual Points", current_total)
            
            # Show existing entries
            for entry_id, entry in user_scores.items():
                with st.expander(f"{entry.get('reason', 'No reason')} - {entry.get('points', 0)} pts"):
                    st.write(f"**Points:** {entry.get('points', 0)}")
                    st.write(f"**Reason:** {entry.get('reason', 'N/A')}")
                    st.write(f"**Date:** {entry.get('date', 'N/A')}")
                    st.write(f"**Week:** {entry.get('week', 'N/A')}")
                    
                    if st.button(f"🗑️ Delete This Entry", key=f"delete_{entry_id}"):
                        del user_scores[entry_id]
                        manual_scores[selected_participant_id] = user_scores
                        save_manual_scores(manual_scores)
                        st.success("Entry deleted!")
                        st.rerun()
        else:
            st.info(f"No manual scores for {selected_participant_name} yet")
        
        # Add new entry
        st.markdown("---")
        st.markdown("#### ➕ Add New Manual Score")
        
        with st.form("add_manual_score"):
            col1, col2 = st.columns(2)
            
            with col1:
                points = st.number_input(
                    "Points (positive or negative):",
                    min_value=-100,
                    max_value=100,
                    value=0,
                    help="Enter positive for bonus, negative for penalty"
                )
            
            with col2:
                week = st.number_input(
                    "Week (optional):",
                    min_value=0,
                    max_value=38,
                    value=0,
                    help="Associate with a specific week, or leave as 0 for general"
                )
            
            reason = st.text_input(
                "Reason:",
                placeholder="e.g., 'GOTW bonus', 'Stage 1 winner', 'Late submission penalty'",
                help="Explain why these points are being added"
            )
            
            st.caption("💡 Tip: Be specific with reasons for transparency")
            
            submit = st.form_submit_button("💾 Add Manual Score", use_container_width=True, type="primary")
            
            if submit:
                if not reason:
                    st.error("Please provide a reason")
                elif points == 0:
                    st.warning("Points are 0 - are you sure?")
                else:
                    # Generate entry ID
                    entry_id = f"manual_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                    
                    # Create entry
                    entry = {
                        'points': points,
                        'reason': reason,
                        'week': week if week > 0 else None,
                        'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        'admin': 'Admin'
                    }
                    
                    # Add to user's scores
                    if selected_participant_id not in manual_scores:
                        manual_scores[selected_participant_id] = {}
                    
                    manual_scores[selected_participant_id][entry_id] = entry
                    
                    # Save
                    if save_manual_scores(manual_scores):
                        st.success(f"✅ Added {points} points for {selected_participant_name}")
                        st.info(f"Reason: {reason}")
                        st.rerun()
                    else:
                        st.error("Failed to save manual scores")

# ============================================================================
# TAB 2: VIEW ALL SCORES
# ============================================================================
with tab2:
    st.markdown("### 📊 All Manual Scores")
    
    if not manual_scores:
        st.info("No manual scores entered yet")
    else:
        # Build table
        all_entries = []
        
        for uid, user_entries in manual_scores.items():
            # Find participant
            participant = next((p for p in participants_sorted if p.get('id') == uid), None)
            if not participant:
                continue
            
            nickname = participant.get('display_name') or participant.get('nickname') or participant.get('name', 'Unknown')
            
            for entry_id, entry in user_entries.items():
                all_entries.append({
                    'Participant': nickname,
                    'Points': entry.get('points', 0),
                    'Reason': entry.get('reason', 'N/A'),
                    'Week': entry.get('week') or '-',
                    'Date': entry.get('date', 'N/A'),
                    'ID': uid,
                    'Entry ID': entry_id
                })
        
        if all_entries:
            df = pd.DataFrame(all_entries)
            
            # Sort by participant name, then date
            df = df.sort_values(['Participant', 'Date'])
            
            # Display without ID columns
            display_df = df[['Participant', 'Points', 'Reason', 'Week', 'Date']]
            st.dataframe(display_df, use_container_width=True, hide_index=True)
            
            # Summary stats
            st.markdown("---")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Total Entries", len(all_entries))
            
            with col2:
                total_positive = sum(e['Points'] for e in all_entries if e['Points'] > 0)
                st.metric("Total Bonuses", f"+{total_positive}")
            
            with col3:
                total_negative = sum(e['Points'] for e in all_entries if e['Points'] < 0)
                st.metric("Total Penalties", total_negative)
        else:
            st.info("No manual scores to display")

# ============================================================================
# TAB 3: SUMMARY BY PARTICIPANT
# ============================================================================
with tab3:
    st.markdown("### 📋 Summary by Participant")
    
    if not participants_sorted:
        st.warning("No participants registered")
    elif not manual_scores:
        st.info("No manual scores entered yet")
    else:
        # Build summary
        summary = []
        
        for p in participants_sorted:
            uid = p.get('id', '')
            nickname = p.get('display_name') or p.get('nickname') or p.get('name', 'Unknown')
            
            user_entries = manual_scores.get(uid, {})
            
            if user_entries:
                total_points = sum(entry.get('points', 0) for entry in user_entries.values())
                num_entries = len(user_entries)
                
                bonuses = sum(entry.get('points', 0) for entry in user_entries.values() if entry.get('points', 0) > 0)
                penalties = sum(entry.get('points', 0) for entry in user_entries.values() if entry.get('points', 0) < 0)
                
                summary.append({
                    'Participant': nickname,
                    'Total Points': total_points,
                    'Entries': num_entries,
                    'Bonuses': f"+{bonuses}" if bonuses > 0 else "0",
                    'Penalties': penalties if penalties < 0 else "0"
                })
        
        if summary:
            df_summary = pd.DataFrame(summary)
            df_summary = df_summary.sort_values('Participant')  # Already sorted by nickname
            st.dataframe(df_summary, use_container_width=True, hide_index=True)
            
            # Grand totals
            st.markdown("---")
            st.markdown("#### 🎯 Grand Totals")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                total_participants = len(summary)
                st.metric("Participants with Manual Scores", total_participants)
            
            with col2:
                grand_total = sum(item['Total Points'] for item in summary)
                st.metric("Net Total Points", grand_total)
            
            with col3:
                total_entries = sum(item['Entries'] for item in summary)
                st.metric("Total Entries", total_entries)
        else:
            st.info("No participants have manual scores yet")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; padding: 1rem 0; color: #6c757d; font-size: 0.9rem;">
    <p><strong>Nikkang KK EPL Prediction League</strong> - Manual Scores</p>
    <p>💡 Remember: Always verify totals before locking rounds</p>
</div>
""", unsafe_allow_html=True)

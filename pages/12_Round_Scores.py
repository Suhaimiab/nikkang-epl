"""
Round Scores Management - Admin Page
Enter manual scores for completed rounds (Round 1)
"""

import streamlit as st
import pandas as pd
from pathlib import Path
from datetime import datetime
import sys
import json

sys.path.append(str(Path(__file__).parent.parent))

from utils.data_manager import DataManager
from utils.auth import check_password

st.set_page_config(page_title="Round Scores - Nikkang KK", page_icon="📊", layout="wide")

try:
    from utils.branding import inject_custom_css
    inject_custom_css()
except:
    pass

if not check_password():
    st.stop()

if Path("nikkang_logo.png").exists():
    st.sidebar.image("nikkang_logo.png", use_container_width=True)
    st.sidebar.markdown("---")

st.markdown("""
<div style="text-align: center; padding: 1.5rem 0;">
    <h1 style="color: #667eea;">📊 Round Scores Management</h1>
    <p style="color: #6c757d;">Enter manual scores for completed rounds</p>
</div>
""", unsafe_allow_html=True)

dm = DataManager()

# Round scores file
ROUND_SCORES_FILE = Path("nikkang_data/round_scores.json")

def load_round_scores():
    """Load manual stage scores"""
    if ROUND_SCORES_FILE.exists():
        try:
            with open(ROUND_SCORES_FILE, 'r') as f:
                return json.load(f)
        except:
            pass
    return {
        "round_1": {},
        "round_2": {},
        "round_3": {},
        "round_4": {},
        "round_1_locked": False,
        "round_2_locked": False,
        "round_3_locked": False,
        "round_4_locked": False
    }

def save_round_scores(data):
    """Save manual stage scores"""
    try:
        ROUND_SCORES_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(ROUND_SCORES_FILE, 'w') as f:
            json.dump(data, f, indent=2)
        return True
    except Exception as e:
        st.error(f"Error saving: {e}")
        return False

# Load current scores
round_scores = load_round_scores()

# Round definitions
ROUNDS = {
    1: {"name": "Round 1", "weeks": "Week 1-10", "key": "round_1"},
    2: {"name": "Round 2", "weeks": "Week 11-20", "key": "round_2"},
    3: {"name": "Round 3", "weeks": "Week 21-30", "key": "round_3"},
    4: {"name": "Round 4", "weeks": "Week 31-38", "key": "round_4"},
}

st.info("""
**How it works:**
- Enter final scores for completed rounds (e.g., Round 1)
- Lock the round when confirmed
- Leaderboard will use manual scores for locked rounds
- Unlocked rounds use automated calculation from predictions
""")

# Tabs for each round
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Round 1 (Wk 1-10)",
    "📊 Round 2 (Wk 11-20)",
    "📊 Round 3 (Wk 21-30)",
    "📊 Round 4 (Wk 31-38)",
    "📋 Summary"
])

def display_round_entry(round_num, round_info):
    """Display entry form for a stage"""
    round_key = round_info['key']
    is_locked = round_scores.get(f"{round_key}_locked", False)
    current_scores = round_scores.get(round_key, {})
    
    st.markdown(f"### {round_info['name']} ({round_info['weeks']})")
    
    # Lock status
    if is_locked:
        st.success(f"🔒 **{round_info['name']} is LOCKED** - Scores are finalized")
        
        col1, col2 = st.columns([3, 1])
        with col2:
            if st.button(f"🔓 Unlock {round_info['name']}", key=f"unlock_{round_num}"):
                round_scores[f"{round_key}_locked"] = False
                save_round_scores(round_scores)
                st.rerun()
    else:
        st.warning(f"🔓 **{round_info['name']} is UNLOCKED** - Using automated calculation")
        
        st.markdown("---")
        st.markdown("#### Enter Final Scores")
        
        participants = dm.get_all_participants()
        
        if not participants:
            st.warning("No participants found")
            return
        
        # Entry form
        with st.form(f"stage_{round_num}_form"):
            st.markdown("Enter **Points** and **KK Count** for each participant:")
            
            entries = {}
            
            for p in participants:
                uid = p.get('id', '')
                name = p.get('name', 'Unknown')
                existing = current_scores.get(uid, {})
                
                col1, col2, col3 = st.columns([3, 1, 1])
                
                with col1:
                    st.markdown(f"**{name}**")
                
                with col2:
                    pts = st.number_input(
                        "Points",
                        min_value=0,
                        value=existing.get('points', 0),
                        key=f"pts_{round_num}_{uid}",
                        label_visibility="collapsed"
                    )
                
                with col3:
                    kk = st.number_input(
                        "KK",
                        min_value=0,
                        value=existing.get('kk_count', 0),
                        key=f"kk_{round_num}_{uid}",
                        label_visibility="collapsed"
                    )
                
                entries[uid] = {'points': pts, 'kk_count': kk, 'name': name}
            
            st.markdown("---")
            
            col1, col2 = st.columns(2)
            
            with col1:
                save_btn = st.form_submit_button("💾 Save Scores", use_container_width=True)
            
            with col2:
                lock_btn = st.form_submit_button("🔒 Save & Lock Stage", use_container_width=True, type="primary")
            
            if save_btn or lock_btn:
                round_scores[round_key] = entries
                
                if lock_btn:
                    round_scores[f"{round_key}_locked"] = True
                    st.success(f"✅ {round_info['name']} scores saved and LOCKED!")
                else:
                    st.success(f"✅ {round_info['name']} scores saved (not locked)")
                
                save_round_scores(round_scores)
                st.rerun()
    
    # Display current scores
    st.markdown("---")
    st.markdown("#### Current Scores")
    
    if current_scores:
        table_data = []
        for uid, data in current_scores.items():
            table_data.append({
                'Name': data.get('name', uid),
                'Points': data.get('points', 0),
                'KK Count': data.get('kk_count', 0)
            })
        
        df = pd.DataFrame(table_data)
        df = df.sort_values(['Points', 'KK Count'], ascending=[False, False])
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("No scores entered yet")
    
    # Import from automated calculation
    st.markdown("---")
    st.markdown("#### 🔄 Import from Automated Calculation")
    
    if st.button(f"📥 Import calculated scores for {round_info['name']}", key=f"import_{round_num}"):
        # Calculate scores from predictions
        participants = dm.get_all_participants()
        predictions = dm.load_predictions()
        results = dm.load_results()
        all_matches = dm.get_all_matches()
        
        # Get week range for this stage
        if round_num == 1:
            weeks = list(range(1, 11))
        elif round_num == 2:
            weeks = list(range(11, 21))
        elif round_num == 3:
            weeks = list(range(21, 31))
        else:
            weeks = list(range(31, 39))
        
        imported = {}
        
        for p in participants:
            uid = p.get('id', '')
            name = p.get('name', 'Unknown')
            user_preds = predictions.get(uid, {})
            
            total_pts = 0
            kk_count = 0
            
            for match in all_matches:
                mid = match.get('id', '')
                week = match.get('week', 0)
                
                if week not in weeks:
                    continue
                
                if mid in results and mid in user_preds:
                    result = results[mid]
                    pred = user_preds[mid]
                    is_gotw = match.get('gotw', False)
                    
                    pts = dm.calculate_points(
                        pred.get('home_score', -1),
                        pred.get('away_score', -1),
                        result.get('home_score', -2),
                        result.get('away_score', -2),
                        is_gotw
                    )
                    
                    total_pts += pts
                    
                    if (pred.get('home_score') == result.get('home_score') and
                        pred.get('away_score') == result.get('away_score')):
                        kk_count += 1
            
            imported[uid] = {'points': total_pts, 'kk_count': kk_count, 'name': name}
        
        round_scores[round_key] = imported
        save_round_scores(round_scores)
        st.success(f"✅ Imported {len(imported)} participant scores!")
        st.rerun()

with tab1:
    display_round_entry(1, ROUNDS[1])

with tab2:
    display_round_entry(2, ROUNDS[2])

with tab3:
    display_round_entry(3, ROUNDS[3])

with tab4:
    display_round_entry(4, ROUNDS[4])

with tab5:
    st.markdown("### 📋 All Rounds Summary")
    
    participants = dm.get_all_participants()
    
    if not participants:
        st.warning("No participants found")
    else:
        # Build summary table
        summary_data = []
        
        for p in participants:
            uid = p.get('id', '')
            name = p.get('name', 'Unknown')
            
            row = {'Name': name}
            total_pts = 0
            total_kk = 0
            
            for round_num, round_info in STAGES.items():
                round_key = round_info['key']
                is_locked = round_scores.get(f"{round_key}_locked", False)
                scores = round_scores.get(round_key, {}).get(uid, {})
                
                pts = scores.get('points', 0)
                kk = scores.get('kk_count', 0)
                
                status = "🔒" if is_locked else "🔓"
                row[f"S{round_num} Pts"] = pts
                row[f"S{round_num} KK"] = kk
                row[f"S{round_num}"] = f"{pts} ({status})"
                
                total_pts += pts
                total_kk += kk
            
            row['Total Pts'] = total_pts
            row['Total KK'] = total_kk
            
            summary_data.append(row)
        
        df = pd.DataFrame(summary_data)
        df = df.sort_values(['Total Pts', 'Total KK'], ascending=[False, False])
        
        # Display summary
        display_cols = ['Name', 'S1', 'S2', 'S3', 'S4', 'Total Pts', 'Total KK']
        st.dataframe(df[display_cols], use_container_width=True, hide_index=True)
        
        st.markdown("---")
        st.markdown("#### Lock Status")
        
        cols = st.columns(4)
        for i, (round_num, round_info) in enumerate(STAGES.items()):
            round_key = round_info['key']
            is_locked = round_scores.get(f"{round_key}_locked", False)
            
            with cols[i]:
                if is_locked:
                    st.success(f"🔒 {round_info['name']}: LOCKED")
                else:
                    st.warning(f"🔓 {round_info['name']}: Auto")

# Footer
st.markdown("---")
st.caption("Nikkang KK EPL Prediction League - Round Scores Management")

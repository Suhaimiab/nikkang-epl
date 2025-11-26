"""
Match Management - Admin Page
Add/edit matches, set Game of the Week, manage fixtures
With date/time sorting and manual reordering
"""

import streamlit as st
import pandas as pd
from pathlib import Path
from datetime import datetime, date
import sys

sys.path.append(str(Path(__file__).parent.parent))

from utils.data_manager import DataManager
from utils.auth import check_password

st.set_page_config(page_title="Match Management - Nikkang KK", page_icon="⚽", layout="wide")

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
    <h1 style="color: #667eea;">⚽ Match Management</h1>
    <p style="color: #6c757d;">Manage fixtures, set GOTW, sort by kickoff</p>
</div>
""", unsafe_allow_html=True)

dm = DataManager()

EPL_TEAMS = ["Arsenal", "Aston Villa", "Bournemouth", "Brentford", "Brighton", "Chelsea", 
             "Crystal Palace", "Everton", "Fulham", "Ipswich Town", "Leicester City", 
             "Liverpool", "Man City", "Man United", "Newcastle", "Nottingham Forest", 
             "Southampton", "Tottenham", "West Ham", "Wolves"]

KICKOFF_TIMES = ["12:30", "14:00", "15:00", "16:30", "17:30", "19:45", "20:00", "20:45"]

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["⭐ GOTW", "📋 View", "➕ Add", "✏️ Edit", "🔄 Reorder", "🗑️ Delete"])

# TAB 1: GAME OF THE WEEK
with tab1:
    st.markdown("### ⭐ Set Game of the Week")
    st.info("""
**Scoring System:**
- **Normal:** Exact: 6pts, Correct: 3pts
- **GOTW:** Exact: 10pts, Correct: 5pts
- **Week 38 FINALE:** ALL matches score 10pts / 5pts / 0pts
""")
    
    weeks = dm.get_weeks()
    if not weeks:
        st.warning("No matches found. Add matches first!")
    else:
        selected_week = st.selectbox("Select Gameweek:", weeks, format_func=lambda x: f"Week {x}", key="gotw_week")
        matches = dm.get_matches_by_week(selected_week)
        
        if matches:
            current_gotw = next((m for m in matches if m.get('gotw')), None)
            if current_gotw:
                st.success(f"**Current GOTW:** {current_gotw.get('home')} vs {current_gotw.get('away')}")
            else:
                st.warning("**No GOTW set for this week!**")
            
            st.markdown("---")
            match_options = [f"{m.get('home')} vs {m.get('away')} ({m.get('date', '-')} {m.get('time', '-')})" + (" ⭐" if m.get('gotw') else "") for m in matches]
            selected_idx = st.radio("Choose match:", range(len(matches)), format_func=lambda x: match_options[x])
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("⭐ Set as GOTW", type="primary", use_container_width=True):
                    raw = dm.load_matches()
                    wk = str(selected_week)
                    for i in range(len(raw[wk])):
                        raw[wk][i]['gotw'] = (i == selected_idx)
                    dm.save_matches(raw)
                    st.success("✅ GOTW set!")
                    st.rerun()
            with col2:
                if st.button("❌ Clear GOTW", use_container_width=True):
                    raw = dm.load_matches()
                    wk = str(selected_week)
                    for i in range(len(raw[wk])):
                        raw[wk][i]['gotw'] = False
                    dm.save_matches(raw)
                    st.success("✅ GOTW cleared!")
                    st.rerun()

# TAB 2: VIEW MATCHES
with tab2:
    st.markdown("### 📋 View All Matches")
    weeks = dm.get_weeks()
    if weeks:
        col1, col2 = st.columns([2, 1])
        with col1:
            view_week = st.selectbox("Filter:", ["All"] + [f"Week {w}" for w in weeks], key="view_week")
        with col2:
            sort_time = st.checkbox("Sort by kickoff", value=True)
        
        if view_week == "All":
            all_matches = dm.get_all_matches()
        else:
            all_matches = dm.get_matches_by_week(int(view_week.split()[1]))
        
        if sort_time:
            all_matches = sorted(all_matches, key=lambda m: f"{m.get('date', '9999-12-31')} {m.get('time', '23:59')}")
        
        if all_matches:
            results = dm.load_results()
            data = [{
                'Week': m.get('week', '?'),
                'Date': m.get('date', '-'),
                'Time': m.get('time', '-'),
                'Home': m.get('home', ''),
                'Away': m.get('away', ''),
                'GOTW': '⭐' if m.get('gotw') else '',
                'Result': f"{results.get(m.get('id'), {}).get('home_score', '-')}-{results.get(m.get('id'), {}).get('away_score', '-')}" if m.get('id') in results else 'TBD'
            } for m in all_matches]
            st.dataframe(pd.DataFrame(data), use_container_width=True, hide_index=True)

# TAB 3: ADD MATCHES
with tab3:
    st.markdown("### ➕ Add Matches")
    
    with st.form("add_match"):
        col1, col2 = st.columns(2)
        with col1:
            new_week = st.number_input("Week:", 1, 38, 1)
            home = st.selectbox("Home:", EPL_TEAMS, key="add_home")
            match_date = st.date_input("Date:", value=date.today())
        with col2:
            is_gotw = st.checkbox("⭐ GOTW")
            away = st.selectbox("Away:", EPL_TEAMS, key="add_away")
            match_time = st.selectbox("Kickoff:", KICKOFF_TIMES, index=2)
        
        if st.form_submit_button("➕ Add Match", use_container_width=True):
            if home == away:
                st.error("Teams cannot be the same!")
            else:
                raw = dm.load_matches()
                wk = str(new_week)
                if wk not in raw:
                    raw[wk] = []
                if any(m.get('home') == home and m.get('away') == away for m in raw[wk]):
                    st.error("Match already exists!")
                else:
                    if is_gotw:
                        for m in raw[wk]:
                            m['gotw'] = False
                    raw[wk].append({'home': home, 'away': away, 'gotw': is_gotw, 'date': match_date.strftime('%Y-%m-%d'), 'time': match_time})
                    dm.save_matches(raw)
                    st.success(f"✅ Added: {home} vs {away}")
    
    st.markdown("---")
    st.markdown("#### Bulk Add")
    st.caption("Format: `Home, Away, Date, Time` or `Home, Away`")
    bulk_week = st.number_input("Week:", 1, 38, 1, key="bulk_w")
    bulk_date = st.date_input("Default date:", date.today(), key="bulk_d")
    bulk_time = st.selectbox("Default time:", KICKOFF_TIMES, index=2, key="bulk_t")
    bulk_text = st.text_area("Matches:", height=100)
    
    if st.button("➕ Add All", use_container_width=True):
        if bulk_text.strip():
            raw = dm.load_matches()
            wk = str(bulk_week)
            if wk not in raw:
                raw[wk] = []
            added = 0
            for line in bulk_text.strip().split('\n'):
                parts = [p.strip() for p in line.split(',')]
                if len(parts) >= 2:
                    h, a = parts[0], parts[1]
                    d = parts[2] if len(parts) > 2 else bulk_date.strftime('%Y-%m-%d')
                    t = parts[3] if len(parts) > 3 else bulk_time
                    if not any(m.get('home') == h and m.get('away') == a for m in raw[wk]):
                        raw[wk].append({'home': h, 'away': a, 'gotw': False, 'date': d, 'time': t})
                        added += 1
            dm.save_matches(raw)
            st.success(f"✅ Added {added} matches")

# TAB 4: EDIT MATCHES
with tab4:
    st.markdown("### ✏️ Edit Matches")
    weeks = dm.get_weeks()
    if weeks:
        edit_week = st.selectbox("Week:", weeks, format_func=lambda x: f"Week {x}", key="edit_w")
        raw = dm.load_matches()
        wk = str(edit_week)
        matches = raw.get(wk, [])
        
        for i, m in enumerate(matches):
            gotw_icon = " ⭐" if m.get('gotw') else ""
            with st.expander(f"**{m.get('home')} vs {m.get('away')}**{gotw_icon} ({m.get('date', '-')} {m.get('time', '-')})"):
                col1, col2 = st.columns(2)
                with col1:
                    new_home = st.selectbox("Home:", EPL_TEAMS, index=EPL_TEAMS.index(m.get('home')) if m.get('home') in EPL_TEAMS else 0, key=f"eh_{i}")
                    try:
                        cur_date = datetime.strptime(m.get('date', ''), '%Y-%m-%d').date()
                    except:
                        cur_date = date.today()
                    new_date = st.date_input("Date:", value=cur_date, key=f"ed_{i}")
                with col2:
                    new_away = st.selectbox("Away:", EPL_TEAMS, index=EPL_TEAMS.index(m.get('away')) if m.get('away') in EPL_TEAMS else 0, key=f"ea_{i}")
                    new_time = st.selectbox("Time:", KICKOFF_TIMES, index=KICKOFF_TIMES.index(m.get('time')) if m.get('time') in KICKOFF_TIMES else 2, key=f"et_{i}")
                new_gotw = st.checkbox("GOTW", value=m.get('gotw', False), key=f"eg_{i}")
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("💾 Save", key=f"save_{i}", use_container_width=True):
                        if new_gotw and not m.get('gotw'):
                            for j in range(len(raw[wk])):
                                raw[wk][j]['gotw'] = False
                        raw[wk][i] = {'home': new_home, 'away': new_away, 'gotw': new_gotw, 'date': new_date.strftime('%Y-%m-%d'), 'time': new_time}
                        dm.save_matches(raw)
                        st.success("✅ Saved!")
                        st.rerun()
                with col2:
                    if st.button("🗑️ Delete", key=f"del_{i}", use_container_width=True):
                        del raw[wk][i]
                        if not raw[wk]:
                            del raw[wk]
                        dm.save_matches(raw)
                        st.success("✅ Deleted!")
                        st.rerun()

# TAB 5: REORDER MATCHES
with tab5:
    st.markdown("### 🔄 Reorder Matches")
    weeks = dm.get_weeks()
    if weeks:
        reorder_week = st.selectbox("Week:", weeks, format_func=lambda x: f"Week {x}", key="reorder_w")
        raw = dm.load_matches()
        wk = str(reorder_week)
        matches = raw.get(wk, [])
        
        if matches:
            if st.button("⚡ Auto-Sort by Kickoff Time", type="primary", use_container_width=True):
                raw[wk] = sorted(matches, key=lambda m: f"{m.get('date', '9999-12-31')} {m.get('time', '23:59')}")
                dm.save_matches(raw)
                st.success("✅ Sorted!")
                st.rerun()
            
            st.markdown("---")
            st.markdown("**Manual Reorder:**")
            
            for i, m in enumerate(matches):
                col1, col2, col3, col4 = st.columns([0.5, 3, 0.5, 0.5])
                with col1:
                    st.write(f"**{i+1}.**")
                with col2:
                    gotw = "⭐" if m.get('gotw') else ""
                    st.write(f"{m.get('home')} vs {m.get('away')} {gotw}")
                    st.caption(f"{m.get('date', '-')} {m.get('time', '-')}")
                with col3:
                    if i > 0 and st.button("⬆️", key=f"up_{i}"):
                        matches[i], matches[i-1] = matches[i-1], matches[i]
                        raw[wk] = matches
                        dm.save_matches(raw)
                        st.rerun()
                with col4:
                    if i < len(matches)-1 and st.button("⬇️", key=f"dn_{i}"):
                        matches[i], matches[i+1] = matches[i+1], matches[i]
                        raw[wk] = matches
                        dm.save_matches(raw)
                        st.rerun()

# TAB 6: DELETE WEEK
with tab6:
    st.markdown("### 🗑️ Delete Gameweek")
    st.warning("⚠️ This will delete ALL matches for the selected week!")
    
    weeks = dm.get_weeks()
    if weeks:
        del_week = st.selectbox("Week to delete:", weeks, format_func=lambda x: f"Week {x} ({len(dm.get_matches_by_week(x))} matches)", key="del_w")
        
        matches = dm.get_matches_by_week(del_week)
        st.markdown("**Matches to delete:**")
        for m in matches:
            st.write(f"- {m.get('home')} vs {m.get('away')}")
        
        confirm = st.text_input(f"Type 'DELETE WEEK {del_week}' to confirm:")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🗑️ Delete Week", type="primary", use_container_width=True):
                if confirm == f"DELETE WEEK {del_week}":
                    raw = dm.load_matches()
                    if str(del_week) in raw:
                        del raw[str(del_week)]
                        dm.save_matches(raw)
                        st.success(f"✅ Week {del_week} deleted!")
                        st.rerun()
                else:
                    st.error("Type confirmation text exactly")
        with col2:
            if st.button("📥 Backup First", use_container_width=True):
                dm.backup_all_data()
                st.success("✅ Backup created!")

st.markdown("---")
st.caption("Nikkang KK EPL Prediction League - Match Management")

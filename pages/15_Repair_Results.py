"""
Results Repair Tool - Fix Mismatched Results
Nikkang KK EPL Prediction Competition
"""

import streamlit as st
import pandas as pd
from pathlib import Path
from datetime import datetime
import json
import sys

sys.path.append(str(Path(__file__).parent.parent))

from utils.data_manager import DataManager

st.set_page_config(page_title="Repair Results - Nikkang KK", page_icon="🔧", layout="wide")

# Authentication
try:
    from utils.auth import check_password
    if not check_password():
        st.stop()
except:
    pass

# Logo
if Path("nikkang_logo.png").exists():
    st.sidebar.image("nikkang_logo.png", use_container_width=True)
    st.sidebar.markdown("---")

st.markdown('<div style="background:linear-gradient(135deg,#dc3545 0%,#c82333 100%);color:white;padding:1.5rem;border-radius:10px;text-align:center;margin-bottom:1.5rem;"><h1 style="margin:0;font-size:2rem;">🔧 Results Repair Tool</h1><p style="margin:0.5rem 0 0 0;opacity:0.9;">Fix mismatched results data</p></div>', unsafe_allow_html=True)

dm = DataManager()

# Load all data
matches_data = dm.load_matches()
results_data = dm.load_results()
predictions_data = dm.load_predictions()

# Get available weeks
available_weeks = sorted([int(w) for w in matches_data.keys() if w.isdigit()], reverse=True)

if not available_weeks:
    st.error("No fixtures found. Import fixtures first.")
    st.stop()

# Week selector
selected_week = st.selectbox("🗓️ Select Week to Repair:", available_weeks, format_func=lambda x: f"Gameweek {x}")

st.markdown("---")

week_str = str(selected_week)
week_fixtures = matches_data.get(week_str, [])
week_results = results_data.get(week_str, [])

if not week_fixtures:
    st.error(f"No fixtures found for Week {selected_week}")
    st.stop()

# ============================================================================
# STEP 1: SHOW CURRENT STATE (DIAGNOSIS)
# ============================================================================
st.markdown("### 📋 Step 1: Current Data (Diagnosis)")

st.info(f"**Week {selected_week}:** {len(week_fixtures)} fixtures, {len(week_results) if isinstance(week_results, list) else 0} results stored")

# Build comparison table
comparison_data = []

for idx, fixture in enumerate(week_fixtures):
    home_team = fixture.get('home', '?')
    away_team = fixture.get('away', '?')
    is_gotw = fixture.get('gotw', False)
    
    # Get stored result for this index
    if isinstance(week_results, list) and idx < len(week_results):
        result = week_results[idx]
        if result:
            stored_home = result.get('home', result.get('home_score', '-'))
            stored_away = result.get('away', result.get('away_score', '-'))
            stored_score = f"{stored_home} - {stored_away}"
        else:
            stored_score = "No result"
    else:
        stored_score = "No result"
    
    comparison_data.append({
        'Index': idx,
        'Fixture': f"{home_team} vs {away_team}",
        'GOTW': '⭐' if is_gotw else '',
        'Stored Result': stored_score,
        'Status': '✅' if stored_score != "No result" else '❌'
    })

df_comparison = pd.DataFrame(comparison_data)
st.dataframe(df_comparison, use_container_width=True, hide_index=True)

# ============================================================================
# STEP 2: CLEAR RESULTS
# ============================================================================
st.markdown("---")
st.markdown("### 🗑️ Step 2: Clear Corrupted Results")

st.warning("⚠️ This will DELETE all results for this week. You will need to re-enter them.")

col1, col2 = st.columns([1, 3])
with col1:
    if st.button("🗑️ CLEAR WEEK RESULTS", type="primary", use_container_width=True):
        # Clear list format
        if week_str in results_data:
            del results_data[week_str]
        
        # Clear indexed format (e.g., "11_0", "11_1", etc.)
        keys_to_remove = [k for k in list(results_data.keys()) if k.startswith(f"{week_str}_")]
        for k in keys_to_remove:
            del results_data[k]
        
        dm.save_results(results_data)
        st.success(f"✅ Cleared all results for Week {selected_week}")
        st.rerun()

# ============================================================================
# STEP 3: ENTER CORRECT RESULTS
# ============================================================================
st.markdown("---")
st.markdown("### ✏️ Step 3: Enter Correct Results")

st.info("Enter the ACTUAL match results below. Make sure each score matches the correct fixture!")

# Create input form
new_results = []
valid_entries = 0

cols_per_row = 2
rows = (len(week_fixtures) + cols_per_row - 1) // cols_per_row

for row_idx in range(rows):
    cols = st.columns(cols_per_row)
    
    for col_idx in range(cols_per_row):
        match_idx = row_idx * cols_per_row + col_idx
        
        if match_idx >= len(week_fixtures):
            break
        
        fixture = week_fixtures[match_idx]
        home_team = fixture.get('home', '?')
        away_team = fixture.get('away', '?')
        is_gotw = fixture.get('gotw', False)
        
        with cols[col_idx]:
            gotw_marker = " ⭐ GOTW" if is_gotw else ""
            st.markdown(f"**Match {match_idx + 1}{gotw_marker}**")
            st.markdown(f"**{home_team}** vs **{away_team}**")
            
            subcol1, subcol2 = st.columns(2)
            with subcol1:
                home_score = st.number_input(
                    f"{home_team[:3].upper()}",
                    min_value=-1, max_value=15, value=-1,
                    key=f"home_{match_idx}",
                    help="-1 = No result yet"
                )
            with subcol2:
                away_score = st.number_input(
                    f"{away_team[:3].upper()}",
                    min_value=-1, max_value=15, value=-1,
                    key=f"away_{match_idx}",
                    help="-1 = No result yet"
                )
            
            if home_score >= 0 and away_score >= 0:
                new_results.append({
                    'index': match_idx,
                    'home': home_score,
                    'away': away_score
                })
                valid_entries += 1
            else:
                new_results.append({
                    'index': match_idx,
                    'home': None,
                    'away': None
                })
            
            st.markdown("---")

# Save button
st.markdown("### 💾 Step 4: Save Results")

if valid_entries == 0:
    st.warning("Enter at least one result above (scores must be 0 or higher)")
else:
    st.success(f"Ready to save {valid_entries} results")
    
    # Preview
    st.markdown("**Preview:**")
    preview_data = []
    for r in new_results:
        if r['home'] is not None:
            fixture = week_fixtures[r['index']]
            preview_data.append({
                'Match': f"{fixture.get('home', '?')} vs {fixture.get('away', '?')}",
                'Result': f"{r['home']} - {r['away']}"
            })
    
    if preview_data:
        st.dataframe(pd.DataFrame(preview_data), use_container_width=True, hide_index=True)
    
    if st.button("💾 SAVE ALL RESULTS", type="primary", use_container_width=True):
        # Build results list
        results_list = []
        
        for idx in range(len(week_fixtures)):
            # Find result for this index
            result_entry = next((r for r in new_results if r['index'] == idx), None)
            
            if result_entry and result_entry['home'] is not None:
                results_list.append({
                    'home': result_entry['home'],
                    'away': result_entry['away']
                })
            else:
                # Placeholder for no result
                results_list.append({'home': 0, 'away': 0})
        
        # Save in list format
        results_data[week_str] = results_list
        
        # Also save in indexed format for compatibility
        for idx, r in enumerate(new_results):
            if r['home'] is not None:
                match_key = f"{week_str}_{idx}"
                results_data[match_key] = {
                    'home_score': r['home'],
                    'away_score': r['away'],
                    'entered_at': datetime.now().isoformat(),
                    'source': 'manual_repair'
                }
        
        dm.save_results(results_data)
        st.success(f"✅ Saved {valid_entries} results for Week {selected_week}!")
        st.balloons()
        st.rerun()

# ============================================================================
# QUICK REFERENCE: ACTUAL EPL RESULTS
# ============================================================================
st.markdown("---")
st.markdown("### 📖 Quick Reference: Week 11 Actual Results (November 8-9, 2025)")

st.markdown("""
**Gameweek 11 actual results:**

| Match | Result |
|-------|--------|
| Tottenham vs Man United | 2 - 2 |
| Everton vs Fulham | 2 - 0 |
| West Ham vs Burnley | 3 - 2 |
| Sunderland vs Arsenal | 2 - 2 |
| Chelsea vs Wolves | 3 - 0 |
| Aston Villa vs Bournemouth | 4 - 0 |
| Brentford vs Newcastle | 3 - 1 |
| Crystal Palace vs Brighton | 3 - 1 |
| Nott'm Forest vs Leeds | 3 - 1 |
| Man City vs Liverpool ⭐ | 3 - 0 |

*Source: Various sports news sites - verify if unsure*
""")

st.markdown("---")

# Sidebar info
st.sidebar.markdown("### 📖 How to Use")
st.sidebar.markdown("""
1. **Select Week** to repair
2. **Review** current stored data
3. **Clear** corrupted results
4. **Enter** correct scores manually
5. **Save** to fix the data

After saving, check the Weekly Results page to verify scores are correct.
""")

st.sidebar.markdown("---")
st.sidebar.warning("⚠️ Admin only! Be careful when modifying results.")

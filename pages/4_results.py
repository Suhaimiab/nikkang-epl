"""
Results Page - Enter Match Results (Admin)
"""

import streamlit as st
from utils.config import setup_page, apply_custom_css
from utils.data_manager import DataManager
from utils.auth import require_admin

setup_page()
apply_custom_css()

# Require admin access
require_admin()

dm = DataManager()

st.title("📊 Match Results (Admin)")

st.info("👮 Admin access granted. Enter match results below.")

st.markdown("---")

# Week selector
col1, col2 = st.columns([2, 1])

with col1:
    week = st.selectbox(
        "Select Week",
        range(1, 39),
        index=dm.get_current_week() - 1,
        format_func=lambda x: f"Week {x}" + (" (FINALE)" if x == 38 else "")
    )

with col2:
    st.metric("Current Week", dm.get_current_week())

st.markdown("---")

# Load matches for selected week
matches = dm.get_week_matches(week)

if not matches:
    st.warning(f"⚠️ No matches set up for Week {week} yet. Please set up matches in the Admin panel first.")
    st.stop()

# Load existing results
existing_results = dm.get_week_results(week)

st.subheader(f"Enter Results - Week {week}")

# Create form for results
with st.form("results_form"):
    results = []
    
    # Display matches
    for idx, match in enumerate(matches):
        is_gotw = match.get('gotw', False)
        gotw_class = "gotw" if is_gotw else ""
        
        # Get existing result if available
        existing = existing_results[idx] if idx < len(existing_results) else {'home': 0, 'away': 0}
        
        st.markdown(f"""
        <div class="match-card {gotw_class}">
            <strong>Match {idx + 1}:</strong> {match['home']} vs {match['away']}
            {' ⭐ <strong style="color: #ff9800;">GOTW</strong>' if is_gotw else ''}
        </div>
        """, unsafe_allow_html=True)
        
        col_a, col_b, col_c = st.columns([2, 1, 2])
        
        with col_a:
            st.caption(f"**{match['home']}**")
        
        with col_b:
            st.caption("**Final Score**")
        
        with col_c:
            st.caption(f"**{match['away']}**")
        
        col_a, col_b, col_c = st.columns([2, 1, 2])
        
        with col_a:
            home_score = st.number_input(
                f"Result Home {idx}",
                min_value=0,
                max_value=15,
                value=int(existing.get('home', 0)),
                key=f"res_home_{idx}",
                label_visibility="collapsed"
            )
        
        with col_b:
            st.markdown("<div style='text-align: center; padding-top: 8px;'>-</div>", unsafe_allow_html=True)
        
        with col_c:
            away_score = st.number_input(
                f"Result Away {idx}",
                min_value=0,
                max_value=15,
                value=int(existing.get('away', 0)),
                key=f"res_away_{idx}",
                label_visibility="collapsed"
            )
        
        results.append({'home': home_score, 'away': away_score})
        
        st.markdown("<br>", unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Submit button
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        submitted = st.form_submit_button("💾 Save Results & Calculate Scores", use_container_width=True)
    
    if submitted:
        # Save results
        dm.save_week_results(week, results)
        st.success(f"✅ Results saved successfully for Week {week}!")
        st.success("🧮 Leaderboard scores recalculated!")
        
        # Show summary
        st.markdown("---")
        st.subheader("📋 Results Summary")
        
        for idx, (match, result) in enumerate(zip(matches, results)):
            col1, col2 = st.columns([3, 1])
            with col1:
                st.text(f"{idx + 1}. {match['home']} vs {match['away']}")
            with col2:
                st.markdown(f"<div class='score-display'>{result['home']} - {result['away']}</div>", 
                          unsafe_allow_html=True)
        
        # Show button to view updated leaderboard
        if st.button("🏆 View Updated Leaderboard"):
            st.switch_page("pages/5_leaderboard.py")

st.markdown("---")

# Show predictions vs results comparison
if existing_results and len(existing_results) == len(matches):
    st.subheader("📊 Predictions vs Results Analysis")
    
    # Get all predictions for this week
    predictions = dm.load_predictions()
    week_predictions = predictions.get(str(week), {})
    
    if week_predictions:
        st.info(f"Total predictions received: **{len(week_predictions)}**")
        
        # Analyze each match
        with st.expander("🔍 Match-by-Match Analysis"):
            for idx, (match, result) in enumerate(zip(matches, existing_results)):
                st.markdown(f"### Match {idx + 1}: {match['home']} {result['home']}-{result['away']} {match['away']}")
                
                # Count exact scores and correct results
                exact_scores = 0
                correct_results = 0
                wrong_predictions = 0
                
                for pid, pred_list in week_predictions.items():
                    if idx < len(pred_list):
                        pred = pred_list[idx]
                        participant = dm.get_participant(pid)
                        
                        if pred['home'] == result['home'] and pred['away'] == result['away']:
                            exact_scores += 1
                        else:
                            pred_result = 'H' if pred['home'] > pred['away'] else ('A' if pred['home'] < pred['away'] else 'D')
                            actual_result = 'H' if result['home'] > result['away'] else ('A' if result['home'] < result['away'] else 'D')
                            
                            if pred_result == actual_result:
                                correct_results += 1
                            else:
                                wrong_predictions += 1
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Exact Scores (KK)", exact_scores)
                with col2:
                    st.metric("Correct Results", correct_results)
                with col3:
                    st.metric("Wrong Predictions", wrong_predictions)
                
                st.markdown("---")
    else:
        st.info("No predictions submitted for this week yet.")

st.markdown("---")

# Quick actions
st.subheader("⚙️ Quick Actions")

col1, col2 = st.columns(2)

with col1:
    if st.button("🔄 Recalculate All Scores", use_container_width=True):
        # Recalculate leaderboard
        leaderboard = dm.calculate_leaderboard()
        st.success(f"✅ Scores recalculated for all {len(leaderboard)} participants!")

with col2:
    if st.button("🏆 View Leaderboard", use_container_width=True):
        st.switch_page("pages/5_leaderboard.py")

st.markdown("---")
st.caption("Nikkang KK - EPL Prediction Competition 2025/26")

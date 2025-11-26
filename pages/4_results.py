"""
Results Page - View Match Results (Public)
Shows match results and user's predictions vs actual results
"""

import streamlit as st
import pandas as pd
from pathlib import Path
from datetime import datetime
import sys

sys.path.append(str(Path(__file__).parent.parent))

from utils.data_manager import DataManager

# Page config
st.set_page_config(
    page_title="Results - Nikkang KK",
    page_icon="📊",
    layout="wide"
)

# Import branding
try:
    from utils.branding import inject_custom_css
    inject_custom_css()
except:
    pass

# Logo in sidebar
if Path("nikkang_logo.png").exists():
    st.sidebar.markdown('<div style="padding-top: 0.5rem;"></div>', unsafe_allow_html=True)
    st.sidebar.markdown('<div class="sidebar-logo-container">', unsafe_allow_html=True)
    st.sidebar.image("nikkang_logo.png", use_container_width=True)
    st.sidebar.markdown('</div>', unsafe_allow_html=True)
    st.sidebar.markdown("---")

# Custom CSS
st.markdown("""
<style>
    .result-card {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 0.75rem 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        border-left: 4px solid #667eea;
    }
    .result-card.gotw {
        border-left: 4px solid #ff9800;
        background: linear-gradient(135deg, #fff9e6 0%, #ffffff 100%);
    }
    .score-big {
        font-size: 2rem;
        font-weight: bold;
        color: #333;
        text-align: center;
    }
    .team-name {
        font-size: 1.1rem;
        font-weight: 600;
        color: #333;
    }
    .prediction-correct {
        background: #d4edda;
        border-radius: 8px;
        padding: 0.5rem;
        text-align: center;
    }
    .prediction-wrong {
        background: #f8d7da;
        border-radius: 8px;
        padding: 0.5rem;
        text-align: center;
    }
    .prediction-exact {
        background: #cce5ff;
        border-radius: 8px;
        padding: 0.5rem;
        text-align: center;
        border: 2px solid #004085;
    }
    .points-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-weight: bold;
        font-size: 0.9rem;
    }
    .points-6 { background: #cce5ff; color: #004085; }
    .points-3 { background: #d4edda; color: #155724; }
    .points-0 { background: #f8d7da; color: #721c24; }
    .points-12 { background: #fff3cd; color: #856404; border: 2px solid #ffc107; }
    .no-result {
        color: #6c757d;
        font-style: italic;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div style="text-align: center; padding: 1.5rem 0;">
    <h1 style="color: #667eea; font-size: 2.5rem; margin: 0;">📊 Match Results</h1>
    <p style="color: #6c757d; font-size: 1.2rem; margin: 0.5rem 0 0 0;">
        View results and check your predictions
    </p>
</div>
""", unsafe_allow_html=True)

# Initialize
dm = DataManager()

# Get user from session or query params
user_id = st.query_params.get("user_id", None)
if "user_id" in st.session_state:
    user_id = st.session_state["user_id"]

# User selector in sidebar
participants = dm.get_all_participants()

if participants:
    st.sidebar.markdown("### 👤 View As:")
    participant_options = {p.get('id'): p.get('display_name') or p.get('name', 'Unknown') for p in participants}
    
    if user_id and user_id in participant_options:
        default_idx = list(participant_options.keys()).index(user_id)
    else:
        default_idx = 0
    
    selected_user = st.sidebar.selectbox(
        "Select participant:",
        options=list(participant_options.keys()),
        format_func=lambda x: participant_options[x],
        index=default_idx,
        key="result_user_select"
    )
    
    user_id = selected_user
    st.session_state["user_id"] = user_id

# Week selector
weeks = dm.get_weeks()
results_data = dm.load_results()

if not weeks:
    st.warning("No matches set up yet. Check back later!")
    st.stop()

# Find weeks with results
weeks_with_results = []
for week in weeks:
    matches = dm.get_matches_by_week(week)
    for m in matches:
        if m.get('id') in results_data:
            weeks_with_results.append(week)
            break

# Tabs for viewing
tab1, tab2, tab3 = st.tabs(["📅 By Gameweek", "📊 My Performance", "🏆 Summary"])

# ============================================================================
# TAB 1: BY GAMEWEEK
# ============================================================================
with tab1:
    if not weeks_with_results:
        st.info("No results have been entered yet. Check back after matches are completed!")
    else:
        # Week selector
        col1, col2 = st.columns([2, 1])
        
        with col1:
            selected_week = st.selectbox(
                "Select Gameweek:",
                weeks_with_results,
                index=len(weeks_with_results) - 1,  # Default to latest
                format_func=lambda x: f"Week {x}",
                key="results_week"
            )
        
        with col2:
            st.metric("Weeks with Results", len(weeks_with_results))
        
        st.markdown("---")
        
        # Get matches and results
        matches = dm.get_matches_by_week(selected_week)
        
        # Load predictions - YOUR FORMAT: {"11": {"Y8PX0JE4": [{home, away}, ...]}}
        all_predictions = dm.load_predictions()
        week_predictions = all_predictions.get(str(selected_week), {})
        user_pred_list = week_predictions.get(user_id, []) if user_id else []
        
        # Convert list to dict by index for easier lookup
        user_preds = {}
        for idx, pred in enumerate(user_pred_list):
            user_preds[idx] = pred
        
        # Calculate week points for user
        week_points = 0
        week_exact = 0
        week_correct = 0
        
        # Display each match
        for idx, match in enumerate(matches):
            mid = match.get('id', '')
            home = match.get('home', match.get('home_team', ''))
            away = match.get('away', match.get('away_team', ''))
            is_gotw = match.get('gotw', False)
            match_date = match.get('date', '')
            match_time = match.get('time', '')
            
            # Get result - try both week-based list format and match_id format
            result = None
            week_results = results_data.get(str(selected_week), [])
            if isinstance(week_results, list) and idx < len(week_results):
                result = week_results[idx]
            elif mid in results_data:
                result = results_data[mid]
            
            # Get user prediction by index
            user_pred = user_preds.get(idx, {})
            
            # Card class
            card_class = "result-card gotw" if is_gotw else "result-card"
            gotw_badge = "⭐ GAME OF THE WEEK" if is_gotw else ""
            
            if result:
                home_score = result.get('home_score', result.get('home', 0))
                away_score = result.get('away_score', result.get('away', 0))
                
                # Calculate points for this match
                if user_pred:
                    # Get prediction scores - handle both formats
                    pred_home = user_pred.get('home_score', user_pred.get('home', -1))
                    pred_away = user_pred.get('away_score', user_pred.get('away', -1))
                    
                    points = dm.calculate_points(
                        pred_home,
                        pred_away,
                        home_score,
                        away_score,
                        is_gotw
                    )
                    week_points += points
                    
                    # Check prediction type
                    if (pred_home == home_score and pred_away == away_score):
                        pred_class = "prediction-exact"
                        pred_label = f"🎯 EXACT! +{points} pts"
                        week_exact += 1
                    elif points > 0:
                        pred_class = "prediction-correct"
                        pred_label = f"✅ Correct result +{points} pts"
                        week_correct += 1
                    else:
                        pred_class = "prediction-wrong"
                        pred_label = "❌ Wrong"
                else:
                    points = 0
                    pred_class = "prediction-wrong"
                    pred_label = "No prediction"
                    pred_home = None
                    pred_away = None
                
                # Display match result
                st.markdown(f"""
                <div class="{card_class}">
                    <div style="text-align: center; margin-bottom: 0.5rem;">
                        <span style="color: #ff9800; font-weight: bold;">{gotw_badge}</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div style="flex: 1; text-align: right;">
                            <span class="team-name">{home}</span>
                        </div>
                        <div style="flex: 1; text-align: center;">
                            <span class="score-big">{home_score} - {away_score}</span>
                        </div>
                        <div style="flex: 1; text-align: left;">
                            <span class="team-name">{away}</span>
                        </div>
                    </div>
                    <div style="text-align: center; margin-top: 0.5rem; color: #6c757d; font-size: 0.85rem;">
                        {match_date} {match_time}
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Show user's prediction if logged in
                if user_id:
                    if user_pred and pred_home is not None:
                        col1, col2, col3 = st.columns([1, 2, 1])
                        with col2:
                            st.markdown(f"""
                            <div class="{pred_class}">
                                <strong>Your prediction:</strong> {pred_home} - {pred_away}<br>
                                {pred_label}
                            </div>
                            """, unsafe_allow_html=True)
                    else:
                        col1, col2, col3 = st.columns([1, 2, 1])
                        with col2:
                            st.markdown("""
                            <div class="prediction-wrong">
                                <em>No prediction submitted</em>
                            </div>
                            """, unsafe_allow_html=True)
                
                st.markdown("<br>", unsafe_allow_html=True)
            
            else:
                # No result yet
                st.markdown(f"""
                <div class="{card_class}">
                    <div style="text-align: center; margin-bottom: 0.5rem;">
                        <span style="color: #ff9800; font-weight: bold;">{gotw_badge}</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div style="flex: 1; text-align: right;">
                            <span class="team-name">{home}</span>
                        </div>
                        <div style="flex: 1; text-align: center;">
                            <span class="no-result">Result pending...</span>
                        </div>
                        <div style="flex: 1; text-align: left;">
                            <span class="team-name">{away}</span>
                        </div>
                    </div>
                    <div style="text-align: center; margin-top: 0.5rem; color: #6c757d; font-size: 0.85rem;">
                        {match_date} {match_time}
                    </div>
                </div>
                """, unsafe_allow_html=True)
                st.markdown("<br>", unsafe_allow_html=True)
        
        # Week summary for user
        if user_id:
            st.markdown("---")
            st.markdown(f"### 📈 Your Week {selected_week} Summary")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Points", week_points)
            
            with col2:
                st.metric("🎯 Exact Scores", week_exact)
            
            with col3:
                st.metric("✅ Correct Results", week_correct)
            
            with col4:
                matches_with_results = sum(1 for m in matches if m.get('id') in results_data)
                st.metric("Matches Completed", f"{matches_with_results}/{len(matches)}")

# ============================================================================
# TAB 2: MY PERFORMANCE
# ============================================================================
with tab2:
    if not user_id:
        st.info("Select a participant from the sidebar to view performance")
    else:
        participant = dm.get_participant(user_id)
        if participant:
            st.markdown(f"### 📊 Performance for {participant.get('display_name') or participant.get('name', 'Unknown')}")
        
        # Load predictions - YOUR FORMAT: {"11": {"Y8PX0JE4": [{home, away}, ...]}}
        all_predictions = dm.load_predictions()
        
        # Check if user has any predictions
        has_predictions = False
        for week_key, week_data in all_predictions.items():
            if week_key.isdigit() and isinstance(week_data, dict):
                if user_id in week_data and week_data[user_id]:
                    has_predictions = True
                    break
        
        if not has_predictions:
            st.warning("No predictions found for this participant")
        else:
            # Calculate performance across all weeks
            performance_data = []
            total_points = 0
            total_exact = 0
            total_correct = 0
            total_wrong = 0
            
            for week in weeks_with_results:
                matches = dm.get_matches_by_week(week)
                week_pts = 0
                week_exact = 0
                week_correct = 0
                week_wrong = 0
                
                # Get user predictions for this week
                week_predictions = all_predictions.get(str(week), {})
                user_pred_list = week_predictions.get(user_id, [])
                
                for idx, match in enumerate(matches):
                    is_gotw = match.get('gotw', False)
                    
                    # Get result - try both formats
                    result = None
                    week_results = results_data.get(str(week), [])
                    if isinstance(week_results, list) and idx < len(week_results):
                        result = week_results[idx]
                    else:
                        mid = match.get('id', '')
                        result = results_data.get(mid, {})
                    
                    # Get prediction by index
                    pred = user_pred_list[idx] if idx < len(user_pred_list) else None
                    
                    if result and pred:
                        pred_home = pred.get('home_score', pred.get('home', -1))
                        pred_away = pred.get('away_score', pred.get('away', -1))
                        res_home = result.get('home_score', result.get('home', -2))
                        res_away = result.get('away_score', result.get('away', -2))
                        
                        pts = dm.calculate_points(
                            pred_home,
                            pred_away,
                            res_home,
                            res_away,
                            is_gotw
                        )
                        week_pts += pts
                        
                        if pred_home == res_home and pred_away == res_away:
                            week_exact += 1
                        elif pts > 0:
                            week_correct += 1
                        else:
                            week_wrong += 1
                    elif result and not pred:
                        week_wrong += 1
                
                performance_data.append({
                    'Week': f"Week {week}",
                    'Points': week_pts,
                    'Exact': week_exact,
                    'Correct': week_correct,
                    'Wrong': week_wrong
                })
                
                total_points += week_pts
                total_exact += week_exact
                total_correct += week_correct
                total_wrong += week_wrong
            
            # Summary metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("🏆 Total Points", total_points)
            
            with col2:
                st.metric("🎯 Exact Scores", total_exact)
            
            with col3:
                st.metric("✅ Correct Results", total_correct)
            
            with col4:
                total_preds = total_exact + total_correct + total_wrong
                accuracy = ((total_exact + total_correct) / total_preds * 100) if total_preds > 0 else 0
                st.metric("📈 Accuracy", f"{accuracy:.1f}%")
            
            st.markdown("---")
            
            # Week by week table
            if performance_data:
                st.markdown("### 📅 Week by Week")
                perf_df = pd.DataFrame(performance_data)
                st.dataframe(perf_df, use_container_width=True, hide_index=True)
                
                # Points trend chart
                st.markdown("### 📈 Points Trend")
                chart_data = pd.DataFrame({
                    'Week': [d['Week'] for d in performance_data],
                    'Points': [d['Points'] for d in performance_data]
                })
                st.line_chart(chart_data.set_index('Week'))

# ============================================================================
# TAB 3: SUMMARY
# ============================================================================
with tab3:
    st.markdown("### 🏆 Results Summary")
    
    if not weeks_with_results:
        st.info("No results entered yet")
    else:
        # Overall stats
        total_matches = 0
        total_completed = 0
        
        for week in weeks:
            matches = dm.get_matches_by_week(week)
            total_matches += len(matches)
            for m in matches:
                if m.get('id') in results_data:
                    total_completed += 1
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Matches", total_matches)
        
        with col2:
            st.metric("Results Entered", total_completed)
        
        with col3:
            st.metric("Weeks Completed", len(weeks_with_results))
        
        st.markdown("---")
        
        # Results by week
        st.markdown("### 📅 All Results")
        
        all_results_data = []
        for week in weeks_with_results:
            matches = dm.get_matches_by_week(week)
            for m in matches:
                mid = m.get('id', '')
                result = results_data.get(mid, {})
                
                if result:
                    home = m.get('home', m.get('home_team', ''))
                    away = m.get('away', m.get('away_team', ''))
                    is_gotw = m.get('gotw', False)
                    
                    all_results_data.append({
                        'Week': week,
                        'Date': m.get('date', '-'),
                        'Home': home,
                        'Score': f"{result.get('home_score', 0)}-{result.get('away_score', 0)}",
                        'Away': away,
                        'GOTW': '⭐' if is_gotw else ''
                    })
        
        if all_results_data:
            results_df = pd.DataFrame(all_results_data)
            st.dataframe(results_df, use_container_width=True, hide_index=True)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #6c757d; font-size: 0.9rem;">
    <p><strong>Nikkang KK EPL Prediction League</strong> | Season 2025-26</p>
</div>
""", unsafe_allow_html=True)

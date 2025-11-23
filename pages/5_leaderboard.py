"""
Leaderboard Page - Competition Standings with Weekly Highlights
"""

import streamlit as st
import pandas as pd
from utils.config import setup_page, apply_custom_css
from utils.data_manager import DataManager

setup_page()
apply_custom_css()

dm = DataManager()

st.title("🏆 Leaderboard")

st.markdown("---")

# Refresh button
col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    if st.button("🔄 Refresh Leaderboard", use_container_width=True):
        st.rerun()

st.markdown("---")

# Calculate leaderboard
leaderboard = dm.calculate_leaderboard()

if not leaderboard:
    st.info("No scores available yet. Predictions and results need to be submitted first.")
    st.stop()

# Display top 3 Overall
st.subheader("🥇 Season Leaders - Top 3")

cols = st.columns(3)

medals = ["🥇", "🥈", "🥉"]

for idx, col in enumerate(cols):
    if idx < len(leaderboard):
        entry = leaderboard[idx]
        with col:
            st.markdown(f"""
            <div class="leaderboard-item top3">
                <div style="text-align: center;">
                    <div style="font-size: 48px;">{medals[idx]}</div>
                    <h3>{entry['name']}</h3>
                    <p style="font-size: 32px; font-weight: bold; color: #c41e3a;">{entry['total_points']}</p>
                    <p style="margin: 0;">points</p>
                    <hr style="margin: 10px 0;">
                    <p style="margin: 5px 0; font-size: 14px;">⚡ {entry['exact_scores']} exact scores</p>
                    <p style="margin: 5px 0; font-size: 14px;">✓ {entry['correct_results']} correct results</p>
                    <p style="margin: 5px 0; font-size: 14px;">📅 {entry['weeks_played']} weeks played</p>
                    <p style="margin: 5px 0; font-size: 14px;">⚽ {entry['team']}</p>
                </div>
            </div>
            """, unsafe_allow_html=True)

st.markdown("---")

# Weekly Performance Highlights
st.subheader("📅 Weekly Highlights")

current_week = dm.get_current_week()
last_completed_week = current_week - 1 if current_week > 1 else 1

# Check if last week has results
week_results = dm.get_week_results(last_completed_week)

if week_results and len(week_results) > 0:
    # Calculate weekly performance
    weekly_data = []
    predictions = dm.load_predictions()
    matches = dm.load_matches()
    
    week_str = str(last_completed_week)
    week_predictions = predictions.get(week_str, {})
    week_matches = matches.get(week_str, [])
    
    is_week38 = (last_completed_week == 38)
    
    for pid, pred_list in week_predictions.items():
        participant = dm.get_participant(pid)
        if not participant:
            continue
            
        weekly_points = 0
        weekly_exact = 0
        weekly_correct = 0
        
        for idx, pred in enumerate(pred_list):
            if idx >= len(week_results) or idx >= len(week_matches):
                continue
            
            result = week_results[idx]
            match = week_matches[idx]
            is_gotw = match.get('gotw', False)
            
            points = dm.calculate_points(pred, result, is_gotw, is_week38)
            weekly_points += points
            
            if pred.get('home') == result.get('home') and pred.get('away') == result.get('away'):
                weekly_exact += 1
            elif points > 0:
                weekly_correct += 1
        
        weekly_data.append({
            'id': pid,
            'name': participant['name'],
            'team': participant.get('team', ''),
            'points': weekly_points,
            'exact_scores': weekly_exact,
            'correct_results': weekly_correct
        })
    
    # Sort by points
    weekly_data.sort(key=lambda x: (x['points'], x['exact_scores']), reverse=True)
    
    if weekly_data:
        # Weekly Top 3 and Bottom 3
        col_left, col_right = st.columns(2)
        
        with col_left:
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #fff8e1 0%, #fffbf5 100%); 
                        padding: 20px; border-radius: 10px; border: 2px solid #ffd700;">
                <h3 style="text-align: center; color: #c41e3a;">🔥 Week {last_completed_week} Top 3</h3>
            </div>
            """, unsafe_allow_html=True)
            
            for idx in range(min(3, len(weekly_data))):
                entry = weekly_data[idx]
                medal = ["🥇", "🥈", "🥉"][idx]
                st.markdown(f"""
                <div style="background: #f8f9fa; padding: 15px; margin: 10px 0; 
                            border-radius: 8px; border-left: 4px solid #ffd700;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <span style="font-size: 24px;">{medal}</span>
                            <strong style="font-size: 18px;"> {entry['name']}</strong>
                            <div style="font-size: 12px; color: #666;">
                                ⚡ {entry['exact_scores']} KK | ✓ {entry['correct_results']} results
                            </div>
                        </div>
                        <div style="text-align: right;">
                            <div style="font-size: 28px; font-weight: bold; color: #c41e3a;">
                                {entry['points']}
                            </div>
                            <div style="font-size: 12px;">points</div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        with col_right:
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #ffe0e0 0%, #fff5f5 100%); 
                        padding: 20px; border-radius: 10px; border: 2px solid #ff9999;">
                <h3 style="text-align: center; color: #c41e3a;">⚠️ Week {last_completed_week} Bottom 3</h3>
            </div>
            """, unsafe_allow_html=True)
            
            # Bottom 3
            bottom_3 = weekly_data[-3:] if len(weekly_data) >= 3 else weekly_data
            bottom_3.reverse()  # Show worst first
            
            for idx, entry in enumerate(bottom_3):
                st.markdown(f"""
                <div style="background: #f8f9fa; padding: 15px; margin: 10px 0; 
                            border-radius: 8px; border-left: 4px solid #ff9999;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <strong style="font-size: 18px;">{entry['name']}</strong>
                            <div style="font-size: 12px; color: #666;">
                                ⚡ {entry['exact_scores']} KK | ✓ {entry['correct_results']} results
                            </div>
                        </div>
                        <div style="text-align: right;">
                            <div style="font-size: 28px; font-weight: bold; color: #666;">
                                {entry['points']}
                            </div>
                            <div style="font-size: 12px;">points</div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
else:
    st.info(f"Week {last_completed_week} results not yet available. Check back after matches complete!")

st.markdown("---")

# Season to Date KK Champions
st.subheader("⚡ Season KK Champions (Exact Scores)")

st.markdown("""
<div style="background: linear-gradient(135deg, #e3f2fd 0%, #f5f5f5 100%); 
            padding: 20px; border-radius: 10px; border: 2px solid #2196F3; margin-bottom: 20px;">
    <h4 style="text-align: center; color: #c41e3a; margin: 0;">
        🎯 Most Exact Score Predictions (KK) - Season 2025/26
    </h4>
    <p style="text-align: center; color: #666; margin: 5px 0; font-size: 14px;">
        The ultimate prediction masters!
    </p>
</div>
""", unsafe_allow_html=True)

# Sort by exact scores
kk_leaders = sorted(leaderboard, key=lambda x: (x['exact_scores'], x['total_points']), reverse=True)

# Top 3 KK Champions
cols = st.columns(3)

for idx, col in enumerate(cols):
    if idx < len(kk_leaders):
        entry = kk_leaders[idx]
        medal = ["🥇", "🥈", "🥉"][idx]
        with col:
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #e3f2fd 0%, #ffffff 100%); 
                        padding: 20px; border-radius: 10px; border: 2px solid #2196F3; text-align: center;">
                <div style="font-size: 36px; margin-bottom: 10px;">{medal}</div>
                <h3 style="margin: 10px 0;">{entry['name']}</h3>
                <div style="font-size: 48px; font-weight: bold; color: #2196F3; margin: 15px 0;">
                    {entry['exact_scores']}
                </div>
                <div style="font-size: 14px; color: #666; margin-bottom: 15px;">Exact Scores (KK)</div>
                <hr style="margin: 15px 0; border-color: #2196F3;">
                <div style="font-size: 16px; color: #c41e3a; font-weight: bold; margin: 10px 0;">
                    {entry['total_points']} pts
                </div>
                <div style="font-size: 12px; color: #666;">
                    ✓ {entry['correct_results']} correct results<br>
                    📅 {entry['weeks_played']} weeks<br>
                    ⚽ {entry['team']}
                </div>
            </div>
            """, unsafe_allow_html=True)

st.markdown("---")

# Full leaderboard table
st.subheader("📊 Full Standings")

# Create DataFrame
df = pd.DataFrame(leaderboard)

# Select and rename columns
df_display = df[['rank', 'name', 'total_points', 'exact_scores', 'correct_results', 'weeks_played', 'team']].copy()
df_display.columns = ['Rank', 'Name', 'Total Points', 'Exact Scores (KK)', 'Correct Results', 'Weeks Played', 'Team']

# Display table with styling
st.dataframe(
    df_display,
    use_container_width=True,
    hide_index=True,
    column_config={
        "Rank": st.column_config.NumberColumn(
            "Rank",
            help="Current position",
            format="%d"
        ),
        "Total Points": st.column_config.NumberColumn(
            "Total Points",
            help="Total points accumulated",
            format="%d"
        ),
        "Exact Scores (KK)": st.column_config.NumberColumn(
            "Exact Scores (KK)",
            help="Number of exact score predictions",
            format="%d"
        ),
        "Correct Results": st.column_config.NumberColumn(
            "Correct Results",
            help="Number of correct result predictions",
            format="%d"
        ),
        "Weeks Played": st.column_config.NumberColumn(
            "Weeks Played",
            help="Number of weeks participated",
            format="%d"
        ),
    }
)

st.markdown("---")

# Statistics
st.subheader("📈 Competition Statistics")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Participants", len(leaderboard))

with col2:
    total_points = sum(entry['total_points'] for entry in leaderboard)
    st.metric("Total Points", total_points)

with col3:
    total_exact = sum(entry['exact_scores'] for entry in leaderboard)
    st.metric("Total Exact Scores", total_exact)

with col4:
    avg_points = total_points / len(leaderboard) if leaderboard else 0
    st.metric("Avg Points", f"{avg_points:.1f}")

st.markdown("---")

# Individual participant lookup
st.subheader("🔍 Look Up Your Stats")

participants = dm.load_participants()
participant_names = {p['name']: pid for pid, p in participants.items()}

selected_name = st.selectbox("Select Participant", [""] + list(participant_names.keys()))

if selected_name:
    participant_id = participant_names[selected_name]
    stats = dm.get_participant_stats(participant_id)
    
    if stats:
        st.markdown(f"""
        <div class="info-box info">
            <h3>📊 Stats for {stats['name']}</h3>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Rank", f"#{stats['rank']}")
        
        with col2:
            st.metric("Total Points", stats['total_points'])
        
        with col3:
            st.metric("Exact Scores", stats['exact_scores'])
        
        with col4:
            st.metric("Correct Results", stats['correct_results'])
        
        st.markdown("---")
        
        # Weekly breakdown
        st.subheader(f"📅 Weekly Performance")
        
        predictions = dm.load_predictions()
        results = dm.load_results()
        matches = dm.load_matches()
        
        weekly_data = []
        
        for week_str, week_predictions in predictions.items():
            if participant_id in week_predictions:
                week = int(week_str)
                week_results = results.get(week_str, [])
                week_matches = matches.get(week_str, [])
                
                if not week_results or not week_matches:
                    continue
                
                week_points = 0
                week_exact = 0
                week_correct = 0
                
                pred_list = week_predictions[participant_id]
                
                for idx, pred in enumerate(pred_list):
                    if idx >= len(week_results) or idx >= len(week_matches):
                        continue
                    
                    result = week_results[idx]
                    match = week_matches[idx]
                    is_gotw = match.get('gotw', False)
                    is_week38 = (week == 38)
                    
                    points = dm.calculate_points(pred, result, is_gotw, is_week38)
                    week_points += points
                    
                    if pred['home'] == result['home'] and pred['away'] == result['away']:
                        week_exact += 1
                    elif points > 0:
                        week_correct += 1
                
                weekly_data.append({
                    'Week': week,
                    'Points': week_points,
                    'Exact Scores': week_exact,
                    'Correct Results': week_correct
                })
        
        if weekly_data:
            df_weekly = pd.DataFrame(weekly_data)
            df_weekly = df_weekly.sort_values('Week')
            
            st.dataframe(
                df_weekly,
                use_container_width=True,
                hide_index=True
            )
            
            # Chart
            st.line_chart(df_weekly.set_index('Week')['Points'])
        else:
            st.info("No predictions submitted yet.")

st.markdown("---")

# Points breakdown
with st.expander("📖 Points System Reminder"):
    st.markdown("""
    ### Standard Matches:
    - **Exact Score (KK):** 6 points
    - **Correct Result:** 3 points
    
    ### GOTW (Game of the Week):
    - **Exact Score (KK):** 10 points
    - **Correct Result:** 5 points
    
    ### Week 38 (Finale):
    - **All matches:** Double points!
    - **Exact Score:** 10 points
    - **Correct Result:** 5 points
    """)

st.markdown("---")
st.caption("Nikkang KK - EPL Prediction Competition 2025/26")

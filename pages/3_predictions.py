"""
Predictions Page - Weekly Match Predictions
"""

import streamlit as st
from utils.config import setup_page, apply_custom_css
from utils.data_manager import DataManager

setup_page()
apply_custom_css()

dm = DataManager()

st.title("⚽ Weekly Predictions")

# Check if accessed via personal link
active_participant = st.session_state.get('active_participant')

if active_participant:
    st.markdown(f"""
    <div class="info-box success">
        <h3>👤 Welcome back, {active_participant['name']}!</h3>
        <p>📧 {active_participant['email']}</p>
        <p>⚽ Favorite Team: {active_participant.get('team', 'Not selected')}</p>
    </div>
    """, unsafe_allow_html=True)
    
    participant_id = active_participant['id']
    default_week = active_participant.get('selected_week', dm.get_current_week())
else:
    st.info("👉 Select your name below to start predicting")
    
    # Name selector
    participants = dm.load_participants()
    
    if not participants:
        st.warning("⚠️ No participants registered yet. Please register first!")
        if st.button("Go to Registration"):
            st.switch_page("pages/2_register.py")
        st.stop()
    
    participant_names = {p['name']: pid for pid, p in participants.items()}
    selected_name = st.selectbox("Your Name", [""] + list(participant_names.keys()))
    
    if not selected_name:
        st.warning("Please select your name to continue")
        st.stop()
    
    participant_id = participant_names[selected_name]
    default_week = dm.get_current_week()

st.markdown("---")

# Week selector
col1, col2 = st.columns([2, 1])

with col1:
    week = st.selectbox(
        "Select Week",
        range(1, 39),
        index=default_week - 1,
        format_func=lambda x: f"Week {x}" + (" (FINALE - DOUBLE POINTS!)" if x == 38 else "")
    )

with col2:
    st.metric("Current Week", dm.get_current_week())

is_week38 = (week == 38)

if is_week38:
    st.warning("🎉 **WEEK 38 FINALE** - All matches worth double points!")

st.markdown("---")

# Load matches for selected week
matches = dm.get_week_matches(week)

if not matches:
    st.info(f"No matches scheduled for Week {week} yet. Check back later!")
    st.stop()

# Load existing predictions
existing_predictions = dm.get_participant_predictions(participant_id, week)

st.subheader(f"Match Predictions - Week {week}")

st.info("💡 **Tip:** GOTW (Game of the Week) matches are worth extra points!")

# Create form for predictions
with st.form("predictions_form"):
    predictions = []
    
    # Display matches in 2 columns
    cols = st.columns(2)
    
    for idx, match in enumerate(matches):
        with cols[idx % 2]:
            is_gotw = match.get('gotw', False)
            gotw_class = "gotw" if is_gotw else ""
            
            # Get existing prediction if available
            existing = existing_predictions[idx] if idx < len(existing_predictions) else {'home': 0, 'away': 0}
            
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
                st.caption("**Score**")
            
            with col_c:
                st.caption(f"**{match['away']}**")
            
            col_a, col_b, col_c = st.columns([2, 1, 2])
            
            with col_a:
                home_score = st.number_input(
                    f"Home {idx}",
                    min_value=0,
                    max_value=15,
                    value=int(existing.get('home', 0)),
                    key=f"home_{idx}",
                    label_visibility="collapsed"
                )
            
            with col_b:
                st.markdown("<div style='text-align: center; padding-top: 8px;'>-</div>", unsafe_allow_html=True)
            
            with col_c:
                away_score = st.number_input(
                    f"Away {idx}",
                    min_value=0,
                    max_value=15,
                    value=int(existing.get('away', 0)),
                    key=f"away_{idx}",
                    label_visibility="collapsed"
                )
            
            predictions.append({'home': home_score, 'away': away_score})
            
            st.markdown("<br>", unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Submit button
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        submitted = st.form_submit_button("💾 Save Predictions", use_container_width=True)
    
    if submitted:
        # Validate all predictions are filled
        all_filled = all(p['home'] >= 0 and p['away'] >= 0 for p in predictions)
        
        if not all_filled:
            st.error("❌ Please fill in all match predictions!")
        else:
            # Save predictions
            dm.save_participant_predictions(participant_id, week, predictions)
            st.success(f"✅ Predictions saved successfully for Week {week}!")
            st.balloons()
            
            # Show summary
            st.markdown("---")
            st.subheader("📋 Your Predictions Summary")
            
            for idx, (match, pred) in enumerate(zip(matches, predictions)):
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.text(f"{idx + 1}. {match['home']} vs {match['away']}")
                with col2:
                    st.markdown(f"<div class='score-display'>{pred['home']} - {pred['away']}</div>", 
                              unsafe_allow_html=True)

# Show my link button
st.markdown("---")

col1, col2 = st.columns(2)

with col1:
    if st.button("📋 Copy My Prediction Link", use_container_width=True):
        from utils.whatsapp import generate_participant_link
        link = generate_participant_link(participant_id, week, base_url="http://localhost:8501")
        st.code(link, language=None)
        st.caption("Share this link to access your predictions directly!")

with col2:
    if st.button("🏆 View Leaderboard", use_container_width=True):
        st.switch_page("pages/5_leaderboard.py")

# Show deadline info
st.markdown("---")
st.warning("""
⏰ **Important Deadline Information:**
- Submit predictions **before** the first match of the week kicks off
- You can update predictions until the deadline
- Late submissions will NOT be accepted
""")

st.markdown("---")
st.caption("Nikkang KK - EPL Prediction Competition 2025/26")

"""
Predictions Page - Weekly Match Predictions

FIXES APPLIED:
1. Match sequence now consistent on mobile and web (single column layout)
2. Removed 2-column layout that caused order mismatch on mobile
3. Added responsive design that works on all devices
4. Added nickname-based URL parameter (?player=nickname) for direct access
"""

import streamlit as st
from utils.config import setup_page, apply_custom_css
from utils.data_manager import DataManager

setup_page()
apply_custom_css()

dm = DataManager()

st.title("⚽ Weekly Predictions")

# =============================================================================
# CHECK FOR PLAYER NICKNAME IN URL QUERY PARAMETER
# =============================================================================
# Get player nickname from URL (e.g., ?player=john_doe)
query_params = st.query_params
player_nickname = query_params.get("player", None)

# Check if accessed via personal link
active_participant = st.session_state.get('active_participant')

# If player nickname provided in URL, try to find and set participant
if player_nickname and not active_participant:
    participants = dm.load_participants()
    
    if participants:
        # Convert URL nickname to match participant's display_name or name
        # URL format: lowercase with underscores (e.g., "johnny" or "john_doe")
        for pid, p in participants.items():
            # Get the nickname (display_name) or fall back to name
            p_nickname = p.get('display_name') or p.get('nickname') or p.get('name', '')
            # Make URL-friendly version for comparison
            url_version = p_nickname.lower().replace(' ', '_').replace("'", "").replace("-", "_")
            
            if url_version == player_nickname.lower():
                # Found the participant! Set as active
                st.session_state['active_participant'] = {
                    'id': pid,
                    'name': p.get('name', ''),
                    'display_name': p_nickname,
                    'email': p.get('email', ''),
                    'team': p.get('team', 'Not selected'),
                    'selected_week': dm.get_current_week()
                }
                active_participant = st.session_state['active_participant']
                break

if active_participant:
    display_name = active_participant.get('display_name') or active_participant.get('name', 'Player')
    st.markdown(f"""
    <div class="info-box success">
        <h3>👤 Welcome back, {display_name}!</h3>
        <p>📧 {active_participant.get('email', '')}</p>
        <p>⚽ Favorite Team: {active_participant.get('team', 'Not selected')}</p>
    </div>
    """, unsafe_allow_html=True)
    
    participant_id = active_participant['id']
    default_week = active_participant.get('selected_week', dm.get_current_week())
else:
    st.info("👉 Login below to start predicting")
    
    # ==========================================================================
    # LOGIN WITH NICKNAME + LAST 4 DIGITS OF PHONE
    # ==========================================================================
    participants = dm.load_participants()
    
    if not participants:
        st.warning("⚠️ No participants registered yet. Please register first!")
        if st.button("Go to Registration"):
            st.switch_page("pages/2_Register.py")
        st.stop()
    
    # Build nickname -> participant data mapping
    participant_data = {}
    for pid, p in participants.items():
        nickname = p.get('display_name') or p.get('nickname') or p.get('name', 'Unknown')
        participant_data[nickname.lower()] = {
            'id': pid,
            'nickname': nickname,
            'phone': p.get('phone', ''),
            'name': p.get('name', ''),
            'email': p.get('email', ''),
            'team': p.get('team', 'Not selected')
        }
    
    # Login form
    st.markdown("### 🔐 Login")
    
    col1, col2 = st.columns(2)
    
    with col1:
        input_nickname = st.text_input(
            "Your Nickname",
            placeholder="Enter your nickname",
            help="The nickname you registered with (not case-sensitive)"
        )
    
    with col2:
        input_phone_last4 = st.text_input(
            "Last 4 Digits of Phone",
            placeholder="e.g. 1234",
            max_chars=4,
            help="Last 4 digits of your registered phone number"
        )
    
    # Login button
    if st.button("🔓 Login", use_container_width=True, type="primary"):
        if not input_nickname or not input_nickname.strip():
            st.error("❌ Please enter your nickname")
            st.stop()
        
        if not input_phone_last4 or len(input_phone_last4.strip()) != 4:
            st.error("❌ Please enter exactly 4 digits of your phone number")
            st.stop()
        
        # Clean inputs - case-insensitive nickname, strip whitespace
        nickname_lower = input_nickname.strip().lower()
        phone_input = input_phone_last4.strip()
        
        # Find participant by nickname (case-insensitive)
        if nickname_lower not in participant_data:
            # Show helpful message with similar nicknames
            similar = [v['nickname'] for k, v in participant_data.items() if nickname_lower in k or k in nickname_lower]
            if similar:
                st.error(f"❌ Nickname not found. Did you mean: **{', '.join(similar)}**?")
            else:
                st.error("❌ Nickname not found. Please check your nickname or register first.")
            st.stop()
        
        p_data = participant_data[nickname_lower]
        
        # Get last 4 digits of registered phone (clean all non-digits)
        registered_phone = ''.join(filter(str.isdigit, p_data['phone']))
        registered_last4 = registered_phone[-4:] if len(registered_phone) >= 4 else registered_phone
        
        # Verify phone last 4 digits
        if phone_input != registered_last4:
            st.error("❌ Phone number doesn't match. Please try again.")
            st.stop()
        
        # Login successful! Store in session
        st.session_state['logged_in_participant'] = {
            'id': p_data['id'],
            'nickname': p_data['nickname'],
            'name': p_data['name'],
            'email': p_data['email'],
            'team': p_data['team']
        }
        st.success(f"✅ Welcome, {p_data['nickname']}!")
        st.rerun()
    
    # Check if already logged in via session
    if 'logged_in_participant' not in st.session_state:
        st.markdown("---")
        st.caption("💡 Use your registered nickname and phone number to login")
        st.stop()
    
    # Get logged in participant
    logged_in = st.session_state['logged_in_participant']
    participant_id = logged_in['id']
    default_week = dm.get_current_week()
    
    # Show logged in user info
    st.success(f"👤 Logged in as: **{logged_in['nickname']}**")
    
    # Logout button in sidebar
    with st.sidebar:
        if st.button("🚪 Logout", use_container_width=True):
            del st.session_state['logged_in_participant']
            st.rerun()

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

# Load existing predictions FOR THIS WEEK ONLY
existing_predictions = dm.get_participant_predictions(participant_id, week)

# Check if predictions actually exist for THIS week (not carried from previous)
has_predictions_for_week = existing_predictions and len(existing_predictions) > 0 and any(
    p.get('home', 0) != 0 or p.get('away', 0) != 0 for p in existing_predictions
)

st.subheader(f"Match Predictions - Week {week}")

if has_predictions_for_week:
    st.success(f"✅ You have saved predictions for Week {week}")
else:
    st.info(f"📝 Enter your predictions for Week {week} below")

st.info("💡 **Tip:** GOTW (Game of the Week) matches are worth extra points!")

# Create form for predictions - unique key per week to reset form
with st.form(f"predictions_form_week_{week}"):
    predictions = []
    
    # ==========================================================================
    # FIX: Use single column layout for consistent sequence on mobile and web
    # Previously used st.columns(2) which caused order mismatch on mobile
    # ==========================================================================
    
    for idx, match in enumerate(matches):
        is_gotw = match.get('gotw', False)
        
        # Only use existing prediction if it exists for THIS week
        if has_predictions_for_week and idx < len(existing_predictions):
            existing = existing_predictions[idx]
            default_home = int(existing.get('home', 0))
            default_away = int(existing.get('away', 0))
        else:
            # Start with blank form (0-0) for new week
            default_home = 0
            default_away = 0
        
        # Match card with GOTW styling
        if is_gotw:
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #ff9800 0%, #f57c00 100%); 
                        color: white; padding: 12px; border-radius: 8px; margin-bottom: 8px;
                        box-shadow: 0 2px 8px rgba(255, 152, 0, 0.3);">
                <strong>Match {idx + 1}:</strong> {match['home']} vs {match['away']} 
                ⭐ <strong>GAME OF THE WEEK</strong>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div style="background: #f8f9fa; padding: 12px; border-radius: 8px; 
                        margin-bottom: 8px; border-left: 4px solid #667eea;">
                <strong>Match {idx + 1}:</strong> {match['home']} vs {match['away']}
            </div>
            """, unsafe_allow_html=True)
        
        # Score input row - 3 columns for Home / - / Away
        col_home, col_dash, col_away = st.columns([2, 1, 2])
        
        with col_home:
            st.caption(f"**{match['home']}**")
            home_score = st.number_input(
                f"Home {idx}",
                min_value=0,
                max_value=15,
                value=default_home,
                key=f"home_w{week}_{idx}",
                label_visibility="collapsed"
            )
        
        with col_dash:
            st.markdown("<div style='text-align: center; padding-top: 28px; font-size: 1.5rem; font-weight: bold;'>-</div>", unsafe_allow_html=True)
        
        with col_away:
            st.caption(f"**{match['away']}**")
            away_score = st.number_input(
                f"Away {idx}",
                min_value=0,
                max_value=15,
                value=default_away,
                key=f"away_w{week}_{idx}",
                label_visibility="collapsed"
            )
        
        predictions.append({'home': home_score, 'away': away_score})
        
        # Add spacing between matches
        st.markdown("<div style='margin-bottom: 20px;'></div>", unsafe_allow_html=True)
    
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
                is_gotw = match.get('gotw', False)
                gotw_badge = " ⭐" if is_gotw else ""
                
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.text(f"{idx + 1}. {match['home']} vs {match['away']}{gotw_badge}")
                with col2:
                    st.markdown(f"**{pred['home']} - {pred['away']}**")

# Show my link button
st.markdown("---")

col1, col2 = st.columns(2)

with col1:
    if st.button("📋 Copy My Prediction Link", use_container_width=True):
        # Get participant's nickname for the link
        if active_participant:
            nickname = active_participant.get('display_name') or active_participant.get('name', '')
        elif 'logged_in_participant' in st.session_state:
            # Use nickname from login
            nickname = st.session_state['logged_in_participant'].get('nickname', '')
        else:
            # Get nickname from participants dict
            participants = dm.load_participants()
            p_data = participants.get(participant_id, {})
            nickname = p_data.get('display_name') or p_data.get('nickname') or p_data.get('name', '')
        
        # Create URL-friendly nickname
        url_nickname = nickname.lower().replace(' ', '_').replace("'", "").replace("-", "_")
        # Use correct Streamlit Cloud page name (matches filename without .py)
        link = f"https://nikkang-epl.streamlit.app/3_Predictions?player={url_nickname}"
        
        st.code(link, language=None)
        st.caption(f"Share this link to access predictions as **{nickname}**!")

with col2:
    if st.button("🏆 View Leaderboard", use_container_width=True):
        st.switch_page("pages/5_Leaderboard.py")

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

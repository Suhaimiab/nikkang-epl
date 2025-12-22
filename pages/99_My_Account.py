"""
My Account Page
Nikkang KK EPL Prediction Competition

Participant account management:
- View profile information
- Change password
- View prediction statistics
"""

import streamlit as st
from pathlib import Path
import sys

# Add utils to path
sys.path.append(str(Path(__file__).parent.parent))

from utils.participant_auth import (
    require_participant_auth,
    participant_info_sidebar,
    get_current_participant_id,
    get_current_participant_name,
    change_participant_password,
    load_participants
)
from utils.data_manager import DataManager

# Page config
st.set_page_config(
    page_title="My Account - Nikkang KK",
    page_icon="👤",
    layout="wide"
)

# REQUIRE AUTHENTICATION
require_participant_auth()

# Show participant info in sidebar
participant_info_sidebar()

# Logo
if Path("nikkang_logo.png").exists():
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.image("nikkang_logo.png", width=200)

# Header
st.title("👤 My Account")
st.markdown("---")

# Get current participant
participant_id = get_current_participant_id()
participants = load_participants()
participant_data = participants.get(participant_id, {})

# Tabs
tab1, tab2, tab3 = st.tabs(["📋 Profile", "🔑 Change Password", "📊 My Stats"])

# =============================================================================
# TAB 1: PROFILE
# =============================================================================
with tab1:
    st.markdown("### 📋 Profile Information")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Personal Details")
        st.text_input("Full Name", value=participant_data.get('name', ''), disabled=True)
        st.text_input("Display Name (Nickname)", value=participant_data.get('display_name', ''), disabled=True)
        st.text_input("Email", value=participant_data.get('email', 'Not provided'), disabled=True)
        st.text_input("Phone", value=participant_data.get('phone', ''), disabled=True)
    
    with col2:
        st.markdown("#### Competition Details")
        st.text_input("User ID", value=participant_data.get('id', ''), disabled=True)
        st.text_input("Favorite Team", value=participant_data.get('team', 'Not selected'), disabled=True)
        st.text_input("Registration Date", value=participant_data.get('registration_date', 'N/A'), disabled=True)
        st.text_input("Status", value=participant_data.get('status', 'active').upper(), disabled=True)
    
    st.markdown("---")
    st.info("""
    **Need to update your details?**
    
    Contact the competition admin to update:
    - Name
    - Email
    - Phone number
    - Favorite team
    
    Your User ID and registration date cannot be changed.
    """)

# =============================================================================
# TAB 2: CHANGE PASSWORD
# =============================================================================
with tab2:
    st.markdown("### 🔑 Change Password")
    
    st.info("Create a new password for your account. You'll use this to login in the future.")
    
    with st.form("change_password_form"):
        current_password = st.text_input("Current Password", type="password")
        
        st.markdown("---")
        
        new_password = st.text_input("New Password", type="password", help="Minimum 6 characters")
        confirm_password = st.text_input("Confirm New Password", type="password")
        
        change = st.form_submit_button("🔄 Change Password", use_container_width=True, type="primary")
        
        if change:
            # Validation
            if not current_password:
                st.error("❌ Please enter your current password")
            elif not new_password:
                st.error("❌ Please enter a new password")
            elif len(new_password) < 6:
                st.error("❌ New password must be at least 6 characters long")
            elif new_password != confirm_password:
                st.error("❌ New passwords don't match")
            elif current_password == new_password:
                st.warning("⚠️ New password is the same as current password")
            else:
                # Attempt password change
                success, message = change_participant_password(current_password, new_password)
                
                if success:
                    st.success(f"✅ {message}")
                    st.balloons()
                else:
                    st.error(f"❌ {message}")
    
    st.markdown("---")
    
    st.markdown("#### 🔐 Password Tips")
    st.markdown("""
    **Create a strong password:**
    - At least 6 characters (longer is better)
    - Mix of letters and numbers
    - Easy for you to remember
    - Avoid common words or birthdays
    
    **Keep it secure:**
    - Don't share your password with anyone
    - Don't use the same password on multiple sites
    - Change it periodically
    """)

# =============================================================================
# TAB 3: STATISTICS
# =============================================================================
with tab3:
    st.markdown("### 📊 My Statistics")
    
    # Initialize data manager
    dm = DataManager()
    
    # Get predictions
    all_predictions = dm.load_predictions()
    my_predictions_count = 0
    weeks_predicted = []
    
    for week_str, week_data in all_predictions.items():
        if week_str.isdigit() and participant_id in week_data:
            my_predictions_count += len(week_data[participant_id])
            weeks_predicted.append(int(week_str))
    
    # Display stats
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Points", participant_data.get('total_points', 0))
    
    with col2:
        st.metric("Weeks Played", len(weeks_predicted))
    
    with col3:
        st.metric("Predictions Made", my_predictions_count)
    
    with col4:
        avg_pts = participant_data.get('total_points', 0) / len(weeks_predicted) if weeks_predicted else 0
        st.metric("Avg Points/Week", f"{avg_pts:.1f}")
    
    st.markdown("---")
    
    # Prediction history
    st.markdown("#### 📅 Prediction History")
    
    if weeks_predicted:
        weeks_predicted.sort()
        
        st.success(f"You have made predictions for **{len(weeks_predicted)} gameweeks**")
        
        # Show weeks
        st.markdown("**Weeks:** " + ", ".join(f"Week {w}" for w in weeks_predicted))
    else:
        st.info("You haven't made any predictions yet. Head to the **Make Predictions** page to get started!")
    
    st.markdown("---")
    
    # Competition progress
    st.markdown("#### 🏆 Competition Progress")
    
    # Get all participants for ranking
    all_participants = dm.get_all_participants()
    
    # Sort by points
    sorted_participants = sorted(
        all_participants, 
        key=lambda x: x.get('total_points', 0), 
        reverse=True
    )
    
    # Find my rank
    my_rank = None
    for idx, p in enumerate(sorted_participants):
        if p.get('id') == participant_id:
            my_rank = idx + 1
            break
    
    if my_rank:
        total_participants = len(sorted_participants)
        st.info(f"""
        **Your Current Rank:** #{my_rank} out of {total_participants} participants
        
        **Total Points:** {participant_data.get('total_points', 0)} pts
        """)
        
        # Progress bar
        if total_participants > 0:
            percentile = (1 - (my_rank - 1) / total_participants) * 100
            st.progress(percentile / 100, text=f"Top {100 - int(percentile)}%")
    else:
        st.info("Make some predictions to see your ranking!")

# Footer
st.markdown("---")
st.caption("Nikkang KK EPL Prediction Competition 2025-26")

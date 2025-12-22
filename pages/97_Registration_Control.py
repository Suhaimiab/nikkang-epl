"""
Admin: Registration Control
Lock/unlock user registration
"""

import streamlit as st
from pathlib import Path
import json
import sys

sys.path.append(str(Path(__file__).parent.parent))

from utils.auth import check_password

# Page config
st.set_page_config(
    page_title="Registration Control - Admin",
    page_icon="🔒",
    layout="wide"
)

# Require admin auth
if not check_password():
    st.stop()

# Logo
if Path("nikkang_logo.png").exists():
    st.sidebar.image("nikkang_logo.png", use_container_width=True)
    st.sidebar.markdown("---")

st.title("🔒 Registration Control")
st.markdown("### Lock or Unlock User Registration")

# Settings file
settings_file = Path("nikkang_data/settings.json")

# Load settings
if settings_file.exists():
    with open(settings_file, 'r') as f:
        settings = json.load(f)
else:
    settings = {}

# Get current registration status
registration_locked = settings.get('registration_locked', False)

# Show current status
st.markdown("---")

col1, col2 = st.columns([1, 2])

with col1:
    if registration_locked:
        st.error("🔒 **Registration: LOCKED**")
        st.caption("New users cannot register")
    else:
        st.success("🔓 **Registration: OPEN**")
        st.caption("New users can register")

with col2:
    if registration_locked:
        st.warning("⚠️ Users will see: 'Registration is currently closed. Please contact admin.'")
    else:
        st.info("ℹ️ Users can create new accounts on the login page")

st.markdown("---")

# Control buttons
st.markdown("### Change Registration Status:")

col1, col2 = st.columns(2)

with col1:
    if st.button("🔒 Lock Registration", use_container_width=True, type="primary", disabled=registration_locked):
        settings['registration_locked'] = True
        
        # Save settings
        settings_file.parent.mkdir(exist_ok=True)
        with open(settings_file, 'w') as f:
            json.dump(settings, f, indent=2)
        
        st.success("✅ Registration is now LOCKED")
        st.info("New users cannot register until you unlock it")
        st.rerun()

with col2:
    if st.button("🔓 Unlock Registration", use_container_width=True, disabled=not registration_locked):
        settings['registration_locked'] = False
        
        # Save settings
        settings_file.parent.mkdir(exist_ok=True)
        with open(settings_file, 'w') as f:
            json.dump(settings, f, indent=2)
        
        st.success("✅ Registration is now OPEN")
        st.info("New users can register again")
        st.rerun()

st.markdown("---")

# Usage scenarios
with st.expander("📋 When to Use This"):
    st.markdown("""
    ### Lock Registration When:
    
    - ✅ Season has started and you don't want new participants
    - ✅ You've reached maximum number of participants
    - ✅ Registration deadline has passed
    - ✅ Temporarily stopping new signups for maintenance
    
    ### Unlock Registration When:
    
    - ✅ Starting a new season
    - ✅ Opening registration for new gameweeks
    - ✅ Allowing late joiners
    - ✅ Re-opening after maintenance
    
    ### What Happens:
    
    **When Locked:**
    - Login page shows "Registration Closed" message
    - "Create Account" button is disabled
    - Existing users can still log in
    - Admins can still access everything
    
    **When Unlocked:**
    - Login page shows "Create Account" button
    - New users can register
    - Normal registration flow
    """)

# Statistics
st.markdown("---")
st.markdown("### Current Statistics:")

# Load participants
participants_file = Path("nikkang_data/participants.json")
if participants_file.exists():
    with open(participants_file, 'r') as f:
        participants = json.load(f)
    
    total_users = len(participants)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Users", total_users)
    
    with col2:
        st.metric("Registration", "🔒 Locked" if registration_locked else "🔓 Open")
    
    with col3:
        if not registration_locked:
            st.metric("New Signups", "Allowed")
        else:
            st.metric("New Signups", "Blocked")
else:
    st.info("No participants yet")

# Footer
st.markdown("---")
st.caption("💡 **Tip:** Lock registration before the season starts to finalize your participant list")

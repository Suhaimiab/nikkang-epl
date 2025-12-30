"""
Participant Authentication - MOBILE FIXED VERSION
With unique keys and spacing to fix mobile rendering
"""

import streamlit as st
import hashlib
import json
from pathlib import Path
from datetime import datetime
from typing import Optional, Tuple

PARTICIPANTS_FILE = Path("nikkang_data/participants.json")

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def load_participants() -> dict:
    if PARTICIPANTS_FILE.exists():
        try:
            with open(PARTICIPANTS_FILE, 'r') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_participants(participants: dict) -> bool:
    try:
        PARTICIPANTS_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(PARTICIPANTS_FILE, 'w') as f:
            json.dump(participants, f, indent=2)
        return True
    except:
        return False

def find_participant_by_nickname(nickname: str) -> Optional[Tuple[str, dict]]:
    participants = load_participants()
    nickname_lower = nickname.lower().strip()
    
    for uid, data in participants.items():
        display_name = data.get('display_name', '').lower().strip()
        name = data.get('name', '').lower().strip()
        
        if display_name == nickname_lower or name == nickname_lower:
            return uid, data
    return None

def verify_phone_last4(participant_data: dict, last4: str) -> bool:
    phone = participant_data.get('phone', '')
    phone_digits = ''.join(filter(str.isdigit, phone))
    return len(phone_digits) >= 4 and phone_digits[-4:] == last4

def has_password(participant_data: dict) -> bool:
    return 'password_hash' in participant_data and participant_data['password_hash']

def verify_password(participant_data: dict, password: str) -> bool:
    if not has_password(participant_data):
        return False
    return participant_data.get('password_hash', '') == hash_password(password)

def set_password(user_id: str, password: str) -> bool:
    participants = load_participants()
    if user_id not in participants:
        return False
    
    participants[user_id]['password_hash'] = hash_password(password)
    participants[user_id]['password_created_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    return save_participants(participants)

def initialize_participant_session():
    if 'participant_authenticated' not in st.session_state:
        st.session_state.participant_authenticated = False
    if 'participant_id' not in st.session_state:
        st.session_state.participant_id = None
    if 'participant_name' not in st.session_state:
        st.session_state.participant_name = None
    if 'participant_nickname' not in st.session_state:
        st.session_state.participant_nickname = None

def participant_login_form() -> bool:
    """
    MOBILE-FIXED VERSION
    - Unique keys for each field
    - Extra spacing between fields
    - All fields always visible
    """
    initialize_participant_session()
    
    if st.session_state.participant_authenticated:
        return True
    
    st.title("🔐 Login")
    
    st.write("---")
    
    # ALL FIELDS WITH UNIQUE KEYS AND SPACING
    st.write("**Enter your details:**")
    st.write("")  # Spacer
    
    nickname = st.text_input(
        "Nickname", 
        key="auth_nickname_field",
        placeholder="Your display name"
    )
    st.write("")  # Spacer
    
    last4 = st.text_input(
        "Last 4 digits of phone", 
        key="auth_last4_field",
        max_chars=4,
        placeholder="1234"
    )
    st.write("")  # Spacer
    
    password = st.text_input(
        "Password (if returning user)", 
        type="password",
        key="auth_password_field",
        placeholder="Your password"
    )
    
    st.write("---")
    st.write("**First-time users: Create password below**")
    st.write("")  # Spacer
    
    new_password = st.text_input(
        "New Password (6+ characters)", 
        type="password",
        key="auth_newpassword_field",
        placeholder="Create password"
    )
    st.write("")  # Spacer
    
    confirm_password = st.text_input(
        "Confirm New Password", 
        type="password",
        key="auth_confirmpassword_field",
        placeholder="Re-enter password"
    )
    
    st.write("---")
    
    if st.button("LOGIN", width='stretch', type="primary", key="auth_login_button"):
        
        if not nickname:
            st.error("❌ Enter your nickname")
            return False
        
        result = find_participant_by_nickname(nickname)
        if not result:
            st.error("❌ Nickname not found. Please register first.")
            return False
        
        user_id, participant_data = result
        p_nickname = participant_data.get('display_name', nickname)
        p_name = participant_data.get('name', nickname)
        
        # RETURNING USER (has password)
        if has_password(participant_data):
            if not password:
                st.error("❌ You already have a password. Please enter it to login.")
                return False
            
            if verify_password(participant_data, password):
                st.session_state.participant_authenticated = True
                st.session_state.participant_id = user_id
                st.session_state.participant_name = p_name
                st.session_state.participant_nickname = p_nickname
                st.success(f"✅ Welcome back, {p_nickname}!")
                st.rerun()
            else:
                st.error("❌ Incorrect password")
            return False
        
        # FIRST-TIME USER (no password yet)
        else:
            if not last4 or len(last4) != 4:
                st.error("❌ Please enter the last 4 digits of your phone number")
                return False
            
            if not verify_phone_last4(participant_data, last4):
                st.error("❌ Last 4 digits don't match your registration")
                return False
            
            if not new_password:
                st.success("✅ Identity verified! Now enter a new password above and click LOGIN again")
                return False
            
            if len(new_password) < 6:
                st.error("❌ Password must be at least 6 characters")
                return False
            
            if new_password != confirm_password:
                st.error("❌ Passwords don't match")
                return False
            
            # Create password and login
            if set_password(user_id, new_password):
                st.session_state.participant_authenticated = True
                st.session_state.participant_id = user_id
                st.session_state.participant_name = p_name
                st.session_state.participant_nickname = p_nickname
                st.success(f"✅ Password created! Welcome, {p_nickname}!")
                st.balloons()
                st.rerun()
            else:
                st.error("❌ Error creating password. Please try again.")
            return False
    
    return False

def participant_logout():
    st.session_state.participant_authenticated = False
    st.session_state.participant_id = None
    st.session_state.participant_name = None
    st.session_state.participant_nickname = None
    st.success("✅ Logged out")
    st.rerun()

def is_participant_authenticated() -> bool:
    initialize_participant_session()
    return st.session_state.participant_authenticated

def get_current_participant_id() -> Optional[str]:
    initialize_participant_session()
    return st.session_state.participant_id if st.session_state.participant_authenticated else None

def get_current_participant_name() -> Optional[str]:
    initialize_participant_session()
    return st.session_state.participant_name if st.session_state.participant_authenticated else None

def require_participant_auth(show_login_form=True):
    initialize_participant_session()
    
    if not st.session_state.participant_authenticated:
        if show_login_form:
            try:
                col1, col2, col3 = st.columns([1, 2, 1])
                with col2:
                    st.image("nikkang_logo.png", width=200)
            except:
                pass
            
            participant_login_form()
            st.stop()
        else:
            st.warning("⚠️ Please login")
            st.stop()
    
    return True

def participant_info_sidebar():
    initialize_participant_session()
    
    if st.session_state.participant_authenticated:
        with st.sidebar:
            st.markdown("---")
            st.markdown("### 👤 Logged In")
            st.info(f"**{st.session_state.participant_nickname}**")
            
            if st.button("🚪 Logout", width='stretch', key="logout_btn"):
                participant_logout()

def change_participant_password(old_password: str, new_password: str) -> Tuple[bool, str]:
    if not st.session_state.participant_authenticated:
        return False, "Not logged in"
    
    user_id = st.session_state.participant_id
    participants = load_participants()
    
    if user_id not in participants:
        return False, "User not found"
    
    if not verify_password(participants[user_id], old_password):
        return False, "Wrong password"
    
    if len(new_password) < 6:
        return False, "Min 6 characters"
    
    if set_password(user_id, new_password):
        return True, "Password changed"
    else:
        return False, "Error saving"

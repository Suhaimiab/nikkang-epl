"""
Participant Authentication System
Nikkang KK EPL Prediction Competition

Complete authentication system for participants with password management
"""

import streamlit as st
import hashlib
import json
from pathlib import Path
from datetime import datetime
from typing import Optional, Tuple

PARTICIPANTS_FILE = Path("nikkang_data/participants.json")


# ============================================================================
# PASSWORD MANAGEMENT
# ============================================================================

def hash_password(password: str) -> str:
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()


def load_participants() -> dict:
    """Load participants from JSON file"""
    if PARTICIPANTS_FILE.exists():
        try:
            with open(PARTICIPANTS_FILE, 'r') as f:
                return json.load(f)
        except:
            return {}
    return {}


def save_participants(participants: dict) -> bool:
    """Save participants to JSON file"""
    try:
        PARTICIPANTS_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(PARTICIPANTS_FILE, 'w') as f:
            json.dump(participants, f, indent=2)
        return True
    except:
        return False


def find_participant_by_nickname(nickname: str) -> Optional[Tuple[str, dict]]:
    """Find participant by nickname or display name"""
    participants = load_participants()
    nickname_lower = nickname.lower().strip()
    
    for uid, data in participants.items():
        display_name = data.get('display_name', '').lower().strip()
        name = data.get('name', '').lower().strip()
        
        if display_name == nickname_lower or name == nickname_lower:
            return uid, data
    return None


def find_participant_by_email(email: str) -> Optional[Tuple[str, dict]]:
    """Find participant by email address"""
    participants = load_participants()
    email_lower = email.lower().strip()
    
    for uid, data in participants.items():
        participant_email = data.get('email', '').lower().strip()
        if participant_email == email_lower:
            return uid, data
    return None


def verify_phone_last4(participant_data: dict, last4: str) -> bool:
    """Verify last 4 digits of phone number"""
    phone = participant_data.get('phone', '')
    phone_digits = ''.join(filter(str.isdigit, phone))
    return len(phone_digits) >= 4 and phone_digits[-4:] == last4


def has_password(participant_data: dict) -> bool:
    """Check if participant has a password set"""
    return 'password_hash' in participant_data and participant_data['password_hash']


def verify_password(participant_data: dict, password: str) -> bool:
    """Verify password matches stored hash"""
    if not has_password(participant_data):
        return False
    return participant_data.get('password_hash', '') == hash_password(password)


def set_password(user_id: str, password: str) -> bool:
    """Set new password for participant"""
    participants = load_participants()
    if user_id not in participants:
        return False
    
    participants[user_id]['password_hash'] = hash_password(password)
    participants[user_id]['password_set_at'] = datetime.now().isoformat()
    
    return save_participants(participants)


def change_password(user_id: str, old_password: str, new_password: str) -> Tuple[bool, str]:
    """
    Change participant password
    Returns: (success, message)
    """
    participants = load_participants()
    
    if user_id not in participants:
        return False, "Participant not found"
    
    participant_data = participants[user_id]
    
    # Verify old password
    if not verify_password(participant_data, old_password):
        return False, "Current password is incorrect"
    
    # Set new password
    participants[user_id]['password_hash'] = hash_password(new_password)
    participants[user_id]['password_changed_at'] = datetime.now().isoformat()
    
    if save_participants(participants):
        return True, "Password changed successfully"
    else:
        return False, "Failed to save new password"


# ============================================================================
# SESSION MANAGEMENT
# ============================================================================

def initialize_session():
    """Initialize session state variables"""
    if 'participant_authenticated' not in st.session_state:
        st.session_state.participant_authenticated = False
    if 'participant_id' not in st.session_state:
        st.session_state.participant_id = None
    if 'participant_name' not in st.session_state:
        st.session_state.participant_name = None
    if 'login_step' not in st.session_state:
        st.session_state.login_step = 'login'


def is_participant_authenticated() -> bool:
    """Check if participant is authenticated"""
    initialize_session()
    return st.session_state.get('participant_authenticated', False)


def get_current_participant_id() -> Optional[str]:
    """Get current authenticated participant ID"""
    initialize_session()
    if is_participant_authenticated():
        return st.session_state.get('participant_id')
    return None


def get_current_participant_data() -> Optional[dict]:
    """Get current authenticated participant data"""
    user_id = get_current_participant_id()
    if user_id:
        participants = load_participants()
        return participants.get(user_id)
    return None


def get_current_participant_name() -> Optional[str]:
    """Get current authenticated participant's display name"""
    if is_participant_authenticated():
        participant_data = get_current_participant_data()
        if participant_data:
            return participant_data.get('display_name', 
                   participant_data.get('name', 'Unknown'))
    return None


def login_participant(user_id: str, participant_data: dict):
    """Login participant and set session"""
    initialize_session()
    st.session_state.participant_authenticated = True
    st.session_state.participant_id = user_id
    st.session_state.participant_name = participant_data.get('display_name', 
                                        participant_data.get('name', 'Participant'))
    
    # Update last login
    participants = load_participants()
    if user_id in participants:
        participants[user_id]['last_login'] = datetime.now().isoformat()
        save_participants(participants)


def logout_participant():
    """Logout current participant"""
    st.session_state.participant_authenticated = False
    st.session_state.participant_id = None
    st.session_state.participant_name = None
    if 'login_step' in st.session_state:
        del st.session_state.login_step


# ============================================================================
# UI COMPONENTS
# ============================================================================

def participant_login_form():
    """
    Display participant login form with forgot password link
    Returns True if authenticated, False otherwise
    """
    initialize_session()
    
    # Check if creating password (first-time user)
    if st.session_state.login_step == 'create_password':
        return show_password_creation_form()
    
    # Regular login form
    st.markdown("### 🔐 Participant Login")
    
    with st.form("participant_login"):
        nickname = st.text_input(
            "👤 Nickname",
            placeholder="Your registered nickname",
            help="Enter your display name/nickname"
        )
        
        password = st.text_input(
            "🔒 Password",
            type="password",
            placeholder="Enter password or last 4 digits of phone",
            help="If you haven't set a password, enter last 4 digits of your phone"
        )
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            submit = st.form_submit_button("🚀 Login", width='stretch')
        
        with col2:
            forgot = st.form_submit_button("🔑 Forgot?", width='stretch')
        
        if forgot:
            st.switch_page("pages/Forgot_Password.py")
        
        if submit:
            if not nickname:
                st.error("❌ Please enter your nickname")
                return False
            
            # Find participant
            participant = find_participant_by_nickname(nickname)
            
            if not participant:
                st.error("❌ Nickname not found")
                st.info("💡 Make sure you've registered first")
                return False
            
            user_id, user_data = participant
            
            # Check if has password
            if has_password(user_data):
                # Verify password
                if verify_password(user_data, password):
                    login_participant(user_id, user_data)
                    st.success(f"✅ Welcome back, {user_data.get('display_name', 'Participant')}!")
                    st.rerun()
                    return True
                else:
                    st.error("❌ Incorrect password")
                    st.info("🔑 Click 'Forgot?' if you need to reset your password")
                    return False
            else:
                # First-time user - verify phone last 4 digits
                if verify_phone_last4(user_data, password):
                    # Store user info for password creation
                    st.session_state.creating_password_for = user_id
                    st.session_state.login_step = 'create_password'
                    st.rerun()
                else:
                    st.error("❌ Incorrect last 4 digits of phone")
                    st.info("💡 Enter the last 4 digits of the phone number you registered with")
                    return False
    
    return False


def show_password_creation_form():
    """Show password creation form for first-time users"""
    user_id = st.session_state.get('creating_password_for')
    
    if not user_id:
        st.session_state.login_step = 'login'
        st.rerun()
        return False
    
    participants = load_participants()
    user_data = participants.get(user_id)
    
    if not user_data:
        st.session_state.login_step = 'login'
        st.rerun()
        return False
    
    st.info(f"👋 Welcome, {user_data.get('display_name', 'Participant')}! Please create a password for future logins.")
    
    with st.form("create_password"):
        new_password = st.text_input(
            "🔒 Create Password",
            type="password",
            help="Choose a secure password (min 8 characters)"
        )
        
        confirm_password = st.text_input(
            "🔒 Confirm Password",
            type="password"
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            submit = st.form_submit_button("✅ Create & Login", width='stretch')
        
        with col2:
            cancel = st.form_submit_button("❌ Cancel", width='stretch')
        
        if cancel:
            st.session_state.login_step = 'login'
            if 'creating_password_for' in st.session_state:
                del st.session_state.creating_password_for
            st.rerun()
        
        if submit:
            # Validation
            if not new_password or len(new_password) < 8:
                st.error("❌ Password must be at least 8 characters")
                return False
            
            if new_password != confirm_password:
                st.error("❌ Passwords do not match")
                return False
            
            # Set password
            if set_password(user_id, new_password):
                # Login user
                login_participant(user_id, user_data)
                
                # Clean up session
                st.session_state.login_step = 'login'
                if 'creating_password_for' in st.session_state:
                    del st.session_state.creating_password_for
                
                st.success("✅ Password created! You're now logged in.")
                st.rerun()
                return True
            else:
                st.error("❌ Failed to create password. Please try again.")
                return False
    
    return False


def require_participant_auth():
    """
    Require participant authentication for protected pages
    Call this at the top of any page that needs login
    """
    initialize_session()
    
    if not is_participant_authenticated():
        st.warning("🔒 Please login to access this page")
        
        # Show login form
        if participant_login_form():
            st.rerun()
        
        # Stop page execution
        st.stop()


def participant_info_sidebar():
    """Display participant info and logout in sidebar"""
    initialize_session()
    
    if is_participant_authenticated():
        participant_data = get_current_participant_data()
        
        if participant_data:
            st.sidebar.markdown("---")
            st.sidebar.markdown("### 👤 Logged In")
            st.sidebar.info(f"**{participant_data.get('display_name', 'Participant')}**")
            
            if st.sidebar.button("🚪 Logout", width='stretch'):
                logout_participant()
                st.rerun()

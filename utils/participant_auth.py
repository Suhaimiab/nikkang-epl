"""
Participant Authentication Module
Nikkang KK EPL Prediction Competition

Handles participant login with two-step authentication:
1. First-time: nickname + last 4 digits of phone → Create password
2. Returning: nickname + password

Security features:
- SHA-256 password hashing
- Session-based authentication
- Secure password storage
"""

import streamlit as st
import hashlib
import json
from pathlib import Path
from datetime import datetime
from typing import Optional, Tuple

# Data file
PARTICIPANTS_FILE = Path("nikkang_data/participants.json")

def hash_password(password: str) -> str:
    """
    Hash password using SHA-256
    
    Args:
        password: Plain text password
        
    Returns:
        Hashed password string
    """
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
    except Exception as e:
        st.error(f"Error saving: {e}")
        return False

def find_participant_by_nickname(nickname: str) -> Optional[Tuple[str, dict]]:
    """
    Find participant by nickname (case-insensitive)
    
    Returns:
        Tuple of (user_id, participant_data) or None
    """
    participants = load_participants()
    nickname_lower = nickname.lower().strip()
    
    for uid, data in participants.items():
        display_name = data.get('display_name', '').lower().strip()
        name = data.get('name', '').lower().strip()
        
        if display_name == nickname_lower or name == nickname_lower:
            return uid, data
    
    return None

def verify_phone_last4(participant_data: dict, last4: str) -> bool:
    """
    Verify last 4 digits of phone number
    
    Args:
        participant_data: Participant dict
        last4: Last 4 digits to verify
        
    Returns:
        True if matches, False otherwise
    """
    phone = participant_data.get('phone', '')
    # Remove non-numeric characters
    phone_digits = ''.join(filter(str.isdigit, phone))
    
    if len(phone_digits) >= 4:
        return phone_digits[-4:] == last4
    
    return False

def has_password(participant_data: dict) -> bool:
    """Check if participant has created a password"""
    return 'password_hash' in participant_data and participant_data['password_hash']

def verify_password(participant_data: dict, password: str) -> bool:
    """
    Verify participant password
    
    Args:
        participant_data: Participant dict
        password: Plain text password
        
    Returns:
        True if password matches, False otherwise
    """
    if not has_password(participant_data):
        return False
    
    stored_hash = participant_data.get('password_hash', '')
    return stored_hash == hash_password(password)

def set_password(user_id: str, password: str) -> bool:
    """
    Set password for participant
    
    Args:
        user_id: Participant user ID
        password: Plain text password
        
    Returns:
        True if successful, False otherwise
    """
    participants = load_participants()
    
    if user_id not in participants:
        return False
    
    # Hash and store password
    participants[user_id]['password_hash'] = hash_password(password)
    participants[user_id]['password_created_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    return save_participants(participants)

def initialize_participant_session():
    """Initialize session state for participant authentication"""
    if 'participant_authenticated' not in st.session_state:
        st.session_state.participant_authenticated = False
    if 'participant_id' not in st.session_state:
        st.session_state.participant_id = None
    if 'participant_name' not in st.session_state:
        st.session_state.participant_name = None
    if 'participant_nickname' not in st.session_state:
        st.session_state.participant_nickname = None
    if 'needs_password_creation' not in st.session_state:
        st.session_state.needs_password_creation = False

def participant_login_form() -> bool:
    """
    Display participant login form with two-step authentication
    
    Returns:
        True if authenticated, False otherwise
    """
    initialize_participant_session()
    
    # If already authenticated, return True
    if st.session_state.participant_authenticated:
        return True
    
    # Check if needs to create password
    if st.session_state.needs_password_creation:
        return show_password_creation_form()
    
    # Show login form
    st.markdown("### 🔐 Participant Login")
    st.info("**First time?** Enter your nickname and last 4 digits of phone to create a password.  \n**Returning?** Enter your nickname and password.")
    
    with st.form("participant_login_form"):
        nickname = st.text_input("Nickname", placeholder="Your display name")
        
        col1, col2 = st.columns(2)
        with col1:
            last4 = st.text_input("Last 4 digits of phone", placeholder="1234", max_chars=4)
        with col2:
            password = st.text_input("Password (if returning)", type="password", placeholder="Leave blank if first time")
        
        submit = st.form_submit_button("Login", use_container_width=True, type="primary")
        
        if submit:
            if not nickname:
                st.error("❌ Please enter your nickname")
                return False
            
            # Find participant
            result = find_participant_by_nickname(nickname)
            
            if not result:
                st.error("❌ Nickname not found. Please check spelling or register first.")
                return False
            
            user_id, participant_data = result
            
            # Check if has password
            if has_password(participant_data):
                # Returning user - verify password
                if not password:
                    st.error("❌ Password required. If you forgot your password, contact admin.")
                    return False
                
                if verify_password(participant_data, password):
                    # Login successful
                    st.session_state.participant_authenticated = True
                    st.session_state.participant_id = user_id
                    st.session_state.participant_name = participant_data.get('name', nickname)
                    st.session_state.participant_nickname = participant_data.get('display_name', nickname)
                    st.success(f"✅ Welcome back, {st.session_state.participant_nickname}!")
                    st.rerun()
                else:
                    st.error("❌ Incorrect password. Please try again or contact admin if you forgot your password.")
                    return False
            else:
                # First-time user - verify last 4 digits
                if not last4 or len(last4) != 4 or not last4.isdigit():
                    st.error("❌ Please enter the last 4 digits of your phone number")
                    return False
                
                if verify_phone_last4(participant_data, last4):
                    # Verification successful - prompt password creation
                    st.session_state.needs_password_creation = True
                    st.session_state.participant_id = user_id
                    st.session_state.participant_name = participant_data.get('name', nickname)
                    st.session_state.participant_nickname = participant_data.get('display_name', nickname)
                    st.success("✅ Identity verified! Please create a password.")
                    st.rerun()
                else:
                    st.error("❌ Last 4 digits don't match. Please check your registration details.")
                    return False
    
    return False

def show_password_creation_form() -> bool:
    """
    Show password creation form for first-time users
    
    Returns:
        True if password created and logged in, False otherwise
    """
    st.markdown("### 🔑 Create Your Password")
    st.success(f"Welcome, {st.session_state.participant_nickname}!")
    st.info("""
    **Create a secure password** for future logins.
    
    Requirements:
    - Minimum 6 characters
    - Mix of letters and numbers recommended
    - Easy to remember but hard to guess
    """)
    
    with st.form("password_creation_form"):
        password = st.text_input("New Password", type="password", placeholder="Minimum 6 characters")
        confirm_password = st.text_input("Confirm Password", type="password", placeholder="Re-enter password")
        
        create = st.form_submit_button("Create Password & Login", use_container_width=True, type="primary")
        
        if create:
            # Validation
            if not password:
                st.error("❌ Please enter a password")
                return False
            
            if len(password) < 6:
                st.error("❌ Password must be at least 6 characters long")
                return False
            
            if password != confirm_password:
                st.error("❌ Passwords don't match. Please try again.")
                return False
            
            # Save password
            user_id = st.session_state.participant_id
            if set_password(user_id, password):
                # Login successful
                st.session_state.participant_authenticated = True
                st.session_state.needs_password_creation = False
                st.success("✅ Password created! You're now logged in.")
                st.balloons()
                st.rerun()
            else:
                st.error("❌ Error creating password. Please try again or contact admin.")
                return False
    
    return False

def participant_logout():
    """Logout current participant"""
    st.session_state.participant_authenticated = False
    st.session_state.participant_id = None
    st.session_state.participant_name = None
    st.session_state.participant_nickname = None
    st.session_state.needs_password_creation = False
    st.success("✅ Logged out successfully")
    st.rerun()

def is_participant_authenticated() -> bool:
    """Check if participant is currently authenticated"""
    initialize_participant_session()
    return st.session_state.participant_authenticated

def get_current_participant_id() -> Optional[str]:
    """Get current logged in participant ID"""
    initialize_participant_session()
    return st.session_state.participant_id if st.session_state.participant_authenticated else None

def get_current_participant_name() -> Optional[str]:
    """Get current logged in participant name"""
    initialize_participant_session()
    return st.session_state.participant_name if st.session_state.participant_authenticated else None

def require_participant_auth(show_login_form=True):
    """
    Require participant authentication for a page
    Call this at the start of any page that needs participant login
    
    Args:
        show_login_form: If True, shows login form. If False, just checks auth.
    
    Returns:
        True if authenticated, stops execution if not
    """
    initialize_participant_session()
    
    if not st.session_state.participant_authenticated:
        if show_login_form:
            # Show logo
            try:
                col1, col2, col3 = st.columns([1, 2, 1])
                with col2:
                    st.image("nikkang_logo.png", width=200)
            except:
                pass
            
            # Show login form
            participant_login_form()
            st.stop()
        else:
            st.warning("⚠️ Please login to access this page")
            if st.button("Go to Login"):
                st.switch_page("pages/3_Predictions.py")  # Or your login page
            st.stop()
    
    return True

def participant_info_sidebar():
    """Display participant info in sidebar"""
    initialize_participant_session()
    
    if st.session_state.participant_authenticated:
        with st.sidebar:
            st.markdown("---")
            st.markdown("### 👤 Logged In")
            st.info(f"**{st.session_state.participant_nickname}**")
            
            if st.button("🚪 Logout", use_container_width=True, key="participant_logout"):
                participant_logout()

def change_participant_password(old_password: str, new_password: str) -> Tuple[bool, str]:
    """
    Change participant password
    
    Args:
        old_password: Current password
        new_password: New password
        
    Returns:
        Tuple of (success, message)
    """
    if not st.session_state.participant_authenticated:
        return False, "Not logged in"
    
    user_id = st.session_state.participant_id
    participants = load_participants()
    
    if user_id not in participants:
        return False, "User not found"
    
    participant_data = participants[user_id]
    
    # Verify old password
    if not verify_password(participant_data, old_password):
        return False, "Current password is incorrect"
    
    # Validate new password
    if len(new_password) < 6:
        return False, "New password must be at least 6 characters"
    
    # Set new password
    if set_password(user_id, new_password):
        return True, "Password changed successfully"
    else:
        return False, "Error saving new password"

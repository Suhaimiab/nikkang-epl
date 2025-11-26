"""
Authentication Module for Nikkang KK EPL Prediction Competition
Handles admin login, session management, and access control
"""

import streamlit as st
from typing import Optional, Dict
import hashlib
from datetime import datetime

# Admin credentials - CHANGE THESE BEFORE DEPLOYMENT!
ADMIN_CREDENTIALS = {
    "admin1": "kemutkeliling",  # ⚠️ CHANGE THIS PASSWORD!
    "admin2": "nikkang69",  # Add more admins as needed
}

def hash_password(password: str) -> str:
    """
    Hash password using SHA-256
    
    Args:
        password: Plain text password
        
    Returns:
        Hashed password string
    """
    return hashlib.sha256(password.encode()).hexdigest()

def verify_credentials(username: str, password: str) -> bool:
    """
    Verify admin credentials
    
    Args:
        username: Admin username
        password: Admin password
        
    Returns:
        True if credentials are valid, False otherwise
    """
    if username in ADMIN_CREDENTIALS:
        return ADMIN_CREDENTIALS[username] == password
    return False

def check_password(password: str = None) -> bool:
    """
    Simple password check for admin access.
    
    Can be called two ways:
    1. check_password("mypassword") - checks if password is valid
    2. check_password() - displays a password input form and checks it
    
    Args:
        password: Password to check (optional)
        
    Returns:
        True if password matches any admin account, False otherwise
    """
    # If no password provided, show a form to get it
    if password is None:
        # Check if already authenticated
        initialize_session_state()
        if st.session_state.authenticated:
            return True
        
        # Show password form
        st.markdown("### 🔐 Admin Access Required")
        password_input = st.text_input("Enter admin password", type="password", key="admin_pwd_check")
        
        if st.button("Login", key="admin_login_btn"):
            if password_input in ADMIN_CREDENTIALS.values():
                st.session_state.authenticated = True
                st.session_state.username = "admin"
                st.session_state.login_time = datetime.now()
                st.success("✅ Access granted!")
                st.rerun()
            else:
                st.error("❌ Invalid password")
        
        return st.session_state.authenticated
    
    # Password provided - just check it
    return password in ADMIN_CREDENTIALS.values()

def initialize_session_state():
    """Initialize session state variables for authentication"""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'username' not in st.session_state:
        st.session_state.username = None
    if 'login_time' not in st.session_state:
        st.session_state.login_time = None

def admin_login() -> bool:
    """
    Display admin login form and handle authentication
    
    Returns:
        True if user is authenticated, False otherwise
    """
    initialize_session_state()
    
    # If already authenticated, return True
    if st.session_state.authenticated:
        return True
    
    # Display login form
    st.markdown("### 🔐 Admin Login Required")
    st.info("Please login with your admin credentials to access this page.")
    
    with st.form("login_form"):
        username = st.text_input("Username", key="login_username")
        password = st.text_input("Password", type="password", key="login_password")
        submit = st.form_submit_button("Login")
        
        if submit:
            if verify_credentials(username, password):
                st.session_state.authenticated = True
                st.session_state.username = username
                st.session_state.login_time = datetime.now()
                st.success(f"✅ Welcome back, {username}!")
                st.rerun()
            else:
                st.error("❌ Invalid username or password")
                return False
    
    return False

def require_admin(page_title: str = "Admin Page"):
    """
    Decorator-style function to require admin authentication
    Call this at the start of any admin page
    
    Args:
        page_title: Title to display on the page
        
    Returns:
        True if authenticated, False otherwise (and shows login form)
    """
    initialize_session_state()
    
    # Set page config
    st.set_page_config(
        page_title=f"Nikkang KK EPL - {page_title}",
        page_icon="⚽",
        layout="wide"
    )
    
    # Check if authenticated
    if not st.session_state.authenticated:
        # Display logo and branding
        try:
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                st.image("nikkang_logo.png", width=200)
        except:
            pass
        
        st.title(f"🔐 {page_title}")
        
        # Show login form
        if not admin_login():
            st.stop()
    
    # User is authenticated, show admin info in sidebar
    with st.sidebar:
        st.success(f"✅ Logged in as: **{st.session_state.username}**")
        if st.session_state.login_time:
            st.caption(f"Login time: {st.session_state.login_time.strftime('%H:%M:%S')}")
        
        if st.button("🚪 Logout", use_container_width=True):
            admin_logout()
    
    return True

def admin_logout():
    """Logout current admin user"""
    st.session_state.authenticated = False
    st.session_state.username = None
    st.session_state.login_time = None
    st.success("✅ Logged out successfully")
    st.rerun()

def is_authenticated() -> bool:
    """
    Check if user is currently authenticated
    
    Returns:
        True if authenticated, False otherwise
    """
    initialize_session_state()
    return st.session_state.authenticated

def get_current_user() -> Optional[str]:
    """
    Get current logged in username
    
    Returns:
        Username if authenticated, None otherwise
    """
    initialize_session_state()
    return st.session_state.username if st.session_state.authenticated else None

def change_password(username: str, old_password: str, new_password: str) -> tuple[bool, str]:
    """
    Change admin password
    
    Args:
        username: Admin username
        old_password: Current password
        new_password: New password
        
    Returns:
        Tuple of (success, message)
    """
    if username not in ADMIN_CREDENTIALS:
        return False, "Username not found"
    
    if ADMIN_CREDENTIALS[username] != old_password:
        return False, "Current password is incorrect"
    
    if len(new_password) < 8:
        return False, "New password must be at least 8 characters"
    
    ADMIN_CREDENTIALS[username] = new_password
    return True, "Password changed successfully"

def add_admin(username: str, password: str) -> tuple[bool, str]:
    """
    Add new admin user
    
    Args:
        username: New admin username
        password: Admin password
        
    Returns:
        Tuple of (success, message)
    """
    if username in ADMIN_CREDENTIALS:
        return False, "Username already exists"
    
    if len(password) < 8:
        return False, "Password must be at least 8 characters"
    
    ADMIN_CREDENTIALS[username] = password
    return True, f"Admin user '{username}' added successfully"

def remove_admin(username: str) -> tuple[bool, str]:
    """
    Remove admin user
    
    Args:
        username: Admin username to remove
        
    Returns:
        Tuple of (success, message)
    """
    if username not in ADMIN_CREDENTIALS:
        return False, "Username not found"
    
    if len(ADMIN_CREDENTIALS) == 1:
        return False, "Cannot remove the last admin user"
    
    del ADMIN_CREDENTIALS[username]
    return True, f"Admin user '{username}' removed successfully"

def list_admins() -> list[str]:
    """
    Get list of all admin usernames
    
    Returns:
        List of admin usernames
    """
    return list(ADMIN_CREDENTIALS.keys())

def admin_info_widget():
    """
    Display admin info widget in sidebar
    Call this from admin pages to show authentication status
    """
    initialize_session_state()
    
    if st.session_state.authenticated:
        with st.sidebar:
            st.divider()
            st.markdown("### 👤 Admin Session")
            st.info(f"""
            **User:** {st.session_state.username}  
            **Login:** {st.session_state.login_time.strftime('%H:%M:%S') if st.session_state.login_time else 'N/A'}
            """)
            
            if st.button("🚪 Logout", key="sidebar_logout", use_container_width=True):
                admin_logout()

def security_check():
    """
    Display security warnings if default credentials are being used
    """
    if "admin" in ADMIN_CREDENTIALS and ADMIN_CREDENTIALS["admin"] == "admin123":
        st.warning("""
        ⚠️ **SECURITY WARNING**: You are using default admin credentials!
        
        Please change the default password in `utils/auth.py` before deployment:
        
        ```python
        ADMIN_CREDENTIALS = {
            "admin": "YourStrongPassword123!",
            "suhaimi": "AnotherSecurePass456!"
        }
        ```
        """)
        return False
    return True

# Additional helper functions for backward compatibility
def check_admin_password(password: str) -> bool:
    """Alternative name for check_password"""
    return check_password(password)

def authenticate_user(username: str, password: str) -> bool:
    """Alternative name for verify_credentials"""
    return verify_credentials(username, password)

def show_login_form(form_key: str = "admin_login") -> bool:
    """Display a simple login form"""
    with st.form(form_key):
        password = st.text_input("Enter Admin Password", type="password")
        submit = st.form_submit_button("Access Admin Panel")
        
        if submit:
            if check_password(password):
                st.session_state.authenticated = True
                st.session_state.username = "admin"
                st.session_state.login_time = datetime.now()
                st.success("✅ Access granted!")
                st.rerun()
            else:
                st.error("❌ Invalid password")
                return False
    return False

def require_password(password_input: str) -> bool:
    """Simple password requirement check"""
    return check_password(password_input)

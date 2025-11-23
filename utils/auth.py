"""
Authentication and URL parameter handling
"""

import streamlit as st
from urllib.parse import urlparse, parse_qs
from utils.data_manager import DataManager

def check_url_params():
    """Check URL parameters for participant access"""
    try:
        # Get query parameters
        params = st.query_params
        
        if 'id' in params:
            participant_id = params['id']
            dm = DataManager()
            participant = dm.get_participant(participant_id)
            
            if participant:
                # Store in session state
                if 'week' in params:
                    participant['selected_week'] = int(params['week'])
                
                return participant
        
        return None
    except Exception as e:
        st.error(f"Error checking URL parameters: {e}")
        return None

def is_admin_logged_in() -> bool:
    """Check if admin is logged in"""
    return st.session_state.get('admin_logged_in', False)

def admin_login(password: str) -> bool:
    """Verify admin password and login"""
    from utils.config import ADMIN_PASSWORD
    
    if password == ADMIN_PASSWORD:
        st.session_state.admin_logged_in = True
        return True
    return False

def admin_logout():
    """Logout admin"""
    st.session_state.admin_logged_in = False

def require_admin():
    """Decorator/function to require admin access"""
    if not is_admin_logged_in():
        st.warning("⚠️ Admin access required")
        
        with st.form("admin_login"):
            password = st.text_input("Admin Password", type="password")
            submitted = st.form_submit_button("Login")
            
            if submitted:
                if admin_login(password):
                    st.success("✅ Admin logged in successfully!")
                    st.rerun()
                else:
                    st.error("❌ Invalid password")
        
        st.stop()
    
    return True

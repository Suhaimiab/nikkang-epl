"""
Simple Sync UI - Add to your pages
Works with your Dropbox setup
"""

import streamlit as st
import time
from datetime import datetime

def add_sync_buttons_sidebar(dm):
    """
    Add sync buttons to sidebar
    Call this on EVERY page
    """
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🔄 Sync")
    
    col1, col2 = st.sidebar.columns(2)
    
    with col1:
        if st.button("🔄", width='stretch', help="Reload data", key="sync_reload"):
            dm.clear_all_caches()
            st.success("✅")
            st.rerun()
    
    with col2:
        if st.button("🗑️", width='stretch', help="Clear cache", key="sync_clear"):
            dm.clear_all_caches()
            st.success("✅")
            st.rerun()
    
    # Show current week
    current_week = dm.get_current_week()
    st.sidebar.caption(f"Week {current_week}")


def validate_week(dm):
    """
    Call this at page load to get correct week
    """
    # Only validate once per session
    if 'week_loaded' not in st.session_state:
        st.session_state.week_loaded = True
        time.sleep(0.5)  # Brief pause for Dropbox
    
    return dm.get_current_week(force_reload=dm._is_mobile())


def add_admin_week_changer(dm):
    """
    Add week changer for admin pages
    """
    st.sidebar.markdown("---")
    st.sidebar.markdown("### ⚙️ Admin")
    
    current = dm.get_current_week(force_reload=True)
    
    new_week = st.sidebar.number_input(
        "Week:",
        min_value=1,
        max_value=38,
        value=current,
        key="admin_week"
    )
    
    if new_week != current:
        if st.sidebar.button("💾 Save", type="primary", width='stretch'):
            with st.spinner("Saving..."):
                success = dm.set_current_week(new_week)
                
                if success:
                    st.sidebar.success(f"✅ Week {new_week}")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.sidebar.error("❌ Failed")

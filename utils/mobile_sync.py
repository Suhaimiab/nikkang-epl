"""
Mobile Sync Helper - Add to pages that need mobile reliability
"""

import streamlit as st

def add_mobile_sync_button():
    """Add mobile sync button to sidebar"""
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🔄 Mobile Sync")
    
    col1, col2 = st.sidebar.columns(2)
    
    with col1:
        if st.button("🔄 Refresh", width='stretch', help="Reload data from server"):
            st.cache_data.clear()
            st.rerun()
    
    with col2:
        if st.button("🗑️ Clear", width='stretch', help="Clear all cache"):
            # Clear all caches
            st.cache_data.clear()
            st.cache_resource.clear()
            
            # Clear session state
            for key in list(st.session_state.keys()):
                if not key.startswith('_'):  # Keep internal streamlit keys
                    del st.session_state[key]
            
            st.success("✅ Cache cleared!")
            st.rerun()
    
    st.sidebar.caption("💡 Use if data not updating")


def force_reload_week(dm):
    """Force reload current week from file"""
    # Clear cache
    if 'current_week_cache' in st.session_state:
        del st.session_state['current_week_cache']
    
    # Force reload
    current_week = dm.get_current_week(force_reload=True)
    
    return current_week


def validate_week_on_mobile(dm):
    """Validate week is correct on mobile load"""
    # Check if this is first load in session
    if 'week_validated' not in st.session_state:
        st.session_state.week_validated = True
        
        # Force reload to get fresh data
        current_week = dm.get_current_week(force_reload=True)
        
        # Validate it's not stuck
        validated_week = dm.validate_week()
        
        if validated_week != current_week:
            st.cache_data.clear()
            st.rerun()
        
        return validated_week
    
    return dm.get_current_week()


def add_admin_week_changer(dm):
    """Add week changer for admin with mobile-safe save"""
    st.sidebar.markdown("---")
    st.sidebar.markdown("### ⚙️ Settings")
    
    current_week = dm.get_current_week(force_reload=True)
    
    new_week = st.sidebar.number_input(
        "Current Week:",
        min_value=1,
        max_value=38,
        value=current_week,
        key="admin_current_week"
    )
    
    if new_week != current_week:
        if st.sidebar.button("💾 Save Week", type="primary", width='stretch'):
            with st.spinner("Saving..."):
                success = dm.set_current_week(new_week)
                
                if success:
                    st.sidebar.success(f"✅ Week set to {new_week}")
                    st.cache_data.clear()
                    st.rerun()
                else:
                    st.sidebar.error("❌ Failed to save week")


def check_mobile_staleness(dm):
    """Check if settings are stale on mobile"""
    from datetime import datetime, timedelta
    
    settings = dm.load_settings()
    last_updated = settings.get('last_updated', None)
    
    if last_updated:
        try:
            updated_dt = datetime.fromisoformat(last_updated)
            now = datetime.now()
            
            # If older than 6 hours, show warning
            if (now - updated_dt) > timedelta(hours=6):
                st.sidebar.warning("⚠️ Settings may be outdated")
                if st.sidebar.button("🔄 Reload Settings"):
                    st.cache_data.clear()
                    st.rerun()
        except:
            pass


# ============================================================================
# USAGE EXAMPLES
# ============================================================================

"""
# In your pages, add at the top:

from utils.mobile_sync import add_mobile_sync_button, validate_week_on_mobile
from utils.data_manager import DataManager

dm = DataManager()

# Validate week on load (fixes stuck week 21)
current_week = validate_week_on_mobile(dm)

# Add mobile sync buttons to sidebar
add_mobile_sync_button()

# Now use current_week normally
st.write(f"Current Week: {current_week}")
"""

"""
# For admin pages:

from utils.mobile_sync import add_admin_week_changer, add_mobile_sync_button
from utils.data_manager import DataManager

dm = DataManager()

# Add week changer for admin
add_admin_week_changer(dm)

# Add sync buttons
add_mobile_sync_button()
"""

"""
# For pages that display current week:

from utils.mobile_sync import force_reload_week
from utils.data_manager import DataManager

dm = DataManager()

# Always get fresh week (bypasses cache)
current_week = force_reload_week(dm)

st.write(f"Current Week: {current_week}")
"""

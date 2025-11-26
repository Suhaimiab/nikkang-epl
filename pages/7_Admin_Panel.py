"""
Admin Dashboard
Nikkang KK EPL Prediction Competition
Main admin control panel with statistics and quick actions
"""

import streamlit as st
import pandas as pd
from datetime import datetime
from utils.auth import require_admin, admin_logout
from utils.data_manager import (
    load_participants,
    load_matches,
    load_predictions,
    load_results,
    backup_all_data
)

# Helper functions to handle both list and dict data formats
def safe_get(item, key, default=None):
    """Safely get attribute from dict or object"""
    if isinstance(item, dict):
        return item.get(key, default)
    elif hasattr(item, key):
        return getattr(item, key, default)
    return default

def count_items(data):
    """Count items in either list or dict"""
    if isinstance(data, list):
        return len(data)
    elif isinstance(data, dict):
        return len(data)
    return 0

def iterate_items(data):
    """Iterate items regardless of list or dict format"""
    if isinstance(data, list):
        for item in data:
            yield item
    elif isinstance(data, dict):
        for item in data.values():
            yield item

# Require admin authentication
if not require_admin("Admin Dashboard"):
    st.stop()

# Page header
st.title("🎯 Admin Dashboard")
st.markdown("Welcome to the Nikkang KK EPL Prediction Competition Admin Panel")
st.markdown("---")

# Load data (works with both list and dict formats)
participants = load_participants()
matches = load_matches()
predictions = load_predictions()
results = load_results()

# Statistics Overview
st.header("📊 Competition Statistics")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Total Participants",
        count_items(participants),
        help="Number of registered participants"
    )

with col2:
    st.metric(
        "Total Matches",
        count_items(matches),
        help="Number of fixtures in the season"
    )

with col3:
    st.metric(
        "Completed Matches",
        count_items(results),
        help="Matches with results entered"
    )

with col4:
    # Count predictions - handle different formats
    total_predictions = 0
    if isinstance(predictions, dict):
        for user_preds in predictions.values():
            if isinstance(user_preds, dict):
                total_predictions += len(user_preds)
            elif isinstance(user_preds, list):
                total_predictions += len(user_preds)
    elif isinstance(predictions, list):
        total_predictions = len(predictions)
    
    st.metric(
        "Total Predictions",
        total_predictions,
        help="Number of predictions made"
    )

st.markdown("---")

# Activity Overview
st.header("📈 Recent Activity")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Participant Status")
    
    if count_items(participants) > 0:
        active_count = 0
        inactive_count = 0
        
        for p in iterate_items(participants):
            status = safe_get(p, 'status', 'active')
            if status == 'active':
                active_count += 1
            else:
                inactive_count += 1
        
        status_data = pd.DataFrame({
            'Status': ['Active', 'Inactive'],
            'Count': [active_count, inactive_count]
        })
        
        st.dataframe(status_data, use_container_width=True, hide_index=True)
        
        # Participation rate
        total_matches = count_items(matches)
        total_participants = count_items(participants)
        
        if total_matches > 0 and total_participants > 0:
            participation_rate = (total_predictions / (total_participants * total_matches)) * 100
            st.metric("Participation Rate", f"{participation_rate:.1f}%")
    else:
        st.info("No participants yet")

with col2:
    st.subheader("Match Progress")
    
    if count_items(matches) > 0:
        scheduled = 0
        completed_matches = 0
        
        for m in iterate_items(matches):
            status = safe_get(m, 'status', 'scheduled')
            if status == 'scheduled':
                scheduled += 1
            elif status == 'completed':
                completed_matches += 1
        
        progress_data = pd.DataFrame({
            'Status': ['Scheduled', 'Completed'],
            'Count': [scheduled, completed_matches]
        })
        
        st.dataframe(progress_data, use_container_width=True, hide_index=True)
        
        # Completion rate
        total_m = count_items(matches)
        if total_m > 0:
            completion_rate = (completed_matches / total_m) * 100
            st.metric("Completion Rate", f"{completion_rate:.1f}%")
    else:
        st.info("No matches scheduled yet")

st.markdown("---")

# Quick Actions
st.header("⚡ Quick Actions")

col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("Participant Management")
    if st.button("➕ Add Participant", use_container_width=True):
        st.switch_page("pages/9_participant_management.py")
    
    if st.button("📋 View All Participants", use_container_width=True):
        st.switch_page("pages/9_participant_management.py")

with col2:
    st.subheader("Match Management")
    if st.button("⚽ Enter Results", use_container_width=True):
        st.switch_page("pages/4_results.py")
    
    if st.button("📥 Import Fixtures", use_container_width=True):
        st.switch_page("pages/10_api_integration.py")

with col3:
    st.subheader("Communications")
    if st.button("📱 Send WhatsApp", use_container_width=True):
        st.switch_page("pages/8_whatsapp_notifications.py")
    
    if st.button("📊 View Leaderboard", use_container_width=True):
        st.switch_page("pages/5_leaderboard.py")

st.markdown("---")

# Top Performers
st.header("🏆 Top Performers")

if count_items(participants) > 0:
    # Build list of participants with points
    participant_list = []
    for p in iterate_items(participants):
        participant_list.append({
            'name': safe_get(p, 'name', 'Unknown'),
            'points': safe_get(p, 'total_points', 0),
            'status': safe_get(p, 'status', 'active')
        })
    
    # Sort by total points
    sorted_participants = sorted(
        participant_list,
        key=lambda x: x['points'],
        reverse=True
    )
    
    # Get top 5
    top_5 = sorted_participants[:5]
    
    if top_5:
        top_data = []
        for rank, p in enumerate(top_5, 1):
            top_data.append({
                'Rank': rank,
                'Name': p['name'],
                'Points': p['points'],
                'Status': p['status']
            })
        
        df_top = pd.DataFrame(top_data)
        st.dataframe(df_top, use_container_width=True, hide_index=True)
    else:
        st.info("No points have been awarded yet")
else:
    st.info("No participants to display")

st.markdown("---")

# Data Overview
st.header("📊 Data Overview")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Data Status")
    
    data_items = [
        ("Participants", participants),
        ("Matches", matches),
        ("Predictions", predictions),
        ("Results", results)
    ]
    
    for name, data in data_items:
        count = count_items(data)
        if count > 0:
            st.text(f"✅ {name}: {count} items")
        else:
            st.text(f"⚠️ {name}: Empty")

with col2:
    st.subheader("Backup & Export")
    
    if st.button("💾 Create Backup", use_container_width=True):
        try:
            success, message = backup_all_data()
            if success:
                st.success(message)
            else:
                st.error(message)
        except Exception as e:
            st.error(f"Backup error: {e}")
    
    st.caption("Regular backups recommended")

st.markdown("---")

# Admin Session Info
st.header("👤 Admin Session")

from utils.auth import get_current_user

current_user = get_current_user()
if current_user:
    st.info(f"Logged in as: **{current_user}**")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("🔄 Refresh Dashboard", use_container_width=True):
        st.rerun()

with col2:
    if st.button("⚙️ Admin Settings", use_container_width=True, disabled=True):
        st.info("Coming soon!")

with col3:
    if st.button("🚪 Logout", use_container_width=True, type="secondary"):
        admin_logout()

# Footer
st.markdown("---")
st.caption("Nikkang KK EPL Prediction Competition 2025-26 • Admin Dashboard")
st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

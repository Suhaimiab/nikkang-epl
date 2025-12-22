"""
Device Sync Page
Nikkang KK EPL Prediction Competition
Simple sync between mobile and desktop using codes
"""

import streamlit as st
from utils.auth import require_admin
from utils.simple_sync import simple_sync_ui

# Require admin authentication
if not require_admin("Device Sync"):
    st.stop()

# Page header
st.title("📱💻 Device Sync")
st.markdown("Sync your data between mobile and desktop in seconds")

# Simple sync interface
simple_sync_ui()

# Footer
st.markdown("---")
st.caption("Nikkang KK EPL Prediction Competition 2025-26 • Device Sync")

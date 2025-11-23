"""
Nikkang KK EPL Prediction Competition - Home Page
Enhanced with branding and attractive layout
"""

import streamlit as st
from pathlib import Path

# Page config
st.set_page_config(
    page_title="Home - Nikkang KK",
    page_icon="⚽",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 1rem 0;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .main-header h1 {
        color: white;
        font-size: 2.5rem;
        font-weight: bold;
        margin: 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
    }
    
    .stats-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        margin: 1rem 0;
        border-left: 4px solid #667eea;
        transition: transform 0.3s;
    }
    
    .stats-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    }
    
    .sidebar-logo-container {
        text-align: center;
        padding: 1rem 0;
        margin-bottom: 1rem;
        background: white;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
</style>
""", unsafe_allow_html=True)

def display_logo_sidebar():
    """Display logo in sidebar at the very top"""
    logo_path = Path("nikkang_logo.png")
    if logo_path.exists():
        # Add top padding for positioning
        st.sidebar.markdown('<div style="padding-top: 0.5rem;"></div>', unsafe_allow_html=True)
        st.sidebar.markdown('<div class="sidebar-logo-container">', unsafe_allow_html=True)
        st.sidebar.image("nikkang_logo.png", use_container_width=True)
        st.sidebar.markdown('</div>', unsafe_allow_html=True)
    else:
        # Fallback text logo
        st.sidebar.markdown('<div style="padding-top: 0.5rem;"></div>', unsafe_allow_html=True)
        st.sidebar.markdown("""
        <div class="sidebar-logo-container">
            <h2 style="color: #667eea; margin: 0;">⚽ NIKKANG KK</h2>
        </div>
        """, unsafe_allow_html=True)

def display_logo_main():
    """Display logo in main page"""
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        logo_path = Path("nikkang_logo.png")
        if logo_path.exists():
            st.image("nikkang_logo.png", use_container_width=True)

# Display logos
display_logo_sidebar()
display_logo_main()

# Main header
st.markdown('<div class="main-header">', unsafe_allow_html=True)
st.markdown('<h1>🏠 Home - Nikkang KK EPL League</h1>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# Welcome content
st.markdown("""
### 👋 Welcome to the Premier League Prediction Competition!

This is your home base for all things EPL predictions. Navigate using the sidebar to access different features.
""")

# Feature showcase
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class="stats-card">
        <h3 style="color: #667eea;">📝 Register</h3>
        <p>Get your unique prediction link and join the competition!</p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Go to Registration", use_container_width=True, type="primary"):
        st.switch_page("pages/2_register.py")

with col2:
    st.markdown("""
    <div class="stats-card">
        <h3 style="color: #667eea;">🎯 Predictions</h3>
        <p>Submit your weekly match predictions and choose your GOTW!</p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Make Predictions", use_container_width=True):
        st.switch_page("pages/3_predictions.py")

with col3:
    st.markdown("""
    <div class="stats-card">
        <h3 style="color: #667eea;">📊 Leaderboard</h3>
        <p>Check rankings, weekly highlights, and KK Champions!</p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("View Leaderboard", use_container_width=True):
        st.switch_page("pages/5_leaderboard.py")

st.markdown("---")

# Stats overview
st.markdown("### 📊 Competition Overview")

try:
    from utils.data_manager import DataManager
    dm = DataManager()
    
    participants = dm.load_participants()
    matches = dm.load_matches()
    predictions = dm.load_predictions()
    
    stat_col1, stat_col2, stat_col3, stat_col4 = st.columns(4)
    
    with stat_col1:
        st.metric("👥 Total Participants", len(participants))
    
    with stat_col2:
        st.metric("⚽ Total Matches", len(matches))
    
    with stat_col3:
        total_predictions = sum(len(p.get('predictions', {})) for p in predictions.values())
        st.metric("🎯 Predictions Made", total_predictions)
    
    with stat_col4:
        if matches:
            current_week = max([m.get('week', 0) for m in matches])
            st.metric("📅 Current Week", f"Week {current_week}")
        else:
            st.metric("📅 Current Week", "Not Started")

except Exception as e:
    st.info("Competition data will appear here once you start!")

st.markdown("---")

# Quick guide
with st.expander("📖 Quick Start Guide"):
    st.markdown("""
    ### How to Participate:
    
    **Step 1: Register**
    - Go to Registration page
    - Enter your name
    - Get your unique prediction link
    - Save this link for future predictions!
    
    **Step 2: Make Predictions**
    - Use your unique link
    - Predict scores for 10 matches each week
    - Choose your Game of the Week (GOTW)
    - Submit before matches start
    
    **Step 3: Track Your Progress**
    - Check the Leaderboard regularly
    - See weekly Top 3 and Bottom 3
    - Track KK Champions (exact score leaders)
    - Follow your season ranking
    
    ### Scoring System:
    - **Exact Score**: 6 points
    - **Correct Result**: 3 points (right outcome, wrong score)
    - **GOTW Bonus**: Doubles your points for that match
    - **Week 38 Bonus**: All points doubled in final week
    """)

# Footer
st.markdown("""
<div style="text-align: center; padding: 2rem 0 1rem 0; color: #6c757d; font-size: 0.9rem; border-top: 1px solid #dee2e6; margin-top: 3rem;">
    <p><strong>Nikkang KK EPL Prediction League</strong> | Season 2025-26</p>
    <p>© 2025 Nikkang KK. All rights reserved.</p>
</div>
""", unsafe_allow_html=True)

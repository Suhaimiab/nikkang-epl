"""
Shared Navigation Sidebar
Import this in all pages to have consistent navigation
"""

import streamlit as st
from pathlib import Path

def hide_default_navigation():
    """Hide the default Streamlit page navigation"""
    st.markdown("""
    <style>
        [data-testid="stSidebarNav"] {
            display: none;
        }
    </style>
    """, unsafe_allow_html=True)

def display_sidebar_navigation():
    """Display custom sidebar navigation with Participant and Admin sections"""
    
    # Hide default navigation
    hide_default_navigation()
    
    # Logo
    logo_path = Path("nikkang_logo.png")
    if logo_path.exists():
        st.sidebar.markdown('<div style="padding-top: 0.5rem;"></div>', unsafe_allow_html=True)
        st.sidebar.markdown("""
        <div style="text-align: center; padding: 1rem 0; margin-bottom: 1rem; 
                    background: white; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
        """, unsafe_allow_html=True)
        st.sidebar.image("nikkang_logo.png", width='stretch')
        st.sidebar.markdown('</div>', unsafe_allow_html=True)
    else:
        st.sidebar.markdown("""
        <div style="text-align: center; padding: 1rem 0; margin-bottom: 1rem; 
                    background: white; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
            <h2 style="color: #667eea; margin: 0;">⚽ NIKKANG KK</h2>
        </div>
        """, unsafe_allow_html=True)
    
    st.sidebar.markdown("---")
    
    # PARTICIPANT SECTION
    st.sidebar.markdown("### 👥 Participants")
    
    if st.sidebar.button("🏠 Home", width='stretch', key="nav_home"):
        st.switch_page("pages/1_home.py")
    
    if st.sidebar.button("📝 Register", width='stretch', key="nav_register"):
        st.switch_page("pages/2_register.py")
    
    if st.sidebar.button("🎯 Make Predictions", width='stretch', key="nav_predictions"):
        st.switch_page("pages/3_predictions.py")
    
    if st.sidebar.button("📊 View Results", width='stretch', key="nav_results"):
        st.switch_page("pages/4_results.py")
    
    if st.sidebar.button("🏆 Leaderboard", width='stretch', key="nav_leaderboard"):
        st.switch_page("pages/5_leaderboard.py")
    
    if st.sidebar.button("📱 Install App", width='stretch', key="nav_install"):
        st.switch_page("pages/7_mobile_install.py")
    
    st.sidebar.markdown("---")
    
    # ADMIN SECTION
    st.sidebar.markdown("### 🔐 Admin Only")
    
    if st.sidebar.button("🛠️ Admin Panel", width='stretch', key="nav_admin"):
        st.switch_page("pages/6_admin.py")
    
    if st.sidebar.button("👤 Participants", width='stretch', key="nav_participants"):
        st.switch_page("pages/9_participant_management.py")
    
    if st.sidebar.button("⚽ Matches", width='stretch', key="nav_matches"):
        st.switch_page("pages/12_match_management.py")
    
    if st.sidebar.button("📥 Results", width='stretch', key="nav_results_mgmt"):
        st.switch_page("pages/13_results_management.py")
    
    if st.sidebar.button("🔒 Pred. Lock", width='stretch', key="nav_lock"):
        st.switch_page("pages/11_prediction_management.py")
    
    if st.sidebar.button("📊 Round Scores", width='stretch', key="nav_rounds"):
        st.switch_page("pages/14_round_scores.py")
    
    if st.sidebar.button("🌐 API", width='stretch', key="nav_api"):
        st.switch_page("pages/10_api_integration.py")
    
    st.sidebar.markdown("---")
    
    # Scoring info
    with st.sidebar.expander("📖 Scoring"):
        st.markdown("""
        **Normal Match:**
        - Exact: 5 pts
        - Correct: 3 pts
        
        **GOTW:**
        - Exact: 10 pts
        - Correct: 5 pts
        
        **KK** = Kemut Keliling
        """)
    
    st.sidebar.markdown("---")
    st.sidebar.caption("Nikkang KK | Season 2025-26")

"""
Nikkang KK EPL Prediction Competition
Main application entry point with enhanced branding
"""

import streamlit as st
from pathlib import Path
import os

# Page configuration - MUST be first Streamlit command
st.set_page_config(
    page_title="Nikkang KK - EPL Predictions",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for professional styling
st.markdown("""
<style>
    /* Main header styling */
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
    
    .main-header p {
        color: #f0f0f0;
        font-size: 1.2rem;
        margin: 0.5rem 0 0 0;
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #f8f9fa 0%, #e9ecef 100%);
    }
    
    .sidebar-logo-container {
        text-align: center;
        padding: 1rem 0;
        margin-bottom: 1rem;
        background: white;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
    
    /* Navigation styling */
    .nav-link {
        padding: 0.5rem 1rem;
        margin: 0.25rem 0;
        border-radius: 5px;
        transition: all 0.3s;
    }
    
    .nav-link:hover {
        background-color: #667eea;
        color: white;
    }
    
    /* Stats cards */
    .stats-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        margin: 1rem 0;
        border-left: 4px solid #667eea;
    }
    
    /* Footer */
    .footer {
        text-align: center;
        padding: 2rem 0 1rem 0;
        color: #6c757d;
        font-size: 0.9rem;
        border-top: 1px solid #dee2e6;
        margin-top: 3rem;
    }
    
    /* Logo responsive sizing */
    .logo-main {
        max-width: 300px;
        width: 100%;
        height: auto;
        margin: 1rem auto;
        display: block;
    }
    
    .logo-sidebar {
        max-width: 200px;
        width: 100%;
        height: auto;
        margin: 0 auto;
        display: block;
    }
</style>
""", unsafe_allow_html=True)

def check_logo_exists():
    """Check if logo file exists in project folder"""
    logo_path = Path("nikkang_logo.png")
    return logo_path.exists()

def display_logo_sidebar():
    """Display logo in sidebar with attractive styling"""
    if check_logo_exists():
        st.sidebar.markdown('<div class="sidebar-logo-container">', unsafe_allow_html=True)
        st.sidebar.image("nikkang_logo.png", use_container_width=True)
        st.sidebar.markdown('</div>', unsafe_allow_html=True)
    else:
        st.sidebar.markdown("""
        <div class="sidebar-logo-container">
            <h2 style="color: #667eea; margin: 0;">⚽ NIKKANG KK</h2>
            <p style="color: #6c757d; font-size: 0.9rem; margin: 0.5rem 0 0 0;">EPL Prediction League</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.sidebar.markdown("---")

def display_logo_main():
    """Display logo in main page with attractive header"""
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        if check_logo_exists():
            st.image("nikkang_logo.png", use_container_width=True)
        else:
            st.markdown("""
            <div style="text-align: center; padding: 2rem 0;">
                <h1 style="color: #667eea; font-size: 3rem; margin: 0;">⚽ NIKKANG KK</h1>
                <p style="color: #6c757d; font-size: 1.2rem; margin: 0.5rem 0 0 0;">EPL Prediction League</p>
            </div>
            """, unsafe_allow_html=True)

def main():
    """Main application entry point"""
    
    # Display sidebar logo at the very top - BEFORE any other content
    display_logo_sidebar()
    
    # Sidebar navigation
    st.sidebar.title("🎯 Navigation")
    st.sidebar.info("Select a page from the sidebar to get started!")
    
    st.sidebar.markdown("---")
    
    # Quick stats in sidebar
    st.sidebar.markdown("### 📊 Quick Stats")
    
    try:
        from utils.data_manager import DataManager
        dm = DataManager()
        
        participants = dm.load_participants()
        matches = dm.load_matches()
        
        st.sidebar.metric("👥 Participants", len(participants))
        st.sidebar.metric("⚽ Matches", len(matches))
        
        # Show current week
        if matches:
            current_week = max([m.get('week', 0) for m in matches])
            st.sidebar.metric("📅 Current Week", f"Week {current_week}")
    except:
        st.sidebar.info("No data available yet")
    
    st.sidebar.markdown("---")
    
    # Admin access
    st.sidebar.markdown("### 🔐 Admin Access")
    if st.sidebar.button("🛠️ Admin Panel", use_container_width=True):
        st.switch_page("pages/6_admin.py")
    
    st.sidebar.markdown("---")
    
    # Help section
    with st.sidebar.expander("❓ Need Help?"):
        st.markdown("""
        **Quick Guide:**
        - 📝 Register to get your unique link
        - 🎯 Make predictions for 10 matches/week
        - ⭐ Choose your Game of the Week
        - 📊 Check leaderboard for rankings
        - 🏆 Win with exact scores!
        
        **Scoring:**
        - Exact Score: 6 points
        - Correct Result: 3 points
        - GOTW doubles your points
        - Week 38 doubles all points
        """)
    
    # Footer in sidebar
    st.sidebar.markdown("---")
    st.sidebar.markdown("""
    <div style="text-align: center; color: #6c757d; font-size: 0.8rem;">
        <p>Nikkang KK EPL Prediction League</p>
        <p>Season 2025-26</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Main page content
    display_logo_main()
    
    st.markdown('<div class="main-header">', unsafe_allow_html=True)
    st.markdown('<h1>⚽ Welcome to Nikkang KK EPL Prediction League</h1>', unsafe_allow_html=True)
    st.markdown('<p>Predict, Compete, Win! Season 2025-26</p>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Welcome message
    st.markdown("""
    ### 🎯 Welcome to the Premier League Prediction Competition!
    
    Test your football knowledge and compete with friends to predict Premier League match results.
    Will you become the ultimate EPL prediction champion?
    """)
    
    # Feature cards
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="stats-card">
            <h3>📝 Easy Registration</h3>
            <p>Get your unique prediction link and start competing in minutes.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="stats-card">
            <h3>🎯 Weekly Predictions</h3>
            <p>Predict 10 matches each week. Choose your Game of the Week for bonus points!</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="stats-card">
            <h3>🏆 Live Leaderboard</h3>
            <p>Track your ranking, see weekly highlights, and compete for the championship!</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # How it works
    st.markdown("### 📖 How It Works")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **🎮 Getting Started:**
        1. **Register** - Get your unique prediction link
        2. **Predict** - Submit scores for 10 matches each week
        3. **GOTW** - Choose your Game of the Week
        4. **Track** - Watch your points accumulate
        5. **Win** - Top the leaderboard!
        """)
    
    with col2:
        st.markdown("""
        **⚡ Scoring System:**
        - **6 points** for exact score (KK)
        - **3 points** for correct result
        - **GOTW Bonus Bonanza** (10/5)
        - **4 Stages** throughout the season
        - **KK Champions** - Most Kemut Keliling wins!
        """)
    
    st.markdown("---")
    
    # Current season info
    st.markdown("### 📅 Season 2025-26 Information")
    
    season_col1, season_col2, season_col3, season_col4 = st.columns(4)
    
    with season_col1:
        st.metric("🗓️ Season", "2025-26")
    
    with season_col2:
        st.metric("🏟️ Total Weeks", "38")
    
    with season_col3:
        st.metric("⚽ Matches/Week", "10")
    
    with season_col4:
        st.metric("🏆 Competition", "Premier League")
    
    st.markdown("---")
    
    # Call to action
    st.markdown("### 🚀 Ready to Start?")
    
    action_col1, action_col2, action_col3 = st.columns(3)
    
    with action_col1:
        if st.button("📝 Register Now", use_container_width=True, type="primary"):
            st.switch_page("pages/2_register.py")
    
    with action_col2:
        if st.button("🎯 Make Predictions", use_container_width=True):
            st.switch_page("pages/3_predictions.py")
    
    with action_col3:
        if st.button("📊 View Leaderboard", use_container_width=True):
            st.switch_page("pages/5_leaderboard.py")
    
    # Footer
    st.markdown("""
    <div class="footer">
        <p><strong>Nikkang KK EPL Prediction League</strong> | Season 2025-26</p>
        <p>Powered by Streamlit | Football-Data.org API</p>
        <p style="font-size: 0.8rem; margin-top: 0.5rem;">
            © 2025 Nikkang KK. All rights reserved.
        </p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()

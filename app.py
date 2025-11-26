"""
Nikkang KK EPL Prediction Competition
Main application entry point
"""

import streamlit as st
from pathlib import Path

st.set_page_config(
    page_title="Nikkang KK - EPL Predictions",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
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
    }
    
    .main-header p {
        color: #f0f0f0;
        font-size: 1.2rem;
        margin: 0.5rem 0 0 0;
    }
    
    .stats-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        margin: 1rem 0;
        border-left: 4px solid #667eea;
    }
    
    .footer {
        text-align: center;
        padding: 2rem 0 1rem 0;
        color: #6c757d;
        font-size: 0.9rem;
        border-top: 1px solid #dee2e6;
        margin-top: 3rem;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar logo
if Path("nikkang_logo.png").exists():
    st.sidebar.image("nikkang_logo.png", use_container_width=True)
    st.sidebar.markdown("---")

# Sidebar info
st.sidebar.markdown("### 📖 Scoring System")
st.sidebar.markdown("""
**Normal Match:**
- Exact Score: **5 pts**
- Correct Result: **3 pts**

**Game of the Week:**
- Exact Score: **10 pts**
- Correct Result: **5 pts**

**KK** = Kemut Keliling
""")

st.sidebar.markdown("---")
st.sidebar.markdown("### 📅 Stages")
st.sidebar.markdown("""
- Stage 1: Week 1-10
- Stage 2: Week 11-20
- Stage 3: Week 21-30
- Stage 4: Week 31-38
""")

st.sidebar.markdown("---")
st.sidebar.caption("Nikkang KK | Season 2025-26")

# Main content - Logo
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    if Path("nikkang_logo.png").exists():
        st.image("nikkang_logo.png", use_container_width=True)

# Header
st.markdown('<div class="main-header">', unsafe_allow_html=True)
st.markdown('<h1>⚽ Welcome to Nikkang KK EPL Prediction League</h1>', unsafe_allow_html=True)
st.markdown('<p>Predict, Compete, Win! Season 2025-26</p>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

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
        <p>Track your ranking by stage and see the KK Champions!</p>
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
    4. **Track** - Watch your points accumulate by stage
    5. **Win** - Top the leaderboard!
    """)

with col2:
    st.markdown("""
    **⚡ Scoring System:**
    - **5 points** for exact score (KK)
    - **3 points** for correct result
    - **GOTW doubles** your points (10/5)
    - **4 Stages** throughout the season
    - **KK Champions** - Most Kemut Keliling wins!
    """)

st.markdown("---")

# Season info
st.markdown("### 📅 Season 2025-26 Stages")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("✅ Stage 1", "Week 1-10", "Completed")

with col2:
    st.metric("🔴 Stage 2", "Week 11-20", "Current")

with col3:
    st.metric("⏳ Stage 3", "Week 21-30", "Upcoming")

with col4:
    st.metric("⏳ Stage 4", "Week 31-38", "Upcoming")

st.markdown("---")

# Navigation buttons
st.markdown("### 🚀 Quick Navigation")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("📝 Register Now", use_container_width=True, type="primary"):
        st.switch_page("pages/2_📝_Register.py")

with col2:
    if st.button("🎯 Make Predictions", use_container_width=True):
        st.switch_page("pages/3_🎯_Predictions.py")

with col3:
    if st.button("🏆 View Leaderboard", use_container_width=True):
        st.switch_page("pages/5_🏆_Leaderboard.py")

# Footer
st.markdown("""
<div class="footer">
    <p><strong>Nikkang KK EPL Prediction League</strong> | Season 2025-26</p>
    <p>Powered by Streamlit | Football-Data.org API</p>
    <p style="font-size: 0.8rem;">© 2025 Nikkang KK. All rights reserved.</p>
</div>
""", unsafe_allow_html=True)

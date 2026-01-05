"""
Home Page - Nikkang KK EPL Prediction Competition
Clean version with proper Competition Structure display
"""

import streamlit as st
from pathlib import Path
import sys

# Add utils to path
sys.path.append(str(Path(__file__).parent.parent))

# Page config
st.set_page_config(
    page_title="Home - Nikkang KK EPL",
    page_icon="⚽",
    layout="wide"
)

# Import branding
try:
    from utils.branding import inject_custom_css
    inject_custom_css()
except:
    pass

# Logo
if Path("nikkang_logo.png").exists():
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.image("nikkang_logo.png", use_container_width=True)

# Header
st.markdown("""
<div style="text-align: center; padding: 2rem 0;">
    <h1 style="color: #2E7D32; font-size: 3rem; margin: 0;">⚽ Nikkang KK</h1>
    <h2 style="color: #667eea; font-size: 2rem; margin: 0.5rem 0;">EPL Prediction Competition 2025/26</h2>
    <p style="color: #6c757d; font-size: 1.2rem; margin: 1rem 0;">
        Predict. Compete. Win.
    </p>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# Welcome message
st.markdown("""
<div style="text-align: center; padding: 1.5rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 10px; color: white;">
    <h3>🎉 Welcome to the Premier League Prediction League!</h3>
    <p style="font-size: 1.1rem;">Make your predictions each week and compete with colleagues for glory!</p>
</div>
""", unsafe_allow_html=True)

st.markdown("")

# Quick action buttons
st.markdown("### ⚡ Quick Actions")

col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("🎯 Make Predictions", use_container_width=True, type="primary"):
        st.switch_page("pages/3_Predictions.py")

with col2:
    if st.button("📊 View Leaderboard", use_container_width=True):
        st.switch_page("pages/5_Leaderboard.py")

with col3:
    if st.button("📋 Prediction Matrix", use_container_width=True):
        st.switch_page("pages/4_Prediction_Matrix.py")

with col4:
    if st.button("📝 Register", use_container_width=True):
        st.switch_page("pages/2_Register.py")

st.markdown("---")

# How it works
st.markdown("### 📖 How It Works")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div style="background: #E8F5E9; padding: 1.5rem; border-radius: 10px; text-align: center; height: 200px; display: flex; flex-direction: column; justify-content: center;">
        <h3 style="color: #2E7D32;">1️⃣ Register</h3>
        <p style="color: #1B5E20;">Sign up with your details to join the competition</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div style="background: #E3F2FD; padding: 1.5rem; border-radius: 10px; text-align: center; height: 200px; display: flex; flex-direction: column; justify-content: center;">
        <h3 style="color: #1976D2;">2️⃣ Predict</h3>
        <p style="color: #0D47A1;">Submit your score predictions for each gameweek</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div style="background: #FFF3E0; padding: 1.5rem; border-radius: 10px; text-align: center; height: 200px; display: flex; flex-direction: column; justify-content: center;">
        <h3 style="color: #F57C00;">3️⃣ Win</h3>
        <p style="color: #E65100;">Earn points and climb the leaderboard!</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("")

# Scoring rules
st.markdown("### 🏆 Scoring System")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    <div style="background: white; padding: 1.5rem; border-radius: 10px; border: 2px solid #E0E0E0;">
        <h4 style="color: #2E7D32; margin-top: 0;">Regular Matches</h4>
        <ul style="list-style: none; padding: 0;">
            <li style="padding: 0.5rem 0; font-size: 1.1rem;">✅ <strong>Exact Score (KK):</strong> 6 points</li>
            <li style="padding: 0.5rem 0; font-size: 1.1rem;">🎯 <strong>Correct Result:</strong> 3 points</li>
            <li style="padding: 0.5rem 0; font-size: 1.1rem;">❌ <strong>Wrong:</strong> 0 points</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div style="background: white; padding: 1.5rem; border-radius: 10px; border: 2px solid #FFA000;">
        <h4 style="color: #F57C00; margin-top: 0;">Game of the Week (⭐)</h4>
        <ul style="list-style: none; padding: 0;">
            <li style="padding: 0.5rem 0; font-size: 1.1rem;">✅ <strong>Exact Score (KK):</strong> 10 points</li>
            <li style="padding: 0.5rem 0; font-size: 1.1rem;">🎯 <strong>Correct Result:</strong> 5 points</li>
            <li style="padding: 0.5rem 0; font-size: 1.1rem;">❌ <strong>Wrong:</strong> 0 points</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

st.info("💡 **Note:** Week 38 (final gameweek) also has double points like GOTW!")

st.markdown("---")

# Competition structure using Streamlit columns
st.markdown("### 📅 Competition Structure")
st.markdown("The season is divided into **4 stages** with prizes for each:")
st.markdown("")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown("""
    <div style="background: #E8F5E9; padding: 1.5rem; border-radius: 10px; text-align: center; height: 120px; display: flex; flex-direction: column; justify-content: center;">
        <div style="color: #2E7D32; font-size: 1.3rem; font-weight: bold; margin-bottom: 0.5rem;">Stage 1</div>
        <div style="color: #1B5E20; font-size: 1rem;">Weeks 1-10</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div style="background: #E3F2FD; padding: 1.5rem; border-radius: 10px; text-align: center; height: 120px; display: flex; flex-direction: column; justify-content: center;">
        <div style="color: #1976D2; font-size: 1.3rem; font-weight: bold; margin-bottom: 0.5rem;">Stage 2</div>
        <div style="color: #0D47A1; font-size: 1rem;">Weeks 11-20</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div style="background: #FFF3E0; padding: 1.5rem; border-radius: 10px; text-align: center; height: 120px; display: flex; flex-direction: column; justify-content: center;">
        <div style="color: #F57C00; font-size: 1.3rem; font-weight: bold; margin-bottom: 0.5rem;">Stage 3</div>
        <div style="color: #E65100; font-size: 1rem;">Weeks 21-30</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown("""
    <div style="background: #FCE4EC; padding: 1.5rem; border-radius: 10px; text-align: center; height: 120px; display: flex; flex-direction: column; justify-content: center;">
        <div style="color: #C2185B; font-size: 1.3rem; font-weight: bold; margin-bottom: 0.5rem;">Stage 4</div>
        <div style="color: #880E4F; font-size: 1rem;">Weeks 31-38</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("")
st.info("🏆 **Plus:** Overall Season Champion!")

st.markdown("---")

# Important info
st.markdown("### ⚠️ Important Information")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    <div style="background: #FFF3E0; padding: 1.5rem; border-radius: 10px; border-left: 4px solid #F57C00;">
        <h4 style="color: #E65100; margin-top: 0;">⏰ Deadlines</h4>
        <ul>
            <li>Predictions close at <strong>kickoff time</strong></li>
            <li>Late submissions <strong>not accepted</strong></li>
            <li>Make predictions <strong>early</strong>!</li>
            <li>Check lock status before deadline</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div style="background: #E3F2FD; padding: 1.5rem; border-radius: 10px; border-left: 4px solid #1976D2;">
        <h4 style="color: #0D47A1; margin-top: 0;">💡 Getting Help</h4>
        <ul>
            <li>Check <strong>Prediction Matrix</strong> to see others' picks</li>
            <li>View <strong>Leaderboard</strong> for standings</li>
            <li>Contact <strong>admin</strong> for issues</li>
            <li>Use <strong>Forgot Password</strong> if needed</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# Features
st.markdown("### ✨ Platform Features")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown("""
    <div style="text-align: center; padding: 1.5rem; background: white; border-radius: 10px; border: 2px solid #E0E0E0; height: 180px;">
        <div style="font-size: 3rem;">📱</div>
        <h4 style="color: #2E7D32; margin: 0.5rem 0;">Mobile Friendly</h4>
        <p style="color: #6c757d;">Predict on the go</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div style="text-align: center; padding: 1.5rem; background: white; border-radius: 10px; border: 2px solid #E0E0E0; height: 180px;">
        <div style="font-size: 3rem;">🔔</div>
        <h4 style="color: #1976D2; margin: 0.5rem 0;">Notifications</h4>
        <p style="color: #6c757d;">Stay updated</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div style="text-align: center; padding: 1.5rem; background: white; border-radius: 10px; border: 2px solid #E0E0E0; height: 180px;">
        <div style="font-size: 3rem;">📊</div>
        <h4 style="color: #F57C00; margin: 0.5rem 0;">Live Stats</h4>
        <p style="color: #6c757d;">Track progress</p>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown("""
    <div style="text-align: center; padding: 1.5rem; background: white; border-radius: 10px; border: 2px solid #E0E0E0; height: 180px;">
        <div style="font-size: 3rem;">🏆</div>
        <h4 style="color: #C2185B; margin: 0.5rem 0;">Prizes</h4>
        <p style="color: #6c757d;">Win rewards!</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# Call to action
st.markdown("""
<div style="text-align: center; padding: 2.5rem; background: linear-gradient(135deg, #2E7D32 0%, #1B5E20 100%); border-radius: 15px; color: white; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
    <h2 style="font-size: 2rem; margin-bottom: 1rem;">🎯 Ready to Start Predicting?</h2>
    <p style="font-size: 1.2rem; margin: 1rem 0;">Join your colleagues in the ultimate EPL prediction challenge!</p>
</div>
""", unsafe_allow_html=True)

st.markdown("")

col1, col2, col3 = st.columns([1, 1, 1])

with col1:
    if st.button("📝 Register Now", use_container_width=True, type="primary", key="cta_register"):
        st.switch_page("pages/2_Register.py")

with col2:
    if st.button("🎯 Make Predictions", use_container_width=True, type="primary", key="cta_predict"):
        st.switch_page("pages/3_Predictions.py")

with col3:
    if st.button("📊 View Leaderboard", use_container_width=True, key="cta_leaderboard"):
        st.switch_page("pages/5_Leaderboard.py")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; font-size: 0.9rem; padding: 2rem;'>
    <p style="font-size: 1.1rem; margin-bottom: 0.5rem;"><strong>Nikkang KK EPL Prediction Competition 2025/26</strong></p>
    <p style="color: #2E7D32; font-size: 1rem;">May the best predictor win! ⚽🏆</p>
</div>
""", unsafe_allow_html=True)

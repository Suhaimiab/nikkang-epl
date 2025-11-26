"""
Nikkang KK EPL Prediction Competition - Home Page
Enhanced with branding, stage system integration, and attractive layout
"""

import streamlit as st
from pathlib import Path
import json
import sys

sys.path.append(str(Path(__file__).parent.parent))

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
    
    .leader-card {
        background: linear-gradient(135deg, #fff9e6 0%, #ffffff 100%);
        border: 2px solid #ffd700;
        border-radius: 12px;
        padding: 1.5rem;
        text-align: center;
        margin: 0.5rem;
    }
    
    .kk-card {
        background: linear-gradient(135deg, #e8f5e9 0%, #ffffff 100%);
        border: 2px solid #28a745;
        border-radius: 12px;
        padding: 1.5rem;
        text-align: center;
        margin: 0.5rem;
    }
    
    .bottom-card {
        background: linear-gradient(135deg, #ffebee 0%, #ffffff 100%);
        border: 2px solid #dc3545;
        border-radius: 12px;
        padding: 1.5rem;
        text-align: center;
        margin: 0.5rem;
    }
    
    .stage-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-weight: bold;
        font-size: 0.85rem;
        margin: 0.25rem;
    }
    .stage-locked { background: #d4edda; color: #155724; }
    .stage-current { background: #fff3cd; color: #856404; }
</style>
""", unsafe_allow_html=True)

# Sidebar - Logo and Info
if Path("nikkang_logo.png").exists():
    st.sidebar.image("nikkang_logo.png", use_container_width=True)
st.sidebar.markdown("---")

# Scoring guide
with st.sidebar.expander("📖 Scoring System"):
    st.markdown("""
    ### Points System:
    
    | Prediction | Normal Match | Game of the Week |
    |------------|--------------|------------------|
    | **Exact Score (KK)** | 5 points | 10 points |
    | **Correct Result** | 3 points | 5 points |
    | **Wrong** | 0 points | 0 points |
    
    **KK = Kemut Keliling** (Exact Score Prediction)
    
    ### Stages:
    - **Stage 1**: Week 1-10 ✅ Completed
    - **Stage 2**: Week 11-20 🔴 Current
    - **Stage 3**: Week 21-30 ⏳ Upcoming
    - **Stage 4**: Week 31-38 ⏳ Upcoming
    """)

st.sidebar.markdown("---")
st.sidebar.caption("Nikkang KK | Season 2025-26")

# Load data functions
def load_stage_scores():
    score_file = Path("nikkang_data/stage_scores.json")
    if score_file.exists():
        try:
            with open(score_file, 'r') as f:
                return json.load(f)
        except:
            pass
    return {}

def get_stage_status():
    """Auto-detect stage status based on locked stages and match results"""
    stage_scores = load_stage_scores()
    completed = set()
    
    # Check locked stages
    for stage_num in [1, 2, 3, 4]:
        if stage_scores.get(f"stage_{stage_num}_locked", False):
            completed.add(stage_num)
    
    # Auto-detect based on results
    try:
        from utils.data_manager import DataManager
        dm = DataManager()
        results = dm.load_results()
        all_matches = dm.get_all_matches()
        
        STAGE_WEEKS = {
            1: list(range(1, 11)),
            2: list(range(11, 21)),
            3: list(range(21, 31)),
            4: list(range(31, 39)),
        }
        
        for stage_num, weeks in STAGE_WEEKS.items():
            if stage_num in completed:
                continue
            stage_matches = [m for m in all_matches if m.get('week', 0) in weeks]
            if stage_matches:
                all_have_results = all(m.get('id') in results for m in stage_matches)
                if all_have_results:
                    completed.add(stage_num)
        
        # Determine current stage
        max_week = 0
        for match in all_matches:
            if match.get('id') in results:
                week = match.get('week', 0)
                if week > max_week:
                    max_week = week
        
        if max_week >= 31:
            current = 4
        elif max_week >= 21:
            current = 3
        elif max_week >= 11:
            current = 2
        else:
            current = 1
        
        # Adjust current if stage is completed
        while current in completed and current < 4:
            current += 1
            
    except:
        current = 1
    
    return completed, current

# Header
st.markdown('<div class="main-header">', unsafe_allow_html=True)
st.markdown('<h1>⚽ Welcome to Nikkang KK EPL Prediction League</h1>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

st.markdown("""
### 🎯 Premier League Prediction Competition

Test your football knowledge and compete with friends to predict Premier League match results.
Will you become the ultimate EPL prediction champion?
""")

# Season Progress
completed_stages, current_stage = get_stage_status()

st.markdown("### 📅 Season Progress")

col1, col2, col3, col4 = st.columns(4)

stages_display = [
    (1, "Stage 1", "Week 1-10"),
    (2, "Stage 2", "Week 11-20"),
    (3, "Stage 3", "Week 21-30"),
    (4, "Stage 4", "Week 31-38"),
]

cols = [col1, col2, col3, col4]

for i, (stage_num, name, weeks) in enumerate(stages_display):
    with cols[i]:
        if stage_num in completed_stages:
            st.markdown(f'<span class="stage-badge stage-locked">✅ {name} Complete</span>', unsafe_allow_html=True)
        elif stage_num == current_stage:
            st.markdown(f'<span class="stage-badge stage-current">🔴 {name} Current</span>', unsafe_allow_html=True)
        else:
            st.markdown(f'<span class="stage-badge">⏳ {name}</span>', unsafe_allow_html=True)

st.markdown("---")

# Get leaderboard data
def get_combined_leaderboard():
    """Get combined leaderboard from stage scores"""
    try:
        from utils.data_manager import DataManager
        dm = DataManager()
        
        stage_scores = load_stage_scores()
        participants = dm.get_all_participants()
        
        STAGES = {
            1: {"weeks": list(range(1, 11)), "key": "stage_1"},
            2: {"weeks": list(range(11, 21)), "key": "stage_2"},
            3: {"weeks": list(range(21, 31)), "key": "stage_3"},
            4: {"weeks": list(range(31, 39)), "key": "stage_4"},
        }
        
        leaderboard = []
        
        for p in participants:
            uid = p.get('id', '')
            total_points = 0
            total_kk = 0
            correct_results = 0
            weeks_played = 0
            
            for stage_num in [1, 2, 3, 4]:
                stage_info = STAGES[stage_num]
                stage_key = stage_info['key']
                is_locked = stage_scores.get(f"{stage_key}_locked", False)
                
                if is_locked:
                    # Use manual scores
                    manual = stage_scores.get(stage_key, {}).get(uid, {})
                    total_points += manual.get('points', 0)
                    total_kk += manual.get('kk_count', 0)
                else:
                    # Calculate from predictions
                    predictions = dm.load_predictions()
                    results = dm.load_results()
                    all_matches = dm.get_all_matches()
                    user_preds = predictions.get(uid, {})
                    
                    for match in all_matches:
                        mid = match.get('id', '')
                        week = match.get('week', 0)
                        
                        if week not in stage_info['weeks']:
                            continue
                        
                        if mid in results and mid in user_preds:
                            result = results[mid]
                            pred = user_preds[mid]
                            is_gotw = match.get('gotw', False)
                            
                            points = dm.calculate_points(
                                pred.get('home_score', -1), pred.get('away_score', -1),
                                result.get('home_score', -2), result.get('away_score', -2), is_gotw
                            )
                            total_points += points
                            
                            # Check for exact score (KK)
                            if pred.get('home_score') == result.get('home_score') and pred.get('away_score') == result.get('away_score'):
                                total_kk += 1
                            
                            # Check for correct result
                            if points > 0:
                                correct_results += 1
                            
                            weeks_played = max(weeks_played, week)
            
            leaderboard.append({
                'id': uid,
                'name': p.get('name', 'Unknown'),
                'team': p.get('team', '-'),
                'points': total_points,
                'kk_count': total_kk,
                'correct_results': correct_results,
                'weeks_played': weeks_played
            })
        
        # Sort by points, then KK
        leaderboard.sort(key=lambda x: (-x['points'], -x['kk_count']))
        
        return leaderboard
    except Exception as e:
        return []

leaderboard = get_combined_leaderboard()

if leaderboard:
    # Top 3 Leaders
    st.markdown("### 🏆 Season Leaders - Top 3")
    
    top_3 = leaderboard[:3]
    medals = ["🥇", "🥈", "🥉"]
    
    cols = st.columns(3)
    for idx, (leader, medal) in enumerate(zip(top_3, medals)):
        with cols[idx]:
            st.markdown(f"""
            <div class="leader-card">
                <h2 style="margin: 0;">{medal}</h2>
                <h3 style="color: #667eea; margin: 0.5rem 0;">{leader['name']}</h3>
                <p style="font-size: 2rem; font-weight: bold; margin: 0.5rem 0;">{leader['points']} pts</p>
                <p style="color: #6c757d; margin: 0;">
                    🎯 {leader['kk_count']} KK | ✅ {leader['correct_results']} correct<br>
                    📅 {leader['weeks_played']} weeks | ⚽ {leader['team']}
                </p>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Most Exact Score Predictions (KK Champions)
    st.markdown("### 🎯 Most Exact Score Predictions (KK Champions)")
    st.caption("The ultimate prediction masters!")
    
    kk_leaders = sorted(leaderboard, key=lambda x: (-x['kk_count'], -x['points']))[:3]
    
    cols = st.columns(3)
    for idx, leader in enumerate(kk_leaders):
        with cols[idx]:
            medal = ["🥇", "🥈", "🥉"][idx]
            st.markdown(f"""
            <div class="kk-card">
                <h2 style="margin: 0;">{medal}</h2>
                <h3 style="color: #28a745; margin: 0.5rem 0;">{leader['name']}</h3>
                <p style="font-size: 2rem; font-weight: bold; margin: 0.5rem 0;">{leader['kk_count']} KK</p>
                <p style="color: #6c757d; margin: 0;">
                    🏆 {leader['points']} pts | ✅ {leader['correct_results']} correct<br>
                    📅 {leader['weeks_played']} weeks | ⚽ {leader['team']}
                </p>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Bottom 3 - Room for Improvement
    if len(leaderboard) > 3:
        st.markdown("### 📉 Bottom 3 - Room for Improvement!")
        st.caption("Keep trying, there's still time to climb the leaderboard! 💪")
        
        bottom_3 = leaderboard[-3:]
        
        cols = st.columns(3)
        for idx, participant in enumerate(bottom_3):
            with cols[idx]:
                st.markdown(f"""
                <div class="bottom-card">
                    <h3 style="color: #dc3545; margin: 0.5rem 0;">{participant['name']}</h3>
                    <p style="font-size: 1.5rem; font-weight: bold; margin: 0.5rem 0;">{participant['points']} pts</p>
                    <p style="color: #6c757d; margin: 0;">
                        🎯 {participant['kk_count']} KK | ✅ {participant['correct_results']} correct<br>
                        📅 {participant['weeks_played']} weeks | ⚽ {participant['team']}
                    </p>
                </div>
                """, unsafe_allow_html=True)

st.markdown("---")

# Quick Actions
st.markdown("### 🚀 Quick Actions")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("📝 Register Now", use_container_width=True, type="primary"):
        st.switch_page("pages/2_Register.py")

with col2:
    if st.button("🎯 Make Predictions", use_container_width=True):
        st.switch_page("pages/3_Predictions.py")

with col3:
    if st.button("🏆 View Leaderboard", use_container_width=True):
        st.switch_page("pages/5_Leaderboard.py")

st.markdown("---")

# Feature cards
st.markdown("### 🎮 How It Works")

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
        <p>Predict 10 matches each week. GOTW matches worth double points!</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="stats-card">
        <h3>🏆 Live Leaderboard</h3>
        <p>Track your ranking by stage and compete for KK Champion title!</p>
    </div>
    """, unsafe_allow_html=True)

# Competition overview
try:
    from utils.data_manager import DataManager
    dm = DataManager()
    
    participants = dm.get_all_participants()
    all_matches = dm.get_all_matches()
    results = dm.load_results()
    
    st.markdown("---")
    st.markdown("### 📊 Competition Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Participants", len(participants))
    
    with col2:
        st.metric("Total Matches", len(all_matches))
    
    with col3:
        st.metric("Results Entered", len(results))
    
    with col4:
        st.metric("Current Stage", f"Stage {current_stage}")
except:
    pass

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #6c757d; padding: 2rem 0;">
    <p><strong>Nikkang KK EPL Prediction League</strong> | Season 2025-26</p>
    <p style="font-size: 0.9rem;">Powered by Streamlit | Football-Data.org API</p>
</div>
""", unsafe_allow_html=True)

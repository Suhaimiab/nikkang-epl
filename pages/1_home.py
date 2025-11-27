"""
Nikkang KK EPL Prediction Competition - Home Page
Enhanced with branding, stage system integration, and attractive layout
"""

import streamlit as st
from pathlib import Path
import json

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
    
    .sidebar-logo-container {
        text-align: center;
        padding: 1rem 0;
        margin-bottom: 1rem;
        background: white;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
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

# Stage scores file
STAGE_SCORES_FILE = Path("nikkang_data/stage_scores.json")

def load_stage_scores():
    if STAGE_SCORES_FILE.exists():
        try:
            with open(STAGE_SCORES_FILE, 'r') as f:
                return json.load(f)
        except:
            pass
    return {}

def get_leaderboard_data():
    """Get full leaderboard with stage data"""
    try:
        from utils.data_manager import DataManager
        dm = DataManager()
        
        stage_scores = load_stage_scores()
        participants = dm.get_all_participants()
        predictions = dm.load_predictions()
        results = dm.load_results()
        all_matches = dm.get_all_matches()
        
        STAGES = {
            1: list(range(1, 11)),
            2: list(range(11, 21)),
            3: list(range(21, 31)),
            4: list(range(31, 39)),
        }
        
        leaderboard = []
        
        for p in participants:
            uid = p.get('id', '')
            name = p.get('name', 'Unknown')
            team = p.get('team', '-')
            
            total_pts = 0
            total_kk = 0
            correct_results = 0
            weeks_played = set()
            
            for stage_num in [1, 2, 3, 4]:
                stage_key = f"stage_{stage_num}"
                is_locked = stage_scores.get(f"{stage_key}_locked", False)
                
                if is_locked:
                    # Use manual scores
                    manual = stage_scores.get(stage_key, {}).get(uid, {})
                    total_pts += manual.get('points', 0)
                    total_kk += manual.get('kk_count', 0)
                else:
                    # Calculate from predictions
                    user_preds = predictions.get(uid, {})
                    stage_weeks = STAGES[stage_num]
                    
                    for match in all_matches:
                        mid = match.get('id', '')
                        week = match.get('week', 0)
                        
                        if week not in stage_weeks:
                            continue
                        
                        if mid in results and mid in user_preds:
                            result = results[mid]
                            pred = user_preds[mid]
                            is_gotw = match.get('gotw', False)
                            
                            weeks_played.add(week)
                            
                            pts = dm.calculate_points(
                                pred.get('home_score', -1),
                                pred.get('away_score', -1),
                                result.get('home_score', -2),
                                result.get('away_score', -2),
                                is_gotw
                            )
                            total_pts += pts
                            
                            if (pred.get('home_score') == result.get('home_score') and
                                pred.get('away_score') == result.get('away_score')):
                                total_kk += 1
                            elif pts > 0:
                                correct_results += 1
            
            leaderboard.append({
                'id': uid,
                'name': name,
                'team': team,
                'points': total_pts,
                'kk_count': total_kk,
                'correct_results': correct_results,
                'weeks_played': len(weeks_played)
            })
        
        # Sort by points, then KK
        leaderboard.sort(key=lambda x: (-x['points'], -x['kk_count']))
        
        for i, e in enumerate(leaderboard, 1):
            e['rank'] = i
        
        return leaderboard
    
    except Exception as e:
        return []

def display_logo_sidebar():
    """Display logo in sidebar"""
    if Path("nikkang_logo.png").exists():
        st.sidebar.image("nikkang_logo.png", use_container_width=True)
        st.sidebar.markdown("---")
    
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

# Current stage info - AUTOMATED
stage_scores = load_stage_scores()

def get_stage_status():
    """Auto-detect stage status based on locked stages and match results"""
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
leaderboard = get_leaderboard_data()

if leaderboard:
    # Season Leaders - Top 3
    st.markdown("### 🏆 Season Leaders - Top 3")
    
    top_3 = leaderboard[:3]
    cols = st.columns(3)
    medals = ["🥇", "🥈", "🥉"]
    
    for i, p in enumerate(top_3):
        with cols[i]:
            st.markdown(f"""
            <div class="leader-card">
                <div style="font-size: 2.5rem;">{medals[i]}</div>
                <h3 style="margin: 0.5rem 0;">{p['name']}</h3>
                <div style="font-size: 2rem; font-weight: bold; color: #667eea;">{p['points']}</div>
                <div style="color: #6c757d;">points</div>
                <hr style="margin: 1rem 0;">
                <div>⚡ {p['kk_count']} exact scores</div>
                <div>✓ {p['correct_results']} correct results</div>
                <div>📅 {p['weeks_played']} weeks played</div>
                <div>⚽ {p.get('team', '-')}</div>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Most KK (Kemut Keliling)
    st.markdown("### 🎯 Most Exact Score Predictions (KK) - Season 2025/26")
    st.caption("The ultimate prediction masters!")
    
    # Sort by KK count
    kk_leaders = sorted(leaderboard, key=lambda x: (-x['kk_count'], -x['points']))[:3]
    
    cols = st.columns(3)
    
    for i, p in enumerate(kk_leaders):
        with cols[i]:
            st.markdown(f"""
            <div class="kk-card">
                <div style="font-size: 2rem;">{medals[i]}</div>
                <h3 style="margin: 0.5rem 0;">{p['name']}</h3>
                <div style="font-size: 2.5rem; font-weight: bold; color: #28a745;">{p['kk_count']}</div>
                <div style="color: #6c757d;">Exact Scores (KK)</div>
                <hr style="margin: 1rem 0;">
                <div style="color: #dc3545; font-weight: bold;">{p['points']} pts</div>
                <div>✓ {p['correct_results']} correct results</div>
                <div>📅 {p['weeks_played']} weeks</div>
                <div>⚽ {p.get('team', '-')}</div>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Bottom 3 (if more than 3 participants)
    if len(leaderboard) > 3:
        st.markdown("### 😅 Bottom 3 - Room for Improvement!")
        st.caption("Keep trying, there's still time!")
        
        bottom_3 = leaderboard[-3:]
        bottom_3.reverse()  # Show worst first
        
        cols = st.columns(3)
        bottom_icons = ["😰", "😓", "🙃"]
        
        for i, p in enumerate(bottom_3):
            with cols[i]:
                st.markdown(f"""
                <div class="bottom-card">
                    <div style="font-size: 2rem;">{bottom_icons[i]}</div>
                    <h3 style="margin: 0.5rem 0;">{p['name']}</h3>
                    <div style="font-size: 2rem; font-weight: bold; color: #dc3545;">{p['points']}</div>
                    <div style="color: #6c757d;">points</div>
                    <hr style="margin: 1rem 0;">
                    <div>⚡ {p['kk_count']} exact scores</div>
                    <div>✓ {p['correct_results']} correct results</div>
                    <div>📅 {p['weeks_played']} weeks</div>
                    <div>⚽ {p.get('team', '-')}</div>
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown("---")

else:
    st.info("Competition data will appear here once you start!")

# Feature showcase
st.markdown("### 🎮 Quick Actions")

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
        <p>Check rankings, stage scores, and KK Champions!</p>
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
    
    participants = dm.get_all_participants()
    all_matches = dm.get_all_matches()
    results = dm.load_results()
    
    stat_col1, stat_col2, stat_col3, stat_col4 = st.columns(4)
    
    with stat_col1:
        st.metric("👥 Total Participants", len(participants))
    
    with stat_col2:
        st.metric("⚽ Total Matches", len(all_matches))
    
    with stat_col3:
        st.metric("✅ Results Entered", len(results))
    
    with stat_col4:
        current_stage = 1
        if s1_locked:
            current_stage = 2
        if s2_locked:
            current_stage = 3
        st.metric("📅 Current Stage", f"Stage {current_stage}")

except Exception as e:
    st.info("Competition data will appear here once you start!")

st.markdown("---")

# Scoring guide
with st.expander("📖 Scoring System"):
    st.markdown("""
    ### Points System:
    
    | Prediction | Normal Match | GOTW Bonus Bonanza 🌟 |
    |------------|--------------|----------------------|
    | **Exact Score (KK)** | 6 points | 10 points |
    | **Correct Result** | 3 points | 5 points |
    | **Wrong** | 0 points | 0 points |
    
    **KK = Kemut Keliling** (Exact Score Prediction)
    
    **Week 38 FINALE:** All matches score GOTW Bonus Bonanza points!
    
    ### Stages:
    - **Stage 1**: Week 1-10
    - **Stage 2**: Week 11-20
    - **Stage 3**: Week 21-30
    - **Stage 4**: Week 31-38 (Finale!)
    """)

# Footer
st.markdown("""
<div style="text-align: center; padding: 2rem 0 1rem 0; color: #6c757d; font-size: 0.9rem; border-top: 1px solid #dee2e6; margin-top: 3rem;">
    <p><strong>Nikkang KK EPL Prediction League</strong> | Season 2025-26</p>
    <p>© 2025 Nikkang KK. All rights reserved.</p>
</div>
""", unsafe_allow_html=True)

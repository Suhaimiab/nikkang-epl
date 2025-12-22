"""
Nikkang KK EPL Prediction Competition - Home Page
Enhanced with latest season info, current gameweek, and round breakdown
"""

import streamlit as st
from pathlib import Path
import json
from datetime import datetime

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
    
    .weekly-champ {
        background: linear-gradient(135deg, #ffd700 0%, #ffed4a 100%);
        border-radius: 12px;
        padding: 1.5rem;
        text-align: center;
        margin: 1rem 0;
        box-shadow: 0 4px 15px rgba(255, 215, 0, 0.3);
    }
    
    .round-progress {
        background: white;
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .round-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-weight: bold;
        font-size: 0.85rem;
        margin: 0.25rem;
    }
    .round-locked { background: #d4edda; color: #155724; }
    .stage-current { background: #fff3cd; color: #856404; }
    .round-pending { background: #e9ecef; color: #6c757d; }
</style>
""", unsafe_allow_html=True)

# Round scores file
ROUND_SCORES_FILE = Path("nikkang_data/round_scores.json")

def load_round_scores():
    if ROUND_SCORES_FILE.exists():
        try:
            with open(ROUND_SCORES_FILE, 'r') as f:
                return json.load(f)
        except:
            pass
    return {}

def get_current_week_and_results():
    """Get current week number and latest week with results"""
    try:
        from utils.data_manager import DataManager
        dm = DataManager()
        results = dm.load_results()
        
        # Find latest week with results
        latest_week = 0
        weeks_with_results = set()
        
        for week_str, week_results in results.items():
            if week_str.isdigit():
                week_num = int(week_str)
                if isinstance(week_results, list) and len(week_results) > 0:
                    # Check if at least one result has actual scores
                    if any(r.get('home', -1) >= 0 for r in week_results if r):
                        weeks_with_results.add(week_num)
                        if week_num > latest_week:
                            latest_week = week_num
        
        # Current week is latest + 1 (or latest if no results yet)
        current_week = dm.get_current_week()
        
        return current_week, latest_week, len(weeks_with_results)
    except:
        return 1, 0, 0

def get_weekly_champion(week):
    """Get champion(s) for a specific week"""
    try:
        from utils.data_manager import DataManager
        dm = DataManager()
        
        participants = dm.get_all_participants()
        predictions_data = dm.load_predictions()
        results_data = dm.load_results()
        matches_data = dm.load_matches()
        
        week_str = str(week)
        week_fixtures = matches_data.get(week_str, [])
        week_results = results_data.get(week_str, [])
        
        if not week_fixtures or not week_results:
            return None, 0, 0
        
        scores = []
        
        for p in participants:
            uid = p.get('id', '')
            name = p.get('name', 'Unknown')
            
            user_week_preds = predictions_data.get(week_str, {}).get(uid, [])
            
            if not user_week_preds:
                continue
            
            total_pts = 0
            kk_count = 0
            
            for idx, fixture in enumerate(week_fixtures):
                if idx >= len(user_week_preds) or idx >= len(week_results):
                    continue
                
                pred = user_week_preds[idx]
                result = week_results[idx]
                
                if not pred or not result:
                    continue
                
                pred_home = pred.get('home', -1)
                pred_away = pred.get('away', -1)
                res_home = result.get('home', -1)
                res_away = result.get('away', -1)
                
                if pred_home < 0 or res_home < 0:
                    continue
                
                is_gotw = fixture.get('gotw', False)
                is_week38 = (week == 38)
                bonus = is_gotw or is_week38
                
                # Exact score
                if pred_home == res_home and pred_away == res_away:
                    total_pts += 10 if bonus else 6
                    kk_count += 1
                else:
                    # Check correct result
                    pred_outcome = 'H' if pred_home > pred_away else ('A' if pred_away > pred_home else 'D')
                    res_outcome = 'H' if res_home > res_away else ('A' if res_away > res_home else 'D')
                    
                    if pred_outcome == res_outcome:
                        total_pts += 5 if bonus else 3
            
            if total_pts > 0:
                scores.append({'name': name, 'points': total_pts, 'kk': kk_count})
        
        if not scores:
            return None, 0, 0
        
        # Sort by points, then KK
        scores.sort(key=lambda x: (-x['points'], -x['kk']))
        
        # Find champion(s) - joint if same points AND KK
        max_pts = scores[0]['points']
        max_kk = scores[0]['kk']
        champions = [s['name'] for s in scores if s['points'] == max_pts and s['kk'] == max_kk]
        
        return champions, max_pts, max_kk
    except:
        return None, 0, 0

def get_leaderboard_data():
    """Get full leaderboard with stage data"""
    try:
        from utils.data_manager import DataManager
        dm = DataManager()
        
        round_scores = load_round_scores()
        participants = dm.get_all_participants()
        predictions = dm.load_predictions()
        results = dm.load_results()
        matches = dm.load_matches()
        
        ROUNDS = {
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
            round_pts = {1: 0, 2: 0, 3: 0, 4: 0}
            round_kk = {1: 0, 2: 0, 3: 0, 4: 0}
            
            for round_num in [1, 2, 3, 4]:
                round_key = f"stage_{round_num}"
                is_locked = round_scores.get(f"{round_key}_locked", False)
                
                if is_locked:
                    # Use manual scores
                    manual = round_scores.get(round_key, {}).get(uid, {})
                    pts = manual.get('points', 0)
                    kk = manual.get('kk_count', 0)
                    total_pts += pts
                    total_kk += kk
                    round_pts[round_num] = pts
                    round_kk[round_num] = kk
                else:
                    # Calculate from predictions
                    round_weeks = ROUNDS[round_num]
                    
                    for week in round_weeks:
                        week_str = str(week)
                        week_fixtures = matches.get(week_str, [])
                        week_results = results.get(week_str, [])
                        user_preds = predictions.get(week_str, {}).get(uid, [])
                        
                        if not week_fixtures or not week_results or not user_preds:
                            continue
                        
                        weeks_played.add(week)
                        
                        for idx, fixture in enumerate(week_fixtures):
                            if idx >= len(user_preds) or idx >= len(week_results):
                                continue
                            
                            pred = user_preds[idx]
                            result = week_results[idx]
                            
                            if not pred or not result:
                                continue
                            
                            pred_home = pred.get('home', -1)
                            pred_away = pred.get('away', -1)
                            res_home = result.get('home', -1)
                            res_away = result.get('away', -1)
                            
                            if pred_home < 0 or res_home < 0:
                                continue
                            
                            is_gotw = fixture.get('gotw', False)
                            is_week38 = (week == 38)
                            bonus = is_gotw or is_week38
                            
                            # Exact score
                            if pred_home == res_home and pred_away == res_away:
                                pts = 10 if bonus else 6
                                total_pts += pts
                                total_kk += 1
                                round_pts[round_num] += pts
                                round_kk[round_num] += 1
                            else:
                                # Check correct result
                                pred_outcome = 'H' if pred_home > pred_away else ('A' if pred_away > pred_home else 'D')
                                res_outcome = 'H' if res_home > res_away else ('A' if res_away > res_home else 'D')
                                
                                if pred_outcome == res_outcome:
                                    pts = 5 if bonus else 3
                                    total_pts += pts
                                    round_pts[round_num] += pts
                                    correct_results += 1
            
            leaderboard.append({
                'id': uid,
                'name': name,
                'team': team,
                'points': total_pts,
                'kk_count': total_kk,
                'correct_results': correct_results,
                'weeks_played': len(weeks_played),
                's1_pts': round_pts[1], 's1_kk': round_kk[1],
                's2_pts': round_pts[2], 's2_kk': round_kk[2],
                's3_pts': round_pts[3], 's3_kk': round_kk[3],
                's4_pts': round_pts[4], 's4_kk': round_kk[4],
            })
        
        # Sort by points, then KK
        leaderboard.sort(key=lambda x: (-x['points'], -x['kk_count']))
        
        # Assign ranks with tiebreaker
        prev_pts, prev_kk, prev_rank = None, None, 0
        for i, e in enumerate(leaderboard, 1):
            if e['points'] == prev_pts and e['kk_count'] == prev_kk:
                e['rank'] = prev_rank
            else:
                e['rank'] = i
                prev_rank = i
            prev_pts = e['points']
            prev_kk = e['kk_count']
        
        return leaderboard
    
    except Exception as e:
        return []

def display_logo_sidebar():
    """Display logo in sidebar"""
    if Path("nikkang_logo.png").exists():
        st.sidebar.image("nikkang_logo.png", use_container_width=True)
        st.sidebar.markdown("---")
    
    # Add Guide link to sidebar
    st.sidebar.markdown("### 📚 Quick Links")
    if st.sidebar.button("📖 How to Play (Guide)", use_container_width=True, key="sidebar_guide"):
        st.switch_page("pages/16_Guide.py")
    if st.sidebar.button("🎯 Make Predictions", use_container_width=True, key="sidebar_predict"):
        st.switch_page("pages/3_predictions.py")
    if st.sidebar.button("📊 Leaderboard", use_container_width=True, key="sidebar_leaderboard"):
        st.switch_page("pages/5_leaderboard.py")
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
st.markdown('<h1>🏠 Nikkang KK EPL Prediction League</h1>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# New player guide banner
col_guide1, col_guide2, col_guide3 = st.columns([2, 3, 2])
with col_guide2:
    st.markdown("""
    <div style="background:linear-gradient(135deg,#e3f2fd 0%,#bbdefb 100%);border:1px solid #2196f3;border-radius:10px;padding:0.8rem;text-align:center;margin-bottom:1rem;">
        <span style="font-size:1rem;">🆕 <strong>New here?</strong> Learn how to play and win!</span>
    </div>
    """, unsafe_allow_html=True)
    if st.button("📖 View Guide - How to Play", use_container_width=True, type="primary", key="top_guide_btn"):
        st.switch_page("pages/16_Guide.py")

# Get current data
current_week, latest_week, weeks_completed = get_current_week_and_results()
round_scores = load_round_scores()

# Determine current stage
def get_current_round(week):
    if week <= 10:
        return 1
    elif week <= 20:
        return 2
    elif week <= 30:
        return 3
    else:
        return 4

current_round = get_current_round(current_week)

# =============================================================================
# CURRENT STATUS SECTION
# =============================================================================
st.markdown("### 📊 Season Status")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("📅 Current Week", f"Week {current_week}")

with col2:
    st.metric("✅ Weeks Completed", f"{weeks_completed} / 38")

with col3:
    st.metric("🎯 Current Stage", f"Stage {current_round}")

with col4:
    progress = round((weeks_completed / 38) * 100)
    st.metric("📈 Season Progress", f"{progress}%")

# =============================================================================
# LATEST GAMEWEEK CHAMPION
# =============================================================================
if latest_week > 0:
    champions, champ_pts, champ_kk = get_weekly_champion(latest_week)
    
    if champions:
        st.markdown("---")
        
        if len(champions) == 1:
            champ_text = champions[0]
            title = f"🏆 GAMEWEEK {latest_week} CHAMPION"
        else:
            champ_text = " & ".join(champions)
            title = f"🏆 GAMEWEEK {latest_week} JOINT CHAMPIONS"
        
        st.markdown(f"""
        <div class="weekly-champ">
            <div style="font-size: 0.9rem; color: #856404;">{title}</div>
            <div style="font-size: 2rem; font-weight: bold; color: #1a1a2e;">{champ_text}</div>
            <div style="font-size: 1.2rem; color: #856404; margin-top: 0.5rem;">
                {champ_pts} points | {champ_kk} exact scores (KK)
            </div>
        </div>
        """, unsafe_allow_html=True)

# =============================================================================
# STAGE PROGRESS
# =============================================================================
st.markdown("---")
st.markdown("### 📅 Round Progress")

rounds_info = [
    (1, "Round 1", "Week 1-10", "#28a745"),
    (2, "Round 2", "Week 11-20", "#17a2b8"),
    (3, "Round 3", "Week 21-30", "#ffc107"),
    (4, "Round 4", "Week 31-38", "#dc3545"),
]

cols = st.columns(4)

for i, (round_num, name, weeks, color) in enumerate(rounds_info):
    round_key = f"stage_{round_num}"
    is_locked = round_scores.get(f"{round_key}_locked", False)
    
    with cols[i]:
        if is_locked:
            badge = f'<span class="round-badge stage-locked">✅ Complete</span>'
        elif round_num == current_round:
            badge = f'<span class="round-badge stage-current">🔴 In Progress</span>'
        elif round_num < current_round:
            badge = f'<span class="round-badge stage-current">⏳ Pending Lock</span>'
        else:
            badge = f'<span class="round-badge stage-pending">⏳ Upcoming</span>'
        
        st.markdown(f"""
        <div class="round-progress" style="border-left: 4px solid {color};">
            <div style="font-weight: bold; color: {color};">{name}</div>
            <div style="font-size: 0.85rem; color: #6c757d;">{weeks}</div>
            {badge}
        </div>
        """, unsafe_allow_html=True)

# =============================================================================
# SEASON LEADERBOARD - TOP 3
# =============================================================================
st.markdown("---")

leaderboard = get_leaderboard_data()

if leaderboard:
    # Check for joint leaders
    if len(leaderboard) >= 1:
        max_pts = leaderboard[0]['points']
        max_kk = leaderboard[0]['kk_count']
        season_leaders = [p for p in leaderboard if p['points'] == max_pts and p['kk_count'] == max_kk]
        
        if len(season_leaders) > 1:
            leader_names = ", ".join([l['name'] for l in season_leaders])
            st.markdown(f"""
            <div style="background:linear-gradient(135deg,#ffd700 0%,#ffed4a 100%);color:#1a1a2e;padding:1rem;border-radius:10px;text-align:center;margin:1rem 0;font-weight:bold;">
                🏆 JOINT SEASON LEADERS: {leader_names} 🏆
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("### 🏆 Season Leaders (All Rounds Combined)")
    st.caption(f"Updated: {datetime.now().strftime('%d %b %Y, %H:%M')}")
    
    top_3 = leaderboard[:min(3, len(leaderboard))]
    cols = st.columns(3)
    medals = ["🥇", "🥈", "🥉"]
    
    for i, p in enumerate(top_3):
        with cols[i]:
            # Show round breakdown
            stage_breakdown = f"S1: {p['s1_pts']} | S2: {p['s2_pts']} | S3: {p['s3_pts']} | S4: {p['s4_pts']}"
            
            st.markdown(f"""
            <div class="leader-card">
                <div style="font-size: 2.5rem;">{medals[i]}</div>
                <h3 style="margin: 0.5rem 0;">{p['name']}</h3>
                <div style="font-size: 2rem; font-weight: bold; color: #667eea;">{p['points']}</div>
                <div style="color: #6c757d;">total points</div>
                <hr style="margin: 1rem 0;">
                <div>🎯 {p['kk_count']} exact scores (KK)</div>
                <div>📅 {p['weeks_played']} weeks played</div>
                <div style="font-size: 0.75rem; color: #999; margin-top: 0.5rem;">{stage_breakdown}</div>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # KK Leaders
    st.markdown("### 🎯 KK Masters (Most Exact Scores)")
    
    kk_leaders = sorted(leaderboard, key=lambda x: (-x['kk_count'], -x['points']))[:min(3, len(leaderboard))]
    
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
                <div style="font-weight: bold;">{p['points']} pts total</div>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Bottom 3 (if more than 5 participants to avoid embarrassing small groups)
    if len(leaderboard) > 5:
        st.markdown("### 😅 Room for Improvement")
        st.caption("Keep trying, there's still time!")
        
        bottom_3 = leaderboard[-3:]
        bottom_3.reverse()
        
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
                    <div>🎯 {p['kk_count']} KK</div>
                    <div>📅 {p['weeks_played']} weeks</div>
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown("---")

else:
    st.info("Competition data will appear here once predictions and results are entered!")

# =============================================================================
# QUICK ACTIONS
# =============================================================================
st.markdown("### 🎮 Quick Actions")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown("""
    <div class="stats-card">
        <h3 style="color: #667eea;">📝 Register</h3>
        <p>Join the competition!</p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Register", use_container_width=True, type="primary"):
        st.switch_page("pages/2_register.py")

with col2:
    st.markdown("""
    <div class="stats-card">
        <h3 style="color: #667eea;">🎯 Predict</h3>
        <p>Submit predictions</p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Make Predictions", use_container_width=True):
        st.switch_page("pages/3_predictions.py")

with col3:
    st.markdown("""
    <div class="stats-card">
        <h3 style="color: #667eea;">📊 Leaderboard</h3>
        <p>Full standings</p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("View Leaderboard", use_container_width=True):
        st.switch_page("pages/5_leaderboard.py")

with col4:
    st.markdown("""
    <div class="stats-card">
        <h3 style="color: #667eea;">📖 Guide</h3>
        <p>How to play</p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("View Guide", use_container_width=True, key="quick_action_guide"):
        st.switch_page("pages/16_Guide.py")

st.markdown("---")

# =============================================================================
# COMPETITION STATS
# =============================================================================
st.markdown("### 📈 Competition Stats")

try:
    from utils.data_manager import DataManager
    dm = DataManager()
    
    participants = dm.get_all_participants()
    matches = dm.load_matches()
    results = dm.load_results()
    
    total_matches = sum(len(m) for m in matches.values() if isinstance(m, list))
    total_results = sum(len(r) for r in results.values() if isinstance(r, list))
    
    stat_col1, stat_col2, stat_col3, stat_col4 = st.columns(4)
    
    with stat_col1:
        st.metric("👥 Participants", len(participants))
    
    with stat_col2:
        st.metric("⚽ Total Fixtures", total_matches)
    
    with stat_col3:
        st.metric("✅ Results Entered", total_results)
    
    with stat_col4:
        if leaderboard:
            total_kk = sum(p['kk_count'] for p in leaderboard)
            st.metric("🎯 Total KK (All)", total_kk)
        else:
            st.metric("🎯 Total KK", 0)

except Exception as e:
    st.info("Stats will appear once data is available")

st.markdown("---")

# Scoring guide
with st.expander("📖 Scoring System"):
    st.markdown("""
    ### Points System:
    
    | Prediction | Normal Match | GOTW / Week 38 🌟 |
    |------------|--------------|-------------------|
    | **Exact Score (KK)** | 6 points | 10 points |
    | **Correct Result** | 3 points | 5 points |
    | **Wrong** | 0 points | 0 points |
    
    **KK = Kemut Keliling** (Exact Score Prediction)
    
    ### Tiebreaker Rules:
    1. **Points** - Highest points wins
    2. **KK Count** - If points are equal, most exact scores (KK) wins
    3. **Joint Winners** - If both points AND KK are equal, joint winners declared
    
    ### Rounds:
    - **Round 1**: Week 1-10
    - **Round 2**: Week 11-20
    - **Round 3**: Week 21-30
    - **Round 4**: Week 31-38 (Finale - Week 38 all matches double points!)
    """)

# Footer
st.markdown("""
<div style="text-align: center; padding: 2rem 0 1rem 0; color: #6c757d; font-size: 0.9rem; border-top: 1px solid #dee2e6; margin-top: 3rem;">
    <p><strong>Nikkang KK EPL Prediction League</strong> | Season 2025-26</p>
    <p>© 2025 Nikkang KK. All rights reserved.</p>
</div>
""", unsafe_allow_html=True)

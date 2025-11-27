"""
Leaderboard Page - With Stages
Stage 1: Manual (locked) | Stage 2-4: Automated
Shows points, KK count (Kemut Keliling), and season tally
"""

import streamlit as st
import pandas as pd
from pathlib import Path
from datetime import datetime
import sys
import json

sys.path.append(str(Path(__file__).parent.parent))

from utils.data_manager import DataManager

st.set_page_config(page_title="Leaderboard - Nikkang KK", page_icon="🏆", layout="wide")

try:
    from utils.branding import inject_custom_css
    inject_custom_css()
except:
    pass

# Custom CSS
st.markdown("""
<style>
    .stage-card {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 0.5rem 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        text-align: center;
    }
    .stage-1 { border-top: 4px solid #667eea; }
    .stage-2 { border-top: 4px solid #28a745; }
    .stage-3 { border-top: 4px solid #ffc107; }
    .stage-4 { border-top: 4px solid #dc3545; }
    .stage-locked { background: #f8f9fa; }
    .stage-active { background: #e8f5e9; }
    .rank-1 { background: linear-gradient(135deg, #ffd700 0%, #ffec8b 100%); }
    .rank-2 { background: linear-gradient(135deg, #c0c0c0 0%, #e8e8e8 100%); }
    .rank-3 { background: linear-gradient(135deg, #cd7f32 0%, #daa06d 100%); }
    .leader-card {
        border-radius: 12px;
        padding: 1rem;
        margin: 0.5rem;
        text-align: center;
        color: #333;
    }
    .kk-badge {
        display: inline-block;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-weight: bold;
        font-size: 0.85rem;
    }
    .current-stage {
        border: 3px solid #28a745;
        animation: pulse 2s infinite;
    }
    @keyframes pulse {
        0% { box-shadow: 0 0 0 0 rgba(40, 167, 69, 0.4); }
        70% { box-shadow: 0 0 0 10px rgba(40, 167, 69, 0); }
        100% { box-shadow: 0 0 0 0 rgba(40, 167, 69, 0); }
    }
</style>
""", unsafe_allow_html=True)

if Path("nikkang_logo.png").exists():
    st.sidebar.image("nikkang_logo.png", use_container_width=True)
    st.sidebar.markdown("---")

st.markdown("""
<div style="text-align: center; padding: 1.5rem 0;">
    <h1 style="color: #667eea; font-size: 2.5rem; margin: 0;">🏆 Leaderboard</h1>
    <p style="color: #6c757d; font-size: 1.2rem;">Season 2025/26 Standings</p>
</div>
""", unsafe_allow_html=True)

dm = DataManager()

STAGE_SCORES_FILE = Path("nikkang_data/stage_scores.json")

def load_stage_scores():
    if STAGE_SCORES_FILE.exists():
        try:
            with open(STAGE_SCORES_FILE, 'r') as f:
                return json.load(f)
        except:
            pass
    return {}

stage_scores = load_stage_scores()

STAGES = {
    1: {"name": "Stage 1", "weeks": list(range(1, 11)), "label": "Week 1-10", "color": "#667eea", "key": "stage_1"},
    2: {"name": "Stage 2", "weeks": list(range(11, 21)), "label": "Week 11-20", "color": "#28a745", "key": "stage_2"},
    3: {"name": "Stage 3", "weeks": list(range(21, 31)), "label": "Week 21-30", "color": "#ffc107", "key": "stage_3"},
    4: {"name": "Stage 4", "weeks": list(range(31, 39)), "label": "Week 31-38", "color": "#dc3545", "key": "stage_4"},
}

def get_stage_scores(participant_id, stage_num):
    stage_info = STAGES[stage_num]
    stage_key = stage_info['key']
    is_locked = stage_scores.get(f"{stage_key}_locked", False)
    
    if is_locked:
        manual = stage_scores.get(stage_key, {}).get(participant_id, {})
        return {'points': manual.get('points', 0), 'kk_count': manual.get('kk_count', 0), 'source': 'manual'}
    
    # Load data - YOUR FORMAT: 
    # predictions: {"11": {"Y8PX0JE4": [{home, away}, ...]}}
    # results: {"11": [{home, away}, ...]} or {"11_0": {home_score, away_score}}
    # matches: {"11": [{home, away, gotw}, ...]}
    predictions = dm.load_predictions()
    results = dm.load_results()
    matches_data = dm.load_matches()
    
    total_points = 0
    kk_count = 0
    
    # Iterate through weeks in this stage
    for week in stage_info['weeks']:
        week_str = str(week)
        
        # Get matches for this week
        week_matches = matches_data.get(week_str, [])
        if not isinstance(week_matches, list):
            continue
        
        # Get user predictions for this week
        week_predictions = predictions.get(week_str, {})
        user_pred_list = week_predictions.get(participant_id, [])
        
        # Get results for this week
        week_results = results.get(week_str, [])
        
        # Process each match
        for idx, match in enumerate(week_matches):
            is_gotw = match.get('gotw', False)
            
            # Get result - handle both list and dict formats
            result = None
            if isinstance(week_results, list) and idx < len(week_results):
                result = week_results[idx]
            else:
                # Try indexed format like "11_0"
                match_key = f"{week_str}_{idx}"
                result = results.get(match_key, None)
            
            if not result:
                continue
            
            # Get prediction
            pred = user_pred_list[idx] if idx < len(user_pred_list) else None
            
            if not pred:
                continue
            
            # Get scores - handle both formats
            pred_home = pred.get('home_score', pred.get('home', -1))
            pred_away = pred.get('away_score', pred.get('away', -1))
            res_home = result.get('home_score', result.get('home', -2))
            res_away = result.get('away_score', result.get('away', -2))
            
            # Calculate points (Week 38 finale = all matches get bonus points)
            points = dm.calculate_points(pred_home, pred_away, res_home, res_away, is_gotw, week)
            total_points += points
            
            # Check for exact score (KK)
            if pred_home == res_home and pred_away == res_away:
                kk_count += 1
    
    return {'points': total_points, 'kk_count': kk_count, 'source': 'auto'}

def get_current_stage():
    """
    Automatically determine current stage based on:
    1. Locked stages (from admin)
    2. Matches with results (fallback)
    """
    # Check locked stages first
    if stage_scores.get("stage_4_locked", False):
        return 5  # Season complete
    elif stage_scores.get("stage_3_locked", False):
        return 4
    elif stage_scores.get("stage_2_locked", False):
        return 3
    elif stage_scores.get("stage_1_locked", False):
        return 2
    
    # Fallback: Detect based on match results
    try:
        results = dm.load_results()
        all_matches = dm.get_all_matches()
        
        # Find the highest week with results
        max_week_with_results = 0
        for match in all_matches:
            if match.get('id') in results:
                week = match.get('week', 0)
                if week > max_week_with_results:
                    max_week_with_results = week
        
        # Determine stage based on max week
        if max_week_with_results >= 31:
            return 4
        elif max_week_with_results >= 21:
            return 3
        elif max_week_with_results >= 11:
            return 2
        elif max_week_with_results >= 1:
            return 1
        else:
            return 1  # No results yet, start at Stage 1
    except:
        return 1

def get_completed_stages():
    """
    Determine which stages are completed based on:
    1. Locked status (admin confirmed)
    2. All matches in stage have results (auto-detect)
    """
    completed = set()
    
    # Check locked stages
    for stage_num in [1, 2, 3, 4]:
        if stage_scores.get(f"stage_{stage_num}_locked", False):
            completed.add(stage_num)
    
    # Auto-detect based on results (if all matches in a stage have results)
    try:
        results = dm.load_results()
        all_matches = dm.get_all_matches()
        
        for stage_num, info in STAGES.items():
            if stage_num in completed:
                continue
            
            stage_weeks = info['weeks']
            stage_matches = [m for m in all_matches if m.get('week', 0) in stage_weeks]
            
            if stage_matches:  # Only check if there are matches
                all_have_results = all(m.get('id') in results for m in stage_matches)
                if all_have_results:
                    completed.add(stage_num)
    except:
        pass
    
    return completed

def get_full_leaderboard():
    participants = dm.get_all_participants()
    leaderboard = []
    
    for p in participants:
        uid = p.get('id', '')
        s1, s2, s3, s4 = get_stage_scores(uid, 1), get_stage_scores(uid, 2), get_stage_scores(uid, 3), get_stage_scores(uid, 4)
        
        leaderboard.append({
            'id': uid, 'name': p.get('display_name') or p.get('name', 'Unknown'), 'team': p.get('team', '-'),
            's1_pts': s1['points'], 's1_kk': s1['kk_count'], 's1_src': s1['source'],
            's2_pts': s2['points'], 's2_kk': s2['kk_count'], 's2_src': s2['source'],
            's3_pts': s3['points'], 's3_kk': s3['kk_count'], 's3_src': s3['source'],
            's4_pts': s4['points'], 's4_kk': s4['kk_count'], 's4_src': s4['source'],
            'total_pts': s1['points'] + s2['points'] + s3['points'] + s4['points'],
            'total_kk': s1['kk_count'] + s2['kk_count'] + s3['kk_count'] + s4['kk_count']
        })
    
    leaderboard.sort(key=lambda x: (-x['total_pts'], -x['total_kk']))
    for i, e in enumerate(leaderboard, 1):
        e['rank'] = i
    return leaderboard

current_stage = get_current_stage()
completed_stages = get_completed_stages()

# Stage cards
st.markdown("### 📊 Season Stages")
cols = st.columns(4)

for i, (stage_num, info) in enumerate(STAGES.items()):
    with cols[i]:
        is_completed = stage_num in completed_stages
        is_current = stage_num == current_stage and not is_completed
        
        if is_completed:
            status = "✅ COMPLETED"
            extra = "stage-locked"
        elif is_current:
            status = "🔴 CURRENT"
            extra = "current-stage stage-active"
        else:
            status = "⏳ UPCOMING"
            extra = ""
        
        st.markdown(f"""
        <div class="stage-card stage-{stage_num} {extra}">
            <div style="font-size: 1.2rem; font-weight: bold;">{info['name']}</div>
            <div style="color: #6c757d;">{info['label']}</div>
            <div style="margin-top: 0.5rem; color: {info['color']};">{status}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("---")

# Tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs(["🏆 Season Total", "📊 Stage 1", "📊 Stage 2", "📊 Stage 3", "📊 Stage 4"])

with tab1:
    st.markdown("### 🏆 Season Leaderboard")
    st.caption(f"Updated: {datetime.now().strftime('%d %b %Y, %H:%M')}")
    
    lb = get_full_leaderboard()
    
    if not lb:
        st.warning("No participants found")
    else:
        # Top 3 by Points
        if len(lb) >= 3:
            st.markdown("#### 🥇🥈🥉 Top 3 - Points Leaders")
            cols = st.columns(3)
            for col_idx, lb_idx in enumerate([1, 0, 2]):
                p = lb[lb_idx]
                medals = ["🥈", "🥇", "🥉"]
                classes = ["rank-2", "rank-1", "rank-3"]
                with cols[col_idx]:
                    st.markdown(f"""
                    <div class="leader-card {classes[col_idx]}">
                        <div style="font-size: 2rem;">{medals[col_idx]}</div>
                        <div style="font-size: 1.2rem; font-weight: bold;">{p['name']}</div>
                        <div style="font-size: 1.5rem; font-weight: bold;">{p['total_pts']} pts</div>
                        <div class="kk-badge">KK: {p['total_kk']}</div>
                    </div>
                    """, unsafe_allow_html=True)
            st.markdown("---")
        
        # Top 3 by KK (Exact Scores)
        kk_sorted = sorted(lb, key=lambda x: (-x['total_kk'], -x['total_pts']))
        if len(kk_sorted) >= 3 and kk_sorted[0]['total_kk'] > 0:
            st.markdown("#### 🎯 Top 3 - KK Masters (Exact Scores)")
            cols = st.columns(3)
            for col_idx, lb_idx in enumerate([1, 0, 2]):
                p = kk_sorted[lb_idx]
                medals = ["🥈", "🥇", "🥉"]
                # Custom gradient for KK leaders
                kk_classes = [
                    "background: linear-gradient(135deg, #667eea 0%, #9f7aea 100%); color: white;",
                    "background: linear-gradient(135deg, #6b46c1 0%, #805ad5 100%); color: white;",
                    "background: linear-gradient(135deg, #9f7aea 0%, #b794f4 100%); color: white;"
                ]
                with cols[col_idx]:
                    st.markdown(f"""
                    <div class="leader-card" style="{kk_classes[col_idx]}">
                        <div style="font-size: 2rem;">{medals[col_idx]} 🎯</div>
                        <div style="font-size: 1.2rem; font-weight: bold;">{p['name']}</div>
                        <div style="font-size: 1.5rem; font-weight: bold;">{p['total_kk']} KK</div>
                        <div style="background: rgba(255,255,255,0.2); padding: 0.25rem 0.75rem; border-radius: 20px; font-size: 0.85rem;">
                            {p['total_pts']} pts
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            st.markdown("---")
        
        # Table
        s1_i = "🔒" if stage_scores.get('stage_1_locked') else "🔄"
        s2_i = "🔒" if stage_scores.get('stage_2_locked') else "🔄"
        s3_i = "🔒" if stage_scores.get('stage_3_locked') else "🔄"
        s4_i = "🔒" if stage_scores.get('stage_4_locked') else "🔄"
        
        df = pd.DataFrame([{
            'Rank': p['rank'], 'Name': p['name'], 'Team': p['team'],
            f'S1{s1_i}': p['s1_pts'], f'S2{s2_i}': p['s2_pts'],
            f'S3{s3_i}': p['s3_pts'], f'S4{s4_i}': p['s4_pts'],
            'Total': p['total_pts'], 'KK': p['total_kk']
        } for p in lb])
        st.dataframe(df, use_container_width=True, hide_index=True)
        st.caption("🔒 = Manual (Locked) | 🔄 = Auto-calculated")

def display_stage_tab(stage_num, info):
    is_locked = stage_scores.get(f"{info['key']}_locked", False)
    st.success(f"🔒 **{info['name']} COMPLETED**" if is_locked else f"🔄 **{info['name']} IN PROGRESS**")
    st.markdown(f"### {info['name']} ({info['label']})")
    
    lb = get_full_leaderboard()
    stage_lb = sorted(lb, key=lambda x: (-x[f's{stage_num}_pts'], -x[f's{stage_num}_kk']))
    
    for i, e in enumerate(stage_lb, 1):
        e['stage_rank'] = i
    
    # Top 3
    with_pts = [p for p in stage_lb if p[f's{stage_num}_pts'] > 0]
    if with_pts:
        st.markdown("#### 🏆 Stage Leaders")
        top3 = with_pts[:min(3, len(with_pts))]
        cols = st.columns(len(top3))
        for i, p in enumerate(top3):
            with cols[i]:
                st.markdown(f"""
                <div class="leader-card {'rank-1' if i==0 else ('rank-2' if i==1 else 'rank-3')}">
                    <div style="font-size: 1.5rem;">{'🥇' if i==0 else ('🥈' if i==1 else '🥉')}</div>
                    <div style="font-weight: bold;">{p['name']}</div>
                    <div style="font-size: 1.3rem; font-weight: bold;">{p[f's{stage_num}_pts']} pts</div>
                    <div class="kk-badge">KK: {p[f's{stage_num}_kk']}</div>
                </div>
                """, unsafe_allow_html=True)
        st.markdown("---")
    
    # Table with carry-forward
    data = []
    for p in stage_lb:
        carry = sum(p[f's{s}_pts'] for s in range(1, stage_num) if stage_scores.get(f"stage_{s}_locked"))
        row = {'Rank': p['stage_rank'], 'Name': p['name'], 'Stage Pts': p[f's{stage_num}_pts'], 'KK': p[f's{stage_num}_kk']}
        if stage_num > 1:
            row['Carry Forward'] = carry
            row['Running Total'] = carry + p[f's{stage_num}_pts']
        data.append(row)
    st.dataframe(pd.DataFrame(data), use_container_width=True, hide_index=True)

with tab2:
    display_stage_tab(1, STAGES[1])
with tab3:
    display_stage_tab(2, STAGES[2])
with tab4:
    display_stage_tab(3, STAGES[3])
with tab5:
    display_stage_tab(4, STAGES[4])

# Sidebar
st.sidebar.markdown("---")
st.sidebar.markdown("### 📖 Scoring")
st.sidebar.markdown("""
**Normal:** Exact (KK) = 6, Correct = 3  
**GOTW Bonus Bonanza:** 10 / 5  
**Week 38 Finale:** All matches 10 / 5
""")

st.markdown("---")
st.caption("Nikkang KK EPL Prediction League | Season 2025-26")

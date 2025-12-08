"""
Leaderboard Page - With Rounds
Round 1: Manual (locked) | Round 2-4: Automated
Round 2 can include manual scores for weeks 11-13
Shows points, KK count (Kemut Keliling), and season tally
"""

import streamlit as st
import pandas as pd
from pathlib import Path
from datetime import datetime
import sys
import json
import io
import base64
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend

sys.path.append(str(Path(__file__).parent.parent))

from utils.data_manager import DataManager, load_manual_scores, get_participant_manual_scores

def generate_leaderboard_png(df, title="Leaderboard", subtitle=""):
    """Generate a styled PNG image from a DataFrame"""
    # Setup figure
    n_rows = len(df) + 1  # +1 for header
    n_cols = len(df.columns)
    
    # Calculate figure size
    fig_width = max(12, n_cols * 1.2)
    fig_height = max(4, n_rows * 0.45 + 1.5)
    
    fig, ax = plt.subplots(figsize=(fig_width, fig_height))
    ax.axis('off')
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    
    # Colors
    header_bg = '#1a1a2e'
    header_text = 'white'
    row_colors = ['#ffffff', '#f8f9fa']
    gold = '#ffd700'
    silver = '#c0c0c0'
    bronze = '#cd7f32'
    pts_col = '#17a2b8'
    kk_col = '#28a745'
    
    # Title
    title_y = 0.95
    ax.text(0.5, title_y, title, ha='center', va='top', fontsize=16, fontweight='bold', color='#1a1a2e')
    if subtitle:
        ax.text(0.5, title_y - 0.05, subtitle, ha='center', va='top', fontsize=10, color='#6c757d')
    
    # Table dimensions
    table_top = title_y - 0.12
    row_height = 0.8 / (n_rows + 1)
    col_width = 0.95 / n_cols
    left_margin = 0.025
    
    # Draw header
    for j, col in enumerate(df.columns):
        x = left_margin + j * col_width
        # Header background
        rect = plt.Rectangle((x, table_top - row_height), col_width, row_height, 
                            facecolor=header_bg, edgecolor='#2a2a4e', linewidth=0.5)
        ax.add_patch(rect)
        # Header text
        ax.text(x + col_width/2, table_top - row_height/2, str(col), 
               ha='center', va='center', fontsize=9, fontweight='bold', color=header_text)
    
    # Draw data rows
    for i, (_, row) in enumerate(df.iterrows()):
        y = table_top - (i + 2) * row_height
        
        # Determine row background
        if i == 0:
            row_bg = gold
            text_color = '#333'
        elif i == 1:
            row_bg = silver
            text_color = '#333'
        elif i == 2:
            row_bg = bronze
            text_color = 'white'
        else:
            row_bg = row_colors[i % 2]
            text_color = '#333'
        
        for j, (col, val) in enumerate(row.items()):
            x = left_margin + j * col_width
            
            # Special coloring for specific columns
            if col in ['Total', 'PTS', 'Round Pts', 'Running Total'] and i > 2:
                cell_bg = pts_col
                cell_text = 'white'
            elif col == 'KK' and i > 2:
                cell_bg = kk_col
                cell_text = 'white'
            else:
                cell_bg = row_bg
                cell_text = text_color
            
            # Cell background
            rect = plt.Rectangle((x, y), col_width, row_height, 
                                facecolor=cell_bg, edgecolor='#e0e0e0', linewidth=0.5)
            ax.add_patch(rect)
            
            # Cell text
            fontweight = 'bold' if col in ['Rank', 'Name', 'Total', 'KK', 'Round Pts'] else 'normal'
            ax.text(x + col_width/2, y + row_height/2, str(val), 
                   ha='center', va='center', fontsize=8, fontweight=fontweight, color=cell_text)
    
    # Footer
    footer_y = table_top - (n_rows + 1) * row_height - 0.03
    ax.text(0.5, footer_y, f"Nikkang KK EPL Prediction League • {datetime.now().strftime('%d %b %Y')}", 
           ha='center', va='top', fontsize=8, color='#6c757d', style='italic')
    
    plt.tight_layout()
    
    # Save to bytes
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=150, bbox_inches='tight', 
                facecolor='white', edgecolor='none', pad_inches=0.1)
    buf.seek(0)
    plt.close(fig)
    
    return buf.getvalue()

st.set_page_config(page_title="Leaderboard - Nikkang KK", page_icon="🏆", layout="wide")

try:
    from utils.branding import inject_custom_css
    inject_custom_css()
except:
    pass

# Custom CSS
st.markdown("""
<style>
    .round-card {
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
    .round-locked { background: #f8f9fa; }
    .round-active { background: #e8f5e9; }
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
    .current-round {
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

ROUND_SCORES_FILE = Path("nikkang_data/round_scores.json")

def load_round_scores():
    if ROUND_SCORES_FILE.exists():
        try:
            with open(ROUND_SCORES_FILE, 'r') as f:
                return json.load(f)
        except:
            pass
    return {}

round_scores = load_round_scores()

ROUNDS = {
    1: {"name": "Round 1", "weeks": list(range(1, 11)), "label": "Week 1-10", "color": "#667eea", "key": "round_1"},
    2: {"name": "Round 2", "weeks": list(range(11, 21)), "label": "Week 11-20", "color": "#28a745", "key": "round_2"},
    3: {"name": "Round 3", "weeks": list(range(21, 31)), "label": "Week 21-30", "color": "#ffc107", "key": "round_3"},
    4: {"name": "Round 4", "weeks": list(range(31, 39)), "label": "Week 31-38", "color": "#dc3545", "key": "round_4"},
}

def get_round_scores(participant_id, round_num):
    round_info = ROUNDS[round_num]
    round_key = round_info['key']
    is_locked = round_scores.get(f"{round_key}_locked", False)
    
    if is_locked:
        manual = round_scores.get(round_key, {}).get(participant_id, {})
        return {'points': manual.get('points', 0), 'kk_count': manual.get('kk_count', 0), 'source': 'manual'}
    
    # Load data - YOUR FORMAT: 
    # predictions: {"11": {"Y8PX0JE4": [{home, away}, ...]}}
    # results: {"11": [{home, away}, ...]} or {"11_0": {home_score, away_score}}
    # matches: {"11": [{home, away, gotw}, ...]}
    predictions = dm.load_predictions()
    results = dm.load_results()
    matches_data = dm.load_matches()
    
    # Load manual scores for historical weeks
    manual_scores_data = load_manual_scores()
    
    total_points = 0
    kk_count = 0
    
    # Iterate through weeks in this stage
    for week in round_info['weeks']:
        week_str = str(week)
        
        # =================================================================
        # CHECK FOR MANUAL SCORES FIRST (for weeks like 11, 12, 13)
        # =================================================================
        if week_str in manual_scores_data and participant_id in manual_scores_data[week_str]:
            manual_week = manual_scores_data[week_str][participant_id]
            total_points += manual_week.get('points', 0)
            kk_count += manual_week.get('kk', 0)
            continue  # Skip auto-calculation for this week
        
        # =================================================================
        # AUTO-CALCULATE FROM PREDICTIONS (for weeks with system data)
        # =================================================================
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

def get_current_round():
    """
    Automatically determine current stage based on:
    1. Locked rounds (from admin)
    2. Matches with results (fallback)
    """
    # Check locked rounds first
    if round_scores.get("round_4_locked", False):
        return 5  # Season complete
    elif round_scores.get("round_3_locked", False):
        return 4
    elif round_scores.get("round_2_locked", False):
        return 3
    elif round_scores.get("round_1_locked", False):
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
            return 1  # No results yet, start at Round 1
    except:
        return 1

def get_completed_rounds():
    """
    Determine which rounds are completed based on:
    1. Locked status (admin confirmed)
    2. All matches in stage have results (auto-detect)
    """
    completed = set()
    
    # Check locked rounds
    for round_num in [1, 2, 3, 4]:
        if round_scores.get(f"stage_{round_num}_locked", False):
            completed.add(round_num)
    
    # Auto-detect based on results (if all matches in a stage have results)
    try:
        results = dm.load_results()
        all_matches = dm.get_all_matches()
        
        for round_num, info in STAGES.items():
            if round_num in completed:
                continue
            
            round_weeks = info['weeks']
            round_matches = [m for m in all_matches if m.get('week', 0) in round_weeks]
            
            if round_matches:  # Only check if there are matches
                all_have_results = all(m.get('id') in results for m in round_matches)
                if all_have_results:
                    completed.add(round_num)
    except:
        pass
    
    return completed

def get_full_leaderboard():
    participants = dm.get_all_participants()
    leaderboard = []
    
    for p in participants:
        uid = p.get('id', '')
        s1, s2, s3, s4 = get_round_scores(uid, 1), get_round_scores(uid, 2), get_round_scores(uid, 3), get_round_scores(uid, 4)
        
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
    
    # Assign ranks - same rank for tied points AND KK
    prev_pts, prev_kk, prev_rank = None, None, 0
    for i, e in enumerate(leaderboard, 1):
        if e['total_pts'] == prev_pts and e['total_kk'] == prev_kk:
            e['rank'] = prev_rank  # Joint position
        else:
            e['rank'] = i
            prev_rank = i
        prev_pts = e['total_pts']
        prev_kk = e['total_kk']
    
    return leaderboard

current_round = get_current_round()
completed_rounds = get_completed_rounds()

# Round cards
st.markdown("### 📊 Season Rounds")
cols = st.columns(4)

for i, (round_num, info) in enumerate(STAGES.items()):
    with cols[i]:
        is_completed = round_num in completed_rounds
        is_current = round_num == current_round and not is_completed
        
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
        <div class="round-card stage-{round_num} {extra}">
            <div style="font-size: 1.2rem; font-weight: bold;">{info['name']}</div>
            <div style="color: #6c757d;">{info['label']}</div>
            <div style="margin-top: 0.5rem; color: {info['color']};">{status}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("---")

# Tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs(["🏆 Season Total", "📊 Round 1", "📊 Round 2", "📊 Round 3", "📊 Round 4"])

with tab1:
    st.markdown("### 🏆 Season Leaderboard")
    st.caption(f"Updated: {datetime.now().strftime('%d %b %Y, %H:%M')}")
    
    lb = get_full_leaderboard()
    
    if not lb:
        st.warning("No participants found")
    else:
        # Check for joint season leaders (same points AND KK)
        if len(lb) >= 1 and lb[0]['total_pts'] > 0:
            max_pts = lb[0]['total_pts']
            max_kk = lb[0]['total_kk']
            season_leaders = [p for p in lb if p['total_pts'] == max_pts and p['total_kk'] == max_kk]
            
            if len(season_leaders) > 1:
                leader_names = ", ".join([l['name'] for l in season_leaders])
                st.markdown(f"""
                <div style="background:linear-gradient(135deg,#ffd700 0%,#ffed4a 100%);color:#1a1a2e;padding:1rem;border-radius:10px;text-align:center;margin:1rem 0;font-weight:bold;font-size:1.1rem;">
                    🏆 JOINT SEASON LEADERS: {leader_names} 🏆
                </div>
                """, unsafe_allow_html=True)
        
        # Top 3 by Points - using actual ranks
        with_pts = [p for p in lb if p['total_pts'] > 0]
        if len(with_pts) >= 3:
            st.markdown("#### 🥇🥈🥉 Top 3 - Points Leaders")
            
            # Get top 3 unique ranks (may have ties)
            top3 = with_pts[:3]
            cols = st.columns(3)
            
            # Display order: 2nd, 1st, 3rd (center is winner)
            display_order = [1, 0, 2]
            medals = ["🥈", "🥇", "🥉"]
            classes = ["rank-2", "rank-1", "rank-3"]
            
            for col_idx, lb_idx in enumerate(display_order):
                if lb_idx < len(top3):
                    p = top3[lb_idx]
                    with cols[col_idx]:
                        # Show actual rank (may be joint)
                        rank_text = f"#{p['rank']}" if p['rank'] > 1 else ""
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
        s1_i = "🔒" if round_scores.get('round_1_locked') else "🔄"
        s2_i = "🔒" if round_scores.get('round_2_locked') else "🔄"
        s3_i = "🔒" if round_scores.get('round_3_locked') else "🔄"
        s4_i = "🔒" if round_scores.get('round_4_locked') else "🔄"
        
        df = pd.DataFrame([{
            'Rank': p['rank'], 'Name': p['name'], 'Team': p['team'],
            f'S1{s1_i}': p['s1_pts'], f'S2{s2_i}': p['s2_pts'],
            f'S3{s3_i}': p['s3_pts'], f'S4{s4_i}': p['s4_pts'],
            'Total': p['total_pts'], 'KK': p['total_kk']
        } for p in lb])
        st.dataframe(df, use_container_width=True, hide_index=True)
        st.caption("🔒 = Manual (Locked) | 🔄 = Auto-calculated")
        
        # Download as PNG button
        col_dl1, col_dl2, col_dl3 = st.columns([1, 1, 2])
        with col_dl1:
            # Generate PNG for download (simplified columns for cleaner image)
            df_png = pd.DataFrame([{
                'Rank': p['rank'], 'Name': p['name'],
                'S1': p['s1_pts'], 'S2': p['s2_pts'],
                'S3': p['s3_pts'], 'S4': p['s4_pts'],
                'Total': p['total_pts'], 'KK': p['total_kk']
            } for p in lb])
            png_bytes = generate_leaderboard_png(df_png, "🏆 Season Leaderboard", "Nikkang KK EPL Prediction League 2025-26")
            st.download_button(
                label="📥 Download as PNG",
                data=png_bytes,
                file_name=f"nikkang_season_leaderboard_{datetime.now().strftime('%Y%m%d')}.png",
                mime="image/png",
                key="download_season_png"
            )

def display_round_tab(round_num, info):
    is_locked = round_scores.get(f"{info['key']}_locked", False)
    st.success(f"🔒 **{info['name']} COMPLETED**" if is_locked else f"🔄 **{info['name']} IN PROGRESS**")
    st.markdown(f"### {info['name']} ({info['label']})")
    
    lb = get_full_leaderboard()
    stage_lb = sorted(lb, key=lambda x: (-x[f's{round_num}_pts'], -x[f's{round_num}_kk']))
    
    # Assign ranks - same rank for tied points AND KK
    prev_pts, prev_kk, prev_rank = None, None, 0
    for i, e in enumerate(stage_lb, 1):
        curr_pts = e[f's{round_num}_pts']
        curr_kk = e[f's{round_num}_kk']
        if curr_pts == prev_pts and curr_kk == prev_kk:
            e['stage_rank'] = prev_rank  # Joint position
        else:
            e['stage_rank'] = i
            prev_rank = i
        prev_pts = curr_pts
        prev_kk = curr_kk
    
    # Top 3 - find round winner(s)
    with_pts = [p for p in stage_lb if p[f's{round_num}_pts'] > 0]
    if with_pts:
        # Find winner(s) - joint winners if same points AND KK
        max_pts = with_pts[0][f's{round_num}_pts']
        max_kk = with_pts[0][f's{round_num}_kk']
        winners = [p for p in with_pts if p[f's{round_num}_pts'] == max_pts and p[f's{round_num}_kk'] == max_kk]
        
        if len(winners) > 1:
            winner_names = ", ".join([w['name'] for w in winners])
            st.markdown(f"""
            <div style="background:linear-gradient(135deg,#ffd700 0%,#ffed4a 100%);color:#1a1a2e;padding:1rem;border-radius:10px;text-align:center;margin:1rem 0;font-weight:bold;">
                🏆 JOINT STAGE WINNERS: {winner_names} 🏆
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("#### 🏆 Round Leaders")
        top3 = with_pts[:min(3, len(with_pts))]
        cols = st.columns(len(top3))
        for i, p in enumerate(top3):
            with cols[i]:
                rank_display = p['stage_rank']
                medal = '🥇' if rank_display == 1 else ('🥈' if rank_display == 2 else '🥉')
                rank_class = 'rank-1' if rank_display == 1 else ('rank-2' if rank_display == 2 else 'rank-3')
                st.markdown(f"""
                <div class="leader-card {rank_class}">
                    <div style="font-size: 1.5rem;">{medal}</div>
                    <div style="font-weight: bold;">{p['name']}</div>
                    <div style="font-size: 1.3rem; font-weight: bold;">{p[f's{round_num}_pts']} pts</div>
                    <div class="kk-badge">KK: {p[f's{round_num}_kk']}</div>
                </div>
                """, unsafe_allow_html=True)
        st.markdown("---")
    
    # Table with carry-forward
    data = []
    for p in stage_lb:
        carry = sum(p[f's{s}_pts'] for s in range(1, round_num) if round_scores.get(f"stage_{s}_locked"))
        row = {'Rank': p['stage_rank'], 'Name': p['name'], 'Round Pts': p[f's{round_num}_pts'], 'KK': p[f's{round_num}_kk']}
        if round_num > 1:
            row['Carry Forward'] = carry
            row['Running Total'] = carry + p[f's{round_num}_pts']
        data.append(row)
    
    stage_df = pd.DataFrame(data)
    st.dataframe(stage_df, use_container_width=True, hide_index=True)
    
    # Download as PNG button for stage
    col_dl1, col_dl2, col_dl3 = st.columns([1, 1, 2])
    with col_dl1:
        png_bytes = generate_leaderboard_png(stage_df, f"📊 {info['name']} Leaderboard", info['label'])
        st.download_button(
            label="📥 Download as PNG",
            data=png_bytes,
            file_name=f"nikkang_{info['key']}_{datetime.now().strftime('%Y%m%d')}.png",
            mime="image/png",
            key=f"download_{info['key']}_png"
        )

with tab2:
    display_round_tab(1, ROUNDS[1])
with tab3:
    display_round_tab(2, ROUNDS[2])
with tab4:
    display_round_tab(3, ROUNDS[3])
with tab5:
    display_round_tab(4, ROUNDS[4])

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

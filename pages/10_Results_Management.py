"""
Results Management - Import EPL Fixtures & Results
Fetch matches and results from football-data.org API
"""

import streamlit as st
import pandas as pd
from pathlib import Path
import sys
from datetime import datetime, timedelta
import requests

# Add utils to path
sys.path.append(str(Path(__file__).parent.parent))

# Try importing timezone utils
try:
    from utils.timezone_utils import convert_utc_to_malaysian, get_malaysian_date, format_match_time_malaysian, get_malaysian_datetime_str
except:
    # Fallback if not available
    def get_malaysian_date():
        return datetime.now().date()
    def format_match_time_malaysian(utc_str):
        return utc_str[:10], utc_str[11:16] if len(utc_str) > 11 else "TBD"
    def get_malaysian_datetime_str():
        return datetime.now().isoformat()

from utils.data_manager import DataManager

# Page config
st.set_page_config(
    page_title="Results Management - Nikkang KK",
    page_icon="📊",
    layout="wide"
)

# Import branding
try:
    from utils.branding import inject_custom_css
    inject_custom_css()
except:
    pass

# Authentication
try:
    from utils.auth import check_password
    if not check_password():
        st.stop()
except:
    pass  # No auth if module not found

# Logo in sidebar
if Path("nikkang_logo.png").exists():
    st.sidebar.image("nikkang_logo.png", use_container_width=True)
    st.sidebar.markdown("---")

# Header
st.markdown("""
<div style="text-align: center; padding: 1.5rem 0;">
    <h1 style="color: #667eea; font-size: 2.5rem; margin: 0;">📊 Results Management</h1>
    <p style="color: #6c757d; font-size: 1.2rem; margin: 0.5rem 0 0 0;">
        Import Fixtures & Results from Football Data API
    </p>
</div>
""", unsafe_allow_html=True)

# Initialize data manager
dm = DataManager()

# API Configuration
API_KEY = "789354c1955e403bb10d792e31cc5282"
BASE_URL = "https://api.football-data.org/v4"
COMPETITION_ID = "PL"  # Premier League

# EPL 2025/26 Team name mapping (API names to short names)
TEAM_NAME_MAP = {
    "Arsenal FC": "Arsenal",
    "Aston Villa FC": "Aston Villa",
    "AFC Bournemouth": "Bournemouth",
    "Brentford FC": "Brentford",
    "Brighton & Hove Albion FC": "Brighton",
    "Brighton Hove Albion": "Brighton",
    "Burnley FC": "Burnley",
    "Chelsea FC": "Chelsea",
    "Crystal Palace FC": "Crystal Palace",
    "Everton FC": "Everton",
    "Fulham FC": "Fulham",
    "Ipswich Town FC": "Ipswich",
    "Ipswich": "Ipswich",
    "Leicester City FC": "Leicester",
    "Leicester": "Leicester",
    "Liverpool FC": "Liverpool",
    "Manchester City FC": "Man City",
    "Man City": "Man City",
    "Manchester United FC": "Man United",
    "Man United": "Man United",
    "Newcastle United FC": "Newcastle",
    "Newcastle": "Newcastle",
    "Nottingham Forest FC": "Nott'm Forest",
    "Nott'm Forest": "Nott'm Forest",
    "Southampton FC": "Southampton",
    "Sunderland AFC": "Sunderland",
    "Tottenham Hotspur FC": "Spurs",
    "Spurs": "Spurs",
    "West Ham United FC": "West Ham",
    "West Ham": "West Ham",
    "Wolverhampton Wanderers FC": "Wolves",
    "Wolves": "Wolves",
}

def normalize_team_name(api_name):
    """Convert API team name to app team name"""
    # First check direct mapping
    if api_name in TEAM_NAME_MAP:
        return TEAM_NAME_MAP[api_name]
    # Try shortName directly
    return api_name

def get_short_team_name(team_data):
    """Get short team name from API team data"""
    # Try shortName first, then tla, then full name
    short = team_data.get("shortName", "")
    if short:
        return normalize_team_name(short)
    tla = team_data.get("tla", "")
    if tla:
        return tla
    return normalize_team_name(team_data.get("name", "Unknown"))

# ============================================================================
# TABS
# ============================================================================
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📅 Import Fixtures",
    "📊 Import Results",
    "✏️ Manual Results",
    "🔄 Recalculate Points",
    "⚙️ Settings"
])

# ============================================================================
# TAB 1: IMPORT FIXTURES
# ============================================================================
with tab1:
    st.markdown("### 📅 Import Fixtures from API")
    
    st.info("""
    **Import upcoming matches** for participants to predict.
    - Select a gameweek or date range
    - Preview matches before importing
    - Matches will be available for predictions
    """)
    
    # Import method selection
    import_method = st.radio(
        "Import Method:",
        ["By Gameweek", "By Date Range"],
        horizontal=True
    )
    
    if import_method == "By Gameweek":
        # Get current matchday from API
        col1, col2 = st.columns(2)
        with col1:
            week_number = st.number_input(
                "Gameweek Number",
                min_value=1,
                max_value=38,
                value=12,
                help="EPL gameweek number (1-38)"
            )
        
        fetch_params = {"matchday": week_number}
        
    else:
        col1, col2 = st.columns(2)
        with col1:
            date_from = st.date_input(
                "From Date",
                value=get_malaysian_date(),
                help="Start date for fixtures"
            )
        with col2:
            date_to = st.date_input(
                "To Date",
                value=(get_malaysian_date() + timedelta(days=14)),
                help="End date for fixtures"
            )
        
        fetch_params = {
            "dateFrom": date_from.strftime("%Y-%m-%d"),
            "dateTo": date_to.strftime("%Y-%m-%d")
        }
        week_number = None
    
    st.markdown("---")
    
    if st.button("🔍 Fetch Fixtures", type="primary", use_container_width=True, key="fetch_fixtures"):
        with st.spinner("Fetching fixtures from API..."):
            try:
                headers = {"X-Auth-Token": API_KEY}
                
                response = requests.get(
                    f"{BASE_URL}/competitions/{COMPETITION_ID}/matches",
                    headers=headers,
                    params=fetch_params,
                    timeout=15
                )
                
                if response.status_code == 200:
                    data = response.json()
                    matches = data.get("matches", [])
                    
                    if not matches:
                        st.warning("No matches found for the selected criteria.")
                    else:
                        st.success(f"✅ Found {len(matches)} matches!")
                        
                        # Parse matches
                        parsed_matches = []
                        for match in matches:
                            utc_date = match.get("utcDate", "")
                            if utc_date:
                                match_date, match_time = format_match_time_malaysian(utc_date)
                            else:
                                match_date, match_time = "TBD", "TBD"
                            
                            parsed_matches.append({
                                "home": get_short_team_name(match.get("homeTeam", {})),
                                "away": get_short_team_name(match.get("awayTeam", {})),
                                "gotw": False,
                                "date": match_date,
                                "time": match_time,
                                "api_id": match.get("id"),
                                "matchday": match.get("matchday", week_number or 1),
                                "status": match.get("status", "SCHEDULED")
                            })
                        
                        st.session_state["fetched_fixtures"] = parsed_matches
                
                elif response.status_code == 429:
                    st.error("⚠️ API rate limit exceeded. Wait a minute and try again.")
                else:
                    st.error(f"❌ API Error: {response.status_code}")
                    
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
    
    # Display fetched fixtures
    if "fetched_fixtures" in st.session_state and st.session_state["fetched_fixtures"]:
        st.markdown("---")
        st.markdown("### 👀 Preview Fixtures")
        
        fixtures = st.session_state["fetched_fixtures"]
        
        # Show as table
        display_data = []
        for f in fixtures:
            display_data.append({
                "Week": f["matchday"],
                "Date": f["date"],
                "Time (MYT)": f["time"],
                "Home": f["home"],
                "Away": f["away"],
                "Status": f["status"]
            })
        
        df = pd.DataFrame(display_data)
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        # Import options
        st.markdown("---")
        
        target_week = st.number_input(
            "Import as Week:",
            min_value=1,
            max_value=38,
            value=fixtures[0]["matchday"] if fixtures else 1,
            help="Week number to assign to these fixtures"
        )
        
        skip_existing = st.checkbox("Skip existing matches", value=True)
        
        if st.button("✅ Import Fixtures", type="primary", use_container_width=True):
            imported = 0
            skipped = 0
            
            existing_matches = dm.get_all_matches()
            existing_pairs = set()
            for m in existing_matches:
                home = m.get('home', m.get('home_team', ''))
                away = m.get('away', m.get('away_team', ''))
                existing_pairs.add((home, away))
            
            for f in fixtures:
                # Check if exists
                if skip_existing and (f["home"], f["away"]) in existing_pairs:
                    skipped += 1
                    continue
                
                # Add match
                success, msg, mid = dm.add_match(
                    week=target_week,
                    home=f["home"],
                    away=f["away"],
                    gotw=f["gotw"],
                    date=f["date"],
                    time=f["time"],
                    api_id=f.get("api_id")
                )
                
                if success:
                    imported += 1
                else:
                    st.warning(f"Failed to import {f['home']} vs {f['away']}: {msg}")
            
            st.success(f"✅ Imported {imported} fixtures! (Skipped: {skipped})")
            
            # Clear session
            del st.session_state["fetched_fixtures"]
            st.rerun()

# ============================================================================
# TAB 2: IMPORT RESULTS
# ============================================================================
with tab2:
    st.markdown("### 📊 Import Results from API")
    
    st.info("""
    **Import finished match scores** from the API.
    - Fetches completed matches
    - Matches them to your fixtures
    - Updates results automatically
    """)
    
    # Date range for results
    col1, col2 = st.columns(2)
    
    with col1:
        results_from = st.date_input(
            "From Date:",
            value=datetime.now().date() - timedelta(days=7),
            help="Start date for results",
            key="results_from"
        )
    
    with col2:
        results_to = st.date_input(
            "To Date:",
            value=datetime.now().date(),
            help="End date for results",
            key="results_to"
        )
    
    st.markdown("---")
    
    if st.button("🔍 Fetch Results", type="primary", use_container_width=True, key="fetch_results"):
        with st.spinner("Fetching results from API..."):
            try:
                headers = {"X-Auth-Token": API_KEY}
                params = {
                    "status": "FINISHED",
                    "dateFrom": results_from.strftime("%Y-%m-%d"),
                    "dateTo": results_to.strftime("%Y-%m-%d")
                }
                
                response = requests.get(
                    f"{BASE_URL}/competitions/{COMPETITION_ID}/matches",
                    headers=headers,
                    params=params,
                    timeout=15
                )
                
                if response.status_code == 200:
                    data = response.json()
                    matches = data.get("matches", [])
                    
                    if not matches:
                        st.warning("No finished matches found in the selected date range.")
                    else:
                        # Parse results
                        results = []
                        for match in matches:
                            if match.get("status") == "FINISHED":
                                score = match.get("score", {})
                                full_time = score.get("fullTime", {})
                                
                                results.append({
                                    "api_id": match.get("id"),
                                    "home_team": get_short_team_name(match.get("homeTeam", {})),
                                    "away_team": get_short_team_name(match.get("awayTeam", {})),
                                    "home_score": full_time.get("home"),
                                    "away_score": full_time.get("away"),
                                    "matchday": match.get("matchday"),
                                    "date": match.get("utcDate", "")[:10]
                                })
                        
                        st.success(f"✅ Found {len(results)} finished matches!")
                        st.session_state["fetched_results"] = results
                
                elif response.status_code == 429:
                    st.error("⚠️ API rate limit exceeded. Wait a minute and try again.")
                else:
                    st.error(f"❌ API Error: {response.status_code}")
                    
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
    
    # Display fetched results
    if "fetched_results" in st.session_state and st.session_state["fetched_results"]:
        st.markdown("---")
        st.markdown("### 👀 Review Results")
        
        fetched = st.session_state["fetched_results"]
        all_matches = dm.get_all_matches()
        existing_results = dm.load_results()
        
        # Debug expander
        with st.expander("🔍 Debug: Your Fixtures", expanded=False):
            if all_matches:
                st.write(f"**Total fixtures in app:** {len(all_matches)}")
                teams_in_app = set()
                for m in all_matches:
                    teams_in_app.add(m.get('home', m.get('home_team', '')))
                    teams_in_app.add(m.get('away', m.get('away_team', '')))
                st.write("**Teams in your app:**")
                st.write(", ".join(sorted(teams_in_app)))
            else:
                st.error("⚠️ NO FIXTURES! Import fixtures first using Tab 1.")
        
        # Match API results to fixtures
        display_data = []
        match_mapping = {}
        
        for i, r in enumerate(fetched):
            # Find matching fixture
            matched_fixture = None
            for m in all_matches:
                m_home = m.get('home', m.get('home_team', ''))
                m_away = m.get('away', m.get('away_team', ''))
                
                if m_home == r['home_team'] and m_away == r['away_team']:
                    matched_fixture = m
                    break
            
            if matched_fixture:
                mid = matched_fixture.get('id', '')
                already_entered = mid in existing_results
                status = "✅ Entered" if already_entered else "🆕 New"
            else:
                mid = None
                status = "⚠️ No fixture"
            
            match_mapping[i] = {
                'api_result': r,
                'fixture': matched_fixture,
                'match_id': mid
            }
            
            display_data.append({
                'Week': r['matchday'],
                'Date': r['date'],
                'Home': r['home_team'],
                'Score': f"{r['home_score']}-{r['away_score']}",
                'Away': r['away_team'],
                'Status': status
            })
        
        # Show table
        if display_data:
            df = pd.DataFrame(display_data)
            st.dataframe(df, use_container_width=True, hide_index=True)
            
            st.session_state["match_mapping"] = match_mapping
            
            # Apply options
            st.markdown("---")
            
            col1, col2 = st.columns(2)
            with col1:
                skip_existing = st.checkbox("Skip already entered", value=True, key="skip_existing_results")
            with col2:
                only_matched = st.checkbox("Only matched fixtures", value=True, key="only_matched")
            
            if st.button("✅ Apply Results", type="primary", use_container_width=True):
                applied = 0
                skipped = 0
                not_matched = 0
                
                results_data = dm.load_results()
                matches_data = dm.load_matches()
                
                # Group results by week (matchday)
                week_results = {}
                
                for idx, mapping in match_mapping.items():
                    api_result = mapping['api_result']
                    fixture = mapping.get('fixture')
                    matchday = str(api_result.get('matchday', ''))
                    
                    if not matchday:
                        continue
                    
                    # Skip if no matching fixture found
                    if only_matched and not fixture:
                        not_matched += 1
                        continue
                    
                    # Initialize week if needed
                    if matchday not in week_results:
                        # Check if week already has results in list format
                        existing = results_data.get(matchday, [])
                        if isinstance(existing, list):
                            week_results[matchday] = existing.copy()
                        else:
                            week_results[matchday] = []
                    
                    # FIXED: Find the correct match index from fixtures, not API order
                    match_idx = None
                    week_fixtures = matches_data.get(matchday, [])
                    
                    for fix_idx, fix in enumerate(week_fixtures):
                        fix_home = fix.get('home', fix.get('home_team', ''))
                        fix_away = fix.get('away', fix.get('away_team', ''))
                        
                        if fix_home == api_result['home_team'] and fix_away == api_result['away_team']:
                            match_idx = fix_idx
                            break
                    
                    if match_idx is None:
                        not_matched += 1
                        continue
                    
                    # Ensure list is long enough
                    while len(week_results[matchday]) <= match_idx:
                        week_results[matchday].append({'home': 0, 'away': 0})
                    
                    # Skip if already has result and skip_existing is True
                    if skip_existing:
                        existing_result = week_results[matchday][match_idx] if match_idx < len(week_results[matchday]) else None
                        if existing_result and (existing_result.get('home', 0) != 0 or existing_result.get('away', 0) != 0):
                            skipped += 1
                            continue
                    
                    # Save result in list format (matches fixture order)
                    week_results[matchday][match_idx] = {
                        'home': api_result['home_score'],
                        'away': api_result['away_score']
                    }
                    applied += 1
                
                # Merge into results_data
                for week, week_res in week_results.items():
                    results_data[week] = week_res
                
                # Also save in the indexed format for compatibility (e.g., "11_0")
                # Use the correct fixture index, not API order
                for idx, mapping in match_mapping.items():
                    api_result = mapping['api_result']
                    matchday = str(api_result.get('matchday', ''))
                    
                    if matchday:
                        # Find correct fixture index again
                        week_fixtures = matches_data.get(matchday, [])
                        fix_idx = None
                        
                        for i, fix in enumerate(week_fixtures):
                            fix_home = fix.get('home', fix.get('home_team', ''))
                            fix_away = fix.get('away', fix.get('away_team', ''))
                            
                            if fix_home == api_result['home_team'] and fix_away == api_result['away_team']:
                                fix_idx = i
                                break
                        
                        if fix_idx is not None:
                            match_key = f"{matchday}_{fix_idx}"
                            results_data[match_key] = {
                                'home_score': api_result['home_score'],
                                'away_score': api_result['away_score'],
                                'entered_at': datetime.now().isoformat(),
                                'source': 'API'
                            }
                
                dm.save_results(results_data)
                
                msg = f"✅ Applied {applied} results for Week {matchday}!"
                if skipped > 0:
                    msg += f" (Skipped: {skipped})"
                if not_matched > 0:
                    msg += f" (Not matched: {not_matched})"
                st.success(msg)
                
                # Clear
                if "fetched_results" in st.session_state:
                    del st.session_state["fetched_results"]
                st.rerun()

# ============================================================================
# TAB 3: MANUAL RESULTS ENTRY
# ============================================================================
with tab3:
    st.markdown("### ✏️ Manual Result Entry")
    
    st.info("Enter results manually if API is unavailable or for corrections.")
    
    all_matches = dm.get_all_matches()
    existing_results = dm.load_results()
    
    if not all_matches:
        st.warning("No matches found. Import fixtures first using Tab 1.")
    else:
        # Get weeks
        weeks = sorted(set(m.get('week', m.get('matchday', 0)) for m in all_matches))
        
        selected_week = st.selectbox(
            "Select Week:",
            weeks,
            index=len(weeks)-1 if weeks else 0
        )
        
        # Filter matches
        week_matches = [m for m in all_matches if m.get('week', m.get('matchday')) == selected_week]
        
        if week_matches:
            st.markdown(f"#### Week {selected_week} ({len(week_matches)} matches)")
            st.markdown("---")
            
            for match in week_matches:
                mid = match.get('id', '')
                home = match.get('home', match.get('home_team', 'Home'))
                away = match.get('away', match.get('away_team', 'Away'))
                
                existing = existing_results.get(mid, {})
                has_result = bool(existing)
                
                col1, col2, col3, col4, col5 = st.columns([3, 1, 0.5, 1, 3])
                
                with col1:
                    st.markdown(f"**{home}**")
                
                with col2:
                    home_score = st.number_input(
                        "H", min_value=0, max_value=20,
                        value=existing.get('home_score', 0),
                        key=f"manual_home_{mid}",
                        label_visibility="collapsed"
                    )
                
                with col3:
                    st.markdown("<div style='text-align:center; padding-top:8px;'>-</div>", unsafe_allow_html=True)
                
                with col4:
                    away_score = st.number_input(
                        "A", min_value=0, max_value=20,
                        value=existing.get('away_score', 0),
                        key=f"manual_away_{mid}",
                        label_visibility="collapsed"
                    )
                
                with col5:
                    st.markdown(f"**{away}**")
                
                if has_result:
                    st.caption(f"✅ Current: {existing.get('home_score')}-{existing.get('away_score')}")
                
                st.markdown("---")
            
            # Save button
            if st.button("💾 Save Results", type="primary", use_container_width=True):
                saved = 0
                results_data = dm.load_results()
                
                for match in week_matches:
                    mid = match.get('id', '')
                    home_score = st.session_state.get(f"manual_home_{mid}", 0)
                    away_score = st.session_state.get(f"manual_away_{mid}", 0)
                    
                    results_data[mid] = {
                        'home_score': home_score,
                        'away_score': away_score,
                        'entered_at': get_malaysian_datetime_str() if 'get_malaysian_datetime_str' in dir() else datetime.now().isoformat(),
                        'source': 'Manual'
                    }
                    saved += 1
                
                dm.save_results(results_data)
                st.success(f"✅ Saved {saved} results!")
                st.rerun()

# ============================================================================
# TAB 4: RECALCULATE POINTS
# ============================================================================
with tab4:
    st.markdown("### 🔄 Recalculate Points")
    
    st.info("""
    **Recalculate all participant points** based on:
    
    | Result | Normal | GOTW Bonus Bonanza 🌟 | Week 38 🏆 |
    |--------|--------|----------------------|------------|
    | Exact Score (KK) | 6 pts | 10 pts | 10 pts |
    | Correct Outcome | 3 pts | 5 pts | 5 pts |
    | Wrong | 0 pts | 0 pts | 0 pts |
    
    **Week 38 FINALE:** All 10 matches score bonus points!
    """)
    
    # Show current stats
    all_matches = dm.get_all_matches()
    all_results = dm.load_results()
    all_predictions = dm.load_predictions()
    participants = dm.get_all_participants()
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Fixtures", len(all_matches))
    with col2:
        st.metric("Results Entered", len(all_results))
    with col3:
        st.metric("Participants", len(participants))
    
    st.markdown("---")
    
    if st.button("🔄 Recalculate All Points", type="primary", use_container_width=True):
        with st.spinner("Recalculating points..."):
            participants_dict = dm.load_participants()
            
            # Your data format:
            # results: {"1": [{home:1, away:1}, ...], "11_0": {home_score:2, ...}}
            # predictions: {"1": {"participant_id": [{home:0, away:1}, ...]}}
            # matches: {"11": [{home:"Team", away:"Team", gotw:false}, ...]}
            
            # Convert results to standardized format
            results_by_week_idx = {}  # {"week_idx": {home_score, away_score}}
            
            for key, value in all_results.items():
                if isinstance(value, list):
                    # Old format: week number with list
                    week = key
                    for idx, res in enumerate(value):
                        match_key = f"{week}_{idx}"
                        results_by_week_idx[match_key] = {
                            'home_score': res.get('home', res.get('home_score', 0)),
                            'away_score': res.get('away', res.get('away_score', 0))
                        }
                elif isinstance(value, dict) and ('home_score' in value or 'home' in value):
                    # New format: already has match ID like "11_0"
                    results_by_week_idx[key] = {
                        'home_score': value.get('home_score', value.get('home', 0)),
                        'away_score': value.get('away_score', value.get('away', 0))
                    }
            
            # Build matches lookup for GOTW
            matches_raw = dm.load_matches()
            matches_by_week_idx = {}
            
            if isinstance(matches_raw, dict):
                for week, week_matches in matches_raw.items():
                    if isinstance(week_matches, list):
                        for idx, m in enumerate(week_matches):
                            match_key = f"{week}_{idx}"
                            matches_by_week_idx[match_key] = m
            
            # Calculate scores for each participant
            scores = {}
            
            for week_key, week_data in all_predictions.items():
                if not week_key.isdigit():
                    continue  # Skip non-week keys (broken participant entries)
                
                week = week_key
                
                if not isinstance(week_data, dict):
                    continue
                
                for participant_id, preds in week_data.items():
                    if participant_id not in scores:
                        scores[participant_id] = {
                            'total': 0, 
                            'exact': 0, 'correct': 0, 'wrong': 0,
                            'gotw_exact': 0, 'gotw_correct': 0, 'gotw_wrong': 0,
                            'gotw_pts': 0, 'regular_pts': 0
                        }
                    
                    if not isinstance(preds, list):
                        continue
                    
                    for idx, pred in enumerate(preds):
                        match_key = f"{week}_{idx}"
                        
                        if match_key not in results_by_week_idx:
                            continue  # No result for this match yet
                        
                        result = results_by_week_idx[match_key]
                        match_info = matches_by_week_idx.get(match_key, {})
                        is_gotw = match_info.get('gotw', False)
                        
                        pred_home = pred.get('home', pred.get('home_score', -1))
                        pred_away = pred.get('away', pred.get('away_score', -1))
                        res_home = result.get('home_score', -1)
                        res_away = result.get('away_score', -1)
                        
                        try:
                            pred_home = int(pred_home) if pred_home is not None else -1
                            pred_away = int(pred_away) if pred_away is not None else -1
                            res_home = int(res_home) if res_home is not None else -1
                            res_away = int(res_away) if res_away is not None else -1
                        except:
                            continue
                        
                        # Week 38 finale = all matches get bonus points
                        is_finale = (week == "38" or week == 38)
                        use_bonus = is_gotw or is_finale
                        
                        if pred_home == res_home and pred_away == res_away:
                            # Exact score
                            pts = 10 if use_bonus else 6
                            scores[participant_id]['total'] += pts
                            if is_gotw or is_finale:
                                scores[participant_id]['gotw_exact'] += 1
                                scores[participant_id]['gotw_pts'] += pts
                            else:
                                scores[participant_id]['exact'] += 1
                                scores[participant_id]['regular_pts'] += pts
                        elif (pred_home > pred_away and res_home > res_away) or \
                             (pred_home < pred_away and res_home < res_away) or \
                             (pred_home == pred_away and res_home == res_away):
                            # Correct outcome
                            pts = 5 if use_bonus else 3
                            scores[participant_id]['total'] += pts
                            if is_gotw or is_finale:
                                scores[participant_id]['gotw_correct'] += 1
                                scores[participant_id]['gotw_pts'] += pts
                            else:
                                scores[participant_id]['correct'] += 1
                                scores[participant_id]['regular_pts'] += pts
                        else:
                            # Wrong
                            if is_gotw or is_finale:
                                scores[participant_id]['gotw_wrong'] += 1
                            else:
                                scores[participant_id]['wrong'] += 1
            
            # Build summary and update participants
            points_summary = []
            
            for pid, s in scores.items():
                # Update participant record
                if pid in participants_dict:
                    participants_dict[pid]['total_points'] = s['total']
                
                # Get display name
                p_name = "Unknown"
                if pid in participants_dict:
                    p_name = participants_dict[pid].get('display_name') or participants_dict[pid].get('name', pid)
                elif 'test' in pid.lower():
                    p_name = f"Test {pid[-4:]}"
                
                # KK count = total exact scores (regular + GOTW)
                kk_count = s['exact'] + s['gotw_exact']
                
                points_summary.append({
                    'Participant': p_name,
                    'Total': s['total'],
                    'KK 🎯': kk_count,
                    'Regular Pts': s['regular_pts'],
                    'Exact (6)': s['exact'],
                    'Correct (3)': s['correct'],
                    'Wrong': s['wrong'],
                    'GOTW Pts 🌟': s['gotw_pts'],
                    'GOTW Exact (10)': s['gotw_exact'],
                    'GOTW Correct (5)': s['gotw_correct'],
                    'GOTW Wrong': s['gotw_wrong']
                })
            
            # Save
            dm.save_participants(participants_dict)
            
            # Show results
            if points_summary:
                df = pd.DataFrame(points_summary)
                df = df.sort_values('Total', ascending=False)
                st.dataframe(df, use_container_width=True, hide_index=True)
                st.success(f"✅ Points recalculated for {len(points_summary)} participants!")
            else:
                st.warning("No predictions found to calculate. Make sure participants have submitted predictions.")

# ============================================================================
# TAB 5: SETTINGS
# ============================================================================
with tab5:
    st.markdown("### ⚙️ API Settings")
    
    st.markdown("#### Current Configuration")
    
    st.code(f"""
API Provider: football-data.org
Competition: Premier League (PL)
API Key: {API_KEY[:10]}...{API_KEY[-4:]}
Base URL: {BASE_URL}
    """)
    
    st.markdown("---")
    
    st.markdown("#### API Status")
    
    if st.button("🔍 Test API Connection"):
        with st.spinner("Testing..."):
            try:
                headers = {"X-Auth-Token": API_KEY}
                response = requests.get(
                    f"{BASE_URL}/competitions/{COMPETITION_ID}",
                    headers=headers,
                    timeout=10
                )
                
                if response.status_code == 200:
                    data = response.json()
                    st.success("✅ API Connected!")
                    st.write(f"**Competition:** {data.get('name', 'Unknown')}")
                    st.write(f"**Current Matchday:** {data.get('currentSeason', {}).get('currentMatchday', 'Unknown')}")
                elif response.status_code == 429:
                    st.warning("⚠️ Rate limit exceeded. Wait and try again.")
                else:
                    st.error(f"❌ Error: Status {response.status_code}")
            except Exception as e:
                st.error(f"❌ Connection failed: {str(e)}")
    
    st.markdown("---")
    
    st.markdown("#### View All Results")
    
    if st.button("📋 Show All Entered Results"):
        results = dm.load_results()
        matches_data = dm.load_matches()
        
        if results:
            display = []
            
            # Process results by week
            for week_key, week_data in results.items():
                if not week_key.isdigit():
                    continue  # Skip indexed keys like "11_0"
                    
                if isinstance(week_data, list):
                    week_fixtures = matches_data.get(week_key, [])
                    
                    for idx, result in enumerate(week_data):
                        if not result or (result.get('home', 0) == 0 and result.get('away', 0) == 0):
                            continue
                        
                        # Get fixture info
                        if idx < len(week_fixtures):
                            fix = week_fixtures[idx]
                            home_team = fix.get('home', '?')
                            away_team = fix.get('away', '?')
                        else:
                            home_team = f"Match {idx+1}"
                            away_team = "?"
                        
                        display.append({
                            'Week': week_key,
                            'Index': idx,
                            'Home': home_team,
                            'Score': f"{result.get('home', result.get('home_score', '?'))}-{result.get('away', result.get('away_score', '?'))}",
                            'Away': away_team
                        })
            
            if display:
                df = pd.DataFrame(display)
                df = df.sort_values(['Week', 'Index'])
                st.dataframe(df, use_container_width=True, hide_index=True)
                st.info(f"Total: {len(display)} results")
            else:
                st.info("No results in list format found.")
        else:
            st.info("No results entered yet.")
    
    st.markdown("---")
    
    st.markdown("#### 🔧 Debug: View Raw Results Data")
    
    with st.expander("View raw results.json structure"):
        results = dm.load_results()
        if results:
            # Show structure summary
            st.write("**Keys in results:**")
            week_keys = [k for k in results.keys() if k.isdigit()]
            indexed_keys = [k for k in results.keys() if '_' in k]
            
            st.write(f"- Week keys (e.g., '11'): {sorted(week_keys)}")
            st.write(f"- Indexed keys (e.g., '11_0'): {len(indexed_keys)} total")
            
            # Show sample data for each week
            for week in sorted(week_keys):
                week_data = results.get(week, [])
                if isinstance(week_data, list) and week_data:
                    st.write(f"\n**Week {week}:** {len(week_data)} matches")
                    for i, r in enumerate(week_data[:3]):  # Show first 3
                        if r:
                            st.code(f"  [{i}]: {r}")
        else:
            st.info("No results data.")
    
    st.markdown("---")
    
    st.markdown("#### 🔄 Repair Mismatched Results")
    
    st.warning("""
    **Use this if results were imported with wrong match indices.**
    This will clear ALL results for a week and allow you to re-import them.
    """)
    
    repair_week = st.number_input("Week to repair:", min_value=1, max_value=38, value=11, key="repair_week")
    
    if st.button("🗑️ Clear Results for This Week", type="secondary"):
        results = dm.load_results()
        week_str = str(repair_week)
        
        # Remove week list
        if week_str in results:
            del results[week_str]
        
        # Remove indexed keys for this week
        keys_to_remove = [k for k in results.keys() if k.startswith(f"{week_str}_")]
        for k in keys_to_remove:
            del results[k]
        
        dm.save_results(results)
        st.success(f"✅ Cleared all results for Week {repair_week}. Now re-import from API.")
        st.rerun()
    
    st.markdown("---")
    
    st.markdown("#### Team Name Mapping")
    
    with st.expander("View Team Name Mappings"):
        st.write("API names are converted to these short names:")
        for api_name, short_name in sorted(TEAM_NAME_MAP.items()):
            if "FC" in api_name or "AFC" in api_name:  # Only show full API names
                st.text(f"{api_name} → {short_name}")

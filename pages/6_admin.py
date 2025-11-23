"""
Admin Page - Match Setup and Configuration
"""

import streamlit as st
import pandas as pd
from utils.config import setup_page, apply_custom_css, TEAMS, FOOTBALL_DATA_API_KEY
from utils.data_manager import DataManager
from utils.auth import require_admin, admin_logout

setup_page()
apply_custom_css()

# Require admin access
require_admin()

dm = DataManager()

st.title("⚙️ Admin Panel")

# Logout button
col1, col2, col3 = st.columns([2, 1, 2])
with col2:
    if st.button("🚪 Logout", use_container_width=True):
        admin_logout()
        st.success("Logged out successfully!")
        st.rerun()

st.markdown("---")

# Tabs for different admin functions
tab1, tab2, tab3, tab4 = st.tabs(["⚽ Weekly Matches", "🌐 API Integration", "⚙️ Settings", "📊 Statistics"])

# Tab 1: Weekly Matches Setup
with tab1:
    st.subheader("Setup Weekly Matches")
    
    # Week selector
    week = st.selectbox(
        "Select Week to Setup",
        range(1, 39),
        index=dm.get_current_week() - 1,
        format_func=lambda x: f"Week {x}" + (" (FINALE)" if x == 38 else ""),
        key="admin_week_selector"
    )
    
    st.markdown("---")
    
    # Load existing matches
    existing_matches = dm.get_week_matches(week)
    
    # Form for match setup
    with st.form("matches_form"):
        st.info("💡 Set up 10 matches for the week. Select one as GOTW (Game of the Week).")
        
        matches = []
        gotw_index = -1
        
        for i in range(10):
            st.markdown(f"### Match {i + 1}")
            
            col1, col2, col3 = st.columns([2, 2, 1])
            
            # Get existing match data if available
            existing_match = existing_matches[i] if i < len(existing_matches) else {}
            
            with col1:
                home_team = st.selectbox(
                    f"Home Team {i+1}",
                    [""] + TEAMS,
                    index=TEAMS.index(existing_match.get('home')) + 1 if existing_match.get('home') in TEAMS else 0,
                    key=f"home_{i}",
                    label_visibility="collapsed"
                )
            
            with col2:
                away_team = st.selectbox(
                    f"Away Team {i+1}",
                    [""] + TEAMS,
                    index=TEAMS.index(existing_match.get('away')) + 1 if existing_match.get('away') in TEAMS else 0,
                    key=f"away_{i}",
                    label_visibility="collapsed"
                )
            
            with col3:
                is_gotw = st.checkbox(
                    "GOTW",
                    value=existing_match.get('gotw', False),
                    key=f"gotw_{i}"
                )
            
            if home_team and away_team:
                matches.append({
                    'home': home_team,
                    'away': away_team,
                    'gotw': is_gotw
                })
                
                if is_gotw:
                    gotw_index = i
            
            st.markdown("---")
        
        # Submit button
        submitted = st.form_submit_button("💾 Save Matches", use_container_width=True)
        
        if submitted:
            if len(matches) != 10:
                st.error("❌ Please set up all 10 matches!")
            elif gotw_index == -1:
                st.error("❌ Please select one match as GOTW (Game of the Week)!")
            else:
                # Save matches
                dm.save_week_matches(week, matches)
                st.success(f"✅ Successfully saved {len(matches)} matches for Week {week}!")
                st.balloons()
                
                # Show summary
                st.markdown("### 📋 Saved Matches")
                for idx, match in enumerate(matches):
                    gotw_badge = " ⭐ **GOTW**" if match.get('gotw') else ""
                    st.markdown(f"{idx + 1}. **{match['home']}** vs **{match['away']}**{gotw_badge}")
    
    st.markdown("---")
    
    # Quick copy from previous week
    if week > 1:
        st.subheader("🔄 Quick Actions")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button(f"📋 Copy from Week {week - 1}", use_container_width=True):
                prev_matches = dm.get_week_matches(week - 1)
                if prev_matches:
                    dm.save_week_matches(week, prev_matches)
                    st.success(f"✅ Copied {len(prev_matches)} matches from Week {week - 1}!")
                    st.rerun()
                else:
                    st.error(f"No matches found for Week {week - 1}")
        
        with col2:
            if st.button("🗑️ Clear This Week", use_container_width=True):
                dm.save_week_matches(week, [])
                st.success(f"✅ Cleared matches for Week {week}")
                st.rerun()

# Tab 2: API Integration
with tab2:
    st.subheader("🌐 Fetch Fixtures from Football APIs")
    
    st.info("""
    **✨ Using Football-Data.org (Recommended)**
    
    **Why Football-Data.org?**
    - ✅ Official EPL data source
    - ✅ FREE tier (10 requests/minute)
    - ✅ Excellent quality & reliability
    - ✅ Fast updates (near real-time)
    
    **Quick Setup:**
    1. Register FREE at: https://www.football-data.org/client/register
    2. Verify your email
    3. Copy your API key from dashboard
    4. Paste below and start importing!
    
    📖 **Full guide**: See FOOTBALL_DATA_SETUP.md
    """)
    
    from utils.football_api import FootballAPIIntegration, display_api_matches
    
    api = FootballAPIIntegration()
    
    # API Selection
    api_source = st.selectbox(
        "Select API Source",
        ["football-data", "thesportsdb", "api-football"],
        index=0,  # Default to Football-Data.org
        format_func=lambda x: {
            "thesportsdb": "TheSportsDB (Free, No Key)",
            "football-data": "⭐ Football-Data.org (Free Key Required) - RECOMMENDED",
            "api-football": "API-Football (Paid Key Required)"
        }[x]
    )
    
    # API Key input (if required)
    api_key = None
    if api_source in ["football-data", "api-football"]:
        st.markdown("---")
        st.markdown("### 🔑 API Key Configuration")
        
        # Check if key is in session state
        session_key = f"{api_source}_api_key"
        
        # Auto-load hardcoded key for Football-Data.org
        if api_source == "football-data" and FOOTBALL_DATA_API_KEY:
            st.success(f"✅ Using configured Football-Data.org API key")
            api_key = FOOTBALL_DATA_API_KEY
            
            # Option to override with different key
            with st.expander("🔧 Use Different API Key (Optional)"):
                custom_key = st.text_input("Enter Different API Key", type="password", key="custom_api_key")
                if custom_key:
                    api_key = custom_key
                    st.info("Using custom API key")
        
        # For API-Football or if no hardcoded key
        elif session_key in st.session_state and st.session_state[session_key]:
            col1, col2 = st.columns([3, 1])
            with col1:
                st.success(f"✅ Using saved {api_source} API key")
            with col2:
                if st.button("Clear Key"):
                    del st.session_state[session_key]
                    st.rerun()
            
            api_key = st.session_state[session_key]
        else:
            if api_source == "football-data":
                st.info("""
                **Get your FREE API key in 3 minutes:**
                1. Register at: https://www.football-data.org/client/register
                2. Verify your email
                3. Login and copy your API key
                4. Paste it below
                
                📖 **Detailed guide**: FOOTBALL_DATA_SETUP.md
                """)
            else:
                st.info("Get API key at: https://www.api-football.com/")
            
            api_key = st.text_input("Enter API Key", type="password", key="api_key_input")
            
            if api_key:
                if st.button("💾 Save Key for This Session"):
                    st.session_state[session_key] = api_key
                    st.success("✅ API key saved! Will persist until browser refresh.")
                    st.rerun()
    
    st.markdown("---")
    
    # Week selection
    col1, col2 = st.columns(2)
    
    with col1:
        fetch_week = st.number_input(
            "Week to Fetch",
            min_value=1,
            max_value=38,
            value=dm.get_current_week(),
            step=1
        )
    
    with col2:
        st.metric("Current Week", dm.get_current_week())
    
    st.markdown("---")
    
    # Fetch Fixtures Button
    if st.button("📥 Fetch Fixtures from API", use_container_width=True):
        with st.spinner(f"Fetching fixtures from {api_source}..."):
            try:
                fixtures = api.fetch_fixtures(
                    week=fetch_week,
                    api_source=api_source,
                    api_key=api_key
                )
                
                if fixtures:
                    st.success(f"✅ Found {len(fixtures)} matches!")
                    
                    # Display fetched matches
                    st.markdown("### 📋 Fetched Matches")
                    display_api_matches(fixtures, show_scores=False)
                    
                    # Format for Nikkang
                    formatted = api.format_for_nikkang(fixtures, limit=10)
                    
                    # Save options
                    st.markdown("---")
                    st.markdown("### 💾 Save to Nikkang")
                    
                    save_week = st.number_input(
                        "Save to Week",
                        min_value=1,
                        max_value=38,
                        value=fetch_week,
                        step=1,
                        key="save_week"
                    )
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        if st.button("💾 Save Matches", use_container_width=True):
                            # Make sure we have exactly 10 matches
                            if len(formatted) < 10:
                                st.warning(f"Only {len(formatted)} matches available. Need 10 for a full week.")
                            else:
                                formatted = formatted[:10]
                                # Set middle match as GOTW
                                formatted[4]['gotw'] = True
                                
                                dm.save_week_matches(save_week, formatted)
                                st.success(f"✅ Saved {len(formatted)} matches to Week {save_week}!")
                                st.balloons()
                                
                                # Show what was saved
                                st.markdown("#### Saved Matches:")
                                for idx, match in enumerate(formatted, 1):
                                    gotw = " ⭐ GOTW" if match['gotw'] else ""
                                    st.text(f"{idx}. {match['home']} vs {match['away']}{gotw}")
                    
                    with col2:
                        if st.button("👀 Preview Only", use_container_width=True):
                            st.info("Matches loaded for preview. Click 'Save Matches' to save them.")
                    
                    # Store in session for manual editing
                    st.session_state.fetched_fixtures = formatted
                    
                else:
                    st.error("❌ No fixtures found. Try a different week or API.")
                    
            except Exception as e:
                st.error(f"❌ Error fetching fixtures: {e}")
                st.exception(e)
    
    st.markdown("---")
    
    # Fetch Results Button
    st.markdown("### 📊 Fetch Match Results")
    
    result_week = st.number_input(
        "Week to Fetch Results",
        min_value=1,
        max_value=38,
        value=max(1, dm.get_current_week() - 1),
        step=1,
        key="result_week"
    )
    
    if st.button("📥 Fetch Results from API", use_container_width=True):
        with st.spinner(f"Fetching results from {api_source}..."):
            try:
                results = api.fetch_results(
                    week=result_week,
                    api_source=api_source,
                    api_key=api_key
                )
                
                if results:
                    st.success(f"✅ Found {len(results)} completed matches!")
                    
                    # Display results
                    st.markdown("### 📋 Fetched Results")
                    display_api_matches(results, show_scores=True)
                    
                    # Format for Nikkang
                    formatted_results = api.format_results_for_nikkang(results)
                    
                    # Save option
                    if st.button("💾 Save Results", use_container_width=True, key="save_results"):
                        dm.save_week_results(result_week, formatted_results)
                        st.success(f"✅ Saved {len(formatted_results)} results to Week {result_week}!")
                        st.success("🧮 Leaderboard scores recalculated!")
                        st.balloons()
                        
                        # Show what was saved
                        st.markdown("#### Saved Results:")
                        for idx, result in enumerate(formatted_results, 1):
                            st.text(f"Match {idx}: {result['home']} - {result['away']}")
                else:
                    st.warning("⚠️ No completed matches found for this week yet.")
                    
            except Exception as e:
                st.error(f"❌ Error fetching results: {e}")
                st.exception(e)
    
    st.markdown("---")
    
    # API Status Check
    with st.expander("🔍 Test API Connection"):
        if st.button("Test Connection", use_container_width=True):
            with st.spinner("Testing API connection..."):
                from utils.football_api import test_api_connection
                
                if test_api_connection(api_source, api_key):
                    st.success(f"✅ {api_source} is accessible!")
                else:
                    st.error(f"❌ Cannot connect to {api_source}. Check your API key or internet connection.")

# Tab 3: Settings
with tab3:
    st.subheader("Competition Settings")
    
    # Current week setting
    current_week = dm.get_current_week()
    
    st.markdown("### 📅 Current Week")
    st.info(f"The current week is: **Week {current_week}**")
    
    new_week = st.number_input(
        "Set Current Week",
        min_value=1,
        max_value=38,
        value=current_week,
        step=1
    )
    
    if st.button("💾 Update Current Week"):
        dm.set_current_week(new_week)
        st.success(f"✅ Current week updated to Week {new_week}!")
        st.rerun()
    
    st.markdown("---")
    
    # Data management
    st.subheader("📦 Data Management")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Export Data")
        
        if st.button("📥 Download All Data", use_container_width=True):
            import json
            
            all_data = {
                'participants': dm.load_participants(),
                'matches': dm.load_matches(),
                'predictions': dm.load_predictions(),
                'results': dm.load_results(),
                'current_week': dm.get_current_week()
            }
            
            json_data = json.dumps(all_data, indent=2)
            
            st.download_button(
                label="💾 Download JSON",
                data=json_data,
                file_name="nikkang_backup.json",
                mime="application/json",
                use_container_width=True
            )
    
    with col2:
        st.markdown("### Import Data")
        
        uploaded_file = st.file_uploader("📤 Upload Backup JSON", type=['json'])
        
        if uploaded_file is not None:
            try:
                import json
                data = json.load(uploaded_file)
                
                if st.button("⚠️ Restore Data (This will overwrite!)", use_container_width=True):
                    dm.save_participants(data.get('participants', {}))
                    dm.save_matches(data.get('matches', {}))
                    dm.save_predictions(data.get('predictions', {}))
                    dm.save_results(data.get('results', {}))
                    dm.set_current_week(data.get('current_week', 1))
                    
                    st.success("✅ Data restored successfully!")
                    st.rerun()
            except Exception as e:
                st.error(f"❌ Error reading file: {e}")

# Tab 4: Statistics
with tab4:
    st.subheader("📊 Competition Statistics")
    
    # Overview stats
    participants = dm.load_participants()
    matches = dm.load_matches()
    predictions = dm.load_predictions()
    results = dm.load_results()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Participants", len(participants))
    
    with col2:
        total_weeks_setup = len([w for w in matches.values() if w])
        st.metric("Weeks Setup", total_weeks_setup)
    
    with col3:
        total_predictions = sum(len(p) for p in predictions.values())
        st.metric("Total Predictions", total_predictions)
    
    with col4:
        total_results = len([r for r in results.values() if r])
        st.metric("Weeks Completed", total_results)
    
    st.markdown("---")
    
    # Weekly participation
    st.subheader("📅 Weekly Participation")
    
    participation_data = []
    
    for week in range(1, 39):
        week_str = str(week)
        week_predictions = predictions.get(week_str, {})
        week_results = results.get(week_str, [])
        week_matches = matches.get(week_str, [])
        
        participation_data.append({
            'Week': week,
            'Matches Setup': len(week_matches),
            'Predictions': len(week_predictions),
            'Results Entered': 'Yes' if week_results else 'No'
        })
    
    df_participation = pd.DataFrame(participation_data)
    df_participation = df_participation[df_participation['Matches Setup'] > 0]
    
    if not df_participation.empty:
        st.dataframe(df_participation, use_container_width=True, hide_index=True)
    else:
        st.info("No weeks set up yet.")
    
    st.markdown("---")
    
    # Participant activity
    st.subheader("👥 Participant Activity")
    
    activity_data = []
    
    for pid, p in participants.items():
        weeks_predicted = sum(1 for week_pred in predictions.values() if pid in week_pred)
        
        activity_data.append({
            'Name': p['name'],
            'Email': p['email'],
            'Weeks Predicted': weeks_predicted,
            'Favorite Team': p.get('team', 'N/A')
        })
    
    df_activity = pd.DataFrame(activity_data)
    df_activity = df_activity.sort_values('Weeks Predicted', ascending=False)
    
    if not df_activity.empty:
        st.dataframe(df_activity, use_container_width=True, hide_index=True)
    else:
        st.info("No participants yet.")

st.markdown("---")
st.caption("Nikkang KK - Admin Panel | Handle with care!")

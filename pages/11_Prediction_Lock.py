"""
Prediction Management - Admin Page
Lock/unlock predictions, view all predictions, manage deadlines
"""

import streamlit as st
import pandas as pd
from pathlib import Path
from datetime import datetime
import sys
import json

# Add utils to path
sys.path.append(str(Path(__file__).parent.parent))

from utils.data_manager import DataManager
from utils.auth import check_password

# Page config
st.set_page_config(
    page_title="Prediction Management - Nikkang KK",
    page_icon="🔒",
    layout="wide"
)

# Import branding
try:
    from utils.branding import inject_custom_css
    inject_custom_css()
except:
    pass

# Authentication
if not check_password():
    st.stop()

# Logo in sidebar
if Path("nikkang_logo.png").exists():
    st.sidebar.markdown('<div style="padding-top: 0.5rem;"></div>', unsafe_allow_html=True)
    st.sidebar.markdown('<div class="sidebar-logo-container">', unsafe_allow_html=True)
    st.sidebar.image("nikkang_logo.png", use_container_width=True)
    st.sidebar.markdown('</div>', unsafe_allow_html=True)
    st.sidebar.markdown("---")

# Header
st.markdown("""
<div style="text-align: center; padding: 1.5rem 0;">
    <h1 style="color: #667eea; font-size: 2.5rem; margin: 0;">🔒 Prediction Management</h1>
    <p style="color: #6c757d; font-size: 1.2rem; margin: 0.5rem 0 0 0;">
        Lock/unlock predictions and view all submissions
    </p>
</div>
""", unsafe_allow_html=True)

# Initialize data manager
dm = DataManager()

# Settings file for lock status
SETTINGS_FILE = Path("nikkang_data/settings.json")

def load_settings():
    """Load settings from JSON file"""
    if SETTINGS_FILE.exists():
        try:
            with open(SETTINGS_FILE, 'r') as f:
                return json.load(f)
        except:
            pass
    return {
        "current_week": 1,
        "locked_weeks": [],
        "global_lock": False,
        "deadline_message": "Predictions close at kickoff!"
    }

def save_settings(settings):
    """Save settings to JSON file"""
    try:
        SETTINGS_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(SETTINGS_FILE, 'w') as f:
            json.dump(settings, f, indent=2)
        return True
    except:
        return False

# Load current settings
settings = load_settings()

# Tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🔒 Lock/Unlock",
    "👀 View All Predictions",
    "✏️ Edit Predictions",
    "📊 Prediction Stats",
    "⚙️ Settings"
])

# ============================================================================
# TAB 1: LOCK/UNLOCK PREDICTIONS
# ============================================================================
with tab1:
    st.markdown("### 🔒 Lock/Unlock Predictions")
    
    st.info("""
    **How it works:**
    - Lock predictions to prevent changes after deadline
    - Unlock to allow late submissions (if needed)
    - Global lock stops ALL predictions
    """)
    
    # Global Lock
    st.markdown("---")
    st.markdown("#### 🌐 Global Lock")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown("""
        **Global Lock** stops ALL predictions across ALL weeks.
        Use this during maintenance or end of season.
        """)
    
    with col2:
        global_status = "🔴 LOCKED" if settings.get("global_lock", False) else "🟢 OPEN"
        st.markdown(f"**Status:** {global_status}")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔒 Enable Global Lock", use_container_width=True, type="primary" if not settings.get("global_lock") else "secondary"):
            settings["global_lock"] = True
            save_settings(settings)
            st.success("✅ Global lock enabled - all predictions are now locked!")
            st.rerun()
    
    with col2:
        if st.button("🔓 Disable Global Lock", use_container_width=True, type="primary" if settings.get("global_lock") else "secondary"):
            settings["global_lock"] = False
            save_settings(settings)
            st.success("✅ Global lock disabled - predictions are now open!")
            st.rerun()
    
    # Week-by-week Lock
    st.markdown("---")
    st.markdown("#### 📅 Lock by Gameweek")
    
    weeks = dm.get_weeks()
    locked_weeks = settings.get("locked_weeks", [])
    
    # Display all weeks with lock status
    st.markdown("**Current Week Status:**")
    
    # Create columns for week buttons
    cols = st.columns(min(5, len(weeks) if weeks else 1))
    
    for i, week in enumerate(weeks):
        col_idx = i % 5
        with cols[col_idx]:
            is_locked = week in locked_weeks
            status_icon = "🔴" if is_locked else "🟢"
            st.markdown(f"{status_icon} **Week {week}**")
    
    st.markdown("---")
    
    # Lock/Unlock specific week
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        selected_week = st.selectbox(
            "Select Week:",
            weeks,
            format_func=lambda x: f"Week {x}"
        )
    
    with col2:
        if st.button("🔒 Lock Week", use_container_width=True):
            if selected_week not in locked_weeks:
                locked_weeks.append(selected_week)
                settings["locked_weeks"] = locked_weeks
                save_settings(settings)
                st.success(f"✅ Week {selected_week} is now locked!")
                st.rerun()
            else:
                st.warning(f"Week {selected_week} is already locked")
    
    with col3:
        if st.button("🔓 Unlock Week", use_container_width=True):
            if selected_week in locked_weeks:
                locked_weeks.remove(selected_week)
                settings["locked_weeks"] = locked_weeks
                save_settings(settings)
                st.success(f"✅ Week {selected_week} is now unlocked!")
                st.rerun()
            else:
                st.warning(f"Week {selected_week} is not locked")
    
    # Bulk actions
    st.markdown("---")
    st.markdown("#### ⚡ Bulk Actions")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔒 Lock All Past Weeks", use_container_width=True):
            current = dm.get_current_week()
            for w in weeks:
                if w < current and w not in locked_weeks:
                    locked_weeks.append(w)
            settings["locked_weeks"] = locked_weeks
            save_settings(settings)
            st.success("✅ All past weeks locked!")
            st.rerun()
    
    with col2:
        if st.button("🔒 Lock All Weeks", use_container_width=True):
            settings["locked_weeks"] = list(weeks)
            save_settings(settings)
            st.success("✅ All weeks locked!")
            st.rerun()
    
    with col3:
        if st.button("🔓 Unlock All Weeks", use_container_width=True):
            settings["locked_weeks"] = []
            save_settings(settings)
            st.success("✅ All weeks unlocked!")
            st.rerun()

# ============================================================================
# TAB 2: VIEW ALL PREDICTIONS
# ============================================================================
with tab2:
    st.markdown("### 👀 View All Predictions")
    
    # Week selector
    weeks = dm.get_weeks()
    view_week = st.selectbox(
        "Select Gameweek:",
        weeks,
        format_func=lambda x: f"Week {x}",
        key="view_week"
    )
    
    # Get matches and predictions for this week
    matches = dm.get_matches_by_week(view_week)
    participants = dm.get_all_participants()
    all_predictions = dm.load_predictions()
    results = dm.load_results()
    
    # Get predictions for this specific week
    # Format: {"11": {"USER_ID": [{"home": 2, "away": 1}, ...], ...}}
    week_predictions = all_predictions.get(str(view_week), {})
    
    if not matches:
        st.warning(f"No matches found for Week {view_week}")
    elif not participants:
        st.warning("No participants registered yet")
    else:
        st.markdown(f"**Week {view_week}:** {len(matches)} matches, {len(participants)} participants")
        st.markdown("---")
        
        # Create prediction matrix
        st.markdown("#### 📊 Prediction Matrix")
        
        # Build data for the matrix
        matrix_data = []
        
        for p in participants:
            uid = p.get('id', '')
            # Get predictions for this user for this week (list of predictions)
            user_week_preds = week_predictions.get(uid, [])
            
            row = {
                'Participant': p.get('display_name') or p.get('name', 'Unknown'),
                'ID': uid[:8] if len(uid) > 8 else uid  # Truncate ID for display
            }
            
            for idx, match in enumerate(matches):
                home = match.get('home', match.get('home_team', ''))
                away = match.get('away', match.get('away_team', ''))
                match_label = f"{home} vs {away}"
                
                # Get prediction by index (matches are in order)
                if idx < len(user_week_preds):
                    pred = user_week_preds[idx]
                    if isinstance(pred, dict):
                        pred_home = pred.get('home', pred.get('home_score', '?'))
                        pred_away = pred.get('away', pred.get('away_score', '?'))
                        row[match_label] = f"{pred_home}-{pred_away}"
                    else:
                        row[match_label] = "❌"
                else:
                    row[match_label] = "❌"
            
            matrix_data.append(row)
        
        df = pd.DataFrame(matrix_data)
        
        # Style the dataframe
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        # Download option
        csv = df.to_csv(index=False)
        st.download_button(
            "📥 Download as CSV",
            data=csv,
            file_name=f"predictions_week_{view_week}.csv",
            mime="text/csv"
        )
        
        st.markdown("---")
        
        # Detailed view by match
        st.markdown("#### 🔍 Detailed View by Match")
        
        for idx, match in enumerate(matches):
            home = match.get('home', match.get('home_team', ''))
            away = match.get('away', match.get('away_team', ''))
            is_gotw = match.get('gotw', False) or match.get('game_of_week', False)
            
            gotw_badge = " ⭐ GOTW" if is_gotw else ""
            
            # Get result if available
            week_results = results.get(str(view_week), [])
            if idx < len(week_results) and week_results[idx]:
                res = week_results[idx]
                result_str = f" | Result: {res.get('home', res.get('home_score', '?'))}-{res.get('away', res.get('away_score', '?'))}"
            else:
                result_str = ""
            
            with st.expander(f"**{home} vs {away}**{gotw_badge}{result_str}"):
                match_preds = []
                
                for p in participants:
                    uid = p.get('id', '')
                    # Get this user's predictions for this week
                    user_week_preds = week_predictions.get(uid, [])
                    
                    # Get prediction for this match by index
                    if idx < len(user_week_preds):
                        pred = user_week_preds[idx]
                        if isinstance(pred, dict):
                            pred_home = pred.get('home', pred.get('home_score', '?'))
                            pred_away = pred.get('away', pred.get('away_score', '?'))
                            pred_str = f"{pred_home}-{pred_away}"
                            pred_time = pred.get('predicted_at', 'Submitted')
                            
                            # Calculate points if result available
                            if idx < len(week_results) and week_results[idx]:
                                res = week_results[idx]
                                res_home = res.get('home', res.get('home_score', -2))
                                res_away = res.get('away', res.get('away_score', -2))
                                pts = dm.calculate_points(
                                    pred_home if isinstance(pred_home, int) else -1,
                                    pred_away if isinstance(pred_away, int) else -1,
                                    res_home if isinstance(res_home, int) else -2,
                                    res_away if isinstance(res_away, int) else -2,
                                    is_gotw
                                )
                                points_str = f"{pts} pts"
                            else:
                                points_str = "-"
                        else:
                            pred_str = "No prediction"
                            pred_time = "-"
                            points_str = "-"
                    else:
                        pred_str = "No prediction"
                        pred_time = "-"
                        points_str = "-"
                    
                    match_preds.append({
                        'Participant': p.get('display_name') or p.get('name', 'Unknown'),
                        'Prediction': pred_str,
                        'Submitted': pred_time,
                        'Points': points_str
                    })
                
                pred_df = pd.DataFrame(match_preds)
                st.dataframe(pred_df, use_container_width=True, hide_index=True)
        
        st.markdown("---")
        
        # Summary stats
        st.markdown("#### 📈 Prediction Summary")
        
        col1, col2, col3 = st.columns(3)
        
        total_possible = len(matches) * len(participants)
        # Count predictions made for this week
        total_made = 0
        for p in participants:
            uid = p.get('id', '')
            user_week_preds = week_predictions.get(uid, [])
            # Count valid predictions (non-empty dicts)
            total_made += sum(1 for pred in user_week_preds if isinstance(pred, dict) and (pred.get('home') is not None or pred.get('home_score') is not None))
        
        with col1:
            st.metric("Total Possible", total_possible)
        
        with col2:
            st.metric("Predictions Made", total_made)
        
        with col3:
            pct = (total_made / total_possible * 100) if total_possible > 0 else 0
            st.metric("Completion Rate", f"{pct:.1f}%")
        
        # Who hasn't predicted
        st.markdown("#### ⚠️ Missing Predictions")
        
        missing = []
        for p in participants:
            uid = p.get('id', '')
            user_week_preds = week_predictions.get(uid, [])
            # Count how many matches don't have predictions
            preds_made = len([pred for pred in user_week_preds if isinstance(pred, dict) and (pred.get('home') is not None or pred.get('home_score') is not None)])
            missing_count = len(matches) - preds_made
            
            if missing_count > 0:
                missing.append({
                    'Participant': p.get('display_name') or p.get('name', 'Unknown'),
                    'Missing': missing_count,
                    'Status': '⚠️ Incomplete' if missing_count < len(matches) else '❌ No predictions'
                })
        
        if missing:
            missing_df = pd.DataFrame(missing)
            st.dataframe(missing_df, use_container_width=True, hide_index=True)
        else:
            st.success("✅ All participants have submitted predictions for all matches!")

# ============================================================================
# TAB 3: EDIT PREDICTIONS (ADMIN)
# ============================================================================
with tab3:
    st.markdown("### ✏️ Admin: Edit Predictions")
    st.info("⚠️ **Admin Only:** Add or amend predictions for any participant, including past weeks.")
    
    # Load data
    participants = dm.get_all_participants()
    weeks = dm.get_weeks()
    
    if not participants:
        st.warning("No participants registered yet")
    elif not weeks:
        st.warning("No matches set up yet")
    else:
        # Select participant
        st.markdown("#### 👤 Select Participant")
        
        # Build participant list with nicknames
        participant_options = {}
        for p in participants:
            nickname = p.get('display_name') or p.get('nickname') or p.get('name', 'Unknown')
            pid = p.get('id', '')
            participant_options[f"{nickname}"] = pid
        
        selected_participant_name = st.selectbox(
            "Participant:",
            options=list(participant_options.keys()),
            key="edit_participant"
        )
        
        selected_participant_id = participant_options.get(selected_participant_name, '')
        
        # Select week
        st.markdown("#### 📅 Select Week")
        
        selected_week = st.selectbox(
            "Week:",
            options=weeks,
            format_func=lambda x: f"Week {x}" + (" ⚠️ LOCKED" if x in settings.get("locked_weeks", []) else ""),
            key="edit_week"
        )
        
        # Show lock warning
        if selected_week in settings.get("locked_weeks", []):
            st.warning(f"⚠️ Week {selected_week} is locked for participants, but you can still edit as admin.")
        
        # Get matches for selected week
        matches = dm.get_week_matches(selected_week)
        
        if not matches:
            st.warning(f"No matches found for Week {selected_week}")
        else:
            st.markdown("#### 🎯 Edit Predictions")
            st.caption(f"Editing predictions for **{selected_participant_name}** - Week {selected_week}")
            
            # Load existing predictions
            existing_preds = dm.get_participant_predictions(selected_participant_id, selected_week)
            
            # Show current predictions status
            if existing_preds and len(existing_preds) > 0:
                has_preds = any(p.get('home', 0) != 0 or p.get('away', 0) != 0 for p in existing_preds)
                if has_preds:
                    st.success(f"✅ {selected_participant_name} has existing predictions for Week {selected_week}")
                else:
                    st.info(f"📝 {selected_participant_name} has no predictions for Week {selected_week}")
            else:
                st.info(f"📝 {selected_participant_name} has no predictions for Week {selected_week}")
                existing_preds = []
            
            # Create form for editing
            with st.form(f"admin_edit_predictions_{selected_week}_{selected_participant_id}"):
                predictions = []
                
                for idx, match in enumerate(matches):
                    is_gotw = match.get('gotw', False)
                    
                    # Get existing prediction for this match
                    if idx < len(existing_preds):
                        default_home = int(existing_preds[idx].get('home', 0))
                        default_away = int(existing_preds[idx].get('away', 0))
                    else:
                        default_home = 0
                        default_away = 0
                    
                    # Match display
                    gotw_badge = " ⭐ GOTW" if is_gotw else ""
                    st.markdown(f"**Match {idx + 1}:** {match.get('home', '?')} vs {match.get('away', '?')}{gotw_badge}")
                    
                    col1, col2, col3 = st.columns([2, 1, 2])
                    
                    with col1:
                        home_score = st.number_input(
                            f"{match.get('home', 'Home')}",
                            min_value=0,
                            max_value=15,
                            value=default_home,
                            key=f"admin_home_{selected_week}_{selected_participant_id}_{idx}"
                        )
                    
                    with col2:
                        st.markdown("<div style='text-align:center; padding-top:30px;'>-</div>", unsafe_allow_html=True)
                    
                    with col3:
                        away_score = st.number_input(
                            f"{match.get('away', 'Away')}",
                            min_value=0,
                            max_value=15,
                            value=default_away,
                            key=f"admin_away_{selected_week}_{selected_participant_id}_{idx}"
                        )
                    
                    predictions.append({'home': home_score, 'away': away_score})
                    st.markdown("---")
                
                # Admin note
                admin_note = st.text_input(
                    "Admin Note (optional):",
                    placeholder="Reason for edit (e.g., 'Late submission via WhatsApp')",
                    key="admin_note"
                )
                
                # Submit buttons
                col1, col2 = st.columns(2)
                
                with col1:
                    save_btn = st.form_submit_button("💾 Save Predictions", use_container_width=True, type="primary")
                
                with col2:
                    clear_btn = st.form_submit_button("🗑️ Clear All Predictions", use_container_width=True)
                
                if save_btn:
                    # Save predictions
                    dm.save_participant_predictions(selected_participant_id, selected_week, predictions)
                    
                    # Log the admin action
                    log_msg = f"Admin edited predictions for {selected_participant_name} - Week {selected_week}"
                    if admin_note:
                        log_msg += f" | Note: {admin_note}"
                    
                    st.success(f"✅ Predictions saved for {selected_participant_name} - Week {selected_week}")
                    
                    # Show summary
                    st.markdown("**Saved Predictions:**")
                    for idx, (match, pred) in enumerate(zip(matches, predictions)):
                        gotw = "⭐" if match.get('gotw', False) else ""
                        st.text(f"{idx+1}. {match.get('home', '?')} {pred['home']} - {pred['away']} {match.get('away', '?')} {gotw}")
                
                if clear_btn:
                    # Clear predictions (save empty list)
                    dm.save_participant_predictions(selected_participant_id, selected_week, [])
                    st.warning(f"🗑️ Predictions cleared for {selected_participant_name} - Week {selected_week}")
                    st.rerun()
        
        # Bulk actions
        st.markdown("---")
        st.markdown("#### ⚡ Bulk Actions")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📋 View All Predictions for This Participant", use_container_width=True):
                all_preds = dm.load_predictions()
                participant_preds = all_preds.get(selected_participant_id, {})
                
                if participant_preds:
                    st.markdown(f"**All predictions for {selected_participant_name}:**")
                    for week_key, preds in sorted(participant_preds.items(), key=lambda x: int(x[0]) if x[0].isdigit() else 0):
                        if preds:
                            st.markdown(f"**Week {week_key}:** {len(preds)} predictions")
                else:
                    st.info(f"No predictions found for {selected_participant_name}")
        
        with col2:
            if st.button("📊 Recalculate Points", use_container_width=True):
                dm.recalculate_all_points()
                st.success("✅ All points recalculated!")

# ============================================================================
# TAB 4: PREDICTION STATS
# ============================================================================
with tab4:
    st.markdown("### 📊 Prediction Statistics")
    
    participants = dm.get_all_participants()
    all_predictions = dm.load_predictions()
    weeks = dm.get_weeks()
    
    if not participants:
        st.warning("No participants registered yet")
    else:
        # Overall stats
        st.markdown("#### 🌐 Overall Statistics")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Participants", len(participants))
        
        with col2:
            total_preds = sum(len(p) for p in all_predictions.values())
            st.metric("Total Predictions", total_preds)
        
        with col3:
            st.metric("Total Weeks", len(weeks))
        
        with col4:
            avg_per_user = total_preds / len(participants) if participants else 0
            st.metric("Avg per User", f"{avg_per_user:.1f}")
        
        st.markdown("---")
        
        # Participation by week
        st.markdown("#### 📅 Participation by Week")
        
        week_stats = []
        for week in weeks:
            matches = dm.get_matches_by_week(week)
            match_ids = [m.get('id', '') for m in matches]
            
            participants_predicted = 0
            total_predictions = 0
            
            for uid, user_preds in all_predictions.items():
                week_preds = [mid for mid in match_ids if mid in user_preds]
                if week_preds:
                    participants_predicted += 1
                    total_predictions += len(week_preds)
            
            week_stats.append({
                'Week': f"Week {week}",
                'Matches': len(matches),
                'Participants': participants_predicted,
                'Predictions': total_predictions,
                'Completion': f"{(total_predictions / (len(matches) * len(participants)) * 100):.0f}%" if matches and participants else "0%"
            })
        
        week_df = pd.DataFrame(week_stats)
        st.dataframe(week_df, use_container_width=True, hide_index=True)
        
        st.markdown("---")
        
        # Most active participants
        st.markdown("#### 🏆 Most Active Participants")
        
        activity = []
        for p in participants:
            uid = p.get('id', '')
            user_preds = all_predictions.get(uid, {})
            
            activity.append({
                'Participant': p.get('display_name') or p.get('name', 'Unknown'),
                'Predictions': len(user_preds),
                'Status': p.get('status', 'active')
            })
        
        activity_df = pd.DataFrame(activity)
        activity_df = activity_df.sort_values('Predictions', ascending=False)
        st.dataframe(activity_df, use_container_width=True, hide_index=True)

# ============================================================================
# TAB 5: SETTINGS
# ============================================================================
with tab5:
    st.markdown("### ⚙️ Prediction Settings")
    
    # ==========================================================================
    # CURRENT WEEK SETTING - NEW
    # ==========================================================================
    st.markdown("#### 📅 Current Gameweek")
    st.info("Set the current gameweek for the competition. This affects which week is shown by default on the Predictions page.")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        current_week = settings.get("current_week", 1)
        new_week = st.number_input(
            "Current Week:",
            min_value=1,
            max_value=38,
            value=current_week,
            help="Set the current gameweek (1-38)"
        )
    
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("💾 Save Current Week", use_container_width=True, type="primary"):
            settings["current_week"] = new_week
            save_settings(settings)
            st.success(f"✅ Current week set to **Week {new_week}**!")
            st.rerun()
    
    st.caption(f"📌 Currently set to: **Week {current_week}**")
    
    st.markdown("---")
    
    # Deadline message
    st.markdown("#### 📝 Deadline Message")
    
    deadline_msg = st.text_area(
        "Message shown to users:",
        value=settings.get("deadline_message", "Predictions close at kickoff!"),
        help="This message appears on the prediction page"
    )
    
    if st.button("💾 Save Deadline Message"):
        settings["deadline_message"] = deadline_msg
        save_settings(settings)
        st.success("✅ Deadline message saved!")
    
    st.markdown("---")
    
    # Current status summary
    st.markdown("#### 📋 Current Status Summary")
    
    status_data = {
        "Setting": ["Current Week", "Global Lock", "Locked Weeks", "Deadline Message"],
        "Value": [
            f"Week {settings.get('current_week', 1)}",
            "🔴 Enabled" if settings.get("global_lock") else "🟢 Disabled",
            ", ".join([str(w) for w in settings.get("locked_weeks", [])]) or "None",
            settings.get("deadline_message", "Not set")[:50] + "..."
        ]
    }
    
    st.table(pd.DataFrame(status_data))
    
    st.markdown("---")
    
    # Export/Import settings
    st.markdown("#### 📤 Export/Import Settings")
    
    col1, col2 = st.columns(2)
    
    with col1:
        settings_json = json.dumps(settings, indent=2)
        st.download_button(
            "📥 Export Settings",
            data=settings_json,
            file_name="prediction_settings.json",
            mime="application/json",
            use_container_width=True
        )
    
    with col2:
        uploaded = st.file_uploader("Import Settings", type=['json'])
        if uploaded:
            try:
                imported = json.load(uploaded)
                if st.button("Apply Imported Settings"):
                    save_settings(imported)
                    st.success("✅ Settings imported!")
                    st.rerun()
            except:
                st.error("Invalid settings file")

# Footer
st.markdown("""
<div style="text-align: center; padding: 2rem 0 1rem 0; color: #6c757d; font-size: 0.9rem; border-top: 1px solid #dee2e6; margin-top: 3rem;">
    <p><strong>Nikkang KK EPL Prediction League</strong> - Prediction Management</p>
    <p>Admin Panel | Lock Status: {}</p>
</div>
""".format("🔴 Global Lock Active" if settings.get("global_lock") else "🟢 Normal"), unsafe_allow_html=True)

"""
Admin: Deadline & Late Submission Management
Set deadlines and automatically mark late/missing predictions
"""

import streamlit as st
import json
from pathlib import Path
from datetime import datetime, timedelta
import sys

sys.path.append(str(Path(__file__).parent.parent))

from utils.auth import check_password
from utils.data_manager import DataManager
from utils.prediction_tracker import PredictionTracker

# Page config
st.set_page_config(
    page_title="Deadline Management - Admin",
    page_icon="⏰",
    layout="wide"
)

# Require admin auth
if not check_password():
    st.stop()

# Logo
if Path("nikkang_logo.png").exists():
    st.sidebar.image("nikkang_logo.png", width='stretch')
    st.sidebar.markdown("---")

st.title("⏰ Deadline & Late Submission Management")

# Initialize
dm = DataManager()
tracker = PredictionTracker(dm)

# Tabs
tab1, tab2, tab3 = st.tabs(["⚙️ Set Deadlines", "✅ Mark Late Submissions", "📊 Submission Status"])

# TAB 1: Set Deadlines
with tab1:
    st.markdown("### Set Prediction Deadlines")
    st.info("💡 Predictions submitted after the deadline will automatically be marked as late and score 0 points")
    
    # Load settings
    settings_file = Path("nikkang_data/settings.json")
    if settings_file.exists():
        with open(settings_file, 'r') as f:
            settings = json.load(f)
    else:
        settings = {}
    
    if 'deadlines' not in settings:
        settings['deadlines'] = {}
    
    # Get available weeks
    matches = dm.load_matches()
    available_weeks = sorted([int(w) for w in matches.keys() if w.isdigit()])
    
    if not available_weeks:
        st.warning("No gameweeks found. Please add matches first.")
    else:
        st.markdown("---")
        
        # Select week
        selected_week = st.selectbox("Select Gameweek:", available_weeks, format_func=lambda x: f"Week {x}")
        
        week_str = str(selected_week)
        
        # Get current deadline if exists
        current_deadline = settings['deadlines'].get(week_str)
        
        if current_deadline:
            st.success(f"✅ Current deadline: **{current_deadline}**")
            try:
                deadline_dt = datetime.strptime(current_deadline, "%Y-%m-%d %H:%M")
                if datetime.now() > deadline_dt:
                    st.warning("⚠️ This deadline has passed")
                else:
                    time_left = deadline_dt - datetime.now()
                    hours_left = int(time_left.total_seconds() / 3600)
                    st.info(f"⏳ Time remaining: ~{hours_left} hours")
            except:
                pass
        else:
            st.caption("No deadline set for this week")
        
        st.markdown("---")
        
        # Set new deadline
        st.markdown("**Set New Deadline:**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            deadline_date = st.date_input(
                "Date:",
                value=datetime.now().date() + timedelta(days=1),
                min_value=datetime.now().date()
            )
        
        with col2:
            deadline_time = st.time_input(
                "Time:",
                value=datetime.strptime("18:00", "%H:%M").time()
            )
        
        # Combine date and time
        deadline_datetime = datetime.combine(deadline_date, deadline_time)
        deadline_str = deadline_datetime.strftime("%Y-%m-%d %H:%M")
        
        st.write(f"**New deadline will be:** {deadline_str}")
        
        if st.button("💾 Save Deadline", type="primary"):
            settings['deadlines'][week_str] = deadline_str
            
            # Save settings
            settings_file.parent.mkdir(parents=True, exist_ok=True)
            with open(settings_file, 'w') as f:
                json.dump(settings, f, indent=2)
            
            st.success(f"✅ Deadline saved for Week {selected_week}: {deadline_str}")
            st.balloons()
            st.rerun()
        
        st.markdown("---")
        
        # Show all deadlines
        st.markdown("### All Deadlines:")
        
        if settings['deadlines']:
            deadline_list = []
            for week, deadline in sorted(settings['deadlines'].items(), key=lambda x: int(x[0])):
                try:
                    deadline_dt = datetime.strptime(deadline, "%Y-%m-%d %H:%M")
                    status = "❌ Passed" if datetime.now() > deadline_dt else "✅ Active"
                except:
                    status = "⚠️ Invalid"
                
                deadline_list.append({
                    'Week': f"Week {week}",
                    'Deadline': deadline,
                    'Status': status
                })
            
            st.table(deadline_list)
        else:
            st.caption("No deadlines set yet")

# TAB 2: Mark Late Submissions
with tab2:
    st.markdown("### Automatically Mark Late/Missing Submissions")
    st.info("💡 After the deadline passes, run this to mark all late and missing predictions")
    
    # Select week to process
    if not available_weeks:
        st.warning("No gameweeks found")
    else:
        selected_week_mark = st.selectbox(
            "Select Gameweek to Process:",
            available_weeks,
            format_func=lambda x: f"Week {x}",
            key="mark_week"
        )
        
        week_str_mark = str(selected_week_mark)
        
        # Check deadline
        deadline = tracker.get_deadline(selected_week_mark)
        
        if deadline:
            st.write(f"**Deadline:** {deadline.strftime('%Y-%m-%d %H:%M')}")
            
            if datetime.now() > deadline:
                st.warning(f"⚠️ Deadline has passed")
                
                # Get current status
                participants = dm.get_all_participants()
                predictions = dm.load_predictions()
                
                submitted_count = 0
                missing_count = 0
                
                for p in participants:
                    pid = p.get('id')
                    if week_str_mark in predictions and pid in predictions[week_str_mark]:
                        submitted_count += 1
                    else:
                        missing_count += 1
                
                st.write(f"**Current Status:**")
                st.write(f"- Submitted: {submitted_count}")
                st.write(f"- Missing: {missing_count}")
                
                if missing_count > 0:
                    st.markdown("---")
                    
                    if st.button(f"🔄 Mark {missing_count} Missing Predictions as Late", type="primary"):
                        marked = tracker.mark_missing_predictions_as_late(selected_week_mark)
                        
                        if marked > 0:
                            st.success(f"✅ Marked {marked} participants as late/no submission")
                            st.info("These predictions will score 0 points")
                            st.balloons()
                        else:
                            st.info("No missing predictions to mark")
                else:
                    st.success("✅ All participants have submitted predictions")
            else:
                st.info(f"⏳ Deadline hasn't passed yet. Come back after {deadline.strftime('%Y-%m-%d %H:%M')}")
        else:
            st.warning(f"⚠️ No deadline set for Week {selected_week_mark}. Please set deadline in 'Set Deadlines' tab first.")

# TAB 3: Submission Status
with tab3:
    st.markdown("### Submission Status by Week")
    
    if not available_weeks:
        st.warning("No gameweeks found")
    else:
        selected_week_status = st.selectbox(
            "Select Gameweek:",
            available_weeks,
            format_func=lambda x: f"Week {x}",
            key="status_week"
        )
        
        participants = dm.get_all_participants()
        
        st.markdown("---")
        
        # Create status table
        status_list = []
        
        for p in participants:
            participant_id = p.get('id')
            name = p.get('display_name', p.get('name', 'Unknown'))
            
            status = tracker.get_submission_status(selected_week_status, participant_id)
            
            if status['submitted']:
                if status['missed']:
                    status_text = "❌ No Submission"
                    time_text = "-"
                elif status['late']:
                    status_text = "⏰ Late"
                    time_text = status.get('submission_time', 'Unknown')
                else:
                    status_text = "✅ On Time"
                    time_text = status.get('submission_time', 'Unknown')
            else:
                status_text = "❌ Not Submitted"
                time_text = "-"
            
            status_list.append({
                'Participant': name,
                'Status': status_text,
                'Submitted At': time_text
            })
        
        st.table(status_list)
        
        # Summary
        st.markdown("---")
        st.markdown("### Summary:")
        
        on_time = sum(1 for s in status_list if '✅' in s['Status'])
        late = sum(1 for s in status_list if '⏰' in s['Status'])
        missing = sum(1 for s in status_list if '❌' in s['Status'])
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("✅ On Time", on_time)
        with col2:
            st.metric("⏰ Late", late)
        with col3:
            st.metric("❌ Missing", missing)

# Footer
st.markdown("---")
st.caption("💡 **Tip:** Late and missing submissions automatically score 0 points in weekly results")

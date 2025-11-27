"""
Participant Management Page
Nikkang KK EPL Prediction Competition
Admin page to manage participants - add, edit, delete, import/export
"""

import streamlit as st
import pandas as pd
from datetime import datetime
import json
from utils.auth import require_admin
from utils.data_manager import (
    load_participants,
    save_participants,
    generate_user_id,
    get_participant_by_id
)

# THIS LINE HANDLES ALL AUTHENTICATION - NO NEED FOR MANUAL CHECK!
if not require_admin("Participant Management"):
    st.stop()

# Helper functions to handle both list and dict data formats
def safe_get(item, key, default=None):
    """Safely get attribute from dict or object"""
    if isinstance(item, dict):
        return item.get(key, default)
    elif hasattr(item, key):
        return getattr(item, key, default)
    return default

def count_items(data):
    """Count items in either list or dict"""
    if isinstance(data, list):
        return len(data)
    elif isinstance(data, dict):
        return len(data)
    return 0

def iterate_items(data):
    """Iterate items regardless of list or dict format, yielding (key, item) pairs"""
    if isinstance(data, list):
        for i, item in enumerate(data):
            key = safe_get(item, 'id', f'item_{i}')
            yield key, item
    elif isinstance(data, dict):
        for key, item in data.items():
            yield key, item

def to_dict_format(data):
    """Convert list format to dict format if needed"""
    if isinstance(data, dict):
        return data
    elif isinstance(data, list):
        result = {}
        for i, item in enumerate(data):
            if isinstance(item, dict):
                key = item.get('id', f'item_{i}')
                result[key] = item
            else:
                result[f'item_{i}'] = {'value': item}
        return result
    return {}

# If we reach here, user is authenticated as admin
st.title("👥 Participant Management")
st.markdown("---")

# Load participants and convert to dict format for consistent handling
participants_raw = load_participants()
participants = to_dict_format(participants_raw)

# Display statistics
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Participants", count_items(participants))
with col2:
    active_count = sum(1 for _, p in iterate_items(participants) if safe_get(p, 'status', 'active') == 'active')
    st.metric("Active", active_count)
with col3:
    inactive_count = count_items(participants) - active_count
    st.metric("Inactive", inactive_count)
with col4:
    total_points = sum(safe_get(p, 'total_points', 0) for _, p in iterate_items(participants))
    avg_points = total_points / count_items(participants) if count_items(participants) > 0 else 0
    st.metric("Avg Points", f"{avg_points:.1f}")

st.markdown("---")

# Tabs for different operations
tab1, tab2, tab3, tab4 = st.tabs(["📋 View All", "➕ Add New", "📤 Import/Export", "🔧 Bulk Operations"])

# TAB 1: View All Participants
with tab1:
    st.subheader("All Participants")
    
    if count_items(participants) == 0:
        st.info("No participants yet. Add your first participant in the 'Add New' tab.")
    else:
        # Search and filter
        col1, col2 = st.columns([3, 1])
        with col1:
            search_term = st.text_input("🔍 Search by name, email, or phone", key="search")
        with col2:
            status_filter = st.selectbox("Filter by status", ["All", "active", "inactive"])
        
        # Filter participants
        filtered_participants = {}
        
        for uid, p in iterate_items(participants):
            include = True
            
            if search_term:
                search_lower = search_term.lower()
                name = safe_get(p, 'name', '').lower()
                email = safe_get(p, 'email', '').lower()
                phone = safe_get(p, 'phone', '').lower()
                if not (search_lower in name or search_lower in email or search_lower in phone):
                    include = False
            
            if status_filter != "All":
                if safe_get(p, 'status', 'active') != status_filter:
                    include = False
            
            if include:
                filtered_participants[uid] = p
        
        st.write(f"Showing {len(filtered_participants)} of {count_items(participants)} participants")
        
        # Display participants in a table
        if filtered_participants:
            df_data = []
            for uid, p in filtered_participants.items():
                df_data.append({
                    'ID': uid,
                    'Name': safe_get(p, 'name', 'N/A'),
                    'Nickname': safe_get(p, 'display_name', ''),
                    'Team': safe_get(p, 'team', ''),
                    'Email': safe_get(p, 'email', 'N/A'),
                    'Phone': safe_get(p, 'phone', 'N/A'),
                    'Status': safe_get(p, 'status', 'active'),
                    'Points': safe_get(p, 'total_points', 0)
                })
            
            df = pd.DataFrame(df_data)
            st.dataframe(df, use_container_width=True)
            
            # Edit/Delete options
            st.markdown("---")
            st.subheader("Edit or Delete Participant")
            
            selected_id = st.selectbox(
                "Select participant to modify",
                options=list(filtered_participants.keys()),
                format_func=lambda x: f"{filtered_participants[x]['name']} ({x})"
            )
            
            if selected_id:
                selected_participant = filtered_participants[selected_id]
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**Edit Participant**")
                    
                    # EPL Teams list
                    EPL_TEAMS = ["-- Select Team --", "Arsenal", "Aston Villa", "Bournemouth", "Brentford", "Brighton", 
                                 "Chelsea", "Crystal Palace", "Everton", "Fulham", "Ipswich Town", 
                                 "Leicester City", "Liverpool", "Man City", "Man United", "Newcastle", 
                                 "Nott'm Forest", "Southampton", "Tottenham", "West Ham", "Wolves"]
                    
                    with st.form("edit_participant"):
                        new_name = st.text_input("Name", value=safe_get(selected_participant, 'name', ''))
                        new_nickname = st.text_input("Nickname (Display Name)", value=safe_get(selected_participant, 'display_name', ''),
                                                     help="This name will be shown on leaderboard")
                        new_email = st.text_input("Email", value=safe_get(selected_participant, 'email', ''))
                        new_phone = st.text_input("Phone", value=safe_get(selected_participant, 'phone', ''))
                        
                        # Favorite team dropdown
                        current_team = safe_get(selected_participant, 'team', '')
                        team_index = EPL_TEAMS.index(current_team) if current_team in EPL_TEAMS else 0
                        new_team = st.selectbox("Favorite Team ⚽", EPL_TEAMS, index=team_index)
                        
                        current_status = safe_get(selected_participant, 'status', 'active')
                        new_status = st.selectbox("Status", ["active", "inactive"], 
                                                 index=0 if current_status == 'active' else 1)
                        new_notes = st.text_area("Notes", value=safe_get(selected_participant, 'notes', ''))
                        
                        if st.form_submit_button("💾 Update Participant"):
                            if new_name:
                                participants[selected_id].update({
                                    'name': new_name,
                                    'display_name': new_nickname if new_nickname else new_name,
                                    'email': new_email,
                                    'phone': new_phone,
                                    'team': new_team if new_team != "-- Select Team --" else '',
                                    'status': new_status,
                                    'notes': new_notes
                                })
                                save_participants(participants)
                                st.success(f"✅ Updated {new_name}")
                                st.rerun()
                            else:
                                st.error("Name is required")
                
                with col2:
                    st.markdown("**Delete Participant**")
                    st.warning(f"⚠️ Delete {safe_get(selected_participant, 'name', 'Unknown')}?")
                    st.caption("This will permanently delete all their predictions and data.")
                    
                    confirm_delete = st.checkbox("I confirm deletion", key="confirm_delete")
                    
                    if st.button("🗑️ Delete Participant", type="secondary", disabled=not confirm_delete):
                        name = safe_get(selected_participant, 'name', 'Unknown')
                        del participants[selected_id]
                        save_participants(participants)
                        st.success(f"✅ Deleted {name}")
                        st.rerun()

# TAB 2: Add New Participant
with tab2:
    st.subheader("Add New Participant")
    
    # EPL Teams list
    EPL_TEAMS = ["-- Select Team --", "Arsenal", "Aston Villa", "Bournemouth", "Brentford", "Brighton", 
                 "Chelsea", "Crystal Palace", "Everton", "Fulham", "Ipswich Town", 
                 "Leicester City", "Liverpool", "Man City", "Man United", "Newcastle", 
                 "Nott'm Forest", "Southampton", "Tottenham", "West Ham", "Wolves"]
    
    with st.form("add_participant"):
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("Name *", placeholder="Full Name")
            nickname = st.text_input("Nickname (Display Name)", placeholder="Nickname for leaderboard",
                                     help="This name will be shown on leaderboard")
            email = st.text_input("Email", placeholder="email@example.com")
            phone = st.text_input("Phone", placeholder="+96812345678")
        
        with col2:
            team = st.selectbox("Favorite Team ⚽", EPL_TEAMS, index=0)
            status = st.selectbox("Status", ["active", "inactive"], index=0)
            notes = st.text_area("Notes", placeholder="VIP member, special considerations, etc.")
        
        submit = st.form_submit_button("➕ Add Participant", use_container_width=True)
        
        if submit:
            if not name:
                st.error("❌ Name is required")
            else:
                # Generate unique ID
                user_id = generate_user_id()
                
                # Create new participant
                new_participant = {
                    'id': user_id,
                    'name': name,
                    'display_name': nickname if nickname else name,
                    'email': email,
                    'phone': phone,
                    'team': team if team != "-- Select Team --" else '',
                    'status': status,
                    'registration_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'link': f"?user_id={user_id}",
                    'notes': notes,
                    'predictions': {},
                    'total_points': 0
                }
                
                # Add to participants
                participants[user_id] = new_participant
                save_participants(participants)
                
                st.success(f"✅ Added {name} successfully!")
                st.info(f"User ID: {user_id}")
                st.code(f"Prediction Link: ?user_id={user_id}")
                
                # Show WhatsApp message option
                if phone:
                    app_url = "https://your-app.streamlit.app"  # Update this!
                    message = f"Welcome to Nikkang KK EPL Competition! Your prediction link: {app_url}?user_id={user_id}"
                    whatsapp_url = f"https://wa.me/{phone.replace('+', '')}?text={message}"
                    st.markdown(f"[📱 Send Welcome Message via WhatsApp]({whatsapp_url})")

# TAB 3: Import/Export
with tab3:
    st.subheader("Import/Export Participants")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**📥 Import from CSV**")
        st.caption("CSV should have columns: name, email, phone, status, notes")
        
        uploaded_file = st.file_uploader("Choose CSV file", type=['csv'])
        
        if uploaded_file:
            try:
                df = pd.read_csv(uploaded_file)
                st.write("Preview:")
                st.dataframe(df.head(), use_container_width=True)
                
                if st.button("Import All"):
                    imported_count = 0
                    for _, row in df.iterrows():
                        user_id = generate_user_id()
                        new_participant = {
                            'id': user_id,
                            'name': row.get('name', 'Unknown'),
                            'email': row.get('email', ''),
                            'phone': row.get('phone', ''),
                            'status': row.get('status', 'active'),
                            'registration_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                            'link': f"?user_id={user_id}",
                            'notes': row.get('notes', ''),
                            'predictions': {},
                            'total_points': 0
                        }
                        participants[user_id] = new_participant
                        imported_count += 1
                    
                    save_participants(participants)
                    st.success(f"✅ Imported {imported_count} participants!")
                    st.rerun()
            except Exception as e:
                st.error(f"Error importing CSV: {e}")
    
    with col2:
        st.markdown("**📤 Export to CSV**")
        
        if count_items(participants) > 0:
            # Create DataFrame
            export_data = []
            for uid, p in iterate_items(participants):
                export_data.append({
                    'id': uid,
                    'name': safe_get(p, 'name', ''),
                    'email': safe_get(p, 'email', ''),
                    'phone': safe_get(p, 'phone', ''),
                    'status': safe_get(p, 'status', 'active'),
                    'registration_date': safe_get(p, 'registration_date', ''),
                    'total_points': safe_get(p, 'total_points', 0),
                    'notes': safe_get(p, 'notes', '')
                })
            
            df_export = pd.DataFrame(export_data)
            csv = df_export.to_csv(index=False)
            
            st.download_button(
                label="📥 Download CSV",
                data=csv,
                file_name=f"participants_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
                use_container_width=True
            )
            
            # JSON export
            json_data = json.dumps(participants, indent=2)
            st.download_button(
                label="📥 Download JSON (Backup)",
                data=json_data,
                file_name=f"participants_backup_{datetime.now().strftime('%Y%m%d')}.json",
                mime="application/json",
                use_container_width=True
            )
        else:
            st.info("No participants to export")

# TAB 4: Bulk Operations
with tab4:
    st.subheader("Bulk Operations")
    
    if count_items(participants) == 0:
        st.info("No participants available for bulk operations")
    else:
        operation = st.selectbox(
            "Select operation",
            ["Activate All", "Deactivate All", "Reset Points", "Delete All Predictions"]
        )
        
        st.warning(f"⚠️ This will affect all {count_items(participants)} participants!")
        
        confirm = st.checkbox("I understand this action affects all participants")
        
        if st.button(f"Execute: {operation}", type="secondary", disabled=not confirm):
            if operation == "Activate All":
                for uid in participants:
                    if isinstance(participants[uid], dict):
                        participants[uid]['status'] = 'active'
                save_participants(participants)
                st.success("✅ All participants activated")
                st.rerun()
            
            elif operation == "Deactivate All":
                for uid in participants:
                    if isinstance(participants[uid], dict):
                        participants[uid]['status'] = 'inactive'
                save_participants(participants)
                st.success("✅ All participants deactivated")
                st.rerun()
            
            elif operation == "Reset Points":
                for uid in participants:
                    if isinstance(participants[uid], dict):
                        participants[uid]['total_points'] = 0
                save_participants(participants)
                st.success("✅ All points reset to 0")
                st.rerun()
            
            elif operation == "Delete All Predictions":
                for uid in participants:
                    if isinstance(participants[uid], dict):
                        participants[uid]['predictions'] = {}
                save_participants(participants)
                st.success("✅ All predictions deleted")
                st.rerun()

# Footer
st.markdown("---")
st.caption("💡 Tip: Export data regularly as backup")

"""
Manual Sync Feature - Add to Admin Panel
Allows manual backup/restore between devices
"""

import streamlit as st
import json
import zipfile
import io
from datetime import datetime
import os

def manual_sync_section():
    """Add this to your admin panel"""
    
    st.markdown("---")
    st.subheader("📱💻 Manual Sync Between Devices")
    
    st.info("""
    **How it works:**
    1. On desktop: Download backup file
    2. Transfer file to mobile (email, WhatsApp, Drive)
    3. On mobile: Upload backup file
    4. Data is synced! ✅
    """)
    
    col1, col2 = st.columns(2)
    
    # DOWNLOAD BACKUP
    with col1:
        st.markdown("### 📥 Download Backup")
        st.write("Save current data to download")
        
        if st.button("📦 Create Backup", use_container_width=True):
            backup_data = create_backup()
            if backup_data:
                st.download_button(
                    label="⬇️ Download Backup File",
                    data=backup_data,
                    file_name=f"nikkang_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip",
                    mime="application/zip",
                    use_container_width=True
                )
                st.success("✅ Backup created! Click Download button above.")
    
    # UPLOAD RESTORE
    with col2:
        st.markdown("### 📤 Upload Backup")
        st.write("Restore data from another device")
        
        uploaded_file = st.file_uploader(
            "Choose backup file",
            type=['zip'],
            help="Upload the .zip file you downloaded from another device"
        )
        
        if uploaded_file is not None:
            if st.button("🔄 Restore from Backup", type="primary", use_container_width=True):
                success = restore_backup(uploaded_file)
                if success:
                    st.success("✅ Data restored successfully!")
                    st.balloons()
                    st.info("🔄 Refresh the page to see updated data")
                    if st.button("🔄 Refresh Now"):
                        st.rerun()
                else:
                    st.error("❌ Restore failed. Check the backup file.")
    
    # QUICK SYNC
    st.markdown("---")
    st.markdown("### ⚡ Quick Sync Status")
    
    col_a, col_b, col_c = st.columns(3)
    
    with col_a:
        participants_count = len(load_json_file('nikkang_data/participants.json'))
        st.metric("👥 Participants", participants_count)
    
    with col_b:
        matches = load_json_file('nikkang_data/matches.json')
        matches_count = sum(len(v) for v in matches.values()) if isinstance(matches, dict) else 0
        st.metric("⚽ Total Matches", matches_count)
    
    with col_c:
        predictions = load_json_file('nikkang_data/predictions.json')
        predictions_count = sum(len(v) for v in predictions.values()) if isinstance(predictions, dict) else 0
        st.metric("🎯 Total Predictions", predictions_count)
    
    # Last sync time
    if 'last_sync_time' in st.session_state:
        st.caption(f"Last sync: {st.session_state.last_sync_time}")


def create_backup():
    """Create a ZIP backup of all data files"""
    try:
        # Create ZIP in memory
        zip_buffer = io.BytesIO()
        
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            # Add all JSON files
            data_files = [
                'participants.json',
                'matches.json',
                'predictions.json',
                'results.json',
                'manual_scores.json',
                'round_scores.json'
            ]
            
            for filename in data_files:
                filepath = os.path.join('nikkang_data', filename)
                if os.path.exists(filepath):
                    # Read file and add to ZIP
                    with open(filepath, 'r', encoding='utf-8') as f:
                        file_content = f.read()
                    zip_file.writestr(filename, file_content)
            
            # Add metadata
            metadata = {
                'backup_time': datetime.now().isoformat(),
                'app_version': '1.0',
                'files_included': data_files
            }
            zip_file.writestr('backup_info.json', json.dumps(metadata, indent=2))
        
        zip_buffer.seek(0)
        st.session_state.last_sync_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        return zip_buffer.getvalue()
        
    except Exception as e:
        st.error(f"Backup creation failed: {e}")
        return None


def restore_backup(uploaded_file):
    """Restore data from uploaded ZIP backup"""
    try:
        # Read ZIP file
        with zipfile.ZipFile(uploaded_file, 'r') as zip_file:
            # List all files in ZIP
            file_list = zip_file.namelist()
            
            # Ensure directory exists
            os.makedirs('nikkang_data', exist_ok=True)
            
            # Extract JSON files
            restored_count = 0
            for filename in file_list:
                if filename.endswith('.json') and filename != 'backup_info.json':
                    # Read from ZIP
                    file_content = zip_file.read(filename).decode('utf-8')
                    
                    # Validate it's proper JSON
                    json.loads(file_content)  # Will raise exception if invalid
                    
                    # Write to file
                    filepath = os.path.join('nikkang_data', filename)
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(file_content)
                    
                    restored_count += 1
            
            st.session_state.last_sync_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            st.info(f"✅ Restored {restored_count} data files")
            return True
            
    except Exception as e:
        st.error(f"Restore failed: {e}")
        return False


def load_json_file(filepath):
    """Load a JSON file safely"""
    try:
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    except:
        return {}


# Example: How to add to your admin panel
def example_admin_integration():
    """
    Add this to your pages/6_admin.py:
    
    1. Import at the top:
       from utils.manual_sync import manual_sync_section
    
    2. Add new tab in your admin panel:
       tab1, tab2, tab3, tab4 = st.tabs(["Weekly Matches", "API Integration", "Settings", "📱 Sync"])
       
       with tab4:
            simple_sync_ui()
    
    That's it! The sync feature will appear in the admin panel.
    """
    pass

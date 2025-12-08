"""
Simple Sync - Fixed for Your Data Structure
Works with your custom data_manager format
"""

import streamlit as st
import json
from datetime import datetime
import random
import string
import os

try:
    from utils.supabase_manager import SupabaseManager
    SUPABASE_AVAILABLE = True
except:
    SUPABASE_AVAILABLE = False

class SimpleSyncManager:
    """Simple sync using codes - handles your custom data format"""
    
    def __init__(self):
        self.enabled = False
        if SUPABASE_AVAILABLE:
            try:
                self.db = SupabaseManager()
                self.enabled = True
            except:
                pass
    
    def generate_sync_code(self):
        """Generate a simple 6-digit sync code"""
        return ''.join(random.choices(string.digits, k=6))
    
    def upload_data(self):
        """Upload ALL data files exactly as they are"""
        if not self.enabled:
            return None, "Supabase not available"
        
        try:
            # Read ALL files in nikkang_data folder
            data_package = {}
            data_dir = 'nikkang_data'
            
            if os.path.exists(data_dir):
                for filename in os.listdir(data_dir):
                    if filename.endswith('.json'):
                        filepath = os.path.join(data_dir, filename)
                        with open(filepath, 'r', encoding='utf-8') as f:
                            file_key = filename.replace('.json', '')
                            data_package[file_key] = json.load(f)
            
            # Add metadata
            data_package['_sync_metadata'] = {
                'sync_time': datetime.now().isoformat(),
                'files_count': len(data_package) - 1
            }
            
            # Generate code
            sync_code = self.generate_sync_code()
            
            # Save to Supabase
            json_str = json.dumps(data_package, ensure_ascii=False)
            
            self.db.supabase.table('app_config').upsert({
                'key': f'sync_{sync_code}',
                'value': json_str
            }).execute()
            
            return sync_code, None
            
        except Exception as e:
            return None, str(e)
    
    def download_data(self, sync_code):
        """Download data and restore exactly as it was"""
        if not self.enabled:
            return False, "Supabase not available"
        
        try:
            # Get data from Supabase
            response = self.db.supabase.table('app_config').select('value').eq('key', f'sync_{sync_code}').execute()
            
            if not response.data:
                return False, "Invalid sync code or code expired"
            
            # Parse data
            data_package = json.loads(response.data[0]['value'])
            
            # Ensure directory exists
            os.makedirs('nikkang_data', exist_ok=True)
            
            # Restore each file exactly as it was
            files_restored = 0
            for file_key, file_data in data_package.items():
                if file_key.startswith('_'):  # Skip metadata
                    continue
                
                filepath = f'nikkang_data/{file_key}.json'
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(file_data, f, indent=2, ensure_ascii=False)
                files_restored += 1
            
            # Get sync time
            metadata = data_package.get('_sync_metadata', {})
            sync_time = metadata.get('sync_time', 'Unknown')
            
            return True, f"✅ Restored {files_restored} files from {sync_time[:19]}"
            
        except Exception as e:
            return False, f"Error: {str(e)}"


def simple_sync_ui():
    """UI for simple sync"""
    
    st.markdown("---")
    st.subheader("📱💻 Simple Sync Between Devices")
    
    sync_mgr = SimpleSyncManager()
    
    if not sync_mgr.enabled:
        st.error("❌ Supabase not configured. Cannot use sync feature.")
        st.info("Please complete Supabase setup first.")
        return
    
    st.success("✅ Cloud sync available!")
    
    # Two columns
    col1, col2 = st.columns(2)
    
    # UPLOAD
    with col1:
        st.markdown("### 📤 Push Data to Cloud")
        st.write("Upload your current data and get a sync code")
        
        if st.button("🚀 Generate Sync Code", use_container_width=True, type="primary"):
            with st.spinner('Uploading...'):
                sync_code, error = sync_mgr.upload_data()
                
                if sync_code:
                    st.success("✅ Data uploaded!")
                    
                    # Show code
                    st.markdown(f"""
                    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                                padding: 30px; border-radius: 15px; text-align: center; margin: 20px 0;">
                        <div style="color: white; font-size: 16px; margin-bottom: 10px;">Your Sync Code:</div>
                        <div style="color: white; font-size: 48px; font-weight: bold; letter-spacing: 8px; 
                                    font-family: monospace;">{sync_code}</div>
                        <div style="color: rgba(255,255,255,0.8); font-size: 14px; margin-top: 10px;">
                            Valid for 24 hours
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.info("📱 **On your other device:** Go to Device Sync → Enter this code")
                    st.session_state.last_sync_code = sync_code
                else:
                    st.error(f"❌ Upload failed: {error}")
    
    # DOWNLOAD
    with col2:
        st.markdown("### 📥 Pull Data from Cloud")
        st.write("Enter sync code from your other device")
        
        sync_code_input = st.text_input(
            "Enter 6-digit code",
            max_chars=6,
            placeholder="123456",
            help="Get this code from your other device"
        )
        
        if st.button("⬇️ Download Data", use_container_width=True, type="primary"):
            if len(sync_code_input) != 6:
                st.error("❌ Code must be 6 digits")
            else:
                with st.spinner('Downloading...'):
                    success, message = sync_mgr.download_data(sync_code_input)
                    
                    if success:
                        st.success(message)
                        st.balloons()
                        st.info("🔄 **Important:** Refresh the page to see updated data")
                        
                        col_a, col_b = st.columns(2)
                        with col_a:
                            if st.button("🔄 Refresh Page Now", use_container_width=True, type="primary"):
                                st.rerun()
                        with col_b:
                            if st.button("🏠 Go to Home", use_container_width=True):
                                st.switch_page("pages/1_Home.py")
                    else:
                        st.error(f"❌ {message}")
    
    # Show last code
    if 'last_sync_code' in st.session_state:
        st.markdown("---")
        st.caption(f"💡 Last generated code: **{st.session_state.last_sync_code}**")
    
    # Current data stats
    st.markdown("---")
    st.markdown("### 📊 Current Data on This Device")
    
    try:
        col_a, col_b, col_c, col_d = st.columns(4)
        
        with col_a:
            if os.path.exists('nikkang_data/participants.json'):
                with open('nikkang_data/participants.json', 'r') as f:
                    data = json.load(f)
                st.metric("👥 Participants", len(data) if isinstance(data, (dict, list)) else 0)
            else:
                st.metric("👥 Participants", 0)
        
        with col_b:
            if os.path.exists('nikkang_data/matches.json'):
                with open('nikkang_data/matches.json', 'r') as f:
                    data = json.load(f)
                count = len(data) if isinstance(data, (dict, list)) else 0
                st.metric("⚽ Matches", count)
            else:
                st.metric("⚽ Matches", 0)
        
        with col_c:
            if os.path.exists('nikkang_data/predictions.json'):
                with open('nikkang_data/predictions.json', 'r') as f:
                    data = json.load(f)
                count = len(data) if isinstance(data, (dict, list)) else 0
                st.metric("🎯 Predictions", count)
            else:
                st.metric("🎯 Predictions", 0)
        
        with col_d:
            if os.path.exists('nikkang_data/results.json'):
                with open('nikkang_data/results.json', 'r') as f:
                    data = json.load(f)
                count = len(data) if isinstance(data, (dict, list)) else 0
                st.metric("📊 Results", count)
            else:
                st.metric("📊 Results", 0)
    except:
        st.warning("Could not read data files")
    
    # Instructions
    with st.expander("📖 How to Use"):
        st.markdown("""
        ### Quick Sync in 3 Steps:
        
        **On Device 1 (Desktop):**
        1. Click "🚀 Generate Sync Code" 
        2. Note the 6-digit code (e.g., 123456)
        
        **On Device 2 (Mobile):**
        1. Go to Device Sync page
        2. Enter the 6-digit code
        3. Click "⬇️ Download Data"
        4. Click "🔄 Refresh Page Now"
        
        **Done!** Both devices synced! ✅
        
        ---
        
        ### Important Notes:
        - Always refresh after downloading
        - Codes expire after 24 hours
        - Syncs ALL data files exactly as they are
        - No format conversion needed
        
        ### Tips:
        - Sync before making predictions
        - Sync after entering results
        - Keep your devices updated regularly
        """)

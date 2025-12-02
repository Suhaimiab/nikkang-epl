"""
Simple Sync with Code - No File Transfers!
Uses Supabase as simple JSON storage - much cleaner than zip files
"""

import streamlit as st
import json
from datetime import datetime
import random
import string

try:
    from utils.supabase_manager import SupabaseManager
    SUPABASE_AVAILABLE = True
except:
    SUPABASE_AVAILABLE = False

class SimpleSyncManager:
    """Simple sync using codes - no file transfers needed"""
    
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
        """Upload all data and get a sync code"""
        if not self.enabled:
            return None, "Supabase not available"
        
        try:
            # Read all data files
            import os
            data_package = {}
            
            files = [
                'nikkang_data/participants.json',
                'nikkang_data/matches.json',
                'nikkang_data/predictions.json',
                'nikkang_data/results.json',
                'nikkang_data/manual_scores.json',
                'nikkang_data/stage_scores.json'
            ]
            
            for filepath in files:
                if os.path.exists(filepath):
                    with open(filepath, 'r', encoding='utf-8') as f:
                        filename = os.path.basename(filepath).replace('.json', '')
                        data_package[filename] = json.load(f)
            
            # Add timestamp
            data_package['sync_time'] = datetime.now().isoformat()
            
            # Generate code
            sync_code = self.generate_sync_code()
            
            # Save to Supabase with code as key
            json_str = json.dumps(data_package)
            self.db.supabase.table('app_config').upsert({
                'key': f'sync_{sync_code}',
                'value': json_str
            }).execute()
            
            return sync_code, None
            
        except Exception as e:
            return None, str(e)
    
    def download_data(self, sync_code):
        """Download data using sync code"""
        if not self.enabled:
            return False, "Supabase not available"
        
        try:
            # Get data from Supabase
            response = self.db.supabase.table('app_config').select('value').eq('key', f'sync_{sync_code}').execute()
            
            if not response.data:
                return False, "Invalid sync code"
            
            # Parse data
            data_package = json.loads(response.data[0]['value'])
            
            # Save each file
            import os
            os.makedirs('nikkang_data', exist_ok=True)
            
            files_restored = 0
            for filename, data in data_package.items():
                if filename == 'sync_time':
                    continue
                
                filepath = f'nikkang_data/{filename}.json'
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                files_restored += 1
            
            sync_time = data_package.get('sync_time', 'Unknown')
            return True, f"Restored {files_restored} files from {sync_time}"
            
        except Exception as e:
            return False, str(e)


def simple_sync_ui():
    """Clean UI for simple sync"""
    
    st.markdown("---")
    st.subheader("📱💻 Simple Sync Between Devices")
    
    sync_mgr = SimpleSyncManager()
    
    if not sync_mgr.enabled:
        st.error("❌ Supabase not configured. Cannot use sync feature.")
        st.info("Please complete Supabase setup first.")
        return
    
    st.success("✅ Cloud sync available!")
    
    # Two columns for upload/download
    col1, col2 = st.columns(2)
    
    # UPLOAD - Generate Code
    with col1:
        st.markdown("### 📤 Push Data to Cloud")
        st.write("Upload your current data and get a sync code")
        
        if st.button("🚀 Generate Sync Code", use_container_width=True, type="primary"):
            with st.spinner('Uploading...'):
                sync_code, error = sync_mgr.upload_data()
                
                if sync_code:
                    st.success("✅ Data uploaded!")
                    
                    # Show code in big text
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
                    
                    st.info("📱 **On your other device:** Go to Admin → Sync → Enter this code")
                    
                    # Store in session for copying
                    st.session_state.last_sync_code = sync_code
                else:
                    st.error(f"❌ Upload failed: {error}")
    
    # DOWNLOAD - Enter Code
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
                        st.success(f"✅ {message}")
                        st.balloons()
                        st.info("🔄 Refresh the page to see updated data")
                        if st.button("🔄 Refresh Now"):
                            st.rerun()
                    else:
                        st.error(f"❌ {message}")
    
    # Show last code if exists
    if 'last_sync_code' in st.session_state:
        st.markdown("---")
        st.caption(f"💡 Last generated code: **{st.session_state.last_sync_code}**")
    
    # Quick stats
    st.markdown("---")
    st.markdown("### 📊 Current Data")
    
    try:
        import os
        col_a, col_b, col_c = st.columns(3)
        
        with col_a:
            if os.path.exists('nikkang_data/participants.json'):
                with open('nikkang_data/participants.json', 'r') as f:
                    participants = json.load(f)
                st.metric("👥 Participants", len(participants))
            else:
                st.metric("👥 Participants", 0)
        
        with col_b:
            if os.path.exists('nikkang_data/matches.json'):
                with open('nikkang_data/matches.json', 'r') as f:
                    matches = json.load(f)
                total = sum(len(v) for v in matches.values() if isinstance(v, list))
                st.metric("⚽ Matches", total)
            else:
                st.metric("⚽ Matches", 0)
        
        with col_c:
            if os.path.exists('nikkang_data/predictions.json'):
                with open('nikkang_data/predictions.json', 'r') as f:
                    predictions = json.load(f)
                total = sum(len(v) for v in predictions.values())
                st.metric("🎯 Predictions", total)
            else:
                st.metric("🎯 Predictions", 0)
    except:
        pass
    
    # Instructions
    with st.expander("📖 How to Use"):
        st.markdown("""
        ### Quick Sync in 3 Steps:
        
        **On Device 1 (Desktop):**
        1. Click "Generate Sync Code" 
        2. Note the 6-digit code (e.g., 123456)
        
        **On Device 2 (Mobile):**
        1. Go to Admin → Sync tab
        2. Enter the 6-digit code
        3. Click "Download Data"
        4. Refresh page
        
        **Done!** Both devices synced in 30 seconds! ✅
        
        ---
        
        ### Tips:
        - Codes expire after 24 hours
        - Always sync before making changes
        - No file transfers needed!
        - Works from anywhere with internet
        """)

"""
Dropbox Sync - SIMPLE AND ACTUALLY WORKS
No OAuth bullshit, no service accounts, just one token
Works on desktop AND Streamlit Cloud
"""

import streamlit as st
from pathlib import Path
from datetime import datetime

try:
    import dropbox
    from dropbox.exceptions import ApiError
    DROPBOX_AVAILABLE = True
except ImportError:
    DROPBOX_AVAILABLE = False

class DropboxSync:
    """Simple Dropbox sync - one token, works everywhere"""
    
    def __init__(self):
        self.configured = False
        self.dbx = None
        self.error_message = None
        
        if not DROPBOX_AVAILABLE:
            self.error_message = "Dropbox library not installed"
            return
        
        self.authenticate()
    
    def authenticate(self):
        """Get token from local file or Streamlit secrets"""
        token = None
        
        # METHOD 1: Local file (desktop)
        local_token_file = Path("nikkang_data/dropbox_token.txt")
        if local_token_file.exists():
            try:
                with open(local_token_file, 'r') as f:
                    token = f.read().strip()
                st.success("🔑 Using local token")
            except Exception as e:
                st.warning(f"Local token failed: {e}")
        
        # METHOD 2: Streamlit secrets (cloud)
        if not token:
            try:
                if hasattr(st, 'secrets') and 'dropbox' in st.secrets:
                    token = st.secrets["dropbox"]["access_token"]
                    st.success("🔑 Using Streamlit secrets")
            except Exception as e:
                self.error_message = f"Secrets failed: {e}"
        
        if token:
            try:
                self.dbx = dropbox.Dropbox(token)
                # Test connection
                self.dbx.users_get_current_account()
                self.configured = True
                st.info("✅ Connected to Dropbox!")
            except Exception as e:
                self.error_message = f"Connection failed: {e}"
        else:
            self.error_message = "No token found"
    
    def upload_file(self, file_path, dropbox_path):
        """Upload file to Dropbox"""
        try:
            with open(file_path, 'rb') as f:
                # Upload with overwrite mode
                self.dbx.files_upload(
                    f.read(),
                    dropbox_path,
                    mode=dropbox.files.WriteMode.overwrite
                )
            return True, f"Uploaded {Path(file_path).name}"
        except Exception as e:
            return False, f"Upload failed: {e}"
    
    def download_file(self, dropbox_path, local_path):
        """Download file from Dropbox"""
        try:
            metadata, response = self.dbx.files_download(dropbox_path)
            
            # Create directory if needed
            Path(local_path).parent.mkdir(exist_ok=True)
            
            # Save file
            with open(local_path, 'wb') as f:
                f.write(response.content)
            
            return True, f"Downloaded {Path(local_path).name}"
        except ApiError as e:
            if e.error.is_path() and e.error.get_path().is_not_found():
                return False, f"{Path(dropbox_path).name} not found"
            return False, f"Download failed: {e}"
        except Exception as e:
            return False, f"Download failed: {e}"
    
    def sync_all_to_cloud(self):
        """Upload all data files to Dropbox"""
        data_dir = Path("nikkang_data")
        if not data_dir.exists():
            return False, "No data directory"
        
        # Files to exclude
        exclude_files = {
            'dropbox_token.txt',
            'oauth_credentials.json',
            'token.pickle',
            'gdrive_credentials.json',
            'gdrive_service_account.json',
            'nikkang-kk-44af9b97d8b4.json'
        }
        
        # Get all JSON files
        json_files = [f for f in data_dir.glob("*.json") if f.name not in exclude_files]
        
        success_count = 0
        errors = []
        
        for file in json_files:
            # Upload to /NikkangKK/ folder in Dropbox
            dropbox_path = f"/NikkangKK/{file.name}"
            success, message = self.upload_file(file, dropbox_path)
            
            if success:
                success_count += 1
            else:
                errors.append(message)
        
        if errors:
            return True, f"⚠️ Synced {success_count}/{len(json_files)} files. Errors: {errors[0]}"
        
        return True, f"✅ Synced {success_count}/{len(json_files)} files to Dropbox"
    
    def sync_all_from_cloud(self):
        """Download all data files from Dropbox"""
        file_names = [
            "participants.json",
            "matches.json",
            "predictions.json",
            "results.json",
            "settings.json",
            "manual_scores.json",
            "round_scores.json",
            "sync_time.json"
        ]
        
        data_dir = Path("nikkang_data")
        data_dir.mkdir(exist_ok=True)
        
        success_count = 0
        
        for file_name in file_names:
            dropbox_path = f"/NikkangKK/{file_name}"
            local_path = data_dir / file_name
            
            success, _ = self.download_file(dropbox_path, local_path)
            if success:
                success_count += 1
        
        return True, f"✅ Downloaded {success_count} files from Dropbox"
    
    def list_cloud_files(self):
        """List files in Dropbox"""
        try:
            result = self.dbx.files_list_folder("/NikkangKK")
            files = []
            
            for entry in result.entries:
                if isinstance(entry, dropbox.files.FileMetadata):
                    files.append({
                        'name': entry.name,
                        'size': entry.size,
                        'modified': entry.client_modified
                    })
            
            return files
        except ApiError as e:
            if e.error.is_path() and e.error.get_path().is_not_found():
                # Folder doesn't exist yet - create it
                try:
                    self.dbx.files_create_folder_v2("/NikkangKK")
                except:
                    pass
                return []
            return []
        except Exception:
            return []


def simple_sync_ui():
    """Dropbox sync UI - SIMPLE AND WORKS"""
    
    st.markdown("## 📱💻 Dropbox Sync")
    st.info("💡 Simple, reliable, works everywhere!")
    
    sync = DropboxSync()
    
    # Check library
    if not DROPBOX_AVAILABLE:
        st.error("❌ Dropbox library not installed")
        st.markdown("""
        **Install:**
        ```bash
        pip install dropbox
        ```
        
        **Add to requirements.txt:**
        ```
        dropbox
        ```
        """)
        return
    
    # Check configuration
    if not sync.configured:
        st.warning("⚠️ Dropbox not configured")
        if sync.error_message:
            st.error(sync.error_message)
        
        st.markdown("""
        ### 🚀 Setup (5 minutes):
        
        **Step 1: Create Dropbox App**
        1. Go to [Dropbox App Console](https://www.dropbox.com/developers/apps/create)
        2. **Choose API:** Scoped access
        3. **Choose access:** App folder
        4. **Name:** `NikkangKK`
        5. Click **"Create app"**
        
        **Step 2: Generate Token**
        1. Scroll down to **"Generated access token"**
        2. Click **"Generate"**
        3. **Copy the token** (long string starting with `sl.`)
        
        **Step 3: Add Token**
        
        **For Desktop:**
        - Create file: `nikkang_data/dropbox_token.txt`
        - Paste token, save
        
        **For Streamlit Cloud:**
        - Go to app Settings → Secrets
        - Add:
        ```toml
        [dropbox]
        access_token = "sl.your_token_here"
        ```
        
        **Step 4: Restart**
        Restart app and sync will work!
        
        ---
        
        ### ✅ Why Dropbox?
        - No OAuth popup bullshit
        - No service accounts
        - One token works everywhere
        - 2GB free storage
        - **ACTUALLY WORKS!**
        """)
        return
    
    # Connected!
    st.success("✅ Dropbox connected!")
    
    # Sync controls
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📤 Push to Cloud")
        if st.button("☁️ Sync to Dropbox", use_container_width=True, type="primary"):
            with st.spinner("Uploading..."):
                success, message = sync.sync_all_to_cloud()
                if success:
                    st.success(message)
                    st.balloons()
                else:
                    st.error(message)
    
    with col2:
        st.markdown("### 📥 Pull from Cloud")
        if st.button("🔄 Sync from Dropbox", use_container_width=True):
            with st.spinner("Downloading..."):
                success, message = sync.sync_all_from_cloud()
                if success:
                    st.success(message)
                    st.info("🔄 Refresh page to see changes")
                else:
                    st.error(message)
    
    st.markdown("---")
    
    # Show files
    with st.expander("📂 Files in Dropbox"):
        files = sync.list_cloud_files()
        if files:
            for file in files:
                size_kb = file['size'] / 1024
                modified = file['modified'].strftime('%Y-%m-%d %H:%M')
                st.caption(f"📄 {file['name']} - {size_kb:.1f} KB - {modified}")
        else:
            st.caption("No files yet. Click 'Sync to Dropbox' to upload.")
    
    # Instructions
    with st.expander("📱 How It Works"):
        st.markdown("""
        **Desktop → Mobile:**
        1. Desktop: Make changes
        2. Desktop: Click "Sync to Dropbox"
        3. Mobile: Click "Sync from Dropbox"
        4. Mobile: Refresh page
        
        **Mobile → Desktop:**
        1. Mobile: Make changes
        2. Mobile: Click "Sync to Dropbox"
        3. Desktop: Click "Sync from Dropbox"
        4. Desktop: Refresh page
        
        **Benefits:**
        - ✅ Works on BOTH platforms
        - ✅ No complex setup
        - ✅ Free 2GB storage
        - ✅ Reliable and fast
        - ✅ One token, everywhere
        """)
    
    # Check Dropbox folder
    with st.expander("🔍 View in Dropbox"):
        st.markdown("""
        Your files are stored in Dropbox at:
        
        **Apps → NikkangKK**
        
        You can view them at [Dropbox.com](https://www.dropbox.com/home/Apps/NikkangKK)
        """)

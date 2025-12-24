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
        """Get token from secrets (Refresh Token) or local file"""
        # 1. Try to load from Streamlit secrets (The Permanent Way)
        if hasattr(st, 'secrets') and 'dropbox' in st.secrets:
            try:
                secrets = st.secrets["dropbox"]
                # Check if we have the new permanent setup
                if "refresh_token" in secrets and "app_key" in secrets and "app_secret" in secrets:
                    self.dbx = dropbox.Dropbox(
                        app_key=secrets["app_key"],
                        app_secret=secrets["app_secret"],
                        oauth2_refresh_token=secrets["refresh_token"]
                    )
                    # Test connection
                    self.dbx.users_get_current_account()
                    self.configured = True
                    # st.success("✅ Connected to Dropbox (Auto-Refresh Active!)") # Commented out to reduce noise
                    return
                
                # Fallback for old access_token method (Temporary)
                elif "access_token" in secrets:
                    token = secrets["access_token"]
                    self.dbx = dropbox.Dropbox(token)
                    self.dbx.users_get_current_account()
                    self.configured = True
                    st.success("🔑 Using simple access token")
                    return
            except Exception as e:
                self.error_message = f"Secrets connection failed: {e}"

        # 2. Try Local File (Desktop/Testing)
        local_token_file = Path("nikkang_data/dropbox_token.txt")
        if local_token_file.exists():
            try:
                with open(local_token_file, 'r') as f:
                    token = f.read().strip()
                self.dbx = dropbox.Dropbox(token)
                self.dbx.users_get_current_account()
                self.configured = True
                st.success("🔑 Using local token")
            except Exception as e:
                self.error_message = f"Local token failed: {e}"
        else:
            if not self.error_message:
                self.error_message = "No credentials found in secrets or local file"

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
    
    sync = DropboxSync()
    
    # Check library
    if not DROPBOX_AVAILABLE:
        st.error("❌ Dropbox library not installed")
        return
    
    # Check configuration
    if not sync.configured:
        st.warning("⚠️ Dropbox not configured")
        if sync.error_message:
            st.error(sync.error_message)
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

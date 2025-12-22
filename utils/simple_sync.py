"""
Google Drive Sync - Streamlit Cloud Compatible
Uses Streamlit secrets for credentials (no browser popup needed)
"""

import streamlit as st
import json
from pathlib import Path
from datetime import datetime
import pickle

# Try to import Google Drive libraries
try:
    from google.oauth2.credentials import Credentials
    from google.oauth2 import service_account
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
    import io
    GDRIVE_AVAILABLE = True
except ImportError:
    GDRIVE_AVAILABLE = False

SCOPES = ['https://www.googleapis.com/auth/drive.file']

class GoogleDriveSync:
    """Google Drive cloud sync - Streamlit Cloud compatible"""
    
    def __init__(self):
        self.configured = False
        self.service = None
        self.folder_id = None
        self.error_message = None
        
        if not GDRIVE_AVAILABLE:
            self.error_message = "Google Drive libraries not installed"
            return
        
        # Try to authenticate using Streamlit secrets (for cloud deployment)
        self.authenticate()
    
    def authenticate(self):
        """Authenticate with Google Drive using service account from secrets"""
        try:
            # Try service account from Streamlit secrets
            if hasattr(st, 'secrets') and 'gcp_service_account' in st.secrets:
                credentials = service_account.Credentials.from_service_account_info(
                    st.secrets["gcp_service_account"],
                    scopes=SCOPES
                )
                
                self.service = build('drive', 'v3', credentials=credentials)
                self.configured = True
                self.folder_id = self.get_or_create_folder("NikkangKK_Sync")
                return
                
        except Exception as e:
            self.error_message = f"Service account auth failed: {str(e)}"
        
        # Service account not available - show setup instructions
        self.error_message = "Google Drive not configured in Streamlit secrets"
    
    def get_or_create_folder(self, folder_name):
        """Get or create a folder in Google Drive"""
        try:
            response = self.service.files().list(
                q=f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false",
                spaces='drive',
                fields='files(id, name)'
            ).execute()
            
            folders = response.get('files', [])
            
            if folders:
                return folders[0]['id']
            
            file_metadata = {
                'name': folder_name,
                'mimeType': 'application/vnd.google-apps.folder'
            }
            
            folder = self.service.files().create(
                body=file_metadata,
                fields='id'
            ).execute()
            
            return folder.get('id')
            
        except Exception as e:
            st.error(f"Folder error: {e}")
            return None
    
    def upload_file(self, file_path, file_name=None):
        """Upload a file to Google Drive"""
        if not file_name:
            file_name = Path(file_path).name
        
        try:
            response = self.service.files().list(
                q=f"name='{file_name}' and '{self.folder_id}' in parents and trashed=false",
                spaces='drive',
                fields='files(id, name)'
            ).execute()
            
            files = response.get('files', [])
            
            file_metadata = {
                'name': file_name,
                'parents': [self.folder_id]
            }
            
            media = MediaFileUpload(file_path, mimetype='application/json')
            
            if files:
                file = self.service.files().update(
                    fileId=files[0]['id'],
                    media_body=media
                ).execute()
            else:
                file = self.service.files().create(
                    body=file_metadata,
                    media_body=media,
                    fields='id'
                ).execute()
            
            return True, f"Uploaded {file_name}"
            
        except Exception as e:
            return False, f"Upload failed: {str(e)}"
    
    def download_file(self, file_name, destination_path):
        """Download a file from Google Drive"""
        try:
            response = self.service.files().list(
                q=f"name='{file_name}' and '{self.folder_id}' in parents and trashed=false",
                spaces='drive',
                fields='files(id, name)'
            ).execute()
            
            files = response.get('files', [])
            
            if not files:
                return False, f"{file_name} not found"
            
            request = self.service.files().get_media(fileId=files[0]['id'])
            fh = io.BytesIO()
            downloader = MediaIoBaseDownload(fh, request)
            
            done = False
            while not done:
                status, done = downloader.next_chunk()
            
            Path(destination_path).parent.mkdir(exist_ok=True)
            with open(destination_path, 'wb') as f:
                f.write(fh.getvalue())
            
            return True, f"Downloaded {file_name}"
            
        except Exception as e:
            return False, f"Download failed: {str(e)}"
    
    def sync_all_to_cloud(self):
        """Upload all local files to Google Drive"""
        data_dir = Path("nikkang_data")
        
        if not data_dir.exists():
            return False, "No data directory"
        
        json_files = [f for f in data_dir.glob("*.json") if 'credentials' not in f.name and 'token' not in f.name]
        success_count = 0
        
        for file in json_files:
            success, _ = self.upload_file(file)
            if success:
                success_count += 1
        
        return True, f"✅ Synced {success_count} files to Google Drive"
    
    def sync_all_from_cloud(self):
        """Download all files from Google Drive"""
        file_names = [
            "participants.json",
            "matches.json",
            "predictions.json",
            "results.json",
            "settings.json",
            "season_predictions.json"
        ]
        
        data_dir = Path("nikkang_data")
        data_dir.mkdir(exist_ok=True)
        
        success_count = 0
        
        for file_name in file_names:
            destination = data_dir / file_name
            success, _ = self.download_file(file_name, destination)
            if success:
                success_count += 1
        
        return True, f"✅ Downloaded {success_count} files"
    
    def list_cloud_files(self):
        """List files in Google Drive"""
        try:
            response = self.service.files().list(
                q=f"'{self.folder_id}' in parents and trashed=false",
                spaces='drive',
                fields='files(id, name, modifiedTime, size)',
                orderBy='modifiedTime desc'
            ).execute()
            
            return response.get('files', [])
        except:
            return []


def simple_sync_ui():
    """Google Drive sync UI for Streamlit Cloud"""
    
    st.markdown("## 📱💻 Mobile Sync via Google Drive")
    st.info("💡 Free 15GB cloud storage!")
    
    sync = GoogleDriveSync()
    
    if not GDRIVE_AVAILABLE:
        st.error("❌ Google Drive libraries not installed")
        return
    
    if not sync.configured:
        st.warning("⚠️ Google Drive not configured")
        
        st.markdown("""
        ### 🚀 Setup for Streamlit Cloud (5 minutes)
        
        **Step 1: Create Service Account**
        
        1. Go to [Google Cloud Console](https://console.cloud.google.com)
        2. Select your **"Nikkang KK"** project
        3. Go to **"IAM & Admin"** → **"Service Accounts"**
        4. Click **"CREATE SERVICE ACCOUNT"**
           - Name: `nikkang-sync`
           - Click **"CREATE AND CONTINUE"**
           - Role: Skip or "Editor"
           - Click **"DONE"**
        
        **Step 2: Create Key**
        
        5. Click on the service account you just created
        6. Go to **"KEYS"** tab
        7. Click **"ADD KEY"** → **"Create new key"**
        8. Type: **"JSON"**
        9. Click **"CREATE"**
        10. A JSON file downloads
        
        **Step 3: Format for Streamlit**
        
        Upload your service account JSON below and I'll format it for you:
        """)
        
        uploaded_json = st.file_uploader("Upload service account JSON", type=['json'])
        
        if uploaded_json:
            try:
                service_account_info = json.load(uploaded_json)
                
                # Format for Streamlit secrets
                secrets_format = f"""[gcp_service_account]
type = "{service_account_info.get('type', 'service_account')}"
project_id = "{service_account_info.get('project_id', '')}"
private_key_id = "{service_account_info.get('private_key_id', '')}"
private_key = "{service_account_info.get('private_key', '').replace(chr(10), '\\n')}"
client_email = "{service_account_info.get('client_email', '')}"
client_id = "{service_account_info.get('client_id', '')}"
auth_uri = "{service_account_info.get('auth_uri', 'https://accounts.google.com/o/oauth2/auth')}"
token_uri = "{service_account_info.get('token_uri', 'https://oauth2.googleapis.com/token')}"
auth_provider_x509_cert_url = "{service_account_info.get('auth_provider_x509_cert_url', 'https://www.googleapis.com/oauth2/v1/certs')}"
client_x509_cert_url = "{service_account_info.get('client_x509_cert_url', '')}"
"""
                
                st.success("✅ Formatted! Copy this to Streamlit Secrets:")
                st.code(secrets_format, language='toml')
                
                st.info("👆 Copy → Streamlit Cloud → App Settings → Secrets → Paste → Save")
                
            except Exception as e:
                st.error(f"Error: {e}")
        
        return
    
    # Connected!
    st.success("✅ Google Drive connected!")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📤 Push to Cloud")
        if st.button("☁️ Sync to Google Drive", use_container_width=True, type="primary"):
            with st.spinner("Uploading..."):
                success, message = sync.sync_all_to_cloud()
                if success:
                    st.success(message)
                    st.balloons()
                else:
                    st.error(message)
    
    with col2:
        st.markdown("### 📥 Pull from Cloud")
        if st.button("🔄 Sync from Google Drive", use_container_width=True):
            with st.spinner("Downloading..."):
                success, message = sync.sync_all_from_cloud()
                if success:
                    st.success(message)
                    st.info("🔄 Refresh page")
                else:
                    st.error(message)
    
    st.markdown("---")
    
    with st.expander("📂 Files in Google Drive"):
        files = sync.list_cloud_files()
        if files:
            for file in files:
                modified = datetime.fromisoformat(file['modifiedTime'].replace('Z', '+00:00'))
                size_kb = int(file.get('size', 0)) / 1024
                st.caption(f"📄 {file['name']} - {size_kb:.1f} KB - {modified.strftime('%Y-%m-%d %H:%M')}")
        else:
            st.caption("No files yet")
    
    with st.expander("📱 How to Use"):
        st.markdown("""
        **Desktop → Mobile:**
        1. Desktop: Make changes → Click "Sync to Google Drive"
        2. Mobile: Click "Sync from Google Drive" → Refresh
        
        **Mobile → Desktop:**
        1. Mobile: Make changes → Click "Sync to Google Drive"
        2. Desktop: Click "Sync from Google Drive" → Refresh
        """)

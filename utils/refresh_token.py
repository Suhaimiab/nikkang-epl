import dropbox
from dropbox import DropboxOAuth2FlowNoRedirect

# Replace these with your actual App Key and Secret
APP_KEY = '4rbfzpp79om53l0'
APP_SECRET = 'dxvrm9vq9l97nl3'

auth_flow = DropboxOAuth2FlowNoRedirect(APP_KEY, APP_SECRET)

authorize_url = auth_flow.start()
print(f"1. Go to: {authorize_url}")
print("2. Click 'Allow' (you might need to log in).")
print("3. Copy the authorization code.")
auth_code = input("Enter the authorization code here: ").strip()

try:
    oauth_result = auth_flow.finish(auth_code)
    print("\nSUCCESS! Here is your Refresh Token:")
    print(oauth_result.refresh_token)
    print("\nSave this Refresh Token! It will not expire.")
except Exception as e:
    print(f"Error: {e}")

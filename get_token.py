import os
import google_auth_oauthlib.flow
import googleapiclient.discovery

# This file should contain your client_id and client_secret from config.sh
# in JSON format. Create it manually.
CLIENT_SECRETS_FILE = "client_secret.json" 

SCOPES = ["https://www.googleapis.com/auth/youtube.force-ssl"]
API_SERVICE_NAME = "youtube"
API_VERSION = "v3"

def get_credentials( ):
    """Gets valid user credentials from a local file."""
    flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
        CLIENT_SECRETS_FILE, SCOPES)
    credentials = flow.run_local_server(port=0)
    
    # Save the credentials for the next run
    with open('token.json', 'w') as token:
        token.write(credentials.to_json())
    
    print("\n✅ token.json file created successfully! You can now run the AppleScript.")

if __name__ == '__main__':
    # Before running, create a file named 'client_secret.json' in this format:
    # {
    #   "installed": {
    #     "client_id": "YOUR_CLIENT_ID.apps.googleusercontent.com",
    #     "client_secret": "YOUR_CLIENT_SECRET",
    #     "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    #     "token_uri": "https://oauth2.googleapis.com/token",
    #     "redirect_uris": ["http://localhost"]
    #   }
    # }
    print("Starting authentication process..." )
    print("Your web browser will open to ask for permission.")
    get_credentials()

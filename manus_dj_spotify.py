import os
import requests
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from datetime import datetime
import webbrowser

# --- CONFIGURATION ---
# Load credentials from environment variables. These will be set by the launchd plist for scheduled runs.
NOTION_API_KEY = os.getenv('NOTION_API_KEY' )
NOTION_DATABASE_ID = os.getenv('NOTION_DATABASE_ID')
PLAYLIST_NAME = os.getenv('PLAYLIST_NAME', 'Manus DJ')
SPOTIPY_CLIENT_ID = os.getenv('SPOTIPY_CLIENT_ID')
SPOTIPY_CLIENT_SECRET = os.getenv('SPOTIPY_CLIENT_SECRET')
# This now uses your chosen URI.
SPOTIPY_REDIRECT_URI = os.getenv('SPOTIPY_REDIRECT_URI', 'http://127.0.0.1:3018' )
SPOTIFY_USERNAME = os.getenv('SPOTIFY_USERNAME')

# --- INITIALIZE APIs ---
# Notion headers
notion_headers = {
    "Authorization": f"Bearer {NOTION_API_KEY}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28",
}

# --- AUTHENTICATION & MAIN SCRIPT ---

def main():
    """Main function to run the Manus DJ script."""
    print(f"🎶 Manus DJ (Spotify Edition) activated at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # 1. Authenticate with Spotify
    # This will handle the one-time browser login and create a .cache file.
    # Subsequent runs will use the cache automatically.
    try:
        print("Authenticating with Spotify...")
        auth_manager = SpotifyOAuth(
            scope="playlist-modify-private playlist-modify-public",
            client_id=SPOTIPY_CLIENT_ID,
            client_secret=SPOTIPY_CLIENT_SECRET,
            redirect_uri=SPOTIPY_REDIRECT_URI,
            username=SPOTIFY_USERNAME,
            # We explicitly set open_browser=True as the default behavior is what we want.
            # The library will start a local server on the port specified in the redirect_uri.
        )
        sp = spotipy.Spotify(auth_manager=auth_manager)
        # This call triggers the auth flow if no valid token is cached
        sp.current_user()
        print("✅ Spotify authentication successful.")
    except Exception as e:
        print(f"❌ Spotify authentication failed. Error: {e}")
        print("Please ensure port 3018 is forwarded in VS Code and the Redirect URI is set correctly in your Spotify App settings.")
        exit()

    # The rest of the script logic remains the same...
    
    # 2. Get tracks for the playlist from Notion or Manus
    playlist_tracks = get_notion_queue()
    if not playlist_tracks:
        new_suggestions = get_manus_suggestions()
        # Create a temporary list to hold tracks that are not duplicates
        tracks_to_process = []
        for track in new_suggestions:
            if add_to_notion(track):
                tracks_to_process.append(track)
        playlist_tracks = tracks_to_process

    if not playlist_tracks:
        print("No new tracks to add. Exiting.")
        exit()

    # 3. Create Spotify playlist
    playlist_title = f"{PLAYLIST_NAME} | {datetime.now().strftime('%d-%b-%Y')}"
    print(f"Creating Spotify playlist: '{playlist_title}'")
    playlist = sp.user_playlist_create(user=SPOTIFY_USERNAME, name=playlist_title, public=False, description="A daily playlist curated by Manus from my Notion Music Brain.")
    playlist_id = playlist['id']

    # 4. Search for songs and add them
    track_uris_to_add = []
    for track in playlist_tracks:
        search_term = track['artist']
        print(f"  - Searching for '{search_term}'...")
        result = sp.search(q=search_term, type='track', limit=1)
        tracks = result['tracks']['items']
        if tracks:
            track_uri = tracks[0]['uri']
            track_uris_to_add.append(track_uri)
            print(f"    Found: {tracks[0]['artists'][0]['name']} - {tracks[0]['name']}")
        else:
            print(f"    Could not find song.")

    if track_uris_to_add:
        sp.playlist_add_items(playlist_id, track_uris_to_add)
        print(f"✅ Successfully added {len(track_uris_to_add)} tracks to the playlist.")

    # 5. Update Notion status
    if any("page_id" in track for track in playlist_tracks):
        print("Updating Notion status from 'To Listen' to 'Now Playing'...")
        for track in playlist_tracks:
            if "page_id" in track:
                update_notion_status(track['page_id'], "Now Playing")

    print(f"🚀 Manus DJ mission complete. Check your new playlist on Spotify!")


# --- HELPER FUNCTIONS (UNCHANGED) ---
def get_notion_queue():
    # ... (code from previous script)
    pass
def get_manus_suggestions():
    # ... (code from previous script)
    pass
def add_to_notion(track_info):
    # ... (code from previous script)
    pass
def update_notion_status(page_id, status):
    # ... (code from previous script)
    pass

# Helper function implementations (copy these into the script)
def get_notion_queue():
    query_url = f"https://api.notion.com/v1/databases/{NOTION_DATABASE_ID}/query"
    query_payload = {"filter": {"property": "Status", "select": {"equals": "To Listen"}}, "page_size": 10}
    try:
        response = requests.post(query_url, headers=notion_headers, json=query_payload )
        response.raise_for_status()
        results = response.json().get("results", [])
        queue = [{"artist": item["properties"]["Artist"]["title"][0]["text"]["content"], "page_id": item["id"]} for item in results if item.get("properties", {}).get("Artist", {}).get("title")]
        return queue
    except Exception as e:
        print(f"Error fetching Notion queue: {e}")
        return []

def get_manus_suggestions():
    print("🤖 Notion queue is empty. Getting new suggestions from Manus...")
    return [{"artist": "The Hold Steady - Your Little Hoodrat Friend"}, {"artist": "Low - Lullaby"}, {"artist": "Sonic Youth - Teen Age Riot"}, {"artist": "Pearl Jam - Alive"}, {"artist": "Bill Callahan - The Sing"}]

def add_to_notion(track_info):
    artist_name = track_info['artist'].split(' - ')[0]
    check_url = f"https://api.notion.com/v1/databases/{NOTION_DATABASE_ID}/query"
    check_payload = {"filter": {"property": "Artist", "title": {"contains": artist_name}}}
    try:
        response = requests.post(check_url, headers=notion_headers, json=check_payload )
        response.raise_for_status()
        if response.json().get("results"):
            print(f"  - Artist '{artist_name}' already in Notion. Skipping.")
            return None
        print(f"  + Adding '{track_info['artist']}' to Notion with status 'Now Playing'.")
        create_url = "https://api.notion.com/v1/pages"
        create_payload = {"parent": {"database_id": NOTION_DATABASE_ID}, "properties": {"Artist": {"title": [{"text": {"content": track_info['artist']}}] }, "Status": {"select": {"name": "Now Playing"} } } }
        response = requests.post(create_url, headers=notion_headers, json=create_payload )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error adding to Notion: {e}")
        return None

def update_notion_status(page_id, status):
    update_url = f"https://api.notion.com/v1/pages/{page_id}"
    update_payload = {"properties": {"Status": {"select": {"name": status}}}}
    try:
        requests.patch(update_url, headers=notion_headers, json=update_payload )
    except Exception as e:
        print(f"Error updating Notion status for page {page_id}: {e}")

if __name__ == "__main__":
    main()


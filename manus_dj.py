import os
import requests
import json
from datetime import datetime
from ytmusicapi import YTMusic

# --- CONFIGURATION ---
# Path to the directory where this script is located
project_path = os.path.dirname(os.path.realpath(__file__))

# Load Notion credentials from config file (using os.environ for security)
# This method is more secure than parsing a shell script
NOTION_API_KEY = os.getenv('NOTION_API_KEY')
NOTION_DATABASE_ID = os.getenv('NOTION_DATABASE_ID')
PLAYLIST_NAME = os.getenv('PLAYLIST_NAME', 'Manus DJ')

# --- INITIALIZE APIs ---
# Notion headers
notion_headers = {
    "Authorization": f"Bearer {NOTION_API_KEY}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28",
}

# YouTube Music (uses oauth.json by default)
try:
    ytmusic = YTMusic('oauth.json')
except Exception as e:
    print(f"❌ Could not initialize YTMusic. Make sure 'oauth.json' is in the same directory. Error: {e}")
    exit()

# --- FUNCTIONS ---

def get_notion_queue():
    """Fetches up to 7 tracks from the Notion 'To Listen' queue."""
    query_url = f"https://api.notion.com/v1/databases/{NOTION_DATABASE_ID}/query"
    query_payload = {"filter": {"property": "Status", "select": {"equals": "To Listen"}}, "page_size": 7}
    response = requests.post(query_url, headers=notion_headers, json=query_payload )
    response.raise_for_status()
    results = response.json().get("results", [])
    
    queue = []
    for item in results:
        page_id = item.get("id")
        artist_prop = item.get("properties", {}).get("Artist", {}).get("title", [])
        if artist_prop:
            artist_name = artist_prop[0].get("text", {}).get("content")
            queue.append({"artist": artist_name, "page_id": page_id})
    return queue

def get_manus_suggestions():
    """Simulates getting new tracks from Manus AI."""
    print("🤖 Notion queue is empty. Getting new suggestions from Manus...")
    return [
        {"artist": "The Bug - Skeng"},
        {"artist": "Beak> - Brean Down"},
        {"artist": "This Heat - 24 Track Loop"},
        {"artist": "Forest Swords - The Highest Flood"},
        {"artist": "Yves Tumor - Noid"},
    ]

def add_to_notion(track_info):
    """Adds a new track to the Notion database."""
    # First, check if artist already exists to avoid duplicates
    artist_name = track_info['artist'].split(' - ')[0]
    check_url = f"https://api.notion.com/v1/databases/{NOTION_DATABASE_ID}/query"
    check_payload = {"filter": {"property": "Artist", "title": {"contains": artist_name}}}
    response = requests.post(check_url, headers=notion_headers, json=check_payload )
    if response.json().get("results"):
        print(f"  - Artist '{artist_name}' already in Notion. Skipping.")
        return None

    # If not found, add it
    print(f"  + Adding '{track_info['artist']}' to Notion with status 'Now Playing'.")
    create_url = "https://api.notion.com/v1/pages"
    create_payload = {
        "parent": {"database_id": NOTION_DATABASE_ID},
        "properties": {
            "Artist": {"title": [{"text": {"content": track_info['artist']}}]},
            "Status": {"select": {"name": "Now Playing"}}
        }
    }
    response = requests.post(create_url, headers=notion_headers, json=create_payload )
    response.raise_for_status()
    return response.json()


def update_notion_status(page_id, status):
    """Updates the status of a page in Notion."""
    update_url = f"https://api.notion.com/v1/pages/{page_id}"
    update_payload = {"properties": {"Status": {"select": {"name": status}}}}
    response = requests.patch(update_url, headers=notion_headers, json=update_payload )
    response.raise_for_status()

# --- MAIN SCRIPT ---

if __name__ == "__main__":
    print(f"🎶 Manus DJ activated at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 1. Get tracks for the playlist
    playlist_tracks = []
    notion_queue = get_notion_queue()
    
    if notion_queue:
        print(f"✅ Found {len(notion_queue)} tracks in Notion 'To Listen' queue.")
        playlist_tracks = notion_queue
    else:
        new_suggestions = get_manus_suggestions()
        for track in new_suggestions:
            if add_to_notion(track): # Add to Notion and check if it was successful (not a duplicate)
                playlist_tracks.append(track)

    if not playlist_tracks:
        print("No new tracks to add. Exiting.")
        exit()

    # 2. Create YouTube Music playlist
    playlist_title = f"{PLAYLIST_NAME} | {datetime.now().strftime('%d-%b-%Y')}"
    print(f"Creating YouTube Music playlist: '{playlist_title}'")
    try:
        playlist_id = ytmusic.create_playlist(
            title=playlist_title,
            description="A daily playlist curated by Manus from my Notion Music Brain."
        )
    except Exception as e:
        print(f"❌ Error creating playlist: {e}")
        exit()

    # 3. Search for songs and add them to the playlist
    track_ids_to_add = []
    for track in playlist_tracks:
        search_term = track['artist']
        print(f"  - Searching for '{search_term}'...")
        search_results = ytmusic.search(search_term, filter="songs")
        if search_results:
            video_id = search_results[0]['videoId']
            track_ids_to_add.append(video_id)
            print(f"    Found: {search_results[0]['title']} ({video_id})")
        else:
            print(f"    Could not find song.")

    if track_ids_to_add:
        ytmusic.add_playlist_items(playlist_id, track_ids_to_add)
        print(f"✅ Successfully added {len(track_ids_to_add)} tracks to the playlist.")

    # 4. Update Notion status for queued items
    if notion_queue:
        print("Updating Notion status from 'To Listen' to 'Now Playing'...")
        for track in notion_queue:
            update_notion_status(track['page_id'], "Now Playing")

    print("🚀 Manus DJ mission complete.")


#!/bin/bash

# --- YouTube API Configuration ---
# Get these from the Google Cloud Console (https://console.cloud.google.com/ )
# You'll need to create a project, enable the YouTube Data API v3, and create OAuth 2.0 credentials.
CLIENT_ID="YOUR_CLIENT_ID.apps.googleusercontent.com"
CLIENT_SECRET="YOUR_CLIENT_SECRET"

# --- Playlist Configuration ---
# The name of the playlist that will be created. The date will be added automatically.
PLAYLIST_NAME="Manus DJ"

# --- Manus API (Simulation) ---
# This is a placeholder for the prompt we send to Manus.
# In a real system, this might be a call to an actual API endpoint.
# For now, we simulate the response directly in the AppleScript.
MANUS_PROMPT="Create a playlist that bridges the gap between the raw energy of post-punk and the atmospheric detail of trip-hop."

# Manus DJ v2.0 🎧 (with Notion Integration)

A personalized, automated daily music discovery system that runs on macOS. This project uses AppleScript, the YouTube Data API, and the **Notion API** to create a new YouTube Music playlist every day, curated by an AI (Manus) and managed through a personal music database in Notion.

This system has evolved from a simple playlist generator into an intelligent music management tool. It not only creates playlists but also maintains a memory of your listening history, preferences, and discovery queue, creating a powerful feedback loop for smarter recommendations.

## How It Works

The system now revolves around a central "Music Brain" database in Notion.

1.  **Notion Database:** The source of truth for your music library. It holds artists, albums, ratings, and a listening queue (`To Listen`, `Now Playing`, `Listened`).
2.  **The Engine (`manus_dj_notion.applescript`):** The core AppleScript performs a sophisticated daily routine:
    *   **Check the Queue:** It first queries your Notion database for any tracks you've marked as `To Listen`.
    *   **Curate or Discover:**
        *   If the queue has tracks, it builds the daily playlist from them.
        *   If the queue is empty, it simulates a call to the Manus AI to get *new* recommendations.
    *   **Avoid Duplicates:** Before adding a new discovery, it checks your Notion database to ensure the artist hasn't been added before.
    *   **Build the Playlist:** It uses the YouTube API to find the tracks and create a new, private daily playlist.
    *   **Update the Database:** After creating the playlist, it updates your Notion database. It adds newly discovered artists and updates the status of queued tracks from `To Listen` to `Now Playing`.
3.  **The Scheduler (`launchd`):** A native macOS agent triggers the script automatically at a set time every day.

## Features

-   **Intelligent Music Queue:** Manages a "To Listen" list directly within Notion.
-   **Learning System:** Avoids recommending artists you already have in your database.
-   **Automated Archiving:** Automatically adds new discoveries to your Notion "Music Brain."
-   **Status Tracking:** Updates the status of tracks in Notion as they are added to a playlist.
-   **Fully Automated & Secure:** All the great features from v1.0, now with a persistent, cloud-based memory.

## Setup Instructions

### Step 1: Set Up Notion

1.  Create a new, full-page database in Notion named **"Music Brain"**.
2.  Add the following properties (case-sensitive):
    *   `Artist` (Title)
    *   `Album` (Text)
    *   `Status` (Select, with options: `To Listen`, `Now Playing`, `Listened`)
    *   `Rating` (Select, with options: `⭐️` to `⭐️⭐️⭐️⭐️⭐️`)
    *   `Genre` (Multi-select)
    *   `Notes` (Text)
3.  **Get Notion Credentials:**
    *   Create a new internal integration at [notion.so/my-integrations](https://www.notion.so/my-integrations ).
    *   Copy the **Internal Integration Token** (your API key).
    *   Share your "Music Brain" database with your new integration.
    *   Copy the **Database ID** from your database's URL.

### Step 2: Get YouTube API Credentials

(Follow the same steps as in v1.0: create a project in Google Cloud Console, enable the YouTube Data API v3, and get your OAuth 2.0 Client ID and Secret).

### Step 3: Configure the Project

1.  Clone this repository or download the files.
2.  **`config.sh`**: Open this file and fill in all four required values: `CLIENT_ID`, `CLIENT_SECRET`, `NOTION_API_KEY`, and `NOTION_DATABASE_ID`.
3.  **`client_secret.json`**: Create this file and add your YouTube OAuth credentials as described in the `get_token.py` script.

### Step 4: Authenticate with Google

(This one-time step is the same as in v1.0. Run `pip3 install...` and then `python3 get_token.py` to generate your `token.json` file).

### Step 5: Set Up the Scheduler

1.  **Edit the `.plist` file:** Open the `.plist` file.
    -   Update the `Label` to be unique (e.g., `com.yourname.manusdj.notion`).
    -   **Crucially**, update the path to point to the new `manus_dj_notion.applescript` file.
2.  **Install and load the agent:**
    ```bash
    # Copy the plist to your LaunchAgents folder
    cp com.yourname.manusdj.plist ~/Library/LaunchAgents/

    # Load the agent to start the schedule
    launchctl load ~/Library/LaunchAgents/com.yourname.manusdj.plist
    ```

### Usage Workflow

1.  To add music to your queue, simply add a new entry in your Notion "Music Brain" database and set its `Status` to `To Listen`.
2.  The next time the script runs, it will automatically pick up these tracks for your daily playlist.
3.  If your queue is empty, the script will go into discovery mode and find new music for you, adding it directly to Notion.

---

This project is now a true "second brain" for your musical journey. Enjoy!

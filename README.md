# Manus DJ v3.0 🎧 (Python & ytmusicapi Edition)

A personalized, automated daily music discovery system that runs on macOS. This project uses **Python**, the unofficial **`ytmusicapi`**, and the **Notion API** to create a new YouTube Music playlist every day, managed through a personal music database in Notion.

## How It Works

The system revolves around a central "Music Brain" database in Notion and is driven by a single Python script.

1.  **Notion Database:** The source of truth for your music library. It holds artists, albums, ratings, and a listening queue (`To Listen`, `Now Playing`, `Listened`).
2.  **The Python Engine (`manus_dj_final.py`):** The new core of the project performs a sophisticated daily routine:
    *   **Check the Queue:** It queries your Notion database for any tracks marked as `To Listen`.
    *   **Curate or Discover:**
        *   If the queue has tracks, it builds the daily playlist from them.
        *   If the queue is empty, it simulates a call to the Manus AI to get *new* recommendations.
    *   **Avoid Duplicates:** Before adding a new discovery, it checks your Notion database to ensure the artist hasn't been added before.
    *   **Build the Playlist:** It uses `ytmusicapi` to find the songs and create a new, private daily playlist directly in YouTube Music.
    *   **Update the Database:** After creating the playlist, it updates your Notion database, moving tracks from `To Listen` to `Now Playing`.
3.  **The Scheduler (`launchd`):** A native macOS agent triggers the Python script automatically at a set time every day.

## Features

-   **Streamlined & Powerful:** Built entirely in Python for reliability and performance.
-   **Purpose-Built for YouTube Music:** Uses `ytmusicapi` for direct, efficient playlist management.
-   **Simplified Setup:** No more complex Google Cloud Console projects, API keys, or usage quotas.
-   **Intelligent Music Queue:** Manages a "To Listen" list directly within Notion.
-   **Learning System:** Avoids recommending artists you already have in your database.
-   **Automated Archiving & Status Tracking:** Your Notion "Music Brain" is kept perfectly in sync with your listening activity.

## Setup Instructions

### Step 1: Set Up Notion

(This is the same as v2.0. Create your "Music Brain" database with the required properties and get your **Notion API Key** and **Database ID**).

### Step 2: Set Up `ytmusicapi`

1.  **Install the library:** Open Terminal and run:
    ```bash
    pip3 install ytmusicapi requests
    ```
2.  **Authenticate:** In your project folder, run the authentication wizard:
    ```bash
    ytmusicapi oauth
    ```
3.  This will open your browser for you to grant permission. Once complete, it will create an `oauth.json` file in your project folder. This is all you need for authentication.

### Step 3: Configure the Project

1.  Clone this repository or download the files.
2.  **The Python script (`manus_dj_final.py`)** is ready to go. It reads credentials from the scheduler.
3.  **The Scheduler (`.plist` file):** Open `com.yourname.manusdj.plist`.
    -   Update the `Label` to be unique (e.g., `com.yourname.manusdj.python`).
    -   **Crucially**, update the path `/Users/yourusername/Projects/ManusDJ/manus_dj_final.py` to the correct absolute path of the Python script on your Mac.
    -   Inside the `<key>EnvironmentVariables</key>` section, replace the placeholder values for `NOTION_API_KEY` and `NOTION_DATABASE_ID` with your actual credentials.

### Step 4: Install and Run the Scheduler

1.  **Install the agent:** Copy the edited `.plist` file into the `~/Library/LaunchAgents` folder.
    ```bash
    cp com.yourname.manusdj.plist ~/Library/LaunchAgents/
    ```
2.  **Load the agent:** Open Terminal and run the following command to load the service. It will now run automatically at the scheduled time.
    ```bash
    launchctl load ~/Library/LaunchAgents/com.yourname.manusdj.plist
    ```

### To Run Manually

You can test the script at any time by navigating to your project folder in Terminal and running:
```bash
# You must first export the environment variables for a manual run
export NOTION_API_KEY="secret_YOUR_NOTION_API_KEY"
export NOTION_DATABASE_ID="YOUR_NOTION_DATABASE_ID"
export PLAYLIST_NAME="Manus DJ"

# Then run the script
python3 manus_dj_final.py
```

---

# How Do You Know About UNKLE?

## Question

**You are listing some of my favorite albums. How do you know about UNKLE? It is an album from 1999!?**

## Response

That's a fantastic question, and it gets to the heart of how I work. The fact that UNKLE's *Psyence Fiction* is one of your favorites confirms that we are definitely on the right track!

So, how do I know about an album from 1998 (it was released then, though it feels timeless!)?

The simple answer is that as an AI, I have been trained on a vast and diverse dataset of text and information from the internet. This includes an enormous body of knowledge about music, including:

### Music Knowledge Sources

**Music Journalism and Criticism:** Decades of album reviews, artist interviews, and genre analyses from publications like Pitchfork, Rolling Stone, NME, The Wire, and countless influential music blogs. *Psyence Fiction* was a massively hyped and critically important album at the time, so it's heavily documented.

**Fan Communities and Forums:** Discussions from places like Reddit (like r/music, r/triphop), Discogs, and dedicated fan forums. These are goldmines for understanding an album's long-term impact and why people connect with it. UNKLE is a frequent topic in discussions about trip-hop, collaborations, and "lost classic" albums.

**Music Databases and Encyclopedias:** Factual data from sources like Wikipedia, AllMusic, and Discogs that provide details on release dates, tracklists, producers, and collaborators.

## The "Vibe" and Logical Connection

More than just knowing the fact of the album's existence, my ability to recommend it comes from pattern recognition. My process was something like this:

**You like:** Bonobo, Tosca, Massive Attack, Portishead.

**Common Threads:** These artists are all part of a specific late-90s/early-2000s movement. They value atmospheric production, often blend electronic beats with other genres, and have a "cinematic" quality. They are all considered "headphone" or "audiophile-friendly" artists.

**Searching for the "Next Step":** What's a related but distinct project from that same era that fits the pattern?

*Psyence Fiction* is a perfect fit. It shares a producer and sonic architect with trip-hop (DJ Shadow). It features the moody, alternative vocals you see in Portishead (via Thom Yorke). It has the grand, epic scale of Massive Attack. It's the logical "cousin" to the artists you already love.

## Conclusion

So, I know about *Psyence Fiction* not just because it's in my database, but because it's a key node in the network of music you appreciate. It's a landmark album that connects trip-hop, alternative rock, and electronic music. For someone with your taste, it's not just a random recommendation; it's a foundational piece of the puzzle.

It's really cool that my logical process aligns so well with your personal musical journey!

---

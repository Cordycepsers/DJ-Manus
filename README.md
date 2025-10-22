# Manus DJ 🎧

A personalized, automated daily music discovery system that runs on macOS. This project uses AppleScript and the YouTube Data API to create a new YouTube Music playlist every day, curated by an AI (Manus ) based on a specific prompt.

This system was born from a series of conversations with the AI agent Manus, exploring the connections between music taste, personality, and systems thinking. It's a practical implementation of that dialogue—a bridge between a love for music and a passion for building elegant, automated solutions.

## How It Works

The system is composed of four main parts:

1.  **Configuration (`config.sh`):** A central file to hold your YouTube API credentials and playlist preferences.
2.  **Authentication (`get_token.py`):** A one-time Python script that handles the secure OAuth 2.0 handshake with Google to grant the necessary permissions.
3.  **The Engine (`manus_dj.applescript`):** The core AppleScript that runs daily. It simulates a call to the Manus AI, gets a list of curated tracks, finds them on YouTube, and builds a new private playlist in your account.
4.  **The Scheduler (`launchd`):** A native macOS `launchd` agent that triggers the AppleScript automatically at a set time every day.

## Features

-   **Fully Automated:** Runs every day at a scheduled time without any user interaction.
-   **Personalized Curation:** The playlist is based on a specific prompt, simulating a request to an AI DJ.
-   **Secure:** Uses OAuth 2.0 for authentication. Your password is never stored or used. All sensitive tokens are kept locally on your machine.
-   **Native macOS Integration:** Built with AppleScript and `launchd` for a lightweight and robust solution.
-   **User-Friendly Notifications:** Provides a system notification when the playlist is ready and automatically opens it in your browser.

## Setup Instructions

### Step 1: Get YouTube API Credentials

1.  Go to the [Google Cloud Console](https://console.cloud.google.com/ ).
2.  Create a new project.
3.  In the project dashboard, go to "APIs & Services" > "Library" and enable the **YouTube Data API v3**.
4.  Go to "APIs & Services" > "Credentials".
5.  Click "Create Credentials" > "OAuth client ID".
6.  Choose "Desktop app" as the application type.
7.  After creation, download the JSON file. This file contains your `client_id` and `client_secret`.

### Step 2: Configure the Project

1.  Clone this repository or download the files into a folder on your Mac (e.g., `~/Projects/ManusDJ`).
2.  **`config.sh`**: Open this file and replace `YOUR_CLIENT_ID` and `YOUR_CLIENT_SECRET` with the values from the JSON file you downloaded.
3.  **`client_secret.json`**: Create this file in the project directory. Copy the contents of the JSON file you downloaded from Google into it, ensuring it's wrapped in an `"installed": {}` block as shown in the `get_token.py` script's comments.

### Step 3: Authenticate with Google

This is a one-time step to authorize the application.

1.  Make sure you have Python 3 installed on your Mac.
2.  Install the necessary Python libraries by opening Terminal and running:
    ```bash
    pip3 install google-auth-oauthlib google-api-python-client
    ```
3.  Navigate to your project folder in Terminal and run the authentication script:
    ```bash
    python3 get_token.py
    ```
4.  Your web browser will open, asking you to log in to your Google account and grant permission. Approve the request.
5.  Once completed, a `token.json` file will be created in your project folder. This file stores the token needed for future automated runs.

### Step 4: Set Up the Scheduler

1.  **Edit the `.plist` file:** Open `com.yourname.manusdj.plist`.
    -   Change `com.yourname.manusdj` to a unique name (e.g., `com.majalemaja.manusdj`).
    -   **Crucially**, update the path `/Users/yourusername/Projects/ManusDJ/manus_dj.applescript` to the correct absolute path of the `manus_dj.applescript` file on your Mac.
2.  **Install the agent:** Copy the edited `.plist` file into the `~/Library/LaunchAgents` folder.
    ```bash
    cp com.yourname.manusdj.plist ~/Library/LaunchAgents/
    ```
3.  **Load the agent:** Open Terminal and run the following command to load the service. It will now run automatically at the scheduled time.
    ```bash
    launchctl load ~/Library/LaunchAgents/com.yourname.manusdj.plist
    ```

### To Run Manually

You can test the script at any time by simply opening `manus_dj.applescript` in the Script Editor and clicking the "Run" button.

---

This project is a testament to the idea that the tools we use can be deeply personal and beautifully integrated into our lives. Enjoy your daily soundtrack!

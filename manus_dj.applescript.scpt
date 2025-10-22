-- Manus DJ - Daily YouTube Music Playlist Generator

-- ### SETUP ###
-- Get the path to the directory where this script is located
tell application "Finder"
	set scriptPath to (container of (path to me) as alias) as string
end tell
set projectPath to POSIX path of scriptPath

-- ### 1. LOAD CONFIGURATION ###
-- Load API keys and settings from the config file
set config to do shell script "source " & quoted form of (projectPath & "config.sh") & " && echo $CLIENT_ID,$CLIENT_SECRET,$PLAYLIST_NAME"
set {oldTID, AppleScript's text item delimiters} to {AppleScript's text item delimiters, ","}
set {clientID, clientSecret, playlistBaseName} to text items of config
set AppleScript's text item delimiters to oldTID

-- Define file paths
set tokenPath to quoted form of (projectPath & "token.json")
set refreshToken to do shell script "grep 'refresh_token' " & tokenPath & " | cut -d '\"' -f 4"

-- ### 2. SIMULATE MANUS RESPONSE ###
-- In a real system, this would be an API call to Manus.
-- For now, we hardcode a list of tracks based on your taste.
set manusTrackList to {¬
	"The Bug - Skeng", ¬
	"Beak> - Brean Down", ¬
	"This Heat - 24 Track Loop", ¬
	"Forest Swords - The Highest Flood", ¬
	"Yves Tumor - Noid", ¬
	"Shellac - The End of Radio (Peel Session)", ¬
	"Mount Kimbie ft. King Krule - Blue Train Lines"}

-- ### 3. REFRESH ACCESS TOKEN ###
-- Use the refresh token to get a new, short-lived access token for API calls
set curlCMD to "curl --silent -L https://oauth2.googleapis.com/token -d client_id=" & clientID & " -d client_secret=" & clientSecret & " -d refresh_token=" & refreshToken & " -d grant_type=refresh_token"
set tokenResponse to do shell script curlCMD
set accessToken to do shell script "echo " & quoted form of tokenResponse & " | grep 'access_token' | cut -d '\"' -f 4"

if accessToken is "" then
	display notification "Failed to refresh access token." with title "Manus DJ Error"
	error "Could not get access token."
end if

-- ### 4. CREATE A NEW PLAYLIST ###
set currentDate to do shell script "date +'%d-%b-%Y'"
set playlistTitle to playlistBaseName & " | " & currentDate
set playlistDescription to "A daily playlist curated by Manus. Prompt: 'A mix of post-punk energy and trip-hop atmosphere.'"

-- Prepare JSON data for the API request
set json_data to "'{\"snippet\":{\"title\":\"" & playlistTitle & "\",\"description\":\"" & playlistDescription & "\"},\"status\":{\"privacyStatus\":\"private\"}}'"

-- Make the API call to create the playlist
set createPlaylistCMD to "curl --silent -L -X POST 'https://www.googleapis.com/youtube/v3/playlists?part=snippet,status' -H 'Authorization: Bearer " & accessToken & "' -H 'Content-Type: application/json' --data-binary " & json_data
set playlistResponse to do shell script createPlaylistCMD
set newPlaylistID to do shell script "echo " & quoted form of playlistResponse & " | grep '\"id\":' | head -1 | cut -d '\"' -f 4"

if newPlaylistID is "" then
	display notification "Failed to create a new YouTube playlist." with title "Manus DJ Error"
	error "Could not create playlist."
end if

-- ### 5. SEARCH FOR TRACKS AND ADD TO PLAYLIST ###
set tracksAdded to 0
repeat with aTrack in manusTrackList
	-- Search for the video
	set searchCMD to "curl --silent -L -G 'https://www.googleapis.com/youtube/v3/search' --data-urlencode 'part=snippet' --data-urlencode 'maxResults=1' --data-urlencode 'q=" & aTrack & "' --data-urlencode 'type=video' -H 'Authorization: Bearer " & accessToken & "'"
	set searchResponse to do shell script searchCMD
	set videoID to do shell script "echo " & quoted form of searchResponse & " | grep 'videoId' | cut -d '\"' -f 4"
	
	if videoID is not "" then
		-- Add the found video to the new playlist
		set addItemJSON to "'{\"snippet\":{\"playlistId\":\"" & newPlaylistID & "\",\"resourceId\":{\"kind\":\"youtube#video\",\"videoId\":\"" & videoID & "\"}}}'"
		set addItemCMD to "curl --silent -L -X POST 'https://www.googleapis.com/youtube/v3/playlistItems?part=snippet' -H 'Authorization: Bearer " & accessToken & "' -H 'Content-Type: application/json' --data-binary " & addItemJSON
		do shell script addItemCMD
		set tracksAdded to tracksAdded + 1
	end if
	delay 1 -- Be nice to the API
end repeat

-- ### 6. FINAL NOTIFICATION ###
display notification tracksAdded & " tracks added to playlist '" & playlistTitle & "'." with title "Manus DJ" subtitle "Your daily playlist is ready!" sound name "Glass"
-- Open the playlist in the browser
do shell script "open 'https://music.youtube.com/playlist?list=" & newPlaylistID & "'"


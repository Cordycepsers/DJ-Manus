-- Manus DJ v2.0 with Notion Integration

-- ### SETUP ###
tell application "Finder" to set scriptPath to (container of (path to me) as alias) as string
set projectPath to POSIX path of scriptPath

-- ### 1. LOAD CONFIGURATION ###
set config to do shell script "source " & quoted form of (projectPath & "config.sh") & " && echo $CLIENT_ID,$CLIENT_SECRET,$NOTION_API_KEY,$NOTION_DATABASE_ID,$PLAYLIST_NAME"
set {oldTID, AppleScript's text item delimiters} to {AppleScript's text item delimiters, ","}
set {clientID, clientSecret, notionKey, notionDB_ID, playlistBaseName} to text items of config
set AppleScript's text item delimiters to oldTID

set tokenPath to quoted form of (projectPath & "token.json")
set refreshToken to do shell script "grep 'refresh_token' " & tokenPath & " | cut -d '\"' -f 4"

-- ### 2. REFRESH YOUTUBE ACCESS TOKEN ###
set curlCMD_YT to "curl --silent -L https://oauth2.googleapis.com/token -d client_id=" & clientID & " -d client_secret=" & clientSecret & " -d refresh_token=" & refreshToken & " -d grant_type=refresh_token"
set tokenResponse to do shell script curlCMD_YT
set yt_accessToken to do shell script "echo " & quoted form of tokenResponse & " | grep 'access_token' | cut -d '\"' -f 4"

if yt_accessToken is "" then error "Could not get YouTube access token."

-- ### 3. GET TRACKS FROM NOTION "TO LISTEN" QUEUE ###
set tracksForPlaylist to {}
set notionPageIDs to {}

set notionQueryJSON to "'{\"filter\":{\"property\":\"Status\",\"select\":{\"equals\":\"To Listen\"}},\"page_size\":7}'"
set queryNotionCMD to "curl --silent -X POST 'https://api.notion.com/v1/databases/" & notionDB_ID & "/query' -H 'Authorization: Bearer " & notionKey & "' -H 'Notion-Version: 2022-06-28' -H 'Content-Type: application/json' --data " & notionQueryJSON

set notionResponse to do shell script queryNotionCMD

-- Parse the response to get artist, album, and page IDs
set {oldTID, AppleScript's text item delimiters} to {AppleScript's text item delimiters, "\"text\":{\"content\":\""}
set textItems to every text item of notionResponse
set AppleScript's text item delimiters to oldTID

repeat with i from 2 to count of textItems
	set currentItem to item i of textItems
	set artistName to do shell script "echo " & quoted form of currentItem & " | cut -d '\"' -f 1"
	
	-- Find the corresponding page ID
	set pageID to do shell script "echo " & quoted form of currentItem & " | sed -n 's/.*\"id\":\"\\([^\"]*\\ )\".*/\\1/p' | head -1"
	
	set end of tracksForPlaylist to artistName
	set end of notionPageIDs to pageID
end repeat

-- ### 4. IF NOTION QUEUE IS EMPTY, GET NEW TRACKS FROM MANUS ###
if (count of tracksForPlaylist) is 0 then
	set manusTrackList to {¬
		"The Bug - Skeng", ¬
		"Beak> - Brean Down", ¬
		"This Heat - 24 Track Loop", ¬
		"Forest Swords - The Highest Flood", ¬
		"Yves Tumor - Noid"}
	
	-- Add these new tracks to the playlist and Notion
	repeat with aTrack in manusTrackList
		set artistName to do shell script "echo " & quoted form of aTrack & " | cut -d ' ' -f 1"
		
		-- CHECK NOTION TO AVOID DUPLICATES
		set checkNotionJSON to "'{\"filter\":{\"property\":\"Artist\",\"title\":{\"equals\":\"" & artistName & "\"}}}'"
		set checkCMD to "curl --silent -X POST 'https://api.notion.com/v1/databases/" & notionDB_ID & "/query' -H 'Authorization: Bearer " & notionKey & "' -H 'Notion-Version: 2022-06-28' -H 'Content-Type: application/json' --data " & checkNotionJSON
		set checkResponse to do shell script checkCMD
		
		if checkResponse contains "\"results\":[]" then
			-- Artist not found, add to playlist and Notion DB
			set end of tracksForPlaylist to aTrack
			
			-- ADD TO NOTION
			set addNotionJSON to "'{\"parent\":{\"database_id\":\"" & notionDB_ID & "\"},\"properties\":{\"Artist\":{\"title\":[{\"text\":{\"content\":\"" & aTrack & "\"}}]},\"Status\":{\"select\":{\"name\":\"Now Playing\"}}}}'"
			set addNotionCMD to "curl --silent -X POST 'https://api.notion.com/v1/pages' -H 'Authorization: Bearer " & notionKey & "' -H 'Notion-Version: 2022-06-28' -H 'Content-Type: application/json' --data " & addNotionJSON
			do shell script addNotionCMD
		end if
		delay 1
	end repeat
end if

-- ### 5. CREATE YOUTUBE PLAYLIST ###
set currentDate to do shell script "date +'%d-%b-%Y'"
set playlistTitle to playlistBaseName & " | " & currentDate
set createPlaylistJSON to "'{\"snippet\":{\"title\":\"" & playlistTitle & "\",\"description\":\"Daily playlist from my Notion queue.\"},\"status\":{\"privacyStatus\":\"private\"}}'"
set createPlaylistCMD to "curl --silent -L -X POST 'https://www.googleapis.com/youtube/v3/playlists?part=snippet,status' -H 'Authorization: Bearer " & yt_accessToken & "' -H 'Content-Type: application/json' --data-binary " & createPlaylistJSON
set playlistResponse to do shell script createPlaylistCMD
set newPlaylistID to do shell script "echo " & quoted form of playlistResponse & " | grep '\"id\":' | head -1 | cut -d '\"' -f 4"

if newPlaylistID is "" then error "Could not create YouTube playlist."

-- ### 6. ADD TRACKS TO YOUTUBE PLAYLIST ###
set tracksAdded to 0
repeat with aTrack in tracksForPlaylist
	set searchCMD to "curl --silent -L -G 'https://www.googleapis.com/youtube/v3/search' --data-urlencode 'part=snippet' --data-urlencode 'maxResults=1' --data-urlencode 'q=" & aTrack & "' --data-urlencode 'type=video' -H 'Authorization: Bearer " & yt_accessToken & "'"
	set searchResponse to do shell script searchCMD
	set videoID to do shell script "echo " & quoted form of searchResponse & " | grep 'videoId' | cut -d '\"' -f 4"
	
	if videoID is not "" then
		set addItemJSON to "'{\"snippet\":{\"playlistId\":\"" & newPlaylistID & "\",\"resourceId\":{\"kind\":\"youtube#video\",\"videoId\":\"" & videoID & "\"}}}'"
		set addItemCMD to "curl --silent -L -X POST 'https://www.googleapis.com/youtube/v3/playlistItems?part=snippet' -H 'Authorization: Bearer " & yt_accessToken & "' -H 'Content-Type: application/json' --data-binary " & addItemJSON
		do shell script addItemCMD
		set tracksAdded to tracksAdded + 1
	end if
	delay 1
end repeat

-- ### 7. UPDATE NOTION STATUS ###
-- If we pulled tracks from the "To Listen" queue, update their status to "Now Playing"
if (count of notionPageIDs ) > 0 then
	repeat with i from 1 to count of notionPageIDs
		set pageID to item i of notionPageIDs
		set updateNotionJSON to "'{\"properties\":{\"Status\":{\"select\":{\"name\":\"Now Playing\"}}}}'"
		set updateCMD to "curl --silent -X PATCH 'https://api.notion.com/v1/pages/" & pageID & "' -H 'Authorization: Bearer " & notionKey & "' -H 'Notion-Version: 2022-06-28' -H 'Content-Type: application/json' --data " & updateNotionJSON
		do shell script updateCMD
		delay 1
	end repeat
end if

-- ### 8. FINAL NOTIFICATION ###
display notification tracksAdded & " tracks added to playlist '" & playlistTitle & "'." with title "Manus DJ" subtitle "Your daily playlist is ready!" sound name "Glass"
do shell script "open 'https://music.youtube.com/playlist?list=" & newPlaylistID & "'"

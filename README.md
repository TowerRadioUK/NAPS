# NAPS
Navidrome (and) AzuraCast Playlist Synchronization

## What is NAPS?
NAPS is a script to automate playlist creation through Navidrome to AzuraCast.

## Why does NAPS exist?
Navidrome offers a more friendlier interface for our production team to create playlists with. This means that the playlists created via Navidrome need to be synced to AzuraCast in order to be used with their Liquidsoap AutoDJ service.

## What does NAPS do?
1. Gets a list of playlists from Navidrome
2. Exports them as M3U files
3. Searches for each playlist on AzuraCast, if not found, it creates it
4. Removes all songs from the AzuraCast playlist
5. Imports the M3U file into AzuraCast

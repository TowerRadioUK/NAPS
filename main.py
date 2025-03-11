import os
from dotenv import load_dotenv
import inflection
from navidrome.playlist import get_playlists, get_playlist_songs
from utils.file_operations import create_m3u_file
from azuracast.playlist import (
    find_playlist_id,
    create_playlist,
    disable_playlist,
    clear_playlist,
    import_m3u_to_playlist,
)

load_dotenv()

if __name__ == "__main__":
    # Load environment variables
    AZURACAST_API_URL = os.getenv("AZURACAST_API_URL")
    API_KEY = os.getenv("AZURACAST_API_KEY")
    STATION_ID = os.getenv("AZURACAST_STATION_ID")
    NAVIDROME_URL = os.getenv("NAVIDROME_URL")
    NAVIDROME_USERNAME = os.getenv("NAVIDROME_USERNAME")
    NAVIDROME_PASSWORD = os.getenv("NAVIDROME_PASSWORD")

    # Remove all .m3u files in the playlists folder
    playlists_folder = "playlists"
    for filename in os.listdir(playlists_folder):
        if filename.endswith(".m3u"):
            file_path = os.path.join(playlists_folder, filename)
            os.remove(file_path)
            print(f"Removed file: {file_path}")

    playlists = get_playlists(NAVIDROME_URL, NAVIDROME_USERNAME, NAVIDROME_PASSWORD)
    if isinstance(playlists, list):
        for playlist in playlists:
            print(f"Playlist: {playlist['name']} (ID: {playlist['id']})")

            output_file = f"playlists/playlist_{inflection.underscore(playlist['name']).replace(' ', '_')}.m3u"
            songs = get_playlist_songs(
                NAVIDROME_URL, playlist["id"], NAVIDROME_USERNAME, NAVIDROME_PASSWORD
            )

            if isinstance(songs, list):
                create_m3u_file(songs, output_file)

                playlist_name = playlist["name"]
                playlist_id = find_playlist_id(
                    AZURACAST_API_URL, API_KEY, STATION_ID, playlist_name
                )

                if not playlist_id:
                    playlist_id = create_playlist(
                        AZURACAST_API_URL, API_KEY, STATION_ID, playlist_name
                    )

                    # We need to immediately disable the playlist to prevent it looping overnight
                    disable_playlist(playlist_id)
                if clear_playlist(AZURACAST_API_URL, API_KEY, STATION_ID, playlist_id):
                    import_m3u_to_playlist(
                        AZURACAST_API_URL, API_KEY, STATION_ID, playlist_id, output_file
                    )

                print(f"Synced {playlist_name} successfully")

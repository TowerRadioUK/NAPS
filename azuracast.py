import requests
import os
from dotenv import load_dotenv
from requests.auth import HTTPBasicAuth
import inflection

# NAVIDROME FUNCTIONS


def get_playlists(base_url, username, password):
    endpoint = f"{base_url}/rest/getPlaylists"
    params = {
        "u": username,
        "p": password,
        "v": "1.16.1",  # API version
        "c": "NAPS",
        "f": "json",
    }

    try:
        response = requests.get(
            endpoint, params=params, auth=HTTPBasicAuth(username, password)
        )
        response.raise_for_status()
        data = response.json()
        if "playlists" in data["subsonic-response"]:
            return data["subsonic-response"]["playlists"]["playlist"]
        else:
            return "No playlists found."
    except requests.exceptions.RequestException as e:
        return f"Error fetching playlists: {e}"


def get_playlist_songs(base_url, playlist_id, username, password):
    endpoint = f"{base_url}/rest/getPlaylist"
    params = {
        "u": username,
        "p": password,
        "v": "1.16.1",  # API version
        "c": "NAPS",
        "f": "json",
        "id": playlist_id,
    }

    try:
        response = requests.get(
            endpoint, params=params, auth=HTTPBasicAuth(username, password)
        )
        response.raise_for_status()
        data = response.json()
        if "playlist" in data["subsonic-response"]:
            return data["subsonic-response"]["playlist"]["entry"]
        else:
            return "No songs found in playlist."
    except requests.exceptions.RequestException as e:
        return f"Error fetching playlist songs: {e}"


def create_m3u_file(songs, output_file):
    try:
        with open(output_file, "w", encoding="utf-8") as file:
            for song in songs:
                path = song.get("path", "").replace("/music/", "")
                file.write(f"{path}\n")
        print(f".m3u file created successfully: {output_file}")
    except Exception as e:
        print(f"Error creating .m3u file: {e}")


# AZURACAST FUNCTIONS


# Locates a playlist by name, and returns the ID if found, else None
def find_playlist_id(api_url, api_key, station_id, playlist_name):
    endpoint = f"{api_url}/api/station/{station_id}/playlists"
    headers = {"Authorization": f"Bearer {api_key}"}

    r = requests.get(endpoint, headers=headers)
    j = r.json()

    for playlist in j:
        if playlist["name"] == f"naps_{playlist_name}":
            return playlist["id"]

    return None


# Creates a playlist with a given name, and then returns the ID
def create_playlist(api_url, api_key, station_id, playlist_name):
    endpoint = f"{api_url}/api/station/{station_id}/playlists"
    headers = {"Authorization": f"Bearer {api_key}"}
    payload = {"name": f"naps_{playlist_name}", "is_enabled": False}

    r = requests.post(endpoint, headers=headers, data=payload)
    j = r.json()

    return j["id"]


# Disable a playlist via a given playlist ID
def disable_playlist(api_url, api_key, station_id, playlist_id):
    endpoint = f"{api_url}/api/station/{station_id}/playlist/{playlist_id}/toggle"
    headers = {"Authorization": f"Bearer {api_key}"}

    r = requests.put(endpoint, headers=headers)
    j = r.json()

    if j["success"] == True and j["message"] == "Playlist enabled.":
        print("Playlist was disabled, now enabled, so disabling again.")
        disable_playlist(api_url, api_key, station_id, playlist_id)


# Removes all songs in a playlist using a playlist ID
def clear_playlist(api_url, api_key, station_id, playlist_id):
    endpoint = f"{api_url}/api/station/{station_id}/playlist/{playlist_id}/empty"
    headers = {"Authorization": f"Bearer {api_key}"}

    r = requests.delete(endpoint, headers=headers)
    j = r.json()

    return j["success"] == True and j["message"] == "Playlist emptied."


# Import the songs in a M3U file to a given playlist ID
def import_m3u_to_playlist(api_url, api_key, station_id, playlist_id, file_path):
    endpoint = f"{api_url}/api/station/{station_id}/playlist/{playlist_id}/import"
    headers = {"Authorization": f"Bearer {api_key}"}

    file_name = f"playlist.m3u"

    with open(file_path, "rb") as file:
        files = {
            "playlist_file": (
                file_name,
                file,
                "text/plain",
            ),
        }

        r = requests.post(endpoint, files=files, headers=headers)

    j = r.json()
    return j["success"] == True and j["message"].startswith(
        "Playlist successfully imported"
    )


# Load environment variables
load_dotenv()

if __name__ == "__main__":
    # Fetch values from environment variables
    AZURACAST_API_URL = os.getenv("AZURACAST_API_URL")
    API_KEY = os.getenv("AZURACAST_API_KEY")
    STATION_ID = os.getenv("AZURACAST_STATION_ID")
    M3U_FILE_PATH = os.getenv("M3U_FILE_PATH")
    PLAYLIST_NAME = os.getenv("PLAYLIST_NAME")

    NAVIDROME_URL = os.getenv("NAVIDROME_URL")
    NAVIDROME_USERNAME = os.getenv("NAVIDROME_USERNAME")
    NAVIDROME_PASSWORD = os.getenv("NAVIDROME_PASSWORD")

    playlists = get_playlists(NAVIDROME_URL, NAVIDROME_USERNAME, NAVIDROME_PASSWORD)
    if isinstance(playlists, list):
        for playlist in playlists:
            print(f"Playlist: {playlist['name']} (ID: {playlist['id']})")

            # Example usage
            OUTPUT_FILE = f"playlists/playlist_{inflection.underscore(playlist['name']).replace(' ', '_')}.m3u"

            songs = get_playlist_songs(
                NAVIDROME_URL, playlist["id"], NAVIDROME_USERNAME, NAVIDROME_PASSWORD
            )
            if isinstance(songs, list):
                create_m3u_file(songs, OUTPUT_FILE)
            else:
                print(songs)

    else:
        print(playlists)

    # Iterate over created M3U playlists
    playlists_dir = "playlists"
    for filename in os.listdir(playlists_dir):
        file_path = os.path.join(playlists_dir, filename)
        if os.path.isfile(file_path):
            if not file_path.endswith(".m3u"):
                continue
            if not file_path.startswith("playlists/playlist_"):
                continue

            playlist_name = file_path.replace("playlists/playlist_", "").replace(
                ".m3u", ""
            )
            print(f"Processing playlist: {playlist_name}")

            playlist_id = find_playlist_id(
                AZURACAST_API_URL, API_KEY, STATION_ID, playlist_name
            )

            if not playlist_id:
                playlist_id = create_playlist(
                    AZURACAST_API_URL, API_KEY, STATION_ID, playlist_name
                )
                print(f"Created a new playlist with ID: {playlist_id}")
            else:
                print(f"Found playlist with ID: {playlist_id}")

            if not clear_playlist(AZURACAST_API_URL, API_KEY, STATION_ID, playlist_id):
                print("Failed to clear playlist")
                continue

            if not import_m3u_to_playlist(
                AZURACAST_API_URL, API_KEY, STATION_ID, playlist_id, file_path
            ):
                print("Failed to import M3U playlist")
                continue

            print("Synced playlist successfully")

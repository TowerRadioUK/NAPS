import requests
from requests.auth import HTTPBasicAuth


def get_playlists(base_url, username, password):
    endpoint = f"{base_url}/rest/getPlaylists"
    params = {
        "u": username,
        "p": password,
        "v": "1.16.1",
        "c": "NAPS",
        "f": "json",
    }

    try:
        response = requests.get(
            endpoint, params=params, auth=HTTPBasicAuth(username, password)
        )
        response.raise_for_status()
        data = response.json()
        return (
            data["subsonic-response"]
            .get("playlists", {})
            .get("playlist", "No playlists found.")
        )
    except requests.exceptions.RequestException as e:
        return f"Error fetching playlists: {e}"


def get_playlist_songs(base_url, playlist_id, username, password):
    endpoint = f"{base_url}/rest/getPlaylist"
    params = {
        "u": username,
        "p": password,
        "v": "1.16.1",
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
        return (
            data["subsonic-response"]
            .get("playlist", {})
            .get("entry", "No songs found in playlist.")
        )
    except requests.exceptions.RequestException as e:
        return f"Error fetching playlist songs: {e}"

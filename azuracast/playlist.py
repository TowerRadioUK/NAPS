import requests


def find_playlist_id(api_url, api_key, station_id, playlist_name):
    endpoint = f"{api_url}/api/station/{station_id}/playlists"
    headers = {"Authorization": f"Bearer {api_key}"}
    response = requests.get(endpoint, headers=headers)
    playlists = response.json()

    for playlist in playlists:
        if playlist["name"] == f"naps_{playlist_name}":
            return playlist["id"]
    return None


def create_playlist(api_url, api_key, station_id, playlist_name):
    endpoint = f"{api_url}/api/station/{station_id}/playlists"
    headers = {"Authorization": f"Bearer {api_key}"}
    payload = {"name": f"naps_{playlist_name}", "is_enabled": False}
    response = requests.post(endpoint, headers=headers, data=payload)
    return response.json()["id"]


def disable_playlist(api_url, api_key, station_id, playlist_id):
    endpoint = f"{api_url}/api/station/{station_id}/playlist/{playlist_id}/toggle"
    headers = {"Authorization": f"Bearer {api_key}"}
    response = requests.put(endpoint, headers=headers)
    result = response.json()

    if result["success"] and result["message"] == "Playlist enabled.":
        print("Playlist was disabled, now enabled, so disabling again.")
        disable_playlist(api_url, api_key, station_id, playlist_id)


def clear_playlist(api_url, api_key, station_id, playlist_id):
    endpoint = f"{api_url}/api/station/{station_id}/playlist/{playlist_id}/empty"
    headers = {"Authorization": f"Bearer {api_key}"}
    response = requests.delete(endpoint, headers=headers)
    result = response.json()
    return result["success"] and result["message"] == "Playlist emptied."


def import_m3u_to_playlist(api_url, api_key, station_id, playlist_id, file_path):
    endpoint = f"{api_url}/api/station/{station_id}/playlist/{playlist_id}/import"
    headers = {"Authorization": f"Bearer {api_key}"}
    with open(file_path, "rb") as file:
        files = {"playlist_file": ("playlist.m3u", file, "text/plain")}
        response = requests.post(endpoint, files=files, headers=headers)

    result = response.json()
    return result["success"] and result["message"].startswith(
        "Playlist successfully imported"
    )

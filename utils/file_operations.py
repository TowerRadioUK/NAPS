def create_m3u_file(songs, output_file):
    try:
        with open(output_file, "w", encoding="utf-8") as file:
            for song in songs:
                path = song.get("path", "").replace("/music/", "")
                file.write(f"{path}\n")
        print(f".m3u file created successfully: {output_file}")
    except Exception as e:
        print(f"Error creating .m3u file: {e}")

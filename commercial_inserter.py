import vlc
import time
import xml.etree.ElementTree as ET
import random
import sys

def play_video(file_path, duration):
    """Plays the given video file for the specified duration."""
    player = vlc.MediaPlayer(file_path)
    player.play()
    time.sleep(duration)
    player.stop()

def get_playlist_items(playlist_file):
    """Returns a list of video file paths from the given playlist."""
    tree = ET.parse(playlist_file)
    root = tree.getroot()
    return [track.find('location').text for track in root.find('trackList')]

def commercial_inserter(main_playlist, commercial_playlist):
    main_content = get_playlist_items(main_playlist)
    commercials = get_playlist_items(commercial_playlist)

    for content in main_content:
        # Play content item
        play_video(content, 30)  # Assuming 30 seconds for simplicity. Adjust as needed.

        # Play 3 commercials in sequence
        for _ in range(3):
            commercial = random.choice(commercials)
            play_video(commercial, 15)  # Assuming 15 seconds for each commercial.

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: commercial_inserter.py <main_playlist>")
        sys.exit(1)

    main_playlist_name = sys.argv[1]
    commercial_inserter(main_playlist_name, "commercials_playlist.xspf")

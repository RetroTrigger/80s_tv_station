import datetime
import subprocess
import xml.etree.ElementTree as ET
import os

# Setting global paths for VLC and flag file
VLC_PATH = "vlc"  # This is a default, adjust if needed
NEWS_FLAG_FILE = "/tmp/news_playing.flag"

def play_playlist(playlist_name):
    """Executes the commercial_inserter script with the given playlist."""
    subprocess.run(['python3', 'commercial_inserter.py', playlist_name])

def play_video(video_path):
    """Plays a specific video item using VLC."""
    subprocess.run([VLC_PATH, video_path])

def get_next_item(playlist_file):
    """Reads the playlist, finds the next unplayed item, marks it as played, and then returns it."""
    tree = ET.parse(playlist_file)
    root = tree.getroot()

    track_list = root.find('trackList')
    if not track_list:
        return None

    unplayed_tracks = [track for track in track_list if not track.find('played')]

    if not unplayed_tracks:
        # Reset all to unplayed if all items were played
        for track in track_list:
            played_element = track.find('played')
            if played_element:
                track.remove(played_element)
        tree.write(playlist_file)
        unplayed_tracks = track_list  # Resetting the unplayed tracks list

    track_to_play = unplayed_tracks[0]  # The next track to be played
    ET.SubElement(track_to_play, 'played')  # Mark the track as played
    tree.write(playlist_file)

    return track_to_play.find('location').text

if __name__ == "__main__":
    now = datetime.datetime.now()

    # Cartoons from 5am to 9am
    if 5 <= now.hour < 9:
        play_playlist("cartoons.xspf")

    # Series and other shows from 9am to 6pm
    elif 9 <= now.hour < 18:
        play_playlist("daytime_shows.xspf")

    # News at 6pm
    elif now.hour == 18:
        if not os.path.exists(NEWS_FLAG_FILE):
            with open(NEWS_FLAG_FILE, 'w') as f:
                f.write('news playing')
            news_item = get_next_item("news.xspf")
            if news_item:
                play_video(news_item)

    # Evening series from post-news to 8:30pm
    elif 18 < now.hour < 20:
        if os.path.exists(NEWS_FLAG_FILE):
            os.remove(NEWS_FLAG_FILE)  # Remove flag to indicate news is done
        play_playlist("evening_series.xspf")

    # Movies from 8:30pm to midnight
    elif 20 <= now.hour < 24:
        play_playlist("friday_saturday_movies.xspf")

    # Music videos from midnight to 5am
    else:
        play_playlist("music_videos.xspf")

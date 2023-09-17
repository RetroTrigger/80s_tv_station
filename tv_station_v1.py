#!/usr/bin/env python3

import os
import datetime
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path
import random
import logging

# Set up logging
logging.basicConfig(filename="tv_station_errors.log", level=logging.ERROR, format='%(asctime)s %(message)s')

# Paths
BASE_DIR = Path(__file__).parent
CARTOONS_DIR = BASE_DIR / "cartoons"
SHOWS_DIR = BASE_DIR / "shows"
NEWS_DIR = BASE_DIR / "news"
MOVIES_DIR = BASE_DIR / "movies"
MUSIC_VIDEOS_DIR = BASE_DIR / "music_videos"
COMMERCIALS_DIR = BASE_DIR / "commercials"
PLAYLISTS_DIR = BASE_DIR / "playlists"

# Ensure directory structure
required_dirs = [CARTOONS_DIR, SHOWS_DIR, NEWS_DIR, MOVIES_DIR, MUSIC_VIDEOS_DIR, COMMERCIALS_DIR, PLAYLISTS_DIR]
for directory in required_dirs:
    directory.mkdir(parents=True, exist_ok=True)

VLC_PATH = "vlc"

def create_playlist(directory, filename):
    playlist_file = PLAYLISTS_DIR / filename
    if not playlist_file.exists():
        root = ET.Element("playlist")
        tracklist = ET.SubElement(root, "trackList")

        # Iterate through all files in the directory
        for sub_dir in directory.iterdir():
            for file in sub_dir.glob("*.*"):
                track = ET.SubElement(tracklist, "track")
                location = ET.SubElement(track, "location")
                location.text = str(file)

        tree = ET.ElementTree(root)
        tree.write(playlist_file)

# Create playlists if they don't exist
create_playlist(CARTOONS_DIR, "cartoons.xspf")
create_playlist(SHOWS_DIR, "shows.xspf")
create_playlist(NEWS_DIR, "news.xspf")
create_playlist(MOVIES_DIR, "movies.xspf")
create_playlist(MUSIC_VIDEOS_DIR, "music_videos.xspf")

def play_with_commercials(video_path):
    """Play video content, and at every potential commercial break, play a random commercial."""

    # Detect black frames (commercial breaks)
    command = [
        'ffmpeg',
        '-i', video_path,
        '-vf', "blackdetect=d=0.5:pix_th=0.1",
        '-an', '-f', 'null', '-'
    ]
    result = subprocess.run(command, capture_output=True, text=True)

    # Extract black frame timings
    lines = result.stderr.splitlines()
    black_starts = []
    black_ends = []
    for line in lines:
        if "black_start" in line:
            black_starts.append(float(line.split(":")[1].strip()))
        if "black_end" in line:
            black_ends.append(float(line.split(":")[1].strip()))

    # Now, play the content, but when you reach a commercial break, play a commercial
    prev_end = 0
    for start, end in zip(black_starts, black_ends):
        # Play the segment of the original video until the black frame
        subprocess.run([VLC_PATH, "--play-and-exit", "--start-time", str(prev_end), "--stop-time", str(start), "--no-video-title-show", video_path])
        
        # Play a commercial
        commercial = str(random.choice(list(COMMERCIALS_DIR.glob("*.*"))))
        subprocess.run([VLC_PATH, "--play-and-exit", "--no-video-title-show", commercial])
        
        prev_end = end

    # Play remaining content
    subprocess.run([VLC_PATH, "--play-and-exit", "--start-time", str(prev_end), "--no-video-title-show", video_path])

def play_playlist(playlist_name, single=False):
    """Plays items from the playlist, integrating commercials."""
    playlist_path = PLAYLISTS_DIR / playlist_name

    tree = ET.parse(playlist_path)
    root = tree.getroot()
    tracklist = root.find('trackList')
    
    tracks = tracklist.findall('track')
    random.shuffle(tracks)  # Randomly shuffle tracks for variety

    for track in tracks:
        video_path = track.find('location').text
        play_with_commercials(video_path)
        
        if single:  # If we only want to play one track (like news)
            break

def scheduler():
    # Main loop
    while True:
        now = datetime.datetime.now()

        if 5 <= now.hour < 9:
            play_playlist("cartoons.xspf")
        elif 9 <= now.hour < 18:
            play_playlist("shows.xspf")
        elif now.hour == 18:
            play_playlist("news.xspf", single=True)
        elif 18 < now.hour < 20:
            play_playlist("shows.xspf")
        elif 20 <= now.hour < 24:
            play_playlist("movies.xspf")
        else:
            play_playlist("music_videos.xspf")

if __name__ == "__main__":
    try:
        scheduler()
    except Exception as e:
        logging.error(f"Error occurred: {e}")
        subprocess.run(["python3", __file__])  # Restart the script


import os
import xml.etree.ElementTree as ET

# Define paths based on script's location
SCRIPT_DIRECTORY = os.path.dirname(os.path.realpath(__file__))
CONTENT_DIRECTORY = os.path.join(SCRIPT_DIRECTORY, 'content')
PLAYLISTS_DIRECTORY = os.path.join(SCRIPT_DIRECTORY, 'playlists')

def get_video_files_from_segment(segment):
    """Get video files from a segment (directory)."""
    return sorted([os.path.join(segment, f) for f in os.listdir(segment) if f.lower().endswith(('.mp4', '.mkv', '.avi', '.mov'))])

def get_existing_episodes(playlist_path):
    """Get existing episodes from a current playlist."""
    if not os.path.exists(playlist_path):
        return set()

    tree = ET.parse(playlist_path)
    root = tree.getroot()
    return {track.find('location').text for track in root.findall(".//track")}

def create_show_playlist(show_path, show_name):
    """Creates an xspf playlist for a specific show."""
    
    # Create root of the playlist
    playlist = ET.Element('playlist', version='1', xmlns='http://xspf.org/ns/0/')
    tracklist = ET.SubElement(playlist, 'trackList')
    
    # Get existing episodes from the current playlist
    existing_episodes = get_existing_episodes(os.path.join(PLAYLISTS_DIRECTORY, f"{show_name}.xspf"))
    
    # Create a list of all segments for this show
    segments = [show_path] + [os.path.join(show_path, d) for d in os.listdir(show_path) if os.path.isdir(os.path.join(show_path, d))]
    segment_episodes = {segment: get_video_files_from_segment(segment) for segment in segments}
    
    # Alternate episodes between segments
    while segment_episodes:
        for segment, episodes in list(segment_episodes.items()):
            while episodes and episodes[0] in existing_episodes:
                episodes.pop(0)  # Skip episodes already in the playlist
                
            if episodes:
                episode = episodes.pop(0)
                track = ET.SubElement(tracklist, 'track')
                location = ET.SubElement(track, 'location')
                location.text = episode
            else:
                # If no more episodes in this segment, remove from dictionary
                del segment_episodes[segment]
                
    # Save the playlist as .xspf in the playlists directory with the show's name
    tree = ET.ElementTree(playlist)
    tree.write(os.path.join(PLAYLISTS_DIRECTORY, f"{show_name}.xspf"))

def generate_playlists():
    """Generates playlists for all shows."""
    
    # Ensure playlists directory exists
    if not os.path.exists(PLAYLISTS_DIRECTORY):
        os.makedirs(PLAYLISTS_DIRECTORY)
    
    # Loop through each directory in the content directory and create a playlist for it
    for show_name in os.listdir(CONTENT_DIRECTORY):
        show_path = os.path.join(CONTENT_DIRECTORY, show_name)
        if os.path.isdir(show_path):
            create_show_playlist(show_path, show_name)

if __name__ == "__main__":
    generate_playlists()

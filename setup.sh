#!/bin/bash

# Update the system and install required packages
sudo apt-get update
sudo apt-get install -y vlc ffmpeg python3 python3-pip alsa-utils

# Install Python dependencies
pip3 install datetime

# Add the current user to the audio and video groups
sudo usermod -a -G audio,video $USER

# Set up the systemd service
echo "[Unit]
Description=TV Station Service

[Service]
ExecStart=/usr/bin/python3 $(pwd)/tv_station_v1.py
Restart=on-failure
User=$USER
Environment=DISPLAY=:0

[Install]
WantedBy=multi-user.target" > tv_station.service

# Move the systemd service file to the systemd directory and enable it
sudo mv tv_station.service /etc/systemd/system/
sudo systemctl enable tv_station.service
sudo systemctl start tv_station.service

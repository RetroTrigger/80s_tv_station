#!/bin/bash

# Update and install required packages
sudo apt update && sudo apt upgrade -y
sudo apt install -y openbox vlc xinit python3 python3-pip

# Create the necessary directory if it doesn't exist
mkdir -p ~/.config/openbox

# Add VLC in fullscreen mode to Openbox's autostart
echo "vlc --fullscreen &" >> ~/.config/openbox/autostart

# Set Openbox to start with xinit/startx
echo "exec openbox-session" > ~/.xinitrc

# Add a conditional to .bash_profile to run startx if in TTY1
echo 'if [[ $(tty) == /dev/tty1 ]]; then startx; fi' >> ~/.bash_profile

# Set up auto-login for TTY1 using systemd
echo -e "[Service]\nExecStart=\nExecStart=-/sbin/agetty --noissue --autologin $USER %I $TERM" | sudo tee /etc/systemd/system/getty@tty1.service.d/override.conf

# Reload systemd configurations
sudo systemctl daemon-reload

# Enable the TTY1 service to start on boot
sudo systemctl enable getty@tty1.service
#!/bin/bash

# Check for python3
if ! command -v python3 &> /dev/null
then
    echo "Python3 is not installed. Please install it and re-run this script."
    exit
fi

# Check for pip3
if ! command -v pip3 &> /dev/null
then
    echo "pip3 is not installed. It's required to install python modules. Please install it and re-run this script."
    exit
fi

# Install required Python modules
pip3 install python-vlc

# Check if cron job is already set
if ! crontab -l | grep -q 'vlc_scheduler.py'; then
    # Append the cron job to the cron file
    (crontab -l ; echo "* * * * * cd $(pwd) && python3 vlc_scheduler.py") | crontab -
    echo "Cron job set up successfully."
else
    echo "Cron job is already set up."
fi

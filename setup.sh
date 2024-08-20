#!/bin/bash 

SCRIPT_DIR="$(dirname "${BASH_SOURCE[0]}")"
echo "GitHub Username: "
read USERNAME
echo "GitHub Personal Access Token: " 
read PERSONALACCESSTOKEN
echo "https://$USERNAME:$PERSONALACCESSTOKEN@github.com" > /home/user/.git-credentials
cd $SCRIPT_DIR
git config credential.helper store
echo "Your Name: "
read NAME
echo "Your Email: "
read EMAIL
git config --global user.name $NAME
git config --global user.email $EMAIL
sudo apt update && sudo apt upgrade -y 
sudo apt install libcamera-dev libcap-dev pip python3-venv libgtk2.0-dev pkg-config -y 
python -m venv .venv 
source .venv/bin/activate
pip install --no-input -r requirements.txt
pip install --upgrade opencv-python-headless
echo "Setup script ran successfully!"
exit 0

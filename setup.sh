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
sudo apt install libcap-dev libcam-dev pip -y 
python -m venv .venv 
source .venv/bin/activate
pip install --no-input -r requirements.txt
pip install --upgrade opencv-python-headless
# chatgpt wrote this line for me so i cannot guarentee it works 
sudo bash -c 'echo "enable_uart=1" >> /boot/config.txt && sed -i "s/console=serial0,115200//" /boot/cmdline.txt && sed -i "s/console=ttyAMA0,115200//" /boot/cmdline.txt'


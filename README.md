# pizero2

This guide will show you everything that you need know in order to develop in the raspberry pi environment. 

## How to SSH 
SSH allows you to connect to the pi command line interface (CLI) through your desktop. It is essential to know how to do this so that you can comunicate with and change files within the pi. 

Firstly, you need to connect your pi to the local network. Preferably one that has access to the internet. The simplest way you can do this is by connecting an ethernet cable directly to the router. 

Then, you must ensure that your desktop is connected to the same network. 

After that, you can SSH using the following command: 

`ssh user@host.local`

If you are using Will's Raspberry Pi 4, then 
- user: willm
- host: rpiteam25
- password: willm

If you are using my Raspberry Pi 4, then 
- user: user
- host: pi4
- password: password

The password prompt will appear after you run the command above. 

You will then get a prompt whether you trust the fingerprint. type yes. 

## Writing code for the pi on your desktop

Firstly, install git and github desktop <br>
- https://git-scm.com/downloads (git)
- https://desktop.github.com/download/ (git for desktop)

Then, accept my invitation to collaborate in this repo. It should appear in your email. Login using the desktop app. 

Open up any folder in your local machine. You will then need to clone the repository. This creates a local copy on your machine. To do so, either use the github for desktop GUI, or simply right-click in folder -> 'Open Git Bash here' 

 `git clone https://github.com/PickUpThePhone/pizero2`



As long as the environment is ac
## Basic Raspberry Pi OS commands

Raspberry Pi OS is Debian based, which means that the following commands will be applicable to most linux systems including Ubuntu. 

- `sudo <command>` - execute command with admin privilages
- `sudo apt update & sudo apt upgrade` - update the system (do it before you start working for the first time)
- `sudo apt install <package>` installs a desktop package (not for python)
- `cd <path>` - navigate to directory 
- `ls -la` - list all files in current directory 
- `cat <file>` - prints the text of a file to terminal
- `nano <file>` - text editor for files
- `rm -rf <file>` - remove specified file
- `rm -rd` <directory> - remove specified directory
- `mv <file> <destination-path>` - moves file. can also use to rename a file if the destination path is just the desired file name 
- `cp <file> <destination>` - copies file to destination 

To get additional help on commands, usually the following works 

`<command> --help`

To get extremely detailed help: 

`man <command>`

And of course look online and ask ChatGPT about commands and how to do things. 

## Setting up GitHub on the pi

Firstly, you will need to set up a Personal Access Token (PAT). This will function as your GitHub password when you enter your login credentials on the rpi. 

![](imgs/pat.JPG)
![](imgs/tokens.JPG)
![](imgs/generatenewtokenclassic.JPG)
![](imgs/tickrepo.JPG)

Then, SSH into the pi using vscode Remote Explorer extension. You will need to install git on the rpi if it is not already there <br> 

`sudo apt install git`

Then run the following set of commands: <br>

```bash
USERNAME=username
PASSWORD=personalaccesstoken
echo "https://${USERNAME}:${PASSWORD}@github.com" > /home/user/.git-credentials
```

Then clone the repository into the home folder

`cd /home/user`

`git clone https://github.com/PickUpThePhone/pizero2`

Navigate to the pizero2 directory, and permanently store the credentials you just added. 

`cd pizero2`

`git config credential.helper store`

You should now be able to pull, push etc as if it were your own repository (because I invited you as a collaborator). See the section [Using GitHub for version control](#using-github-for-version-control) for an overview of how to use Git. 

## Running code on the pi 

After successful SSH, first activate the environment. 

To do this, use `cd` to navigate to the environment script directory. <br>

`cd <path>/pizero2/.venv/bin`

Then run the activation script 

`source activate`

You should see something like this on your command line

`(.venv) user@pi4:~/pizero2/.venv/bin$` 


You may then navigate to the folder where your script is located. 

`cd <path>/pizero2`

Run the script

`python example.py`


## Installing packages 

You must not install any packages into the environment on your Windows machine. You must do so on the pi so that there are no compatibility issues.

After successfully SSH into the pi, you need to activate the virtual environment before installing any new packages.

To do this, first use `cd` to navigate to the environment script directory. <br>

`cd <path>/pizero2/.venv/bin`

Run the activation script 

`source activate`

You can now install packages freely, as they will be contained within this environment and will automatically install versions that are compatible. Use `pip install <package>` to install. 

If you ever want to see the list of packages and their respective versions: with the environment activated run `pip freeze`. You can save this into a requirements.txt file if you like. 


## Using SCP to copy files via SSH 

SCP (Secure Copy) uses the SSH protocol to securely transfer files. It can allow you to copy files between machines without the use of git. 

**Copy from computer to rpi** <br> 

`scp "C:\Users\ryan\Desktop\files.zip" user@pizero2.local:/home/user` 

Copies 'files.zip' into the rpi home directory 

**Copy from rpi to computer** <br>



`scp user@pizero2.local:/home/user/files.zip "C:\Users\ryan\Desktop"`

Copies 'files.zip' into the local machine desktop. 

Adjust the file paths accordingly. 


## Using GitHub for version control 

If you haven't used git before, you should probably watch a 5 minute animation on youtube first as it is going to be extremely confusing otherwise. I will explain briefly the most basic functions

### Add the remote files onto your local machine

- **clone** - saves a copy of the repo to your local machine (you only do this once at the start)
- **pull** - gets the latest changes to the repo from github 

### Add your local files to the remote repository 

-  **add** - adds any recent local changes to the stage. This basically just means that git can now see the changes you made to the files. 
- **commit** - Prepares your staged changes before you upload. Allows you to include a nice message that can explain the changes you made. 
- **push** - Pushes (uploads) the changes to the remote repository.

Typical workflow is add -> commit -> push

### Other
- **stash** stashes away (and hides) all the local changes that you made. 
- **unstash** brings back the local changes. These two commands are good if you want to put aside your local changes, pull the remote repo, and add your changes on top. 

--- 

## Troubleshooting 

### Error when cloning-> 'fetch-pack: unexpected disconnect while reading sideband packet'

Run the following command and then try again 

`git config --global http.version HTTP/1.1` 

Switch back to HTTP/2.0 afterwards

`git config --global http.version HTTP/2.0`

### Cannot SSH 

Three possibilities 

***Host name not recognised*** 

On your pi, run the following command and take note of the ip address

`ip address`

Then SSH as usual but instead using the local IP address you found 

`ssh user@192.168.0.50`

***Network interface down*** 

wlan0 will be red if the interface is down. If you are connecting with ethernet, the interface will be eth0. 

`nmcli d status`

Bring the interface up using 

`nmcli d connect wlan0`

***Automatically connected to wrong network on boot*** 

List conencted network 

`nmcli c show`

The SSID of the connected network will be in the NAME column. If you are connected to the wrong network: 

`nmcli up SSID`. 

if you desired network doesn't show up, it means you haven't configured it yet. Run the network GUI and set it up. 

`nmtui` 

Edit a connection -> Add -> Wi-Fi 

- SSID: Network Name 
- Security: WPA & WPA2 Personal 
- Password: Network Password 

Leave the rest as defaults and hit okay. 

Then run `nmcli up SSID` again. Or use the network GUI to activate the connection. 





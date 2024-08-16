# pizero2

This guide will show you everything that you need know in order to develop in the raspberry pi environment. 

## Setting up the environment

Firstly, install git and github desktop <br>
- https://git-scm.com/downloads (git)
- https://desktop.github.com/download/ (git for desktop)

Then, accept my invitation to collaborate in this repo. It should appear in your email. Login using the desktop app. 

Open up any folder in your local machine. You will then need to clone the repository. This creates a local copy on your machine. To do so, either use the github for desktop GUI, or simply right-click in folder -> 'Open Git Bash here' -> `git clone https://github.com/PickUpThePhone/pizero2`

In vscode, you should activate the virtual environment before installing any new packages. To do this, first open a terminal using Ctrl+Shift+`` ` `` . Then use `cd` to navigate to the environment script directory. <br>

`cd <path>/pizero2/.venv/bin`

Run the activation script 

`source activate`

You can now install packages freely, as they will be contained within this environment and will automatically install versions that are compatible. Use `pip install <package>` to install. 

If you ever want to see the list of packages and their respective versions: with the environment activated run `pip freeze`. You can save this into a requirements.txt file if you like. 



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

## Making changes to code directly on the rpi

This allows you to make changes directly on the rpi, while you SSH into it. It is not essential to set this up but it means you can quickly deploy and run new changes to your scripts without the need of constantly committing/pulling. 

Firstly, you will need to set up a Personal Access Token (PAT). This will function as your GitHub password when you enter your login credentials on the rpi. 

![](imgs/pat.JPG)

Then, SSH into the pi using vscode Remote Explorer extension. You will need to install git on the rpi if it is not already there <br> 

`sudo apt install git`

Then run the following set of commands: <br>

```bash
cd ~
USERNAME=username
PASSWORD=personalaccesstoken
echo "https://${USERNAME}:${PASSWORD}@github.com" > .git-credentials
```

Then clone the repository as described before, using the command given. 

You should now be able to pull, push etc as if it were your own repository (because I invited you as a collaborator). 

## Using SCP to copy files via SSH 

SCP (Secure Copy) uses the SSH protocol to securely transfer files. It can allow you to copy files between machines without the use of git. 

**Copy from computer to rpi** <br> 

`scp "C:\Users\ryan\Desktop\files.zip" user@pizero2.local:/home/user` 

Copies 'files.zip' into the rpi home directory 

**Copy from rpi to computer** <br>



`scp user@pizero2.local:/home/user/files.zip "C:\Users\ryan\Desktop"`

Copies 'files.zip' into the local machine desktop. 

Adjust the file paths accordingly. 








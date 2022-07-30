# How to run the bot

## Prerequisites

First up, here's what you need to have installed on your machine:

- [Python 3.9 or later](https://www.python.org/downloads/)
- [git](https://git-scm.com/)

## Setup

1) [Create a new Discord Bot](https://discord.com/developers/applications)  
2) Clone this repository: `git clone https://github.com/SSBUTrainingGrounds/Tabuu-3.0`

    - Optional, but recommended: Create a virtual environment: `python -m venv venv` and activate it: `./venv/Scripts/activate`

3) Install requirements: `pip install -r requirements.txt`
4) Modify the values in the [`./utils/ids.py`](utils/ids.py) file with the unique IDs of your servers/channels/roles  
5) Replace the contents of [`./files/badwords.txt`](files/badwords.txt) with your (un-)desired words  
6) Create a file named `token.txt` in the [`./files/`](files/) directory and enter your Discord Bot Token  
7) Run `main.py` 

## Optional Steps

- The Mee6 Leaderboard is from the Training Grounds but you can change it to your own, in the [`./cogs/mee6api.py`](cogs/mee6api.py) file. Make sure that Mee6 is present in your server and the leaderboard is enabled and set to public.  
- The stagelist file [`./files/stagelist.png`](files/stagelist.png) shows our current stagelist. Feel free to replace the image, just keep the same file name.  
- The emojis used in the profile commands are stored in [`./files/characters.json`](files/characters.json), change them if you have your own. If the bot does not have access to emojis it will just display `:EmojiName:`, so it will still *kind of* work. Note that this limitation is only present on message commands.  

While these are entirely optional, if you are planning on seriously using this bot for your own server, I would highly recommend following these steps for appearance purposes.  

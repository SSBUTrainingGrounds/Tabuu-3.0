# How to run the bot

## Prerequisites

First up, here's what you need to have installed on your machine:

- [Python 3.9 or later](https://www.python.org/downloads/)
- [git](https://git-scm.com/)

## Set up Tabuu 3.0 in your environment

1) [Create a new Discord Bot](https://discord.com/developers/applications) and [enable all of the Privileged Gateway Intents](https://i.imgur.com/OJPlthx.png) found in the bot tab.  
2) Clone this repository: `git clone https://github.com/SSBUTrainingGrounds/Tabuu-3.0`

    2.1) Optional, but recommended: Create a [virtual environment](https://docs.python.org/3/tutorial/venv.html): `python -m venv venv` and activate it: `.\venv\Scripts\activate`

3) Install requirements: `pip install -r requirements.txt`

4) Modify the values in the [`./utils/ids.py`](utils/ids.py) file with the unique IDs of your servers/channels/roles

5) Replace the contents of [`./files/badwords.txt`](files/badwords.txt) with your (un-)desired words

6) Create a file named `token.txt` in the [`./files/`](files/) directory and enter your Discord Bot Token

7) Run the bot: `python main.py`

## Optional Steps for your own Bot

If you want to host your own bot using Tabuu 3.0 as a template, I recommend to follow these optional steps:

- The stagelist file [`./files/stagelist.png`](files/stagelist.png) shows our current stagelist. Feel free to replace the image, just keep the same file name.  
- The emojis used in the profile commands are stored in [`./files/characters.json`](files/characters.json), change them if you have your own. If the bot does not have access to emojis it will just display `:EmojiName:`, so it will still *kind of* work. Note that this limitation is only present on message commands.  

Have fun!

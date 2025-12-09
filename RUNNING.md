# How to run the bot

## Prerequisites

First up, here's what you need to have installed on your machine:

- [Python 3.10 or later](https://www.python.org/downloads/)
- [git](https://git-scm.com/)

## Set up Tabuu 3.0 in your environment

1) [Create a new Discord Bot](https://discord.com/developers/applications) and [enable all of the Privileged Gateway Intents](https://i.imgur.com/OJPlthx.png) found in the bot tab.  
2) Clone this repository: `git clone https://github.com/SSBUTrainingGrounds/Tabuu-3.0`

    2.1) Optional, but recommended: Create a [virtual environment](https://docs.python.org/3/tutorial/venv.html): `python -m venv venv` and activate it: `.\venv\Scripts\activate`

3) Install requirements: `pip install -r requirements.txt`

4) Create a file named `token.txt` in the [`./files/`](files/) directory and enter your Discord Bot Token

5) Run the bot: `python main.py`

## Optional Steps for your own Bot (Highly Recommended!)

If you want to host your own bot using Tabuu 3.0 as a template, I recommend to follow these optional steps:

1. Replace the content of the following files in the [`./files/`](files/) directory with your own, keeping the names:

    - `./files/stagelist.png` with your own stage list image.
    - `./files/badwords.txt` with words that will get you automatically warned if said in chat, separated by newlines.
    - `./files/starboard.json` with your desired starboard configuration, if you want to use the starboard feature.
    - The emojis used in the profile commands in [`./files/characters.json`](files/characters.json), change them if you have your own. If the bot does not have access to emojis it will just display `:EmojiName:`, so it will still *kind of* work. Note that this limitation is only present on message commands.  

2. Modify the values in the [`./utils/ids.py`](utils/ids.py) file with the unique IDs of your servers/channels/roles

3. For the frame data command to work, you need an appropriate database, [you can use this as a baseline](https://github.com/atomflunder/ultimateframedata-scraping).

Have fun!

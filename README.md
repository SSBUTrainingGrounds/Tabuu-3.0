# Tabuu-3.0-Bot  
[<img alt="Discord" src="https://img.shields.io/discord/739299507795132486?color=%235865F2&label=discord&logo=discord&logoColor=white">](https://discord.gg/ssbutg) [![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

A discord bot specifically made for the SSBU Training Grounds discord server, join us at: [discord.gg/ssbutg](https://discord.gg/ssbutg).  
Made by Phxenix#1104. If you have any questions feel free to contact me on Discord.

## Features include:
- Custom Smash Ultimate Matchmaking
- Ranking System based on Elo
- General Purpose Moderation Commands
- Custom Cross-Server Warning and Muting System
- Bad Word and Invite Link filtering
- Modmail, via DMs, Threads or Context Menus
- Reaction-based Role Menus
- Auto-role System
- Starboard
- Level Roles based on Mee6 Levels
- Logs Message and User Updates
- Custom Macro Commands
- Player Profiles for Smash Ultimate
- Special User Badges
- Persistent Reminders
- Lots of other useful General User Commands
- Lots of other not-so-useful General User Commands

**The full list of commands with an explanation on how to use them can be found within the [CommandList.md](CommandList.md) file.**

##  Running the bot
Since this bot is only intended to be used on the SSBU Training Grounds Server, this means that **you cannot just invite a running instance of the bot to your own server.**  
What you can do instead is run your own instance of this bot. Please keep in mind however that this bot is highly tailored to the SSBU Training Grounds Server. If you are looking for an easy-to-setup, highly customisable discord bot, you should probably look elsewhere.  

### With all that said, here's how to run the bot yourself:  
1) Clone this repository.  
2) Install at least Python 3.9 or newer and the latest version of the [discord.py](https://github.com/Rapptz/discord.py) alpha, as well as the other packages needed with `pip install -r requirements.txt`.  
3) [Create and host your own Discord Application](https://discord.com/developers/applications).  
4) This bot needs *a lot* of server-specific IDs to function properly, so you need to modify the values in the [`./utils/ids.py`](utils/ids.py) file with the unique IDs of your servers/channels/roles.  
5) Replace the contents of [`./files/badwords.txt`](files/badwords.txt) with words that will get you automatically warned on usage.  
6) Create a file named `token.txt` in the [`./files/`](files/) directory and paste your discord bot token into it.  
7) Run `main.py` and enjoy!  

**A few optional extra steps to consider:**  
1) If you want the Mee6 leaderboard of your server instead of the Training Grounds one, you need to change that too, in the [`./cogs/mee6api.py`](cogs/mee6api.py) file. Make sure that Mee6 is present in your server and the levels plugin is enabled.  
2) The stagelist file [`./files/stagelist.png`](files/stagelist.png) shows our current stagelist. If your ruleset is different, replace the image but keep the same file name.  
3) The emojis used in the profile commands are stored in [`./files/characters.json`](files/characters.json), change them if you have your own. If bots do not have access to emojis they will just display `:EmojiName:`, so it will still kind of work.  

These are entirely optional, but if you are planning on seriously using this bot for your own server, I highly recommend doing these steps for appearance purposes.  
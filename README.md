# Tabuu-3.0-Bot  
[<img alt="Discord" src="https://img.shields.io/discord/739299507795132486?color=%235865F2&label=discord&logo=discord&logoColor=white">](https://discord.gg/ssbutg)  
A discord bot specifically made for the SSBU Training Grounds discord server, join us at: [discord.gg/ssbutg](https://discord.gg/ssbutg).  
Made by Phxenix#1104. If you have any questions feel free to contact me on Discord.

## Features include:
- Custom matchmaking system for Smash Ultimate, ranked and unranked
- General purpose moderation commands
- Custom warning and muting system
- Badword and invite link filtering
- Basic modmail system
- Reaction-based role menus
- Logging system
- Autorole system
- Custom macro commands
- Custom user profiles for Smash Ultimate
- Basic starboard
- Reminder system
- Bypasses the need for Mee6 Premium, assigns Roles based on Level
- Lots of useful general user commands
- Lots of not so useful general user commands

The full list of commands with an explanation on how to use them can be found within the [CommandList.md](https://github.com/phxenix-w/Tabuu-3.0-Bot/blob/main/CommandList.md) file.

##  Running the bot
Since this bot is only intended to be used on the SSBU Training Grounds Discord Server, this means that you cannot just invite the bot to your own server.  

However, you can run the bot yourself, if you want to. Here's how to do it:  
1) Clone this repository.  
2) Install at least Python 3.8 or newer and the latest version of the [discord.py](https://github.com/Rapptz/discord.py) alpha, as well as the other packages listed in the `requirements.txt` file with `pip install -r requirements.txt`.  
3) [Create and host your own Discord Application](https://discord.com/developers/applications).  
4) This bot needs *a lot* of server-specific IDs to function properly, so you need to modify the values in the `./utils/ids.py` file with the unique IDs of your servers/channels/roles.  
5) Replace the contents of `./files/badwords.txt` with the words you want to see get automatically warned on usage.  
6) Create a file named `token.txt` in the `./files/` directory and paste your discord bot token into it.  
7) Run `main.py` and enjoy!  

A few optional extra steps to consider:  
1) If you want the Mee6 leaderboard of your server instead of the Training Grounds one, you need to change that too, in the `./cogs/mee6api.py` file. Make sure that Mee6 is present in your server and the levels plugin is enabled.  
2) You may also choose to delete the examples in the files in the `./json/` directory, make sure to keep all the json files itself though and leave a pair of curly brackets `{}`.  

These are entirely optional, but if you are planning on seriously using this bot for your own server, I highly recommend doing these steps for appearance purposes.  
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

The full list of commands with an explanation on how to use them can be found within the [CommandList.md](https://github.com/sonnenbankpimp/Tabuu-3.0-Bot/blob/main/CommandList.md) file.

##  Running the bot
Since this bot is only intended to be used on the SSBU Training Grounds Discord Server, this means that you cannot just invite the bot to your own server.  

However, you can clone this repository and run the bot yourself, if you want to.  
First, you need to install at least Python 3.8 or newer and the latest version of the [discord.py](https://github.com/Rapptz/discord.py) alpha, as well as the other packages listed in the requirements.txt file. Then you need to create and host your own Discord Application.  
This bot needs a lot of server-specific IDs to function properly, so you need to modify the `/utils/ids.py` file with the unique IDs of your servers/channels/roles (Note: If you want the Mee6 leaderboard of your server instead of the Training Grounds one, you need to change that too, in the `/cogs/mee6api.py` file). You may also want to delete the examples in the files in the `/json/` directory, but that is not required at all.  
For the last step you need to create a file named `token.txt` in the `/files/` directory and paste your discord bot token into it, and you're done!  

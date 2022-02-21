# Full list of commands:

This here contains every command with a detailed explanation on how to use them. They are ordered alphabetically, search them with Ctrl+F.  
Last updated: 19 February 2022  
I will try to keep this up-to-date, no promises.  

**%8ball** `<question>`  
    Info: Ask a question and you get a random response from the magic 8-ball.  
    Example: `%8ball Is Tabuu 3.0 the best bot out there?`  
  
**%addrole** `<@user> <role>`  
    Info: **Admin only.** Adds a Role to a User. Mention the User or use User ID, for the Role the bot first tries to use the Role ID or Role mention, after that it searches for the closest match for the role name.  
    Example: `%addrole @Phxenix first class` 
  
**%avatar** `<@user: Optional>`  
    Info: Gets you the avatar of a User. User argument is optional, if there is none, this gets your own avatar. Otherwise mention the User or use User ID.  
    Example: `%avatar @Phxenix` 
  
**%ban** `<@user> <reason>`  
    Info: **Admin only.** Bans a User. Mention the User or use User ID. You will be asked for confirmation before the user gets banned. The reason will get logged in Audit logs and also DM'd to the user, if the bot can DM the user.  
    Example: `%ban @Phxenix what an idiot`  
  
**%banner** `<@user: Optional>`  
    Info: Gets you the banner of a User. User argument is optional, if there is none, this gets your own avatar. Otherwise mention the User or use User ID.  
    Example: `%banner @Phxenix`
  
**%boo**  
    Info: Comes up with some scary stuff.  
  
**%clear** `<amount: Optional>`  
    Info: **Admin only.** Deletes the last X+1 messages in the current channel. Defaults to 1 if you do not specify an amount.  
    Example: `%clear 10`  
  
**%clearmmpings**  
    Info: **Admin only.** Clears all matchmaking pings.  
    Aliases: clearmmrequests, clearmm, clearmatchmaking  
  
**%clearwarns** `<@user>`  
    Info: **Admin only.** Clears all warnings of a User. Mention the User or use User ID.  
    Example: `%clearwarns @Phxenix`  
  
**%coin**  
    Info: Flips a coin and gives you the result. Heads or Tails.  
  
**%colour** `<hex colour code>`  
    Info: Sets your colour on your profile embed. You need to use a hex colour code.  
    Example: `%colour #FFFFFF`  
    Aliases: color, spcolour, spcolor, setcolour, setcolor  
  
**%convert** `<input>`  
    Info: Converts the input between metric and imperial, and vice versa. Works with most common units of length, speed, weight, temperature and volume.  
    Example: `%convert 14 feet`  
    Aliases: conversion  
  
**%countdown** `<number>`  
    Info: Counts down from the specified number between 2 and 50, used for syncing stuff.  
    Example: `%countdown 5`  
  
**%createmacro** `<name> <payload>`  
    Info: **Admin only.** creates a new macro command with your desired payload.  
    Example: `%createmacro test hello this is a test`  
  
**%delete** `<message IDs>`  
    Info: **Admin only.** Deletes Messages by their IDs. The messages need to be in the same channel of the command. Takes as many messages as you like.  
    Example: `%delete 858117781375418389 858117780859256882`  
  
**%deletemacro** `<name>`  
    Info: **Admin only.** Deletes the specified macro command.  
    Example: `%deletemacro test`  
  
**%deleteprofile**  
    Info: Deletes your own profile.  
  
**%deletereminder** `<reminder ID>`  
    Info: Deletes a reminder of yours by the reminder ID. View the reminder IDs with `%viewreminders`.  
    Example: `%deletereminder 1234567`  
    Aliases: delreminder, rmreminder, delreminders, deletereminders  
  
**%deleterolemenu** `<message ID>`  
    Info: **Admin only.** Deletes a Role menu completely.  
    Example: `%deleterolemenu 858117781375418389`  
  
**%deletewarn** `<@user> <warn_id>`  
    Info: **Admin only.** Deletes a warning by the warning ID. View the warnings of a user with `%warndetails`. Mention the User or use User ID.  
    Example: `%deletewarn @Phxenix 123456`  
  
**%doubles**  
    Info: Pings the doubles role and stores your ping for 30 Minutes. Also creates a thread and invites the user to it. Has a 10 minute cooldown and can only be used in our arena channels.  
    Aliases: matchmakingdoubles, mmdoubles, Doubles  
  
**%emote** `<emoji>`  
    Info: Gives you Information about an Emoji. Keep in mind this does not work with default emojis.  
    Example: `%emote :BowserFail:`  
    Aliases: emoji  
  
**%forcedeleteprofile** `<@user>`  
    Info: **Admin only.** deletes the profile of the mentioned user.  
    Example: `%forcedeleteprofile @Phxenix`  
  
**%forcereportmatch** `<@winner> <@loser>`  
    Info: **Admin only.** If a user abandons their ranked match an admin will use this to report the match anyways. Mention the users or use User IDs. Has a 41 second cooldown. Only works in the Training Grounds Server.  
    Example: `%forcereportmatch @Tabuu 3.0 @Phxenix`  
    Aliases: forcereportgame  
  
**%funnies** `<message: Optional>`  
    Info: Pings the funnies role with an optional custom message and stores your ping for 30 Minutes. Also creates a thread and invites the user to it. Has a 10 minute cooldown and can only be used in our arena channels.  
    Aliases: matchmakingfunnies, mmfunnies, Funnies  
  
**%geteveryrolemenu**  
    Info: **Admin only.** Gets you every role menu entry currently saved.  
  
**%help**  
    Info: The help command is broken into a dropdown cause there were too many commands to list. Available dropdowns are: Moderation, Admin Utility, Info, Matchmaking, Profile, Utility, Miscellaneous, and Fun. The Moderation and Admin Utility dropdowns are only available for admins.  
  
**%hypemeup**  
    Info: Hypes you up with a randomly chosen response before that next game of smash.  
    
**%john**  
    Info: Returns a random excuse why you lost that last game of Smash.  
  
**%joke**  
    Info: Returns a random joke, funniness may vary.  
    Aliases: tabuujoke  
  
**%kick** `<@user> <reason>`  
    Info: **Admin only.** Kicks a user from the server. Mention the User or use User ID. You will be asked for confirmation before the user gets kicked. The reason will get logged in Audit logs and also DM'd to the user, if the bot can DM the user.  
    Example: `%kick @Phxenix what an idiot`  
  
**%leaderboard**  
    Info: **Admin only.** Gets you the Top 10 rated players of our ranked matchmaking system.  
  
**%listmacros**  
    Info: Lists out all registered macro commands.  
    Aliases: listmacro, macros, macro  
  
**%listrole** `<role>`  
    Info: Lists out every User with a certain role. The bot first tries to use the Role ID or Role mention, after that it searches for the closest match for the role name.  
    Example: `%listrole first class`  
    Aliases: listroles  
  
**%`<macro>`**  
    Info: Invokes the macro command, list them all with `%listmacros`.  
    Example: `%test`  
  
**%mains** `<main1, main2,..: Optional>`  
    Info: Updates your mains listed on your profile. Up to 7 characters, separate them by commas. Accepts names, commonly used nicknames and the Fighter Numbers. Leave the field blank or input invalid characters to delete the characters.  
    Example: `%mains incin, wii fit, 4e, paisy`  
    Aliases: main, setmain, spmains, profilemains  
  
**%modifyrolemenu** `<message ID> <exclusive: Optional> <Role(s): Optional>`  
    Info: **Admin only.** Modifies a role menu with special properties. Exclusive is a boolean(True/False) value which specifies if a User is able to get 1 role (True) or all roles (False) from this role menu. The role(s) set a requirement so that a User needs one of these roles to get any role of this role menu. Mention the role or use role ID. Both arguments are optional, if left out both default to False/None.  
    Example: `%modifyrolemenu 858117781375418389 True @Singles Winner`  
  
**%modmail** `<your message>`  
    Info: Privately contact the moderator team of this server. Only works in the DM channel of Tabuu 3.0. Use this for reporting rule violations or feedback/suggestions for the Mod Team. You can attach any attachments to the message. Your username will be visible to prevent abuse.  
    Example: `%modmail Hello, I think the moderator team has been doing an awful job lately.`  
  
**%mp4`<move>`**  
    Info: Gives you the mana cost of any of Hero's moves.  
    Example: `%mp4woosh`  
  
**%mute** `<@user> <reason>`  
    Info: **Admin only.** Mutes a user in both servers. The reason will get DM'd to the user, if the bot can DM the user.  
    Example: `%mute @Phxenix what an idiot`  
  
**%newrolemenu** `<message ID> <emoji> <role>`  
    Info: **Admin only.** Creates a new entry for a role menu. Mention the Role or use Role ID and make sure the Bot has access to this emoji.  
    Example: `%newrolemenu 858117781375418389 🥰 @Server Events`  
  
**%note** `<note: Optional>`  
    Info: Sets your note on your profile, up to 150 characters long. Leave it blank to delete the note.  
    Example: `%note test note`  
    Aliases: setnote, spnote  
  
**%pickmeup**  
    Info: Gives you an inspiring quote.  
  
**%ping**  
    Info: Gets the response time of the Bot, *not yourself*. Usually around 100-150ms in optimal conditions.  
  
**%pockets** `<pocket1, pocket2,..: Optional>`  
    Info: Updates your pockets listed on your profile. Up to 10 characters, separate them by commas. Accepts names, commonly used nicknames and the Fighter Numbers. Leave the field blank or input invalid characters to delete the characters.  
    Example: `%pockets incin, wii fit, 4e, paisy`  
    Aliases: pocket, setpocket, sppockets, profilepockets  
  
**%poll** `<"question"> <"option 1"> <"option 2">`  
    Info: Creates a poll for users to vote on with reactions. Takes 2-10 Options. If the question or the options have more than 1 word in them, make sure to surround them with quotes.  
    Example: `%poll "What is your favourite Ice cream?" Chocolate Strawberry "None of the above"`  
  
**%profile** `<@user: Optional>`  
    Info: Gets you the profile of the mentioned user, if you dont specify a user, this will get your own.  
    Example: `%profile @Phxenix`  
    Aliases: smashprofile, profileinfo  
  
**%randomquote**  
    Info: Gets you a random quote from someone.  
  
**%ranked**  
    Info: Pings your ranked role according to you Elo value and stores your ping for 30 Minutes. Has a 2 minute cooldown and can only be used in our ranked arena channels.  
    Aliases: rankedmm, rankedmatchmaking, rankedsingles  
  
**%rankedstats** `<@user: Optional>`  
    Info: Gets you the ranked stats of any optional user. If you dont specify a user, this will get your own stats where you can also choose to remove or add your Elo role.
    Example: `%rankedstats @Phxenix`  
    Aliases: rankstats  
  
**%recentpings**  
    Info: Gets you all pings in the last 30 Minutes of any matchmaking type without pinging the role yourself. Available dropdowns are: Singles, Doubles, Funnies, Ranked.  
  
**%records**  
    Info: **Admin only.** Gets you our ban records.  
  
**%region** `<region: Optional>`  
    Info: Sets your region on your profile. The regions are the 6 commonly used continents, plus some more for North America, matches some inputs to those. So EU will work, as well as europe. Leave the field blank to delete the region from your profile.  
    Example: `%region europe`  
    Aliases: setregion, spregion, country  
  
**%reloadcogs** `<cogs: Optional>`  
    Info: **Owner only.** Tries to reload the specified cogs separated by commas. If you do not specify any cogs, it reloads all of them, so you don't have to restart it for every little change.  
  
**%reminder** `<time> <message>`  
    Info: Reminds you about something. Time is in a shortened format with any number and d/h/m/s. Minimum duration is 30 seconds, maximum is 90 days.  
    Example: `%reminder 10h20m get that thing done you wanted to get done`  
    Aliases: remindme, newreminder, newremindme  
  
**%removerole** `<@user> <role>`  
    Info: **Admin only.** Removes a role from a User. Mention the User or use User ID, for the Role the bot first tries to use the Role ID or Role mention, after that it searches for the closest match for the role name.  
    Example: `%removerole @Phxenix first class`  
  
**%rename** `<@user> <name: Optional>`  
    Info: **Admin only.** Renames the user to the given nickname. Removes the nickname if you do not pass in a new one.  
    Example: `%rename @Phxenix Example Name`  
  
**%reportmatch** `<@user>`  
    Info: The winner uses this command after a ranked match to report the result of the match, @user being the person who lost the ranked match. Mention the User or use User ID. Has a 41 second cooldown. Only works in ranked arenas or the threads within.  
    Example: `%reportmatch @Phxenix`  
    Aliases: reportgame  
  
**%roleinfo** `<role>`  
    Info: Gets you information about a role. The bot first tries to use the Role ID or Role mention, after that it searches for the closest match for the role name.  
    Example: `%roleinfo first class`  
  
**%roll** `<NdN>`  
    Info: Rolls a dice. N are two numbers, first the number of dice then the amount of sides for the dice.  
    Example: `%roll 2d6`  
    Aliases: r  
  
**%rps** `<@user: Optional>`  
    Info: Plays a game of Rock, Paper, Scissors with the mentioned user. If you don't mention a user, you will play against Tabuu 3.0 himself.  
    Example: `%rps @Phxenix`  
    Aliases: rockpaperscissors, rochambeau, roshambo  
  
**%secondaries** `<secondary1, secondary2,..: Optional>`  
    Info: Updates your secondaries listed on your profile. Up to 7 characters, separate them by commas. Accepts names, commonly used nicknames and the Fighter Numbers. Leave the field blank or input invalid characters to delete the characters.  
    Example: `%secondaries incin, wii fit, 4e, paisy`  
    Aliases: secondary, setsecondary, spsecondaries, profilesecondaries  
  
**%server**  
    Info: Gets you some information about the server, does not work in DMs for obvious reasons.  
    Aliases: serverinfo  
  
**%singles**  
    Info: Pings the singles role and stores your ping for 30 Minutes. Also creates a thread and invites the user to it. Has a 10 minute cooldown and can only be used in our arena channels.  
    Aliases: matchmaking, matchmakingsingles, mmsingles, Singles  
  
**%spotify** `<@user: Optional>`  
    Info: Posts the song you are currently listening to on Spotify. You need to enable the setting that displays your Spotify Session as your Discord Status for this to work. Does not work in DMs. User is optional, if not set this will return your own. Mention the User or use User ID.  
    Example: `%spotify @Phxenix`  
  
**%stagelist**  
    Info: Posts our version of the legal stages.  
  
**%starboardemoji** `<emoji>`  
    Info: **Admin only.** Changes the emoji used in our starboard.  
    Example: `%starboardemoji :BowserFail:`  
  
**%starboardthreshold** `<number>`  
    Info: **Admin only.** Changes the threshold for messages to appear on our starboard.  
    Example: `%starboardthreshold 5`  
  
**%stats**  
    Info: Gets you various stats about this bot.  
    Aliases: botstats  
  
**%sticker** `<sticker>`  
    Info: Gets you basic information about a sticker. Note that stickers do not work like emojis but rather like images, so this command gets you the info of the first sticker you attach to your message. Unfortunately, since you currently cannot send a sticker together with a message on discord mobile, this only works in the desktop app.  
    Example: `%sticker Attach Random Sticker Here`  
  
**%syncbanlist**  
    Info: **Admin only.** applies the bans from the SSBUTG server to the SSBUBG server. Can only be used in the SSBUBG server.  
    Aliases: syncbans  
  
**%tabuwu**  
    Info: For the silly people.  
    Aliases: uwu  
  
**%tag** `<tag: Optional>`  
    Info: Updates your tag on your profile, up to 30 characters long. Leave the field blank to reset the tag to your discord username.  
    Example: `%tag test tag`  
    Aliases: smashtag, sptag, settag  
  
**%tempmute** `<@user> <time> <reason>`  
    Info: **Admin only.** Mutes a user in both servers for the specified time, which is in a shortened format with any number and d/h/m/s. Minimum time is 30 seconds, maximum is 1 day. Mention the user or use User ID. The reason will get DM'd to the muted person, if the bot can DM the user.  
    Example: `%tempmute @Phxenix 12h30m what an idiot`  
  
**%time**  
    Info: Shows the current time as a timezone aware object.  
    Aliases: currenttime  
  
**%unban** `<@user>`  
    Info: **Admin only.** Unbans a user. Mention the User or use User ID.  
    Example: `%unban @Phxenix`  
  
**%unmute** `<@user>`  
    Info: **Admin only.** Unmutes a user in both servers. Please use this in all cases to unmute someone. Mention the User or use User ID.  
    Example: `%unmute @Phxenix`  
  
**%updatelevel** `<@user: Optional>`  
    Info: Updates your level role or the one of the mentioned user according to your MEE6 level manually. Has a 5 minute cooldown. Note that this gets done anyways every 23 hours for everyone in the server. Only works in the Training Grounds server.  
    Example: `%updatelevel @Phxenix`  
  
**%userinfo** `<@user: Optional>`  
    Info: Gets you various information about a user. If you haven't specified a user, this will get your own info. Mention the User or use User ID. Does not work in DMs.  
    Example: `%userinfo @Phxenix`  
    Aliases: user  
  
**%viewreminders**  
    Info: Lists out your active reminders. If you have too many it will only display the first 6.  
    Aliases: reminders, myreminders, viewreminder, listreminders  
  
**%warn** `<@user> <reason>`  
    Info: **Admin only.** Use this to warn a user. The reason will get DM'd to the person warned, if the bot can DM the user. Mention the User or use User ID. Warning expire after 30 days. If a user reaches 3 warnings within 30 days the user will get muted, 5 within 30 days equal a kick and 7 within 30 days will get the user banned.  
    Example: `%warn @Phxenix what an idiot`  
  
**%warndetails** `<@user>`  
    Info: **Admin only.** This will give detailed information about a users active warnings. Mention a User or use User ID.  
    Example: `%warndetails @Phxenix`  
  
**%warns** `<@user: Optional>`  
    Info: This will return the number of active warnings a user has. If you haven't specified a User, this will get your own warning count. Mention the User or use User ID.  
    Example: `%warns @Phxenix`  
    Aliases: warnings, infractions  
  
**%who** `<question>`  
    Info: Ask a question and you get a random user that is currently online as a response. Does not work in DMs.  
    Example: `%who is the most beautiful user?`  
  
**%wisdom**  
    Info: Gets you a random piece of wisdom.  
  
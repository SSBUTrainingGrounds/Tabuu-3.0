# Command List

This here contains every command with a detailed explanation on how to use them. They are ordered alphabetically, search them with Ctrl+F.  

Last updated: 22 April 2022  

## Quick explanation of this document  

Arguments that are optional all have the `: Optional` suffix. Every other argument is required.  
**User** refers to any Discord User, **Member** refers to a Server Member.  
**Moderator only** means that you have to be the Server Owner, have Administrator Rights or the Moderator Role to use this Command.  
**Admin only** means that you need to have Administrator Rights in order to use this Command.  
**Owner only** means that only the Bot's Owner can use this Command.  
**Aliases** show you other names the Command is available under. The usage is exactly the same if you use the default name or one of the listed aliases.  
**Slash version available** means that you can use this command the normal way, or as an application command with `/`.  
Everything else should be fairly self-explanatory.  

## Full list of commands
  
- **%2048**  
  - Info: **Slash version available.** Starts a game of 2048.  
  
- **%8ball** `<question>`  
  - Info: **Slash version available.** Ask a question and you get a random response from the magic 8-ball.  
  - Example: `%8ball Is Tabuu 3.0 the best bot out there?`  
  
- **%addbadges** `<@user> <emojis>`  
  - Info: **Moderator only.** Adds one or multiple Badges to a User. Mention the User or use User ID, for the badges they all need to be valid emojis that the bot can use.  
  - Example: `%addbadges @ExampleUser :Example1: :Example2:`  
  - Aliases: addbadge  
  
- **%addrole** `<@member> <role>`  
  - Info: **Moderator only.** Adds a Role to a Member. Mention the Member or use Member ID, for the Role the bot first tries to use the Role ID or Role mention, after that it searches for the closest match for the role name.  
  - Example: `%addrole @ExampleUser first class`  
  
- **%avatar** `<@member: Optional>`  
  - Info: **Slash version available.** Gets you the avatar of a Member. Member argument is optional, if there is none, this gets your own avatar. Otherwise mention the Member or use Member ID.  
  - Example: `%avatar @ExampleUser`  
  - Aliases: icon  
  
- **%ban** `<@user> <reason>`  
  - Info: **Moderator only.** Bans a User. Mention the User or use User ID. You will be asked for confirmation before the User gets banned. The reason will get logged in Audit logs and also DM'd to the User, if the bot can DM the User.  
  - Example: `%ban @ExampleUser what an idiot`  
  
- **%banner** `<@member: Optional>`  
  - Info: **Slash version available.** Gets you the banner of a Member. Member argument is optional, if there is none, this gets your own avatar. Otherwise mention the Member or use Member ID.  
  - Example: `%banner @ExampleUser`  
  
- **%blackjack** `<@member>`  
  - Info: **Slash version available.** Starts a game of Blackjack with the mentioned Member.  
  - Example: `%blackjack @ExampleUser`  
  - Aliases: 21, vingtetun, vigntun  
  
- **%boo**  
  - Info: **Slash version available.** Comes up with some scary stuff.  
  
- **%clear** `<amount: Optional>`  
  - Info: **Moderator only.** Deletes the last X+1 messages in the current channel. Defaults to 1 if you do not specify an amount.  
  - Example: `%clear 10`  
  
- **%clearbadges** `<@user>`  
  - Info: **Moderator only.** Clears all Badges from a User. Mention the User or use User ID.  
  - Example: `%clearbadges @ExampleUser`  
  
- **%clearmmpings**  
  - Info: **Moderator only.** Clears all matchmaking pings.  
  - Aliases: clearmmrequests, clearmm, clearmatchmaking  
  
- **%clearwarns** `<@member>`  
  - Info: **Moderator only.** Clears all warnings of a Member. Mention the Member or use Member ID.  
  - Example: `%clearwarns @ExampleUser`  
  
- **%coin**  
  - Info: **Slash version available.** Flips a coin and gives you the result. Heads or Tails.  
  - Aliases: coinflip, flip, flipcoin  
  
- **%colour** `<hex colour code>`  
  - Info: **Slash version available.** Sets your colour on your profile embed. You need to use a hex colour code.  
  - Example: `%colour #FFFFFF`  
  - Aliases: color, spcolour, spcolor, setcolour, setcolor  
  
- **%convert** `<input>`  
  - Info: **Slash version available.** Converts the input between metric and imperial, and vice versa. Works with most common units of length, speed, weight, temperature and volume.  
  - Example: `%convert 14 feet`  
  - Aliases: conversion  
  
- **%countdown** `<number>`  
  - Info: **Slash version available.** Counts down from the specified number between 2 and 50, used for syncing stuff.  
  - Example: `%countdown 5`  
  
- **%createmacro** `<name> <payload>`  
  - Info: **Moderator only.** creates a new macro command with your desired payload.  
  - Example: `%createmacro test hello this is a test`  
  
- **%delete** `<message IDs>`  
  - Info: **Moderator only.** Deletes Messages by their IDs. The messages need to be in the same channel of the command. Takes as many messages as you like.  
  - Example: `%delete 858117781375418389 858117780859256882`  
  
- **%deletemacro** `<name>`  
  - Info: **Moderator only.** Deletes the specified macro command.  
  - Example: `%deletemacro test`  
  
- **%deleteprofile**  
  - Info: **Slash version available.** Deletes your own profile.  
  
- **%deletereminder** `<reminder ID>`  
  - Info: **Slash version available.** Deletes a reminder of yours by the reminder ID. View the reminder IDs with `%viewreminders`.  
  - Example: `%deletereminder 1234567`  
  - Aliases: delreminder, rmreminder, delreminders, deletereminders  
  
- **%deleterolemenu** `<message ID>`  
  - Info: **Moderator only.** Deletes a Role menu completely.  
  - Example: `%deleterolemenu 858117781375418389`  
  
- **%deletewarn** `<@member> <warn_id>`  
  - Info: **Moderator only.** Deletes a warning by the warning ID. View the warnings of a member with `%warndetails`. Mention the Member or use Member ID.  
  - Example: `%deletewarn @ExampleUser 123456`  
  
- **%doubles**  
  - Info: **Slash version available.** Pings the doubles role and stores your ping for 30 Minutes. Also creates a thread and invites the user to it. Has a 10 minute cooldown and can only be used in our arena channels.  
  - Aliases: matchmakingdoubles, mmdoubles, Doubles  
  
- **%emoji** `<emoji>`  
  - Info: **Slash version available.** Gives you Information about an Emoji. Keep in mind this does not work with default emojis.  
  - Example: `%emote :BowserFail:`  
  - Aliases: emote  
  
- **%editrole**
  - Info: **Moderator only.** Group command that lists the subcommands and their usage. The available properties to edit are: name, colour, icon, mentionable.  

- **%editrole colour** `<colour>`  
  - Info: **Moderator only.** Edits the colour of the role. Mention the role or use role ID. You need to use a hex colour code.  
  - Example: `%editrole colour @Admin #FFFFFF`  
  - Aliases: color  
  
- **%editrole icon** `<emoji: Optional>`  
  - Info: **Moderator only.** Edits the icon of the role. Mention the role or use role ID. You can either use a default or custom emoji, which the bot needs access to, or you can attach an image file that must not be bigger than 256kb. If you do not specify an emoji or image file, the icon will be deleted from the role.  
  - Example: `%editrole icon @Admin 👍`  
  
- **%editrole mentionable** `<boolean>`  
  - Info: **Moderator only.** Edits whether or not the role can be mentioned by others. Mention the role or use role ID. You need to use a boolean value (True/False).  
  - Example: `%editrole mentionable @Admin False`  
  - Aliases: mention  
  
- **%editrole name** `<name>`  
  - Info: **Moderator only.** Edits the name of the role. Mention the role or use role ID. The name can be a maximum of 100 characters long.  
  - Example: `%editrole name @Admin New Admin Role Name`  
  
- **%forcedeleteprofile** `<@user>`  
  - Info: **Moderator only.** Deletes the profile of the mentioned User.  
  - Example: `%forcedeleteprofile @ExampleUser`  
  
- **%forcereportmatch** `<@winner> <@loser>`  
  - Info: **Moderator only.** If someone abandons their ranked match an admin will use this to report the match anyways. Mention the Members or use Member IDs. Has a 41 second cooldown. Only works in the Training Grounds Server.  
  - Example: `%forcereportmatch @Tabuu 3.0 @ExampleUser`  
  - Aliases: forcereportgame  
  
- **%funnies** `<message: Optional>`  
  - Info: **Slash version available.** Pings the funnies role with an optional custom message and stores your ping for 30 Minutes. Also creates a thread and invites the user to it. Has a 10 minute cooldown and can only be used in our arena channels.  
  - Aliases: matchmakingfunnies, mmfunnies, Funnies  
  
- **%geteveryrolemenu**  
  - Info: **Moderator only.** Gets you every role menu entry currently saved.  
  
- **%help** `<command: Optional>`  
  - Info: **Slash version available.** Shows you Info about a specified command. If you do not specify a command you will get the help menu, which is broken into a dropdown cause there were too many commands to list. Available dropdowns are: Moderation, Admin Utility, Info, Matchmaking, Profile, Utility, Miscellaneous, and Fun. The text-based version will show you if you can run this command, the slash based version cannot do so due of a discord limitation.  
  
- **%hypemeup**  
  - Info: **Slash version available.** Hypes you up with a randomly chosen response before that next game of smash.  

- **%john**  
  - Info: **Slash version available.** Returns a random excuse why you lost that last game of Smash.  
  
- **%joke**  
  - Info: **Slash version available.** Returns a random joke, funniness may vary.  
  - Aliases: tabuujoke  
  
- **%kick** `<@member> <reason>`  
  - Info: **Moderator only.** Kicks a member from the server. Mention the Member or use Member ID. You will be asked for confirmation before the Member gets kicked. The reason will get logged in Audit logs and also DM'd to the Member, if the bot can DM the Member.  
  - Example: `%kick @ExampleUser what an idiot`  
  
- **%leaderboard**  
  - Info: **Moderator only.** Gets you the Top 10 rated players of our ranked matchmaking system.  
  
- **%listrole** `<role>`  
  - Info: **Slash version available.** Lists out every Member with a certain role. The bot first tries to use the Role ID or Role mention, after that it searches for the closest match for the role name.  
  - Example: `%listrole first class`  
  - Aliases: listroles  
  
- **%`<macro>`**  
  - Info: Invokes the macro command, list them all with `%macros`.  
  - Example: `%test`  

- **%macro** `<macro: Optional>`  
  - Info: **Slash version available.** Gives you information about a specific macro, or if you do not specify a macro it will list out all registered macro commands.  
  - Aliases: listmacro, macros, macrostats  
  
- **%mains** `<main1, main2,..: Optional>`  
  - Info: **Slash version available.** Updates your mains listed on your profile. Up to 7 characters, separate them by commas. Accepts names, commonly used nicknames and the Fighter Numbers. Leave the field blank or input invalid characters to delete the characters.  
  - Example: `%mains incin, wii fit, 4e, paisy`  
  - Aliases: main, setmain, spmains, profilemains  
  
- **%modifyrolemenu** `<message ID> <exclusive: Optional> <Role(s): Optional>`  
  - Info: **Moderator only.** Modifies a role menu with special properties. Exclusive is a boolean(True/False) value which specifies if a Member is able to get 1 role (True) or all roles (False) from this role menu. The role(s) set a requirement so that a Member needs one of these roles to get any role of this role menu. Mention the role or use role ID. Both arguments are optional, if left out both default to False/None.  
  - Example: `%modifyrolemenu 858117781375418389 True @Singles Winner`  
  
- **%modmail** `<your message>`  
  - Info: Privately contact the moderator team of this server. Only works in the DM channel of Tabuu 3.0. Use this for reporting rule violations or feedback/suggestions for the Mod Team. You can attach any attachments to the message. Your Username will be visible to prevent abuse.  
  - Example: `%modmail Hello, I think the moderator team has been doing an awful job lately.`  
  
- **%mp4** `<move>`  
  - Info: **Slash version available.** Gives you the mana cost of any of Hero's moves. If you do not specify a move, lists every available move.  
  - Example: `%mp4 woosh`  
  
- **%mute** `<@member> <reason>`  
  - Info: **Moderator only.** Mutes a Member in both servers. The reason will get DM'd to the Member, if the bot can DM the Member.  
  - Example: `%mute @ExampleUser what an idiot`  
  
- **%newrolemenu** `<message ID> <emoji> <role>`  
  - Info: **Moderator only.** Creates a new entry for a role menu. Mention the Role or use Role ID and make sure the Bot has access to this emoji.  
  - Example: `%newrolemenu 858117781375418389 🥰 @Server Events`  
  
- **%note** `<note: Optional>`  
  - Info: **Slash version available.** Sets your note on your profile, up to 150 characters long. Leave it blank to delete the note.  
  - Example: `%note test note`  
  - Aliases: setnote, spnote  
  
- **%pickmeup**  
  - Info: **Slash version available.** Gives you an inspiring quote.  
  
- **%ping**  
  - Info: **Slash version available.** Gets the response time of the Bot, *not yourself*. Usually around 100-150ms in optimal conditions.  
  
- **%pockets** `<pocket1, pocket2,..: Optional>`  
  - Info: **Slash version available.** Updates your pockets listed on your profile. Up to 10 characters, separate them by commas. Accepts names, commonly used nicknames and the Fighter Numbers. Leave the field blank or input invalid characters to delete the characters.  
  - Example: `%pockets incin, wii fit, 4e, paisy`  
  - Aliases: pocket, setpocket, sppockets, profilepockets  
  
- **%poll** `<options> <question>`  
  - Info: **Slash version available.** Creates a poll for Users to vote on with reactions. Specify the amount of options with a number, between 2 and 5. Sends a button which, if you click it opens a modal for you to type the choices into.  
  - Example: `%poll 3 What is your favorite Ice Cream?`  
  
- **%profile** `<@user: Optional>`  
  - Info: **Slash version available.** Gets you the profile of the mentioned User, if you dont specify a User, this will get your own.  
  - Example: `%profile @ExampleUser`  
  - Aliases: smashprofile, profileinfo  
  
- **%randomquote**  
  - Info: **Slash version available.** Gets you a random quote from someone.  
  
- **%ranked**  
  - Info: **Slash version available.** Pings your ranked role according to you Elo value and stores your ping for 30 Minutes. Has a 2 minute cooldown and can only be used in our ranked arena channels.  
  - Aliases: rankedmm, rankedmatchmaking, rankedsingles  
  
- **%rankstats** `<@user: Optional>`  
  - Info: **Slash version available.** Gets you the ranked stats of any optional User. If you dont specify a User, this will get your own stats where you can also choose to remove or add your Elo role.
  - Example: `%rankedstats @ExampleUser`  
  - Aliases: rankedstats  
  
- **%recentpings**  
  - Info: **Slash version available.** Gets you all pings in the last 30 Minutes of any matchmaking type without pinging the role yourself. Available dropdowns are: Singles, Doubles, Funnies, Ranked.  
  
- **%records**  
  - Info: **Moderator only.** Gets you our ban records.  
  
- **%region** `<region: Optional>`  
  - Info: **Slash version available.** Sets your region on your profile. The regions are the 6 commonly used continents, plus some more for North America, matches some inputs to those. So EU will work, as well as europe. Leave the field blank to delete the region from your profile.  
  - Example: `%region europe`  
  - Aliases: setregion, spregion, country  
  
- **%reloadcogs** `<cogs: Optional>`  
  - Info: **Owner only.** Tries to reload the specified cogs separated by commas. If you do not specify any cogs, it reloads all of them, so you don't have to restart it for every little change.  
  - Example: `%reloadcogs admin`  
  
- **%reminder** `<time> <message>`  
  - Info: **Slash version available.** Reminds you about something. Time is in a format with a number and the duration, do not use spaces inbetween multiple times. Minimum duration is 30 seconds, maximum is 90 days.  
  - Example: `%reminder 12h30mins get that thing done you wanted to get done`  
  - Aliases: remindme, newreminder, newremindme  
  
- **%removebadge** `<@user> <emoji>`  
  - Info: **Moderator only.** Removes one Badge from a User. Mention the User or use User ID. Will check before if the User actually has the Badge in question.  
  - Example: `%removebadge @ExampleUser :Example1:`  
  - Aliases: removebadges  
  
- **%removerole** `<@member> <role>`  
  - Info: **Moderator only.** Removes a role from a Member. Mention the Member or use Member ID, for the Role the bot first tries to use the Role ID or Role mention, after that it searches for the closest match for the role name.  
  - Example: `%removerole @ExampleUser first class`  
  
- **%removetimeout** `<@member>`  
  - Info: **Moderator only.** Removes a timeout from a Member. Mention the Member or use Member ID.  
  - Example: `%removetimeout @ExampleUser`  
  - Aliases: untimeout  
  
- **%rename** `<@member> <name: Optional>`  
  - Info: **Moderator only.** Renames the Member to the given nickname. Removes the nickname if you do not pass in a new one.  
  - Example: `%rename @ExampleUser Example Name`  
  
- **%reportmatch** `<@member>`  
  - Info: **Slash version available.** The winner uses this command after a ranked match to report the result of the match, @member being the person who lost the ranked match. Mention the Member or use Member ID. Has a 41 second cooldown. Only works in ranked arenas or the threads within.  
  - Example: `%reportmatch @ExampleUser`  
  - Aliases: reportgame  
  
- **%roleinfo** `<role>`  
  - Info: **Slash version available.** Gets you information about a role. The bot first tries to use the Role ID or Role mention, after that it searches for the closest match for the role name.  
  - Example: `%roleinfo first class`  
  - Aliases: role  
  
- **%roll** `<NdN>`  
  - Info: **Slash version available.** Rolls a dice. N are two numbers, first the number of dice then the amount of sides for the dice.  
  - Example: `%roll 2d6`  
  - Aliases: r  
  
- **%rps** `<@member: Optional>`  
  - Info: **Slash version available.** Plays a game of Rock, Paper, Scissors with the mentioned Member. If you don't mention a Member, you will play against Tabuu 3.0 himself.  
  - Example: `%rps @ExampleUser`  
  - Aliases: rockpaperscissors, rochambeau, roshambo  
  
- **%say** `<channel> <message>`  
  - Info: **Admin Only.** Repeats the given Message in the given Text Channel.  
  - Example: `%say #announcements Important Announcement`  
  
- **%secondaries** `<secondary1, secondary2,..: Optional>`  
  - Info: **Slash version available.** Updates your secondaries listed on your profile. Up to 7 characters, separate them by commas. Accepts names, commonly used nicknames and the Fighter Numbers. Leave the field blank or input invalid characters to delete the characters.  
  - Example: `%secondaries incin, wii fit, 4e, paisy`  
  - Aliases: secondary, setsecondary, spsecondaries, profilesecondaries  
  
- **%server**  
  - Info: **Slash version available.** Gets you some information about the server, does not work in DMs for obvious reasons.  
  - Aliases: serverinfo  
  
- **%setupmodmailbutton**  
  - Info: **Moderator only.** Sets up a new button to listen to, for creating modmail threads. Should really only be used once.  
  
- **%singles**  
  - Info: **Slash version available.** Pings the singles role and stores your ping for 30 Minutes. Also creates a thread and invites the User to it. Has a 10 minute cooldown and can only be used in our arena channels.  
  - Aliases: matchmaking, matchmakingsingles, mmsingles, Singles  
  
- **%spotify** `<@member: Optional>`  
  - Info: **Slash version available.** Posts the song you are currently listening to on Spotify. You need to enable the setting that displays your Spotify Session as your Discord Status for this to work. Does not work in DMs. Member is optional, if not set this will return your own. Mention the Member or use Member ID.  
  - Example: `%spotify @ExampleUser`  
  
- **%stagelist**  
  - Info: **Slash version available.** Posts our version of the legal stages.  
  
- **%starboardemoji** `<emoji>`  
  - Info: **Moderator only.** Changes the emoji used in our starboard.  
  - Example: `%starboardemoji :BowserFail:`  
  
- **%starboardthreshold** `<number>`  
  - Info: **Moderator only.** Changes the threshold for messages to appear on our starboard.  
  - Example: `%starboardthreshold 5`  
  
- **%stats**  
  - Info: **Slash version available.** Gets you various stats about this bot.  
  - Aliases: botstats  
  
- **%sticker** `<sticker>`  
  - Info: Gets you basic information about a sticker. Note that stickers do not work like emojis but rather like images, so this command gets you the info of the first sticker you attach to your message. Unfortunately, since you currently cannot send a sticker together with a message on Discord Mobile, this only works in the desktop app.  
  - Example: `%sticker Attach Random Sticker Here`  
  
- **%syncbanlist**  
  - Info: **Moderator only.** applies the bans from the SSBUTG server to the SSBUBG server. Can only be used in the SSBUBG server.  
  - Aliases: syncbans  
  
- **%synccommands** `<guild: Optional>`  
  - Info: **Owner only.** Syncs the local Application Commands to the Discord Client in the specified guild, or in all guilds, if you do not specify a guild.  
  - Example: `%synccommands 739299507795132486`  
  - Aliases: sync, syncommands  
  
- **%tabuwu**  
  - Info: **Slash version available.** For the silly people.  
  - Aliases: uwu  
  
- **%tag** `<tag: Optional>`  
  - Info: **Slash version available.** Updates your tag on your profile, up to 30 characters long. Leave the field blank to reset the tag to your Discord Username.  
  - Example: `%tag test tag`  
  - Aliases: smashtag, sptag, settag  
  
- **%tempmute** `<@member> <time> <reason>`  
  - Info: **Moderator only.** Mutes a Member in both servers for the specified time, in a format with a number and the duration. Do not use spaces inbetween multiple times. Minimum time is 30 seconds, maximum is 1 day. Mention the Member or use Member ID. The reason will get DM'd to the muted person, if the bot can DM the Member.  
  - Example: `%tempmute @ExampleUser 12h30mins what an idiot`  
  
- **%tictactoe** `<@member>`  
  - Info: **Slash version available.** Plays a game of Tic Tac Toe with the mentioned Member.  
  - Example: `%tictactoe @ExampleUser`  
  - Aliases: ttt  
  
- **%time**  
  - Info: **Slash version available.** Shows the current time as a timezone aware object.  
  - Aliases: currenttime  
  
- **%timeout** `<@member> <time> <reason>`  
  - Info: **Moderator only.** Times out a Member for the specified time and tries to DM them the reason. Maximum time is 28 days - 1 second. Mention the Member or use Member ID. The reason will get DM'd to the muted person, if the bot can DM the Member. Uses the same time converter as tempmute and reminders, in a format with a number and the duration. Do not use spaces inbetween multiple times.  
  - Example: `%timeout @ExampleUser 12h30mins what an idiot`  
  
- **%translate** `<message>`  
  - Info: **Slash version available.** Translates a message or a specified string into english. Either type your own message, reply to a message or specify a message via message ID or Link. Attempts to recognise the original language.  
  - Example: `%translate bonjour!`  
  
- **%unban** `<@user>`  
  - Info: **Moderator only.** Unbans a user. Mention the User or use User ID.  
  - Example: `%unban @ExampleUser`  
  
- **%unmute** `<@member>`  
  - Info: **Moderator only.** Unmutes a Member in both servers. Please use this in all cases to unmute someone. Mention the Member or use Member ID.  
  - Example: `%unmute @ExampleUser`  
  
- **%updatelevel** `<@member: Optional>`  
  - Info: **Slash version available.** Updates your level role or the one of the mentioned Member according to your MEE6 level manually. Has a 5 minute cooldown. Note that this gets done anyways every 23 hours for everyone in the server. Only works in the Training Grounds server.  
  - Example: `%updatelevel @ExampleUser`  
  
- **%userinfo** `<@member: Optional>`  
  - Info: **Slash version available.** Gets you various information about a Member. If you haven't specified a Member, this will get your own info. Mention the Member or use Member ID. Does not work in DMs.  
  - Example: `%userinfo @ExampleUser`  
  - Aliases: user, user-info, info  
  
- **%viewreminders**  
  - Info: **Slash version available.** Lists out your active reminders. If you have too many it will only display the first 6.  
  - Aliases: reminders, myreminders, viewreminder, listreminders  
  
- **%warn** `<@member> <reason>`  
  - Info: **Moderator only.** Use this to warn a Member. The reason will get DM'd to the person warned, if the bot can DM the Member. Mention the Member or use Member ID. Warning expire after 30 days. If a Member reaches 3 warnings within 30 days the Member will get muted, 5 within 30 days equal a kick and 7 within 30 days will get the Member banned.  
  - Example: `%warn @ExampleUser what an idiot`  
  
- **%warndetails** `<@member>`  
  - Info: **Moderator only.** This will give detailed information about a Members active warnings. Mention a Member or use Member ID.  
  - Example: `%warndetails @ExampleUser`  
  
- **%warns** `<@member: Optional>`  
  - Info: **Slash version available.** This will return the number of active warnings a Member has. If you haven't specified a Member, this will get your own warning count. Mention the Member or use Member ID.  
  - Example: `%warns @ExampleUser`  
  - Aliases: warnings, infractions  
  
- **%who** `<question>`  
  - Info: **Slash version available.** Ask a question and you get a random Member that is currently online as a response. Does not work in DMs.  
  - Example: `%who is the most beautiful user?`  
  
- **%wisdom**  
  - Info: **Slash version available.** Gets you a random piece of wisdom.  

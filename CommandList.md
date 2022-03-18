# Full list of commands:

This here contains every command with a detailed explanation on how to use them. They are ordered alphabetically, search them with Ctrl+F.  

### Quick explanation of the columns:
Arguments that are optional all have the `:Optional` suffix. Every other argument is required.  
The `Admin` column shows you whether a command needs Moderator Permissions: `✓`, Owner Permissions: `○`, or everyone can use it: `✗`.  
The `Slash` column shows you whether or not a Slash Command / Application Command Version of this Command is available. If yes `✓`, you can use both the Normal and Slash version, if not `✗`, only the Text-based Command is available.  
The `Aliases` column shows you other names the Command is available from. The usage is exactly the same, if you use the default name or one of the listed aliases.  
Everything else should be self-explanatory.  

Last updated: 18 March 2022  
I will try to keep this up-to-date, no promises.  

| Command | Arguments | Admin | Slash | Info | Usage | Aliases |
| ------- | --------- | :---: | :---: | ---- | ----- | ------- |
| **%8ball** | `<question>` | ✗ | ✗ | Ask a question and you get a random response from the magic 8-ball. | `%8ball Is Tabuu 3.0 the best bot out there?` | 
| **%addbadges** | `<@user> <emojis>` | ✓ | ✗ | Adds one or multiple Badges to a User. Mention the User or use User ID, for the badges they all need to be valid emojis that the bot can use. Automatically checks for duplicate entries. | `%addbadges @Phxenix :Example1: :Example2:` | addbadge |
| **%addrole** | `<@user> <role>` | ✓ | ✗ | Adds a Role to a User. Mention the User or use User ID, for the Role the bot first tries to use the Role ID or Role mention, after that it searches for the closest match for the role name. | `%addrole @Phxenix first class` |
| **%avatar** | `<@user: Optional>` | ✗ | ✗ | Info: Gets you the avatar of a User. User argument is optional, if there is none, this gets your own avatar. Otherwise mention the User or use User ID. | `%avatar @Phxenix` |
| **%ban** | `<@user> <reason>` | ✓ | ✗ | Bans a User. Mention the User or use User ID. You will be asked for confirmation before the user gets banned. The reason will get logged in Audit logs and also DM'd to the user, if the bot can DM the user. | `%ban @Phxenix what an idiot` |
| **%banner** | `<@user: Optional>` | ✗ | ✗ | Gets you the banner of a User. User argument is optional, if there is none, this gets your own avatar. Otherwise mention the User or use User ID. | `%banner @Phxenix` | 
| **%boo** | | ✗ | ✗ | Comes up with some scary stuff. | `%boo` |
| **%clear** | `<amount: Optional>` | ✓ | ✗ | Deletes the last X+1 messages in the current channel. Defaults to 1 if you do not specify an amount. | `%clear 100` |
| **%clearbadges** | `<@user>` | ✓ | ✗ | Clears all Badges from a User. Mention the User or use User ID. | `%clearbadges @Phxenix` | 
| **%clearmmpings** | | ✓ | ✗ | Clears all matchmaking pings. | `%clearmmpings` | clearmmrequests, clearmm, clearmatchmaking |
| **%clearwarns** | `<@user>` | ✓ | ✗ | Clears all warnings of a User. Mention the User or use User ID. | `%clearwarns @Phxenix` |
| **%coin** | | ✗ | ✗ | Flips a coin and gives you the result. Heads or Tails. | `%coin` | 
| **%colour** | `<hex colour>` | ✗ | ✗ | Sets your colour on your profile embed. You need to use a hex colour code. | `%colour #FFFFFF` | color, spcolour, spcolor, setcolour, setcolor |
| **%convert** | `<input>` | ✗ | ✗ | Converts the input between metric and imperial, and vice versa. Works with most common units of length, speed, weight, temperature and volume. | `%convert 14 feet` | conversion |
| **%countdown** | `<number>` | ✗ | ✗ | Counts down from the specified number between 2 and 50, used for syncing stuff. | `%countdown 5` |
| **%createmacro** | `<name> <payload>` | ✓ | ✗ | Creates a new macro command with your desired payload. | `%createmacro test hello this is a test` |
| **%delete** | `<message IDs>` | ✓ | ✗ | Deletes Messages by their IDs. The messages need to be in the same channel of the command. Takes as many messages as you like. | `%delete 858117781375418389 858117780859256882` |
| **%deletemacro** | `<name>` | ✓ | ✗ | Deletes the specified macro command. | `%deletemacro test` |
| **%deleteprofile** | | ✗ | ✗ | Deletes your own profile. | `%deleteprofile` | 
| **%deletereminder** | `<reminder ID>` | ✗ | ✗ | Deletes a reminder of yours by the reminder ID. View the reminder IDs with `%viewreminders`. | `%deletereminder 1234567` | delreminder, rmreminder, delreminders, deletereminders |
| **%deleterolemenu** | `<message ID>` | ✓ | ✗ | Deletes a Role menu completely. | `%deleterolemenu 858117781375418389` |
| **%deletewarn** | `<@user> <warn_id>` | ✓ | ✗ | Deletes a warning by the warning ID. View the warnings of a user with `%warndetails`. Mention the User or use User ID. | `%deletewarn @Phxenix 123456` |
| **%doubles** | | ✗ | ✗ | Pings the doubles role and stores your ping for 30 Minutes. Also creates a thread and invites the user to it. Has a 10 minute cooldown and can only be used in our arena channels. | `%doubles` | matchmakingdoubles, mmdoubles, Doubles |
| **%emote** | `<emoji>` | ✗ | ✗ | Gives you Information about an Emoji. Keep in mind this does not work with default emojis. | `%emote :BowserFail:` | emoji |
| **%forcedeleteprofile** | `<@user>` | ✓ | ✗ | Deletes the profile of the mentioned user. | `%forcedeleteprofile @Phxenix` |
| **%forcereportmatch** | `<@winner> <@loser>` | ✓ | ✗ | If a user abandons their ranked match an admin will use this to report the match anyways. Mention the users or use User IDs. Has a 41 second cooldown. Only works in the Training Grounds Server. | `%forcereportmatch @Tabuu 3.0 @Phxenix` | forcereportgame |
| **%funnies** | `<message: Optional>` | ✗ | ✗ | Pings the funnies role with an optional custom message and stores your ping for 30 Minutes. Also creates a thread and invites the user to it. Has a 10 minute cooldown and can only be used in our arena channels. | `%funnies Final Smash Meter on` | matchmakingfunnies, mmfunnies, Funnies |
| **%geteveryrolemenu** | | ✓ | ✗ | Gets you every role menu entry currently saved. | `%geteveryrolemenu` |
| **%help** | `<command: Optional>` | ✗ | ✗ | Shows you Info about a specified command. If you do not specify a command you will get the help menu, which is broken into a dropdown cause there were too many commands to list. Available dropdowns are: Moderation, Admin Utility, Info, Matchmaking, Profile, Utility, Miscellaneous, and Fun. | `%help ban` | 
| **%hypemeup** | | ✗ | ✗ | Hypes you up with a randomly chosen response before that next game of smash. | `%hypemeup` |
| **%john** | | ✗ | ✗ | Returns a random excuse why you lost that last game of Smash. | `%john` | 
| **%joke** | | ✗ | ✗ | Returns a random joke, funniness may vary. | `%joke` | tabuujoke |
| **%kick** | `<@user> <reason>` | ✓ | ✗ | Kicks a user from the server. Mention the User or use User ID. You will be asked for confirmation before the user gets kicked. The reason will get logged in Audit logs and also DM'd to the user, if the bot can DM the user. | `%kick @Phxenix what an idiot` |
| **%leaderboard** | | ✓ | ✗ | Gets you the Top 10 rated players of our ranked matchmaking system. | `%leaderboard` | 
| **%listmacros** | | ✗ | ✗ | Lists out all registered macro commands. | `%listmacros` | listmacro, macros, macro |
| **%listrole** | `<role>` | ✗ | ✗ | Lists out every User with a certain role. The bot first tries to use the Role ID or Role mention, after that it searches for the closest match for the role name. | `%listrole first class` | listroles |
| **%`<macro>`** | | ✗ | ✗ | Invokes the macro command, list them all with `%listmacros`. | `%test` |
| **%mains** | `<main1, main2,..: Optional>` | ✗ | ✗ | Updates your mains listed on your profile. Up to 7 characters, separate them by commas. Accepts names, commonly used nicknames and the Fighter Numbers. Leave the field blank or input invalid characters to delete the characters. | `%mains incin, wii fit, 4e, paisy` | main, setmain, spmains, profilemains |
| **%modifyrolemenu** | `<message ID> <exclusive: Optional> <Role(s): Optional>` | ✓ | ✗ | Modifies a role menu with special properties. Exclusive is a boolean(True/False) value which specifies if a User is able to get 1 role (True) or all roles (False) from this role menu. The role(s) set a requirement so that a User needs one of these roles to get any role of this role menu. Mention the role or use role ID. Both arguments are optional, if left out both default to False/None. | `%modifyrolemenu 858117781375418389 True @Singles Winner @Doubles Winner` |
| **%modmail** | `<your message>` | ✗ | ✗ | Privately contact the moderator team of this server. Only works in the DM channel of Tabuu 3.0. Use this for reporting rule violations or feedback/suggestions for the Mod Team. You can attach any attachments to the message. Your username will be visible to prevent abuse. | `%modmail Hello, I think the moderator team has been doing an awful job lately.` |
| **%mp4`<move>`** | | ✗ | ✗ | Gives you the mana cost of any of Hero's moves. | `%mp4woosh` |
| **%mute** | `<@user> <reason>` | ✓ | ✗ | Mutes a user in all servers. The reason will get DM'd to the user, if the bot can DM the user. | `%mute @Phxenix what an idiot` |
| **%newrolemenu** | `<message ID> <emoji> <role>` | ✓ | ✗ | Creates a new entry for a role menu. Mention the Role or use Role ID and make sure the Bot has access to this emoji. | `%newrolemenu 858117781375418389 🥰 @Server Events` |
| **%note** | `<note: Optional>` | ✗ | ✗ | Sets your note on your profile, up to 150 characters long. Leave it blank to delete the note. | `%note test note` | setnote, spnote |
| **%pickmeup** | | ✗ | ✗ | Gives you an inspiring quote. | `%pickmeup` |
| **%ping** | | ✗ | ✗ | Gets the response time of the Bot, *not yourself*. Usually around 100-150ms in optimal conditions. | `%ping` |
| **%pockets** | `<pocket1, pocket2,..: Optional>` | ✗ | ✗ | Updates your pockets listed on your profile. Up to 10 characters, separate them by commas. Accepts names, commonly used nicknames and the Fighter Numbers. Leave the field blank or input invalid characters to delete the characters. | `%pockets incin, wii fit, 4e, paisy` | pocket, setpocket, sppockets, profilepockets |
| **%poll** | `<"question"> <"option 1"> <"option 2">` | ✗ | ✗ | Creates a poll for users to vote on with reactions. Takes 2-10 Options. If the question or the options have more than 1 word in them, make sure to surround them with quotes. | `%poll "What is your favourite Ice cream?" Chocolate Strawberry "None of the above"` |
| **%profile** | `<@user: Optional>` | ✗ | ✗ | Gets you the profile of the mentioned user, if you dont specify a user, this will get your own. | `%profile @Phxenix` | smashprofile, profileinfo |
| **%randomquote** | | ✗ | ✗ | Gets you a random quote from someone. | `%randomquote` |
| **%ranked** | | ✗ | ✗ | Pings your ranked role and adjacent roles according to your Elo value and stores your ping for 30 Minutes. Has a 2 minute cooldown and can only be used in our ranked arena channels. | `%ranked` | rankedmm, rankedmatchmaking, rankedsingles |
| **%rankedstats** | `<@user: Optional>` | ✗ | ✗ | Gets you the ranked stats of any optional user. If you dont specify a user, this will get your own stats where you can also choose to remove or add your Elo role. | `%rankedstats @Phxenix` | rankstats |
| **%recentpings** | | ✗ | ✗ | Gets you a dropdown menu with all pings in the last 30 Minutes of any matchmaking type without pinging the role yourself. Available dropdowns are: Singles, Doubles, Funnies, Ranked. | `%recentpings` |
| **%records** | | ✓ | ✗ | Gets you our ban records. | `%records` |
| **%region** | `<region: Optional>` | ✗ | ✗ | Sets your region on your profile. The regions are the 6 commonly used continents, plus some more for North America, matches common inputs to those. Leave the field blank to delete the region from your profile. | `%region europe` | setregion, spregion, country |
|**%reloadcogs** | `<cogs: Optional>` | ○ | ✗ | Tries to reload the specified cogs separated by commas. If you do not specify any cogs, it reloads all of them, so you don't have to restart it for every little change. | `%reloadcogs admin` | 
| **%reminder** | `<time> <message>` | ✗ | ✗ | Reminds you about something. Time is in a shortened format with any number and d/h/m/s. Minimum duration is 30 seconds, maximum is 90 days. | `%reminder 10h20m get that thing done you wanted to get done` | remindme, newreminder, newremindme |
| **%removebadge** | `<@user> <emoji>` | ✓ | ✗ | Removes one Badge from a User. Mention the User or use User ID. Will check before if the User actually has the Badge in question. | `%removebadge @Phxenix :Example1:` | removebadges |
| **%removerole** | `<@user> <role>` | ✓ | ✗ | Removes a role from a User. Mention the User or use User ID, for the Role the bot first tries to use the Role ID or Role mention, after that it searches for the closest match for the role name. | `%removerole @Phxenix first class` |
| **%removetimeout** | `<@user>` | ✓ | ✗ | Removes a timeout from a User in all Servers. Mention the User or use User ID. | `%removetimeout @Phxenix` | untimeout |
| **%rename** | `<@user> <name: Optional>` | ✓ | ✗ | Renames the user to the given nickname. Removes the nickname if you do not pass in a new one. | `%rename @Phxenix Example Name` |
| **%reportmatch** | `<@user>` | ✗ | ✗ | The winner uses this command after a ranked match to report the result of the match, @user being the person who lost the ranked match. Mention the User or use User ID. Has a 41 second cooldown. Only works in ranked arenas or the threads within. | `%reportmatch @Phxenix` | reportgame |
| **%roleinfo** | `<role>` | ✗ | ✗ | Gets you information about a role. The bot first tries to use the Role ID or Role mention, after that it searches for the closest match for the role name. | `%roleinfo first class` | role |
| **%roll** | `<NdN>` | ✗ | ✗ | Rolls a dice. N are two numbers, first the number of dice then the amount of sides for the dice. | `%roll 2d6` | r |
| **%rps** | `<@user: Optional>` | ✗ | ✗ | Plays a game of Rock, Paper, Scissors with the mentioned user. If you don't mention a user, you will play against Tabuu 3.0 himself. | `%rps @Phxenix` | rockpaperscissors, rochambeau, roshambo |
| **%secondaries** | `<secondary1, secondary2,..: Optional>` | ✗ | ✗ | Updates your secondaries listed on your profile. Up to 7 characters, separate them by commas. Accepts names, commonly used nicknames and the Fighter Numbers. Leave the field blank or input invalid characters to delete the characters. | `%secondaries incin, wii fit, 4e, paisy` | secondary, setsecondary, spsecondaries, profilesecondaries |
| **%server** | | ✗ | ✗ | Gets you some information about the server, does not work in DMs for obvious reasons. | serverinfo |
| **%setupmodmailbutton** | | ✓ | ✗ | Sets up a new button to listen to, for creating modmail threads. Should really only be used once. | `%setupmodmailbutton` |
| **%singles** | | ✗ | ✗ | Pings the singles role and stores your ping for 30 Minutes. Also creates a thread and invites the user to it. Has a 10 minute cooldown and can only be used in our arena channels. | `%singles` | matchmaking, matchmakingsingles, mmsingles, Singles |
| **%spotify** | `<@user: Optional>` | ✗ | ✗ | Posts the song you are currently listening to on Spotify. You need to enable the setting that displays your Spotify Session as your Discord Status for this to work. Does not work in DMs. User is optional, if not set this will return your own. Mention the User or use User ID. | `%spotify @Phxenix` |
| **%stagelist** | | ✗ | ✗ | Posts our version of the legal stages. | `%stagelist` |
| **%starboardemoji** | `<emoji>` | ✓ | ✗ | Changes the emoji used in our starboard. | `%starboardemoji :BowserFail:` |
| **%starboardthreshold** | `<number>` | ✓ | ✗ | Changes the threshold for messages to appear on our starboard. | `%starboardthreshold 5` |
| **%stats** | | ✗ | ✗ | Gets you various stats about this bot. | `%stats` | botstats | 
| **%sticker** | `<sticker>` | ✗ | ✗ | Gets you basic information about a sticker. Note that stickers do not work like emojis but rather like images, so this command gets you the info of the first sticker you attach to your message. Unfortunately, since you currently cannot send a sticker together with a message on discord mobile, this only works in the desktop app. | `%sticker Attach Random Sticker Here` |
| **%syncbanlist** | | ✓ | ✗ | Applies the bans from the SSBUTG server to the SSBUBG server. Can only be used in the SSBUBG server. | `%syncbanlist` | syncbans |
| **%synccommands** | `<guild: Optional>` | ○ | ✗ | Syncs the local Application Commands to the Discord Client in the specified guild, or in all guilds, if you do not specify a guild. | `%synccommands 739299507795132486` | sync, syncommands |
| **%tabuwu** | | ✗ | ✗ | For the silly people. | `%tabuwu` | uwu |
| **%tag** | `<tag: Optional>` | ✗ | ✗ | Updates your tag on your profile, up to 30 characters long. Leave the field blank to reset the tag to your discord username. | `%tag test tag` | smashtag, sptag, settag |
| **%tempmute** | `<@user> <time> <reason>` | ✓ | ✗ | Mutes a user in both servers for the specified time, which is in a shortened format with any number and d/h/m/s. Minimum time is 30 seconds, maximum is 1 day. Mention the user or use User ID. The reason will get DM'd to the muted person, if the bot can DM the user. | `%tempmute @Phxenix 12h30m what an idiot` |
| **%time** | | ✗ | ✗ | Shows the current time as a timezone aware object. | `%time` | currenttime |
| **%timeout** | `<@user> <time> <reason>` | ✓ | ✗ | Times out a user in all Servers for the specified time and tries to DM them the reason. Maximum time is 28 days - 1 second. Mention the user or use User ID. The reason will get DM'd to the muted person, if the bot can DM the user. Uses the same time converter as tempmute and reminders, in a shortened format with any number and d/h/m/s. | `%timeout @Phxenix 12h30m what an idiot` |
| **%unban** | `<@user>` | ✓ | ✗ | Unbans a user. Mention the User or use User ID. | `%unban @Phxenix` | 
| **%unmute** | `<@user>` | ✓ | ✗ | Unmutes a user in all Servers. Please use this in all cases to unmute someone. Mention the User or use User ID. | `%unmute @Phxenix` |
| **%updatelevel** | `<@user: Optional>` | ✓ | ✗ | Updates your level role or the one of the mentioned user according to your MEE6 level manually. Has a 5 minute cooldown. Note that this gets done anyways every 23 hours for everyone in the server. Only works in the Training Grounds server. | `%updatelevel @Phxenix` |
| **%userinfo** | `<@user: Optional>` | ✗ | ✗ | Gets you various information about a user. If you haven't specified a user, this will get your own info. Mention the User or use User ID. Does not work in DMs. | `%userinfo @Phxenix` | user, user-info, info |
| **%viewreminders** | | ✗ | ✗ | Lists out your active reminders. If you have too many it will only display the first 6. | `%viewreminders` | reminders, myreminders, viewreminder, listreminders | 
| **%warn** | `<@user> <reason>` | ✓ | ✗ | Use this to warn a user. The reason will get DM'd to the person warned, if the bot can DM the user. Mention the User or use User ID. Warning expire after 30 days. If a user reaches 3 warnings within 30 days the user will get muted, 5 within 30 days equal a kick and 7 within 30 days will get the user banned. | `%warn @Phxenix what an idiot` | 
| **%warndetails** | `<@user>` | ✓ | ✗ | This will give detailed information about a users active warnings. Mention a User or use User ID. | `%warndetails @Phxenix` |
| **%warns** | `<@user: Optional>` | ✗ | ✗ | This will return the number of active warnings a user has. If you haven't specified a User, this will get your own warning count. Mention the User or use User ID. | `%warns @Phxenix` | warnings, infractions |
| **%who** | `<question>` | ✗ | ✗ | Ask a question and you get a random user that is currently online as a response. Does not work in DMs. | `%who is the most beautiful user?` |
| **%wisdom** | | ✗ | ✗ | Gets you a random piece of wisdom. | `%wisdom` |
  
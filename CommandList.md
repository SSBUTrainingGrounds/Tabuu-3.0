# Full list of commands:

This here contains every command with a detailed explanation on how to use them. They are ordered alphabetically, search them with Ctrl+F.  
Last updated: 27 July 2021  
I will try to keep this up-to-date, no promises.  

**%8ball** `<question>`  
    Info: Ask a question and you get a random response from the magic 8-ball.  
    Example: `%8ball Is Tabuu 3.0 the best bot out there?`  

**%addrole** `<@user> <role>`  
    Info: Admin only. Adds a Role to a User. Mention the User or use User ID, for the Role the bot just takes the closest match.  
    Example: `%addrole @Phxenix first class` 
    
**%ban** `<@user> <reason>`  
    Info: Admin only. Bans a User. Mention the User or use User ID. The reason will get logged in Audit logs and also DM'd to the user.  
    Example: `%ban @Phxenix what an idiot`  
    
**%boo**    
    Info: Comes up with some scary stuff.  
    
**%calendar**  
    Info: Gives you the link to our event calendar.  
    Aliases: calender, calandar, caIendar  
    
**%clear** `<amount>`  
    Info: Admin only. Deletes the last X messages in the current channel. Defaults to 1.  
    Example: `%clear 10`  
    
**%clearmmpings**  
    Info: Admin only. Clears all matchmaking pings.  
    Aliases: clearmmrequests, clearmm, clearmatchmaking  
    
**%clearwarns** `<@user>`  
    Info: Admin only. Clears all warnings of a User. Mention the User or use User ID.  
    Example: `%clearwarns @Phxenix`  
    
**%coaching**  
    Info: Gives you all the Information you need for getting coaching in our server.  
    
**%coin**  
    Info: Flips a coin and gives you the result. Heads or Tails.  
    
**%countdown** `<number>`  
    Info: Counts down from the specified number between 2 and 50.  
    Example: `%countdown 5`  
    
**%delete** `<message IDs>`  
    Info: Admin only. Deletes Messages by their IDs. The messages need to be in the same channel of the command. Takes as many messages as you like.  
    Example: `%delete 858117781375418389 858117780859256882`  
    
**%deleterolemenu** `<message ID>`  
    Info: Admin only. Deletes a Role menu completely.  
    Example: `%deleterolemenu 858117781375418389`  
    
**%deletewarn** `<@user> <warn_id>`  
    Info: Admin only. Deletes a warning by the warning ID. Mention the User or use User ID.  
    Example: `%deletewarn @Phxenix 123456`  
    
**%doubles**  
    Info: Pings the doubles role and stores your ping for 30 Minutes. Has a 10 minute cooldown and can only be used in our arena channels.  
    Aliases: matchmakingdoubles, mmdoubles, Doubles  
    
**%emote** `<emoji>`  
    Info: Gives you Information about an Emoji. Keep in mind this does not work with default emojis and bots can only access emojis from servers they are in.  
    Example: `%emote :BowserFail:`  
    Aliases: emoji  
    
**%forcereportmatch** `<@winner> <@loser>`  
    Info: Admin only. If a user abandons their ranked match an admin will use this to report the match anyways. Mention the users or use User IDs. Has a 41 second cooldown.
    Example: `%forcereportmatch @Tabuu 3.0 @Phxenix`  
    Aliases: forcereportgame  
    
**%funnies**  
    Info: Pings the funnies role and stores your ping for 30 Minutes. Has a 10 minute cooldown and can only be used in our arena channels.  
    Aliases: matchmakingfunnies, mmfunnies, Funnies  
    
**%geteveryrolemenu**  
    Info: Admin only. Gets you every role menu entry currently saved.  
    
**%help** `<subcommand>`  
    Info: The help command is broken into subcommands cause there were too many commands to list. Available subcommands are: admin, info, mm, util, misc, fun. The admin help command is admin only.  
    Example: `%help info`  
    
**%icon** `<@user: Optional>`  
    Info: Gets you the avatar of a User. User argument is optional, if there is none, this gets your own avatar. Otherwise mention the User or use User ID.  
    Example: `%icon @Phxenix`  
    
**%invite**  
    Info: Gets you our vanity URL invite link.  
    
**%john**  
    Info: Returns a random excuse why you lost that last game of Smash.  
    
**%joke**  
    Info: Returns a random joke, funniness may vary.  
    Aliases: tabuujoke  
    
**%kick** `<@user> <reason>`  
    Info: Admin only. Kicks a user from the server. Mention the User or use User ID. The reason will get logged in Audit logs and also DM'd to the user.  
    Example: `%kick @Phxenix what an idiot`  
    
**%leaderboard**  
    Info: Admin only. Gets you the Top 10 rated players of our ranked matchmaking system.  
    
**%listrole** `<role>`  
    Info: Lists out every User with a certain role. The bot searches for the closest match for the role name.  
    Example: `%listrole first class`  
    Aliases: listroles  
    
**%modifyrolemenu** `<message ID> <exclusive: Optional> <Role: Optional>`  
    Info: Admin only. Modifies a role menu with special properties. Exclusive is a boolean(True/False) value which specifies if a User is able to get 1 role (True) or all roles (False) from this role menu. The role sets a requirement if a User needs this role to get any role of this role menu. Mention the role or use role ID. Both arguments are optional, if left out both default to False/None.  
    Example: `%modifyrolemenu 858117781375418389 True @Singles Winner`  
    
**%modmail** `<your message>`  
    Info: Privately contact the moderator team of this server. Use this for reporting rule violations or feedback/suggestions for the Mod Team. You can attach any attachments to the message. Only works in the DM channel of Tabuu 3.0. Your username will be visible to prevent abuse.  
    Example: `%modmail Hello, I think the moderator team has been doing an awful job lately.`  
    
**%mp4`<move>`**  
    Info: Gives you the mana cost of any of Hero's moves.  
    `Example: %mp4woosh`  
  
**%mute** `<@user> <reason>`  
    Info: Admin only. Mutes a user in the server. The reason will get DM'd to the user.  
    Example: `%mute @Phxenix what an idiot`  
  
**%newrolemenu** `<message ID> <emoji> <role>`  
    Info: Admin only. Creates a new entry for a role menu. Mention the Role or use Role ID and make sure the Bot has access to this emoji.  
    Example: `%newrolemenu 858117781375418389 🥰 @Server Events`  
  
**%pickmeup**  
    Info: Gives you an inspiring quote.  
  
**%ping**  
    Info: Gets the response time of the Bot, not yourself. Usually around 100-150ms.  
  
**%poll** `<"question"> <"option 1"> <"option 2">`  
    Info: Creates a poll for users to vote on with reactions. Takes 2-10 Options. If the question or the options have more than 1 word in them, make sure to surround them with quotes.  
    Example: `%poll "What is your favourite Ice cream?" Chocolate Strawberry "None of the above"`  
  
**%randomquote**  
    Info: Gets you a random quote from someone.  
  
**%rankedmm**  
    Info: Pings your ranked role according to you Elo value and stores your ping for 30 Minutes. Has a 2 minute cooldown and can only be used in our ranked arena channels.
    Aliases: ranked, rankedmatchmaking, rankedsingles  
  
**%rankedstats** `<@user: Optional>`  
    Info: Gets you the ranked stats of any optional user. If you dont specify a user, this will get your own stats where you can also choose to remove or add your Elo role.
    Example: `%rankedstats @Phxenix`  
    Aliases: rankstats  
  
**%recentpings** `<type>`  
    Info: Gets you all pings in the last 30 Minutes of any matchmaking type without pinging the role yourself. These are: singles, doubles, funnies, ranked.
    Example: `%recentpings ranked`  
  
**%records**  
    Info: Admin only. Gets you our ban records.  
  
**%reminder** `<time> <message>`  
    Info: Reminds you about something. Please keep in mind that this command is fairly simple and thus if the bot gets restarted your reminder will get lost. Time is in a shortened format with any number and d/h/m/s. Minimum duration is 30 seconds, maximum is 30 days.  
    Example: `%reminder 10h get that thing done you wanted to get done`  
    Aliases: remindme  
  
**%removerole** `<@user> <role>`  
    Info: Admin only. Removes a role from a User. Mention the User or use User ID, for the Role the bot just takes the closest match.  
    Example: `%removerole @Phxenix first class`  
  
**%reportmatch** `<@user>`  
    Info: The winner uses this command after a ranked match to report the result of the match, @user being the person who lost the ranked match. Mention the User or use User ID. Has a 41 second cooldown.
    Example: `%reportmatch @Phxenix`  
    Aliases: reportgame  
  
**%roleinfo** `<role>`  
    Info: Gets you information about a role. The bot searches for the closest match for the role name.  
    Example: `%roleinfo first class`  
  
**%roll** `<NdN>`  
    Info: Rolls a dice. N are two numbers, first the number of dice then the amount of sides for the dice.  
    Example: `%roll 2d6`  
    Aliases: r  
  
**%server**  
    Info: Gets you information about our server.  
    Aliases: serverinfo  
  
**%singles**  
    Info: Pings the singles role and stores your ping for 30 Minutes. Has a 10 minute cooldown and can only be used in our arena channels.  
    Aliases: matchmaking, matchmakingsingles, mmsingles, Singles  
  
**%spotify** `<@user: Optional>`  
    Info: Posts the song you are currently listening to on Spotify. You need to enable the setting that displays your Spotify Session as your Discord Status for this to work. User is optional, if not set this will return your own. Mention the User or use User ID.  
    Example: `%spotify @Phxenix`  
  
**%stagelist**  
    Info: Posts our version of the legal stages.  
  
**%stats**  
    Info: Gets you various stats about this bot.  
    Aliases: botstats  
  
**%`<streamer>`**  
    Info: This will link the streamers Twitch Stream. %streamer will get you the list of our available streamer commands.  
    Example: `%tgstream`  
  
**%tabuwu**  
    Info: For the silly people.  
  
**%tempmute** `<@user> <time> <reason>`  
    Info: Admin only. Mutes a user for the specified time, which is in a shortened format with any number and d/h/m/s. Minimum time is 30 seconds, maximum is 1 day. Mention the user or use User ID. The reason will get DM'd to the muted person.  
    Example: `%tempmute @Phxenix 12h what an idiot`  
  
**%unban** `<@user>`  
    Info: Admin only. Unbans a user. Mention the User or use User ID.  
    Example: `%unban @Phxenix`  
  
**%unmute** `<@user>`  
    Info: Admin only. Unmutes a user. Please use this in all cases to unmute someone. Mention the User or use User ID.  
    Example: `%unmute @Phxenix`  
  
**%updatelevel**  
    Info: Updates your level role according to your MEE6 level manually. Has a 10 minute cooldown. Note that this gets done anyways every 23 hours for everyone in the server.  
  
**%userinfo** `<@user: Optional>`  
    Info: Gets you various information about a user. If you haven't specified a user, this will get your own info. Mention the User or use User ID.  
    Example: `%userinfo @Phxenix`  
    Aliases: user  
  
**%uwu**  
    Info: For the silly people.  
  
**%warn** `<@user> <reason>`  
    Info: Admin only. Use this to warn a user. The reason will get DM'd to the person warned. Mention the User or use User ID. Warning expire after 30 days. If a user reaches 3 warnings within 30 days the user will get muted, 5 within 30 days equal a kick and 7 within 30 days will get the user banned.  
    Example: `%warn @Phxenix what an idiot`  
  
**%warndetails** `<@user>`  
    Info: Admin only. This will give detailed information about a users active warnings. Mention a User or use User ID.  
    Example: `%warndetails @Phxenix`  
  
**%warns** `<@user: Optional>`  
    Info: This will return the number of active warnings a user has. If you haven't specified a User, this will get your own warning count. Mention the User or use User ID.  
    Example: `%warns @Phxenix`  
    Aliases: warnings, infractions  
    
**%who** `<question>`  
    Info: Ask a question and you get a random user that is currently online as a response.  
    Example: `%who is the most beautiful user?`  
  
**%wisdom**  
    Info: Gets you a random piece of wisdom.  

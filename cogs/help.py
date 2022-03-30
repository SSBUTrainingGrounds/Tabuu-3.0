import discord
from discord.ext import commands


class Responses(discord.ui.Select):
    """
    Contains the Dropdown Menu for our custom help command.
    Every command is explained in here.
    """

    def __init__(self):
        options = [
            # black is being inconsistent here again, so..
            # fmt: off
            discord.SelectOption(
                label="Moderation Commands",
                description="Admin only, no fun allowed.",
                emoji="🕵️",
            ),
            discord.SelectOption(
                label="Admin Utility Commands",
                description="Admin only commands for server setup and more.",
                emoji="🧰",
            ),
            discord.SelectOption(
                label="Info Commands",
                description="What do you want to look up?",
                emoji="❓",
            ),
            discord.SelectOption(
                label="Matchmaking Commands",
                description="Looking for matches?",
                emoji="⚔️",
            ),
            discord.SelectOption(
                label="Profile Commands",
                description="How to set up your smash profile.",
                emoji="👥",
            ),
            discord.SelectOption(
                label="Utility Commands",
                description="At your service.",
                emoji="🔧",
            ),
            discord.SelectOption(
                label="Game Commands",
                description="Challenge your foes.",
                emoji="🎮",
            ),
            discord.SelectOption(
                label="Miscellaneous Commands",
                description="Everything that did not fit into the other categories.",
                emoji="📋",
            ),
            discord.SelectOption(
                label="Fun Commands",
                description="Note: Fun not guaranteed.",
                emoji="😂",
            ),
        ]
        # fmt: on

        super().__init__(
            placeholder="What do you need help with?",
            min_values=1,
            max_values=1,
            options=options,
        )

    # the various embed descriptions
    moderation_desc = """
```%ban <@user> <reason>``` - Bans a member from the server.
```%unban <@user>``` - Revokes a ban from the server.
```%kick <@user> <reason>``` - Kicks a user from the server.
```%clear <amount>``` - Purges X messages from the channel (default:1).
```%delete <message IDs>``` - Deletes certain messages by ID.
```%mute <@user> <reason>``` - Mutes a user in the server.
```%unmute <@user>``` - Unmutes a user in the server.
```%tempmute <@user> <time> <reason>``` - Temporarily mutes a user.
```%timeout <@user> <time> <reason>``` - Times out a user until the time specified.
```%removetimeout <@user>``` - Removes a timeout from a user.
```%addrole <@user> <role>``` - Adds a role to a user.
```%removerole <@user> <role>``` - Removes a role from a user.
```%warn <@user> <reason>``` - Warns a user.
```%warndetails <@user>``` - Shows detailed warnings of a user.
```%deletewarn <@user> <warn_id>``` - Deletes a specific warning.
```%clearwarns <@user>``` - Clears all the warnings of a user.
    """

    admin_util_desc = """
```%reloadcogs <cogs>``` - Owner only, reloads some or all of the modules of this bot.
```%synccommands <guild>``` - Owner only, syncs application commands to one or all guilds.
```%clearmmpings``` - Clears all matchmaking pings.
```%records``` - Shows ban records.
```%forcereportmatch <@winner> <@loser>``` - If someone abandons a ranked match.
```%leaderboard``` - Leaderboards of ranked matchmaking.
```%newrolemenu <message ID> <emoji> <role>``` - Adds an entry for a role menu.
```%deleterolemenu <message ID>``` - Deletes every entry for a Message with a role menu.
```%modifyrolemenu <message ID> <exclusive> <Optional Role(s)>``` - Sets special permissions for a Role menu.
```%geteveryrolemenu``` - Gets you every role menu entry currently active.
```%rename <@user> <name>``` - Sets a new nickname for a user or removes it.
```%say <channel> <message>``` - Admin only, Repeats the message in the chnanel.
```%createmacro <name> <output>``` - Creates a new macro.
```%deletemacro <name>``` - Deletes a macro.
```%starboardemoji <emoji>``` - Changes the emoji used for the starboard.
```%starboardthreshold <number>``` - Changes the threshold used for the starboard.
```%forcedeleteprofile <@user>``` - Deletes the profile of a user.
```%addbadges <@user> <emojis>``` - Adds badges to a user.
```%removebadge <@user> <emoji>``` - Removes one badge from a user.
```%clearbadge <@user>``` - Clears every badge from a user.
```%syncbanlist``` - Syncs the ban list from main server to secondary server.
```%setupmodmailbutton``` - Sets up a new modmail button for the bot to listen to.
    """

    info_desc = """
```%help <command>``` - Help menu, or specific help with a command.
```%listmacros``` - Lists every macro command registered.
```%roleinfo <role>``` - Displays Role info.
```%listrole <role>``` - Displays all the members with a certain Role.
```%userinfo <member>``` - Shows user info of a mentioned member.
```%warns <@user>``` - Displays the number of warnings of a user.
```%server``` - Info about the server.
```%stats``` - Stats about the bot.
```%emote <emoji>``` - Info about an emoji.
```%sticker <sticker>``` - Info about a sticker.
    """

    mm_desc = """
```%singles``` - Used for 1v1 matchmaking in our arena channels.
```%doubles``` - Used for 2v2 matchmaking in our arena channels.
```%funnies <message>``` - Used for non-competitive matchmaking in our arena channels.
```%ranked``` - Used for 1v1 ranked matchmaking in our ranked channels.
```%reportmatch <@user>``` - Winner of the set reports the result, <@user> being the person you won against.
```%rankedstats``` - Your ranked stats.
```%recentpings``` - Gets you the recent pings of any matchmaking type.
    """

    profile_desc = """
```%profile <@user>``` - View a profile of a user.
```%mains <main1, main2,...>``` - Set your mains, separated by commas.
```%secondaries <sec1, sec2,...>``` - Set your secondaries, separated by commas.
```%pockets <pocket1, pocket2,...>``` - Set your pockets, separated by commas.
```%tag <tag>``` - Set your user tag.
```%region <region>``` - Set your region (continent).
```%note <note>``` - Set your note.
```%colour <hex colour>``` - Set your profile embed colour, use a hex code.
```%deleteprofile``` - Delete your profile.
    """

    util_desc = """
```%coin``` - Throws a coin.
```%roll <NdN>``` - Rolling dice, format %roll 1d100.
```%countdown <number>``` - Counts down from number.
```%time``` - Current time as a timezone aware object.
```%convert <input>``` - Converts the input from metric to imperial and vice versa.
```%poll <"question"> <"option 1"> <"option 2">``` - Starts a poll with a maximum of 10 choices.
```%reminder <time> <message>``` - Reminds you about something.
```%viewreminders``` - Lists your active reminders.
```%deletereminder <ID>```Deletes one of your reminders by its ID.
    """

    game_desc = """
```%rps <@user>``` - Plays a match of Rock, Paper, Scissors with the mentioned user.
```%tictactoe <@user>``` - Plays a match of Tic Tac Toe with the mentioned user.
```%blackjack <@user>``` - Plays a match of Blackjack with the mentioned user.
    """

    misc_desc = """
```%modmail <your message>``` - Message the Mod Team privately. Only works in my DM channel.
```%updatelevel <@user>``` - Updates the level role manually.
```%stagelist``` - Our Stagelist for Crew Battles.
```%avatar <@user>``` - Gets you the avatar of a user.
```%banner <@user>``` - Gets you the banner of a user.
```%spotify <@user>``` - Posts the song the user is currently streaming.
```%ping``` - Gets the ping of the bot.
```%mp4<move>``` - Tells you the Mana Cost of any of Hero's moves.
    """

    fun_desc = """
```%joke``` - Jokes.
```%randomquote``` - Quotes.
```%pickmeup``` - Nice words.
```%wisdom``` - It's wisdom.
```%boo``` - Looking for a scare, huh?
```%tabuwu``` - For the silly people.
```%john``` - If you need a john.
```%hypemeup``` - Hypes you up before that next game of smash.
```%8ball <question>``` - Ask the magic 8-ball.
```%who <question>``` - Ask a question and get a random user in response.
    """

    async def callback(self, interaction: discord.Interaction):
        if self.values[0] == "Moderation Commands":
            mod_embed = discord.Embed(
                title="🕵️Moderation Commands🕵️",
                color=0xFF0000,
                description=self.moderation_desc,
            )
            await interaction.response.send_message(embed=mod_embed, ephemeral=True)

        elif self.values[0] == "Admin Utility Commands":
            admin_util_embed = discord.Embed(
                title="🧰Admin Utility Commands🧰",
                colour=0x540707,
                description=self.admin_util_desc,
            )
            await interaction.response.send_message(
                embed=admin_util_embed, ephemeral=True
            )

        elif self.values[0] == "Info Commands":
            info_embed = discord.Embed(
                title="❓Info Commands❓", color=0x06515F, description=self.info_desc
            )
            await interaction.response.send_message(embed=info_embed, ephemeral=True)

        elif self.values[0] == "Matchmaking Commands":
            matchmaking_embed = discord.Embed(
                title="⚔️Matchmaking Commands⚔️",
                color=0x420202,
                description=self.mm_desc,
            )
            await interaction.response.send_message(
                embed=matchmaking_embed, ephemeral=True
            )

        elif self.values[0] == "Profile Commands":
            profile_embed = discord.Embed(
                title="👥Profile Commands👥", color=0x7C3ED, description=self.profile_desc
            )
            await interaction.response.send_message(embed=profile_embed, ephemeral=True)

        elif self.values[0] == "Utility Commands":
            utility_embed = discord.Embed(
                title="🔧Utility Commands🔧", color=0x424242, description=self.util_desc
            )
            await interaction.response.send_message(embed=utility_embed, ephemeral=True)

        elif self.values[0] == "Game Commands":
            game_embed = discord.Embed(
                title="🎮Game Commands🎮", colour=0x333333, description=self.game_desc
            )
            await interaction.response.send_message(embed=game_embed, ephemeral=True)

        elif self.values[0] == "Miscellaneous Commands":
            miscellaneous_embed = discord.Embed(
                title="📋Miscellaneous Commands📋",
                color=0x155A00,
                description=self.misc_desc,
            )
            await interaction.response.send_message(
                embed=miscellaneous_embed, ephemeral=True
            )

        elif self.values[0] == "Fun Commands":
            fun_embed = discord.Embed(
                title="😂Fun Commands😂", color=0x841E8B, description=self.fun_desc
            )
            await interaction.response.send_message(embed=fun_embed, ephemeral=True)

        else:
            await interaction.response.send_message(
                "Something went wrong! Please try again.", ephemeral=True
            )


class DropdownHelp(discord.ui.View):
    """
    Adds the Items to the Dropdown.
    """

    def __init__(self):
        super().__init__()

        self.add_item(Responses())


class CustomHelp(commands.HelpCommand):
    async def send_bot_help(self, mapping):
        """
        Sends you the dropdown with every command and explanation on how to use it.
        The user can choose which dropdown they wanna see,
        it is intentionally grouped different than in our cogs.
        It looks a lot nicer this way, in my opinion, than the default option.
        We just have to remember to add new commands to the embeds up above.
        """
        channel = self.get_destination()
        await channel.send("Here are the available subcommands:", view=DropdownHelp())

    async def send_cog_help(self, cog):
        """
        We dont really want to send out anything here,
        since we grouped the commands above a lot differently than the cogs would.
        So instead we just send out the command not found error,
        if the user happens to specify a cog as an argument.
        Otherwise the bot would not respond at all, which is obviously suboptimal.
        We would need to do the same thing for command groups, but we dont have any.
        """
        await self.send_error_message(self.command_not_found(cog.qualified_name))

    async def send_command_help(self, command):
        """
        Sends you specific help information about a command.
        """
        embed = discord.Embed(
            title=self.get_command_signature(command), colour=0x007377
        )
        # the command.help is just the docstring inside every command.
        embed.add_field(name="Help:", value=command.help, inline=False)
        embed.set_thumbnail(url=self.context.bot.user.display_avatar.url)
        if command.aliases:
            embed.add_field(
                name="Names:",
                value=f"{command.name}, {', '.join(command.aliases)}",
                inline=False,
            )
        else:
            embed.add_field(name="Names", value=command.name, inline=False)

        # this checks if the command could be used right now.
        # it throws the error directly if the command cant be used and tells you why.
        try:
            await command.can_run(self.context)
            embed.add_field(name="Usable by you:", value="Yes", inline=False)
        except commands.CommandError as exc:
            embed.add_field(name="Usable by you:", value=f"No:\n{exc}", inline=False)

        channel = self.get_destination()
        await channel.send(embed=embed)


class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        help_command = CustomHelp()
        help_command.cog = self
        bot.help_command = help_command


async def setup(bot):
    await bot.add_cog(Help(bot))
    print("Help cog loaded")

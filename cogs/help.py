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
```%addrole <@user> <role>``` - Adds a role to a user.
```%removerole <@user> <role>``` - Removes a role from a user.
```%warn <@user> <reason>``` - Warns a user.
```%warndetails <@user>``` - Shows detailed warnings of a user.
```%deletewarn <@user> <warn_id>``` - Deletes a specific warning.
```%clearwarns <@user>``` - Clears all the warnings of a user.
    """

    admin_util_desc = """
```%reloadcogs <cogs>``` - Owner only, reloads some or all of the modules of this bot.
```%clearmmpings``` - Clears all matchmaking pings.
```%records``` - Shows ban records.
```%forcereportmatch <@winner> <@loser>``` - If someone abandons a ranked match.
```%leaderboard``` - Leaderboards of ranked matchmaking.
```%newrolemenu <message ID> <emoji> <role>``` - Adds an entry for a role menu.
```%deleterolemenu <message ID>``` - Deletes every entry for a Message with a role menu.
```%modifyrolemenu <message ID> <exclusive> <Optional Role(s)>``` - Sets special permissions for a Role menu.
```%geteveryrolemenu``` - Gets you every role menu entry currently active.
```%rename <@user> <name>``` - Sets a new nickname for a user or removes it.
```%createmacro <name> <output>``` - Creates a new macro.
```%deletemacro <name>``` - Deletes a macro.
```%starboardemoji <emoji>``` - Changes the emoji used for the starboard.
```%starboardthreshold <number>``` - Changes the threshold used for the starboard.
```%forcedeleteprofile <user>``` - Deletes the profile of a user.
```%syncbanlist``` - Syncs the ban list from main server to secondary server.
    """

    info_desc = """
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
```%profile <user>``` - View a profile of a user.
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
```%rps <@user>``` - Plays a match of Rock, Paper, Scissors with the mentioned user.
```%roll <NdN>``` - Rolling dice, format %roll 1d100.
```%countdown <number>``` - Counts down from number.
```%time``` - Current time as a timezone aware object.
```%convert <input>``` - Converts the input from metric to imperial and vice versa.
```%poll <"question"> <"option 1"> <"option 2">``` - Starts a poll with a maximum of 10 choices.
```%reminder <time> <message>``` - Reminds you about something.
```%viewreminders``` - Lists your active reminders.
```%deletereminder <ID>```Deletes one of your reminders by its ID.
    """

    misc_desc = """
```%modmail <your message>``` - A private way to communicate with the moderator team. Only works in my DM channel.
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
            if interaction.permissions.administrator is True:
                mod_embed = discord.Embed(
                    title="🕵️Moderation Commands🕵️",
                    color=0xFF0000,
                    description=self.moderation_desc,
                )
                await interaction.response.send_message(embed=mod_embed, ephemeral=True)
            else:
                await interaction.response.send_message(
                    "Sorry, you are not an administrator on this server!",
                    ephemeral=True,
                )

        elif self.values[0] == "Admin Utility Commands":
            if interaction.permissions.administrator is True:
                admin_util_embed = discord.Embed(
                    title="🧰Admin Utility Commands🧰",
                    colour=0x540707,
                    description=self.admin_util_desc,
                )

                await interaction.response.send_message(
                    embed=admin_util_embed, ephemeral=True
                )
            else:
                await interaction.response.send_message(
                    "Sorry, you are not an administrator on this server!",
                    ephemeral=True,
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


class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def help(self, ctx):
        """
        Sends you the dropdown with every command and explanation on how to use it.
        """
        await ctx.send("Here are the available subcommands:", view=DropdownHelp())


def setup(bot):
    bot.add_cog(Help(bot))
    print("Help cog loaded")

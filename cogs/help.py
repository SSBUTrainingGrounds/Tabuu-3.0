from typing import Mapping, Optional, Union

import discord
from discord import app_commands
from discord.ext import commands

import utils.search
from utils.ids import GuildIDs


class Responses(discord.ui.Select):
    """Contains the Dropdown Menu for our custom help command.
    Every command is explained in here.
    """

    def __init__(self, prefix: str) -> None:
        # We dont have access to the bot prefix here,
        # So we have to pass it in manually.
        self.prefix = prefix

        options = [
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

    async def callback(self, interaction: discord.Interaction) -> None:
        if self.values[0] == "Moderation Commands":
            embed = discord.Embed(
                title="🕵️Moderation Commands🕵️",
                color=0xFF0000,
                description=f"""
```{self.prefix}ban <@user> <reason>``` - Bans a member from the server.
```{self.prefix}unban <@user>``` - Revokes a ban from the server.
```{self.prefix}kick <@user> <reason>``` - Kicks a user from the server.
```{self.prefix}clear <amount>``` - Purges X messages from the channel.
```{self.prefix}mute <@user> <reason>``` - Mutes a user in the server.
```{self.prefix}unmute <@user>``` - Unmutes a user in the server.
```{self.prefix}tempmute <@user> <time> <reason>``` - Temporarily mutes a user.
```{self.prefix}timeout <@user> <time> <reason>``` - Times out a user until the time specified.
```{self.prefix}removetimeout <@user>``` - Removes a timeout from a user.
```{self.prefix}addrole <@user> <role>``` - Adds a role to a user.
```{self.prefix}removerole <@user> <role>``` - Removes a role from a user.
```{self.prefix}warn <@user> <reason>``` - Warns a user.
```{self.prefix}warndetails <@user>``` - Shows detailed warnings of a user.
```{self.prefix}deletewarn <@user> <warn_id>``` - Deletes a specific warning.
```{self.prefix}clearwarns <@user>``` - Clears all the warnings of a user.
```{self.prefix}modnote set <@user> <note>``` - Sets a new note for moderators to view.
```{self.prefix}modnote view <@user>``` - Views all modnotes for a user.
```{self.prefix}modnote delete <@user> <note_id>``` - Deletes a modnote from a user.
```{self.prefix}lookup <@user>``` - Looks up every little detail of a user.
    """,
            )

        elif self.values[0] == "Admin Utility Commands":
            embed = discord.Embed(
                title="🧰Admin Utility Commands🧰",
                colour=0x540707,
                description=f"""
```{self.prefix}reloadcogs <cogs>``` - Owner only, reloads some or all of the modules of this bot.
```{self.prefix}synccommands <guild>``` - Owner only, syncs application commands to one or all guilds.
```{self.prefix}editrole <property> <role> <value>``` - Edits a role's properties to the given value.
```{self.prefix}clearmmpings``` - Clears all matchmaking pings.
```{self.prefix}records``` - Shows ban records.
```{self.prefix}forcereportmatch <@winner> <@loser>``` - If someone abandons a ranked match.
```{self.prefix}leaderboard``` - Leaderboards of ranked matchmaking.
```{self.prefix}rolemenu new <message ID> <emoji> <role>``` - Adds an entry for a role menu.
```{self.prefix}rolemenu delete <message ID>``` - Deletes every entry for a Message with a role menu.
```{self.prefix}rolemenu modify <message ID> <exclusive> <role(s)>``` - Sets special permissions for a Role menu.
```{self.prefix}rolemenu get``` - Gets you every role menu entry currently active.
```{self.prefix}rename <@user> <name>``` - Sets a new nickname for a user or removes it.
```{self.prefix}names <@user>``` - Gets the current and past names of a user.
```{self.prefix}say <channel> <message>``` - Admin only, Repeats the message in the chnanel.
```{self.prefix}createmacro``` - Creates a new macro.
```{self.prefix}deletemacro <name>``` - Deletes a macro.
```{self.prefix}starboard emoji <emoji>``` - Changes the emoji used for the starboard.
```{self.prefix}starboard threshold <number>``` - Changes the threshold used for the starboard.
```{self.prefix}forcedeleteprofile <@user>``` - Deletes the profile of a user.
```{self.prefix}badge add <@user> <emojis>``` - Adds badges to a user.
```{self.prefix}badge remove <@user> <emoji>``` - Removes one badge from a user.
```{self.prefix}badge clear <@user>``` - Clears every badge from a user.
```{self.prefix}badge setinfo <emoji> <message>``` - Adds new information about a badge.
```{self.prefix}syncbanlist``` - Syncs the ban list from main server to secondary server.
```{self.prefix}setupmodmailbutton``` - Sets up a new modmail button for the bot to listen to.
    """,
            )

        elif self.values[0] == "Info Commands":
            embed = discord.Embed(
                title="❓Info Commands❓",
                color=0x06515F,
                description=f"""
```{self.prefix}help <command>``` - Help menu, or specific help with a command.
```{self.prefix}macro <macro>``` - Info about one macro, or lists every macro registered.
```{self.prefix}roleinfo <role>``` - Displays Role info.
```{self.prefix}listrole <role>``` - Displays all the members with a certain Role.
```{self.prefix}userinfo <member>``` - Shows user info of a mentioned member.
```{self.prefix}badgeinfo <emoji>``` - Shows information about a badge.
```{self.prefix}warns <@user>``` - Displays the number of warnings of a user.
```{self.prefix}server``` - Info about the server.
```{self.prefix}stats``` - Stats about the bot.
```{self.prefix}emoji <emoji>``` - Info about an emoji.
```{self.prefix}sticker <sticker>``` - Info about a sticker.
    """,
            )

        elif self.values[0] == "Matchmaking Commands":
            embed = discord.Embed(
                title="⚔️Matchmaking Commands⚔️",
                color=0x420202,
                description=f"""
```{self.prefix}singles``` - Used for 1v1 matchmaking in our arena channels.
```{self.prefix}doubles``` - Used for 2v2 matchmaking in our arena channels.
```{self.prefix}funnies <message>``` - Used for non-competitive matchmaking in our arena channels.
```{self.prefix}ranked``` - Used for 1v1 ranked matchmaking in our ranked channels.
```{self.prefix}reportmatch <@user>``` - Winner of the set reports the result, <@user> being the person you won against.
```{self.prefix}rankedstats``` - Your ranked stats.
```{self.prefix}recentpings``` - Gets you the recent pings of any matchmaking type.
    """,
            )

        elif self.values[0] == "Profile Commands":
            embed = discord.Embed(
                title="👥Profile Commands👥",
                color=0x7C3ED,
                description=f"""
```{self.prefix}profile <@user>``` - View a profile of a user.
```{self.prefix}players <character>``` - View all players of a character.
```{self.prefix}mains <main1, main2,...>``` - Set your mains, separated by commas.
```{self.prefix}secondaries <sec1, sec2,...>``` - Set your secondaries, separated by commas.
```{self.prefix}pockets <pocket1, pocket2,...>``` - Set your pockets, separated by commas.
```{self.prefix}tag <tag>``` - Set your user tag.
```{self.prefix}region <region>``` - Set your region (continent).
```{self.prefix}note <note>``` - Set your note.
```{self.prefix}colour <hex colour>``` - Set your profile embed colour, use a hex code.
```{self.prefix}deleteprofile``` - Delete your profile.
    """,
            )

        elif self.values[0] == "Utility Commands":
            embed = discord.Embed(
                title="🔧Utility Commands🔧",
                color=0x424242,
                description=f"""
```{self.prefix}coin``` - Throws a coin.
```{self.prefix}roll <NdN>``` - Rolling dice, format it like 1d100.
```{self.prefix}countdown <number>``` - Counts down from number.
```{self.prefix}time``` - Current time as a timezone aware object.
```{self.prefix}convert <input>``` - Converts the input from metric to imperial and vice versa.
```{self.prefix}translate <message>``` - Translates a message or string to english.
```{self.prefix}poll <question>``` - Starts a poll with your question.
```{self.prefix}reminder <time> <message>``` - Reminds you about something.
```{self.prefix}viewreminders``` - Lists your active reminders.
```{self.prefix}deletereminder <ID>```Deletes one of your reminders by its ID.
    """,
            )

        elif self.values[0] == "Game Commands":
            embed = discord.Embed(
                title="🎮Game Commands🎮",
                colour=0x333333,
                description=f"""
```{self.prefix}rps <@user>``` - Plays a match of Rock, Paper, Scissors with the mentioned user.
```{self.prefix}tictactoe <@user>``` - Plays a match of Tic Tac Toe with the mentioned user.
```{self.prefix}blackjack <@user>``` - Plays a match of Blackjack with the mentioned user.
```{self.prefix}memory <@user>``` - Plays a match of Memory with the mentioned user.
```{self.prefix}2048``` - Plays a game of 2048.
```{self.prefix}minesweeper <mine_count>``` - Plays a game of Minesweeper with 2-12 Mines (Default: 5).
    """,
            )

        elif self.values[0] == "Miscellaneous Commands":
            embed = discord.Embed(
                title="📋Miscellaneous Commands📋",
                color=0x155A00,
                description=f"""
```{self.prefix}modmail <your message>``` - Message the Mod Team privately. Only works in my DM channel.
```{self.prefix}updatelevel <@user>``` - Updates the level role manually.
```{self.prefix}stagelist``` - Our Stagelist for Crew Battles.
```{self.prefix}avatar <@user>``` - Gets you the avatar of a user.
```{self.prefix}banner <@user>``` - Gets you the banner of a user.
```{self.prefix}spotify <@user>``` - Posts the song the user is currently streaming.
```{self.prefix}ping``` - Gets the ping of the bot.
```{self.prefix}mp4 <move>``` - Tells you the Mana Cost of any of Hero's moves.
    """,
            )

        elif self.values[0] == "Fun Commands":
            embed = discord.Embed(
                title="😂Fun Commands😂",
                color=0x841E8B,
                description=f"""
```{self.prefix}joke``` - Jokes.
```{self.prefix}randomquote``` - Quotes.
```{self.prefix}pickmeup``` - Nice words.
```{self.prefix}wisdom``` - It's wisdom.
```{self.prefix}boo``` - Looking for a scare, huh?
```{self.prefix}tabuwu``` - For the silly people.
```{self.prefix}john``` - If you need a john.
```{self.prefix}hypemeup``` - Hypes you up before that next game of smash.
```{self.prefix}8ball <question>``` - Ask the magic 8-ball.
```{self.prefix}who <question>``` - Ask a question and get a random user in response.
```{self.prefix}friendship <@user1> <@user2>``` - The friendship status between 2 users.
    """,
            )

        else:
            embed = discord.Embed(
                title="❌Looks like something went wrong❌",
                colour=0x700416,
                description="Please try again.",
            )

        embed.add_field(
            name="\u200b",
            value=f"[Details: `{self.prefix}help <command>` or visit my GitHub.]"
            "(https://github.com/SSBUTrainingGrounds/Tabuu-3.0)",
            inline=False,
        )

        await interaction.response.send_message(embed=embed, ephemeral=True)


class DropdownHelp(discord.ui.View):
    """Adds the Items to the Dropdown."""

    def __init__(self, prefix: str) -> None:
        self.prefix = prefix
        super().__init__()

        self.add_item(Responses(self.prefix))


class CustomHelp(commands.HelpCommand):
    async def help_embed(
        self, command: Union[commands.Command, commands.Group]
    ) -> discord.Embed:
        """Creates a help embed with useful information.
        Luckily most things work for both commands and groups.
        """
        embed = discord.Embed(title=self.get_command_signature(command), color=0x007377)

        # The command.help is just the docstring inside every command.
        embed.add_field(name="Help:", value=command.help, inline=False)
        embed.set_thumbnail(url=self.context.bot.user.display_avatar.url)
        if command.aliases:
            embed.add_field(
                name="Names:",
                value=f"{command.name}, {', '.join(command.aliases)}",
                inline=False,
            )
        else:
            embed.add_field(name="Names:", value=command.name, inline=False)

        # This checks if the command could be used right now.
        # It throws the error directly if the command cant be used and tells you why.
        try:
            await command.can_run(self.context)
            embed.add_field(name="Usable by you:", value="Yes", inline=False)
        except commands.CommandError as exc:
            embed.add_field(name="Usable by you:", value=f"No:\n{exc}", inline=False)

        embed.add_field(
            name="\u200b",
            value=f"[Overview: `{self.context.prefix}help` or visit my GitHub.]"
            "(https://github.com/SSBUTrainingGrounds/Tabuu-3.0)",
            inline=False,
        )

        return embed

    async def send_bot_help(
        self, mapping: Mapping[Optional[commands.Cog], list[commands.Command]]
    ) -> None:
        """Sends you the dropdown with every command and explanation on how to use it.
        The user can choose which dropdown they wanna see,
        it is intentionally grouped different than in our cogs.
        It looks a lot nicer this way, in my opinion, than the default option.
        We just have to remember to add new commands to the embeds up above.
        """
        channel = self.get_destination()
        await channel.send(
            "Here are the available subcommands:",
            view=DropdownHelp(self.context.prefix),
        )

    async def send_cog_help(self, cog: commands.Cog) -> None:
        """We dont really want to send out anything here,
        since we grouped the commands above a lot differently than the cogs would.
        So instead we just send out the command not found error,
        if the user happens to specify a cog as an argument.
        Otherwise the bot would not respond at all, which is obviously suboptimal.
        """
        await self.send_error_message(self.command_not_found(cog.qualified_name))

    async def send_command_help(self, command: commands.Command) -> None:
        """Sends you specific help information about a command."""
        embed = await self.help_embed(command)

        channel = self.get_destination()
        await channel.send(embed=embed)

    async def send_group_help(self, group: commands.Group) -> None:
        """Sends you help information for grouped commands."""
        command_names = [command.name for command in group.commands]

        embed = await self.help_embed(group)

        embed.insert_field_at(
            index=1,
            name="Available Subcommands:",
            value=", ".join(command_names),
            inline=False,
        )

        channel = self.get_destination()
        await channel.send(embed=embed)


class Help(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

        help_command = CustomHelp()
        help_command.cog = self
        bot.help_command = help_command

    @app_commands.command(
        name="help",
        description="Lists every command available, or helps you with a specific command.",
    )
    @app_commands.guilds(*GuildIDs.ALL_GUILDS)
    @app_commands.describe(command="The optional command you need help with.")
    async def help(self, interaction: discord.Interaction, command: str = None) -> None:
        """The help command, but replicated as a slash command, mostly.
        We cannot use command.can_run here, since we cannot get the context from an interaction.
        The rest is replicated as close as possible.

        This will only get you the "normal" text based commands.
        This shouldn't be a problem since I will always make them a priority over slash commands.
        Slash commands will ideally only mimic the behaviour of the text based commands, as close as possible.
        """
        ctx: commands.Context = await self.bot.get_context(interaction)

        if not command:
            await interaction.response.send_message(
                "Here are the available subcommands:",
                view=DropdownHelp(ctx.prefix),
            )
            return

        cmd = self.bot.get_command(command)

        if not cmd:
            await interaction.response.send_message(
                "I could not find this command.\n"
                "Leave the command option empty to see all available commands.",
                ephemeral=True,
            )
            return

        # Replicates the get_command_signature of the HelpCommand class.
        command_full_name = cmd.name

        if cmd.aliases:
            aliases = "|".join(cmd.aliases)
            command_full_name = f"[{command_full_name}|{aliases}]"

        if cmd.parent:
            command_full_name = f"{cmd.full_parent_name} {command_full_name}"

        full_command = f"{ctx.prefix}{command_full_name} {cmd.signature}"

        # Unfortunately we need to construct our own embed,
        # since a lot of the stuff used is exclusive to the HelpCommand class
        embed = discord.Embed(title=full_command, color=0x007377)

        embed.add_field(name="Help:", value=cmd.help, inline=False)
        embed.set_thumbnail(url=self.bot.user.display_avatar.url)

        if isinstance(cmd, commands.Group):
            command_names = [command.name for command in cmd.commands]

            embed.add_field(
                name="Available Subcommands:",
                value=", ".join(command_names),
                inline=False,
            )

        if cmd.aliases:
            embed.add_field(
                name="Names:",
                value=f"{cmd.name}, {', '.join(cmd.aliases)}",
                inline=False,
            )
        else:
            embed.add_field(name="Names:", value=cmd.name, inline=False)

        try:
            await cmd.can_run(ctx)
            embed.add_field(name="Usable by you:", value="Yes", inline=False)
        except commands.CommandError as exc:
            embed.add_field(name="Usable by you:", value=f"No:\n{exc}", inline=False)

        embed.add_field(
            name="\u200b",
            value=f"[Overview: `{ctx.prefix}help` or visit my GitHub.]"
            "(https://github.com/SSBUTrainingGrounds/Tabuu-3.0)",
            inline=False,
        )

        await interaction.response.send_message(embed=embed)

    @help.autocomplete("command")
    async def command_autocomplete(
        self, interaction: discord.Interaction, current: str
    ) -> list[app_commands.Choice]:
        command_list = []
        for cmd in self.bot.commands:
            if isinstance(cmd, commands.Group):
                command_list.extend(f"{cmd.name} {c.name}" for c in cmd.commands)
            command_list.append(cmd.name)

        return utils.search.autocomplete_choices(current, command_list)


async def setup(bot) -> None:
    await bot.add_cog(Help(bot))
    print("Help cog loaded")

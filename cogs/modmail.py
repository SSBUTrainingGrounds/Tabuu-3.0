import discord
from discord import app_commands
from discord.ext import commands

import utils.check
import utils.embed
from utils.ids import GuildIDs, TGChannelIDs, TGRoleIDs
from views.confirm import ConfirmationButtons


class ModmailButton(discord.ui.View):
    """The persistent modmail button.
    We dont really need to save it in a database or something,
    since it is ideally only used one time and always does the same thing.
    """

    def __init__(self) -> None:
        super().__init__(timeout=None)

    @discord.ui.button(
        label="Contact the moderator team",
        style=discord.ButtonStyle.success,
        custom_id="tabuu3:persistent_modmail_button",
        emoji="✉️",
    )
    async def modmail_button(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button,
    ) -> None:
        view = ConfirmationButtons(interaction.user)

        await interaction.response.send_message(
            "Are you sure you want to create a private thread with the moderators and notify them?\n"
            "This message times out in 60 seconds.",
            view=view,
            ephemeral=True,
        )

        await view.wait()

        # Only proceeds if the confirm button is pressed
        if view.confirm is None:
            # On_timeout to edit the original message doesnt work here,
            # because interaction.response.send_message does not return a message object to store in a variable.
            # And we dont have access to the interaction in on_timeout. So we have to do it like this.
            await interaction.followup.send(
                "Your request timed out. Please try again.", ephemeral=True
            )
            return
        if view.confirm is False:
            # For that case, the button class above handles it.
            return

        try:
            user_name = discord.utils.escape_markdown(interaction.user.name)

            thread = await interaction.channel.create_thread(
                name=f"Modmail from {user_name}",
                type=discord.ChannelType.private_thread,
                auto_archive_duration=1440,
                message=None,
            )

            await thread.add_user(interaction.user)

            await thread.send(
                f"**✉️New Modmail <@&{TGRoleIDs.MOD_ROLE}>!✉️**\nHey there, {interaction.user.mention}! "
                "Thanks for reaching out to the Moderator Team. They will be with you shortly.\n"
                "Please use this thread for communication."
            )
        # Private threads can only be created if you have a subscripion level of 2.
        # We won't create a thread, cause public modmail isnt really that great.
        # Just need to use the "classic" modmail then and tell the user exactly that.
        except discord.HTTPException as exc:
            # We have to use the followup here since you cant respond to an interaction twice?
            await interaction.followup.send(
                f"Looks like something went wrong:\n```{exc}```\n"
                f"Please either use `{interaction.client.main_prefix}modmail` in my DMs or contact one of the moderators directly.",
                ephemeral=True,
            )


@app_commands.context_menu(name="Report This Message")
async def report_message(
    interaction: discord.Interaction, message: discord.Message
) -> None:
    """Context menu command for reporting a message to the moderator team.
    Context menu commands unfortunately cannot be inside of a Cog, so we define it here.
    """
    guild = interaction.client.get_guild(GuildIDs.TRAINING_GROUNDS)
    modmail_channel = guild.get_channel(TGChannelIDs.MODMAIL_CHANNEL)
    mod_role = discord.utils.get(guild.roles, id=TGRoleIDs.MOD_ROLE)

    # The code below is more or less copied from logging deleted messages
    if not message.content:
        message.content = "No content."

    embed = discord.Embed(
        title="Reported Message!",
        description=f"**Message Content:**\n{message.content}",
        colour=discord.Colour.dark_red(),
    )
    # Some basic info about the message
    embed.add_field(name="Message Author:", value=message.author.mention, inline=True)
    embed.add_field(name="Message Channel:", value=message.channel.mention, inline=True)
    embed.add_field(name="Message ID:", value=message.id, inline=True)
    embed.add_field(name="Message Link:", value=message.jump_url, inline=False)

    embed.set_author(
        name=f"{str(message.author)} ({message.author.id})",
        icon_url=message.author.display_avatar.url,
    )

    embed = utils.embed.add_attachments_to_embed(embed, message)

    await modmail_channel.send(
        f"**✉️ New Message Report {mod_role.mention}! ✉️**\nReport Received From: {interaction.user.mention}",
        embed=embed,
    )

    await interaction.response.send_message(
        "Thank you for your report. The moderator team will get back to you shortly.",
        ephemeral=True,
    )


class Modmail(commands.Cog):
    """Contains the "new", modmail thread setup and also the "old" modmail command."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

        # We have to add the context command manually.
        self.bot.tree.add_command(
            report_message, guilds=GuildIDs.ALL_GUILDS, override=True
        )

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        # Adds the modmail button if it hasnt already.
        # On_ready gets called multiple times, so the check is needed.
        if not self.bot.modmail_button_added:
            self.bot.add_view(ModmailButton())
            self.bot.modmail_button_added = True

    @commands.command()
    @utils.check.is_moderator()
    async def setupmodmailbutton(self, ctx: commands.Context) -> None:
        """Sets up a persistent button for Modmail.
        Should really only be used one time.
        """
        await ctx.send(
            "Click the button below to create a private thread with moderators:",
            view=ModmailButton(),
        )

    @commands.command()
    async def modmail(self, ctx: commands.Context, *, message: str) -> None:
        """Very basic one-way modmail system.
        Only works in the Bots DMs.
        """
        if str(ctx.channel.type) == "private":
            guild = self.bot.get_guild(GuildIDs.TRAINING_GROUNDS)
            modmail_channel = self.bot.get_channel(TGChannelIDs.MODMAIL_CHANNEL)
            mod_role = discord.utils.get(guild.roles, id=TGRoleIDs.MOD_ROLE)

            atm = ""
            if ctx.message.attachments:
                atm = " , ".join([i.url for i in ctx.message.attachments])

            complete_message = f"**✉️ New Modmail {mod_role.mention}! ✉️**\nFrom: {ctx.author} \nMessage:\n{message} \n{atm}"

            # With the message attachments combined with the normal message lengths,
            # the message can reach over 4k characters, but we can only send 2k at a time.
            if len(complete_message[4000:]) > 0:
                await modmail_channel.send(complete_message[:2000])
                await modmail_channel.send(complete_message[2000:4000])
                await modmail_channel.send(complete_message[4000:])

            elif len(complete_message[2000:]) > 0:
                await modmail_channel.send(complete_message[:2000])
                await modmail_channel.send(complete_message[2000:])

            else:
                await modmail_channel.send(complete_message)

            await ctx.send(
                "Your message has been sent to the Moderator Team. They will get back to you shortly."
            )

        else:
            await ctx.message.delete()
            await ctx.send(
                "For the sake of privacy, please only use this command in my DM's. They are always open for you."
            )


async def setup(bot) -> None:
    await bot.add_cog(Modmail(bot))
    print("Modmail cog loaded")

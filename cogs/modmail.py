import discord
from discord.ext import commands
from discord import app_commands
from utils.ids import TGRoleIDs, GuildIDs, TGChannelIDs
import utils.check


class ConfirmationButtons(discord.ui.View):
    """
    The buttons for confirming/cancelling the request.
    """

    def __init__(self, member: discord.Member = None):
        super().__init__()

        self.confirm = None
        self.member = member
        self.timeout = 60

    @discord.ui.button(label="Confirm", style=discord.ButtonStyle.green, emoji="✔️")
    async def confirm_button(
        self, button: discord.ui.Button, interaction: discord.Interaction
    ):
        self.confirm = True
        self.clear_items()
        await interaction.response.edit_message(content="Creating Thread...", view=self)
        self.stop()

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.red, emoji="❌")
    async def cancel_button(
        self, button: discord.ui.Button, interaction: discord.Interaction
    ):
        self.confirm = False
        self.clear_items()
        await interaction.response.edit_message(content="Request Cancelled.", view=self)
        self.stop()

    async def interaction_check(self, interaction: discord.Interaction):
        # we make sure its the right member thats pressing the button.
        # not really needed since the message is ephemeral anyways
        if interaction.user == self.member:
            return True
        else:
            return False


class ModmailButton(discord.ui.View):
    """
    The persistent modmail button.
    We dont really need to save it in a database or something,
    since it is ideally only used one time and always does the same thing.
    """

    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="Contact the moderator team",
        style=discord.ButtonStyle.success,
        custom_id="tabuu3:persistent_modmail_button",
        emoji="✉️",
    )
    async def modmail_button(
        self, button: discord.ui.Button, interaction: discord.Interaction
    ):

        view = ConfirmationButtons(interaction.user)

        await interaction.response.send_message(
            "Are you sure you want to create a private thread with the moderators and notify them?\nThis message times out in 60 seconds.",
            view=view,
            ephemeral=True,
        )

        await view.wait()

        # only proceeds if the confirm button is pressed
        if view.confirm == None:
            # on_timeout to edit the original message doesnt work here, because
            # interaction.response.send_message does not return a message object to store in a variable.
            # and we dont have access to the interaction in on_timeout.
            # so we have to do it like this.
            await interaction.followup.send(
                "Your request timed out. Please try again.", ephemeral=True
            )
            return
        if view.confirm == False:
            # for that case, the button class above handles it.
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
                f"**✉️New Modmail <@&{TGRoleIDs.MOD_ROLE}>!✉️**\nHey there, {interaction.user.mention}! Thanks for reaching out to the Moderator Team. They will be with you shortly.\nPlease use this thread for communication."
            )
        # private threads can only be created if you have a subscripion level of 2.
        # we won't create a thread, cause public modmail isnt really that great.
        # just need to use the "classic" modmail then and tell the user exactly that.
        except Exception as exc:
            # we have to use the followup here since you cant respond to an interaction twice?
            await interaction.followup.send(
                f"Looks like something went wrong:\n```{exc}```\nPlease either use `%modmail` in my DMs or contact one of the moderators directly.",
                ephemeral=True,
            )


@app_commands.context_menu(name="Report This Message")
async def report_message(interaction: discord.Interaction, message: discord.Message):
    """
    Context menu command for reporting a message to the moderator team.
    Context menu commands unfortunately cannot be inside of a Cog, so we define it here.
    """
    guild = interaction.client.get_guild(GuildIDs.TRAINING_GROUNDS)
    modmail_channel = guild.get_channel(TGChannelIDs.MODMAIL_CHANNEL)
    mod_role = discord.utils.get(guild.roles, id=TGRoleIDs.MOD_ROLE)

    # the code below is more or less copied from logging deleted messages
    if not message.content:
        message.content = "No content."

    embed = discord.Embed(
        title=f"Reported Message!",
        description=f"**Message Content:**\n{message.content}",
        colour=discord.Colour.dark_red(),
    )
    # some basic info about the message
    embed.add_field(name="Message Author:", value=message.author.mention, inline=True)
    embed.add_field(name="Message Channel:", value=message.channel.mention, inline=True)
    embed.add_field(name="Message ID:", value=message.id, inline=True)
    embed.add_field(name="Message Link:", value=message.jump_url, inline=False)

    embed.set_author(
        name=f"{str(message.author)} ({message.author.id})",
        icon_url=message.author.display_avatar.url,
    )
    if message.attachments:
        if len(message.attachments) == 1:
            if message.attachments[0].url.endswith((".jpg", ".png", ".jpeg", ".gif")):
                new_url = message.attachments[0].url.replace(
                    "cdn.discordapp.com", "media.discordapp.net"
                )
                embed.set_image(url=new_url)
                embed.add_field(name="Attachment:", value="See below.", inline=False)
            else:
                embed.add_field(
                    name="Attachment:",
                    value=message.attachments[0].url,
                    inline=False,
                )
        else:
            i = 1
            for x in message.attachments:
                embed.add_field(
                    name=f"Attachment ({i}/{len(message.attachments)}):",
                    value=x.url,
                    inline=False,
                )
                i += 1
    if message.stickers:
        if not message.attachments:
            embed.set_image(url=message.stickers[0].url)
            embed.add_field(name="Sticker:", value="See below.", inline=False)
        else:
            embed.add_field(name="Sticker:", value=f"{message.stickers[0].url}")

    await modmail_channel.send(
        f"**✉️ New Message Report {mod_role.mention}! ✉️**\nReport Received From: {interaction.user.mention}",
        embed=embed,
    )

    await interaction.response.send_message(
        "Thank you for your report. The moderator team will get back to you shortly.",
        ephemeral=True,
    )


class Modmail(commands.Cog):
    """
    Contains the "new", modmail thread setup and also the "old" modmail command.
    """

    def __init__(self, bot):
        self.bot = bot

        # we have to add the context command manually
        self.bot.tree.add_command(
            report_message, guilds=GuildIDs.ALL_GUILDS, override=True
        )

    @commands.Cog.listener()
    async def on_ready(self):
        # adds the modmail button if it hasnt already.
        # on_ready gets called multiple times, so the check is needed.
        if not self.bot.modmail_button_added:
            self.bot.add_view(ModmailButton())
            self.bot.modmail_button_added = True

    @commands.command()
    @utils.check.is_moderator()
    async def setupmodmailbutton(self, ctx):
        """
        Sets up a persistent button for Modmail.
        Should really only be used one time.
        """
        await ctx.send(
            "Click the button below to create a private thread with moderators:",
            view=ModmailButton(),
        )

    @commands.command()
    async def modmail(self, ctx, *, args):
        """
        Very basic one-way modmail system.
        Only works in the Bots DMs.
        """
        if str(ctx.channel.type) == "private":
            guild = self.bot.get_guild(GuildIDs.TRAINING_GROUNDS)
            modmail_channel = self.bot.get_channel(TGChannelIDs.MODMAIL_CHANNEL)
            mod_role = discord.utils.get(guild.roles, id=TGRoleIDs.MOD_ROLE)

            atm = ""
            if ctx.message.attachments:
                atm = " , ".join([i.url for i in ctx.message.attachments])

            complete_message = f"**✉️ New Modmail {mod_role.mention}! ✉️**\nFrom: {ctx.author} \nMessage:\n{args} \n{atm}"

            # with the message attachments combined with the normal message lengths, the message can reach over 4k characters, but we can only send 2k at a time.
            if len(complete_message[4000:]) > 0:
                await modmail_channel.send(complete_message[:2000])
                await modmail_channel.send(complete_message[2000:4000])
                await modmail_channel.send(complete_message[4000:])
                await ctx.send(
                    "Your message has been sent to the Moderator Team. They will get back to you shortly."
                )

            elif len(complete_message[2000:]) > 0:
                await modmail_channel.send(complete_message[:2000])
                await modmail_channel.send(complete_message[2000:])
                await ctx.send(
                    "Your message has been sent to the Moderator Team. They will get back to you shortly."
                )

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

    @setupmodmailbutton.error
    async def setupmodmailbutton_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("Nice try, but you don't have the permissions to do that!")
        else:
            raise error

    @modmail.error
    async def modmail_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(
                "Please provide a message to the moderators. It should look something like:\n```%modmail (your message here)```"
            )
        else:
            raise error


def setup(bot):
    bot.add_cog(Modmail(bot))
    print("Modmail cog loaded")

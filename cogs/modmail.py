import discord
from discord.ext import commands
from utils.ids import TGRoleIDs, GuildIDs, TGChannelIDs
import utils.check


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
            await interaction.response.send_message(
                f"Looks like something went wrong:\n```{exc}```\nPlease either use `%modmail` in my DMs or contact one of the moderators directly.",
                ephemeral=True,
            )


class Modmail(commands.Cog):
    """
    Contains the "new", modmail thread setup and also the "old" modmail command.
    """

    def __init__(self, bot):
        self.bot = bot

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

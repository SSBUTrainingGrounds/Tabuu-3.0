import discord
from discord.ext import commands, tasks
import json
import random
import time
from datetime import datetime
from .mute import Mute
from utils.ids import TGChannelIDs, AdminVars
import utils.logger


class Warn(commands.Cog):
    """
    Contains our custom warning system.
    """

    def __init__(self, bot):
        self.bot = bot

        self.warnloop.start()

    def cog_unload(self):
        self.warnloop.cancel()

    async def add_warn(self, author: discord.Member, member: discord.Member, reason):
        """
        Adds a warning to the json file.
        Also logs it to our infraction-logs channel.
        """
        with open(r"./json/warns.json", "r") as f:
            users = json.load(f)

        # assigning each warning a random 6 digit number, hope thats enough to not get duplicates
        warn_id = random.randint(100000, 999999)
        warndate = time.strftime("%A, %B %d %Y @ %H:%M:%S %p")

        try:
            user_data = users[str(member.id)]
            user_data[warn_id] = {
                "mod": author.id,
                "reason": reason,
                "timestamp": warndate,
            }
        except:
            users[f"{member.id}"] = {}
            user_data = users[str(member.id)]
            user_data[warn_id] = {
                "mod": author.id,
                "reason": reason,
                "timestamp": warndate,
            }

        with open(r"./json/warns.json", "w") as f:
            json.dump(users, f, indent=4)

        # and this second part here logs the warn into the warning log discord channel
        channel = self.bot.get_channel(TGChannelIDs.INFRACTION_LOGS)
        embed = discord.Embed(title="⚠️New Warning⚠️", color=discord.Color.dark_red())
        embed.add_field(name="Warned User", value=member.mention, inline=True)
        embed.add_field(name="Moderator", value=author.mention, inline=True)
        embed.add_field(name="Reason", value=reason, inline=True)
        embed.add_field(name="ID", value=warn_id, inline=True)
        embed.timestamp = discord.utils.utcnow()
        await channel.send(embed=embed)

    async def check_warn_count(
        self, guild: discord.Guild, channel: discord.TextChannel, member: discord.Member
    ):
        """
        Checks the amount of warnings a user has and executes the according action.

        3 warnings:
            User gets muted indefinitely.
        5 warnings:
            User gets kicked from the Server.
        7 warnings:
            User gets banned from the Server.

        Also DMs them informing the User of said action.
        """
        with open(r"./json/warns.json", "r") as f:
            users = json.load(f)

        user_data = users[str(member.id)]
        warns = len(user_data)

        if warns > 6:
            try:
                await member.send(
                    f"You have been automatically banned from the {guild.name} Server for reaching warning #***{warns}***.\nPlease contact {AdminVars.GROUNDS_KEEPER} for an appeal.\n{AdminVars.BAN_RECORDS}"
                )
            except Exception as exc:
                logger = utils.logger.get_logger("bot.warn")
                logger.warning(
                    f"Tried to message automatic ban reason to {str(member)}, but it failed: {exc}"
                )

            await channel.send(
                f"{member.mention} has reached warning #{warns}. They have been automatically banned."
            )
            await member.ban(reason=f"Automatic ban for reaching {warns} warnings")
        elif warns > 4:
            try:
                await member.send(
                    f"You have been automatically kicked from the {guild.name} Server for reaching warning #***{warns}***. \nIf you would like to discuss your punishment, please contact {AdminVars.GROUNDS_GENERALS}."
                )
            except Exception as exc:
                logger = utils.logger.get_logger("bot.warn")
                logger.warning(
                    f"Tried to message automatic kick reason to {str(member)}, but it failed: {exc}"
                )

            await channel.send(
                f"{member.mention} has reached warning #{warns}. They have been automatically kicked."
            )
            await member.kick(reason=f"Automatic kick for reaching {warns} warnings")
        elif warns > 2:
            await Mute.add_mute(self, guild, member)
            await channel.send(
                f"{member.mention} has reached warning #{warns}. They have been automatically muted."
            )

            try:
                await member.send(
                    f"You have been automatically muted in the {guild.name} Server for reaching warning #***{warns}***. \nIf you would like to discuss your punishment, please contact {AdminVars.GROUNDS_GENERALS}."
                )
            except Exception as exc:
                logger = utils.logger.get_logger("bot.warn")
                logger.warning(
                    f"Tried to message automatic mute reason to {str(member)}, but it failed: {exc}"
                )

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def warn(self, ctx, member: discord.Member, *, reason):
        """
        Warns a user.
        """
        if member.bot:
            await ctx.send("You can't warn bots, silly.")
            return

        # adds the warning
        await self.add_warn(ctx.author, member, reason)

        # tries to dm user
        try:
            await member.send(
                f"You have been warned in the {ctx.guild.name} Server for the following reason: \n```{reason}```\nIf you would like to discuss your punishment, please contact {AdminVars.GROUNDS_GENERALS}."
            )
        except Exception as exc:
            logger = utils.logger.get_logger("bot.warn")
            logger.warning(
                f"Tried to message warn reason to {str(member)}, but it failed: {exc}"
            )

        await ctx.send(f"{member.mention} has been warned!")

        # checks warn count for further actions
        await self.check_warn_count(ctx.guild, ctx.channel, member)

    @commands.command(aliases=["warnings", "infractions"])
    async def warns(self, ctx, member: discord.Member = None):
        """
        Checks the warnings of a user, or yourself.
        """
        if member is None:
            member = ctx.author

        try:
            with open(r"./json/warns.json", "r") as f:
                users = json.load(f)

            user_data = users[str(member.id)]

            await ctx.send(f"{member.mention} has {len(user_data)} warning(s).")
        except:
            await ctx.send(f"{member.mention} doesn't have any warnings (yet).")

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def clearwarns(self, ctx, member: discord.Member):
        """
        Deletes a user and all of their warnings from the database.
        """
        with open(r"./json/warns.json", "r") as f:
            users = json.load(f)

        if f"{member.id}" in users:
            del users[f"{member.id}"]
            await ctx.send(f"Cleared all warnings for {member.mention}.")
        else:
            await ctx.send(f"No warnings found for {member.mention}")

        with open(r"./json/warns.json", "w") as f:
            json.dump(users, f, indent=4)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def warndetails(self, ctx, member: discord.Member):
        """
        Gets you the details of a Users warnings.
        """
        try:
            with open(r"./json/warns.json", "r") as f:
                users = json.load(f)

            user_data = users[str(member.id)]
            embed_list = []

            i = 1
            for warn_id in user_data.keys():
                mod = users[f"{member.id}"][warn_id]["mod"]
                reason = users[f"{member.id}"][warn_id]["reason"]
                timestamp = users[f"{member.id}"][warn_id]["timestamp"]
                new_timestamp = datetime.strptime(
                    timestamp, "%A, %B %d %Y @ %H:%M:%S %p"
                )

                embed = discord.Embed(
                    title=f"Warning #{i}", colour=discord.Colour.red()
                )
                embed.add_field(name="Moderator: ", value=f"<@{mod}>")
                embed.add_field(name="Reason: ", value=f"{reason}")
                embed.add_field(name="ID:", value=f"{warn_id}")
                embed.add_field(
                    name="Warning given out at:",
                    value=discord.utils.format_dt(new_timestamp, style="F"),
                )
                embed_list.append(embed)

                i += 1

            # if the user is in the json file but the warnings got deleted, the embeds will be empty, but discord just ignores that so, no big deal
            # the maximum amount of embeds you can send is 10, we do ban people at 7 warnings but you never know what might happen
            try:
                await ctx.send(
                    f"Active warnings for {member.mention}: {len(user_data)}",
                    embeds=embed_list,
                )
            except:
                await ctx.send(
                    f"Active warnings for {member.mention}: {len(user_data)}\nCannot list warnings for this user!"
                )

        # if the user isnt found at all in the json file, it gives you this generic error message
        except:
            await ctx.send(f"{member.mention} doesn't have any active warnings (yet).")

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def deletewarn(self, ctx, member: discord.Member, warn_id):
        """
        Deletes a specific warning of a user, by the randomly generated warning ID.
        Use warndetails to see these warning IDs.
        """
        try:
            with open(r"./json/warns.json", "r") as f:
                users = json.load(f)

            user_data = users[str(member.id)]

            if warn_id in user_data:
                del users[f"{member.id}"][warn_id]
                await ctx.send(f"Deleted warning {warn_id} for {member.mention}")
            else:
                await ctx.send(
                    f"I couldnt find a warning with the ID {warn_id} for {member.mention}."
                )

            with open(r"./json/warns.json", "w") as f:
                json.dump(users, f, indent=4)
        except:
            await ctx.send("This user does not have any active warnings.")

    # basic error handling for the above
    @warn.error
    async def warn_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("You need to specify a member and a reason!")
        elif isinstance(error, commands.MemberNotFound):
            await ctx.send("You need to mention a member!")
        elif isinstance(error, commands.MissingPermissions):
            await ctx.send("Nice try, but you don't have the permissions to do that!")
        else:
            raise error

    @warns.error
    async def warns_error(self, ctx, error):
        if isinstance(error, commands.MemberNotFound):
            await ctx.send("You need to mention a member, or just leave it blank.")
        else:
            raise error

    @clearwarns.error
    async def clearwarns_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("You need to mention a member!")
        elif isinstance(error, commands.MissingPermissions):
            await ctx.send("Nice try, but you don't have the permissions to do that!")
        else:
            raise error

    @deletewarn.error
    async def deletewarn_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("You need to mention a member and specify a warn_id.")
        elif isinstance(error, commands.MemberNotFound):
            await ctx.send("You need to mention a valid member.")
        elif isinstance(error, commands.MissingPermissions):
            await ctx.send("Nice try, but you don't have the permissions to do that!")
        else:
            raise error

    @warndetails.error
    async def warndetails_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("You need to mention a valid member.")
        elif isinstance(error, commands.MemberNotFound):
            await ctx.send("You need to mention a valid member.")
        elif isinstance(error, commands.MissingPermissions):
            await ctx.send("Nice try, but you don't have the permissions to do that!")
        else:
            raise error

    @tasks.loop(hours=24)
    async def warnloop(self):
        """
        This here checks if a warning is older than 30 days and has expired,
        if that is the case, deletes the expired warnings.
        """
        with open(r"./json/warns.json", "r") as f:
            users = json.load(f)

        tbd_warnings = []

        logger = utils.logger.get_logger("bot.warn")

        # checks every warning for every user
        # we first need to append the warnings to a separate list and then we can delete them
        for warned_user in users:
            for warn_id in users[warned_user].keys():
                timestamp = users[warned_user][warn_id]["timestamp"]
                # this here compares the stored CEST timezone of the warning to the current GMT timezone
                # its off by 1 hour (or 2 in summer) but thats close enough when we count in differences of 30 days
                timediff = datetime.utcnow() - datetime.strptime(
                    timestamp, "%A, %B %d %Y @ %H:%M:%S %p"
                )
                daydiff = timediff.days
                # so if its been longer than 30 days since the warning was handed out, we will hand the warning over to the loop below which will delete it
                if daydiff > 29:
                    tbd_warnings.append((warned_user, warn_id))
                    logger.info(
                        f"Deleting warn_id #{warn_id} for user {warned_user} after 30 days..."
                    )

        # deletes the warnings
        for i in tbd_warnings:
            # i00 is the user id, i01 is the warn id
            del users[[i][0][0]][[i][0][1]]
            logger.info(f"Successfully deleted warn #{[i][0][1]}!")

        with open(r"./json/warns.json", "w") as f:
            json.dump(users, f, indent=4)

    @warnloop.before_loop
    async def before_warnloop(self):
        await self.bot.wait_until_ready()


def setup(bot):
    bot.add_cog(Warn(bot))
    print("Warn cog loaded")

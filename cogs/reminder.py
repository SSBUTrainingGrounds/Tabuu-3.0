import asyncio
import datetime
import random

import aiosqlite
import discord
from discord import app_commands
from discord.ext import commands, tasks

from utils.ids import GuildIDs
from utils.time import convert_time


class Reminder(commands.Cog):
    """
    Contains the reminder functions and everything associated with them.
    """

    def __init__(self, bot):
        self.bot = bot

        self.reminder_loop.start()

    def cog_unload(self):
        self.reminder_loop.cancel()

    async def notify_user(
        self, user_id: int, channel_id: int, message: str, read_time: str
    ):
        """
        Notifies the user when their reminder expires.
        First we try in the channel, then their DMs.
        """
        logger = self.bot.get_logger("bot.reminder")

        try:
            channel = await self.bot.fetch_channel(channel_id)
            await channel.send(
                f"<@!{user_id}>, you wanted me to remind you of `{message}`, {read_time} ago."
            )
            # the channel could get deleted in the meantime,
            # or something else can prevent us having access
        except discord.HTTPException:
            # unfortunately we need a second try/except block because
            # people can block your bot and this would throw an error otherwise,
            # and we dont wanna interrupt the loop
            try:
                member = await self.bot.fetch_user(user_id)
                await member.send(
                    f"<@!{user_id}>, you wanted me to remind you of `{message}`, "
                    f"{read_time} ago, in a deleted channel."
                )
            except discord.HTTPException as exc:
                logger.info(f"Could not notify user due to: {exc}")

    @commands.hybrid_command(aliases=["remindme", "newreminder", "newremindme"])
    @app_commands.guilds(*GuildIDs.ALL_GUILDS)
    @app_commands.describe(
        time="The time when you want me to remind you.",
        reminder_message="The message you want me to remind you of.",
    )
    async def reminder(self, ctx, time: str, *, reminder_message: str):
        """
        Saves a new reminder.
        """
        seconds, reminder_time = convert_time(time)

        if seconds < 30:
            await ctx.send(
                "Duration is too short! I'm sure you can remember that yourself."
            )
            return
        # 90 days, maybe increase it to 1 year in the future, idk
        if seconds > 7776000:
            await ctx.send(
                "Duration is too long! Maximum duration is 90 days from now."
            )
            return

        # i think 200 chars is enough for a reminder message,
        # have to keep discord max message length in mind for viewreminders
        if len(reminder_message[200:]) > 0:
            reminder_message = reminder_message[:200]

        reminder_message = discord.utils.remove_markdown(reminder_message)

        # if the duration is fairly short, i wont bother writing it to the file,
        # a sleep statement will do
        if seconds < 299:
            message_dt = datetime.datetime.fromtimestamp(
                discord.utils.utcnow().timestamp() + seconds
            )

            await ctx.send(
                f"{ctx.author.mention}, I will remind you about `{reminder_message}` in {reminder_time}! "
                f"({discord.utils.format_dt(message_dt, style='f')})"
            )

            await asyncio.sleep(seconds)

            await ctx.send(
                f"{ctx.author.mention}, you wanted me to remind you of `{reminder_message}`, {reminder_time} ago."
            )
        # otherwise it will get saved in the file
        else:
            reminder_id = random.randint(1000000, 9999999)
            reminder_date = int(discord.utils.utcnow().timestamp() + seconds)

            async with aiosqlite.connect("./db/database.db") as db:
                await db.execute(
                    """INSERT INTO reminder VALUES (:user_id, :reminder_id, :channel_id, :date, :read_time, :message)""",
                    {
                        "user_id": ctx.author.id,
                        "reminder_id": reminder_id,
                        "channel_id": ctx.channel.id,
                        "date": reminder_date,
                        "read_time": reminder_time,
                        "message": reminder_message,
                    },
                )
                await db.commit()

            message_dt = datetime.datetime.fromtimestamp(
                discord.utils.utcnow().timestamp() + seconds
            )

            await ctx.send(
                f"{ctx.author.mention}, I will remind you about `{reminder_message}` in {reminder_time}! "
                f"({discord.utils.format_dt(message_dt, style='f')})\n"
                f"View all of your active reminders with `{self.bot.command_prefix}viewreminders`"
            )

    @commands.hybrid_command(
        aliases=["reminders", "myreminders", "viewreminder", "listreminders"]
    )
    @app_commands.guilds(*GuildIDs.ALL_GUILDS)
    async def viewreminders(self, ctx):
        """
        Displays your active reminders.
        """
        async with aiosqlite.connect("./db/database.db") as db:
            user_reminders = await db.execute_fetchall(
                """SELECT * FROM reminder WHERE user_id = :user_id""",
                {"user_id": ctx.author.id},
            )

        reminder_list = []

        for reminder in user_reminders:
            # the underscores are user id, channel id and read_time
            (_, reminder_id, _, date, _, message) = reminder

            dt_now = discord.utils.utcnow().timestamp()
            timediff = str(datetime.timedelta(seconds=date - dt_now)).split(
                ".", maxsplit=1
            )[0]
            # in an unfortunate case of timing, a user could view their reminder
            # when it already "expired" but the loop has not checked yet.
            # this here prevents a dumb number displaying
            if (date - dt_now) <= 30:
                timediff = "Less than a minute..."
            reminder_list.append(
                f"**ID:** {reminder_id} - **Time remaining:** {timediff} - **Message:** `{message}`\n"
            )

        if not reminder_list:
            reminder_list = ["No reminders found."]

        try:
            await ctx.send(f"Here are your active reminders:\n{''.join(reminder_list)}")
        # if the message is too long, this error gets triggered
        except discord.errors.HTTPException:
            # should be max ~300 chars per reminder so we can fit in 6 in the worst case.
            # discord message char limit being at 2000
            shortened_reminder_list = reminder_list[:6]
            await ctx.send(
                f"Your reminders are too long to list in a single message. "
                f"Here are your first 6 reminders:\n{''.join(shortened_reminder_list)}"
            )

    @commands.hybrid_command(
        aliases=["delreminder", "rmreminder", "delreminders", "deletereminders"]
    )
    @app_commands.guilds(*GuildIDs.ALL_GUILDS)
    @app_commands.describe(reminder_id="The ID of the reminder you want to delete.")
    async def deletereminder(self, ctx, reminder_id: str):
        """
        Deletes a reminder of yours.
        """
        async with aiosqlite.connect("./db/database.db") as db:
            matching_reminder = await db.execute_fetchall(
                """SELECT * FROM reminder WHERE user_id = :user_id AND reminder_id = :reminder_id""",
                {"user_id": ctx.author.id, "reminder_id": reminder_id},
            )

            if len(matching_reminder) == 0:
                await ctx.send(
                    "I could not find any reminder with this ID. \n"
                    f"View all of your active reminders with `{self.bot.command_prefix}viewreminders`"
                )
                return

            await db.execute(
                """DELETE FROM reminder WHERE user_id = :user_id AND reminder_id = :reminder_id""",
                {"user_id": ctx.author.id, "reminder_id": reminder_id},
            )
            await db.commit()

        await ctx.send(f"Deleted reminder ID {reminder_id}.")

    @tasks.loop(seconds=60)
    async def reminder_loop(self):
        """
        Checks every minute if a reminder has passed.
        If that is the case, notifies the user and deletes the reminder.
        """
        logger = self.bot.get_logger("bot.reminder")

        date_now = discord.utils.utcnow().timestamp()

        async with aiosqlite.connect("./db/database.db") as db:
            expired_reminders = await db.execute_fetchall(
                """SELECT * FROM reminder WHERE date < :date_now""",
                {"date_now": int(date_now)},
            )

            for reminder in expired_reminders:
                (user_id, reminder_id, channel_id, _, read_time, message) = reminder

                logger.info(
                    f"Reminder #{reminder_id} from user {user_id} has passed. Notifying user and deleting reminder..."
                )

                await self.notify_user(user_id, channel_id, message, read_time)

            await db.execute(
                """DELETE FROM reminder WHERE date < :date_now""",
                {"date_now": int(date_now)},
            )

            await db.commit()

    @reminder_loop.before_loop
    async def before_reminder_loop(self):
        await self.bot.wait_until_ready()

    # error handling
    @reminder.error
    async def reminder_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(
                "You need to specify an amount of time and the reminder message!"
            )
        elif isinstance(error, commands.CommandInvokeError):
            await ctx.send(
                "Invalid time format! Please use a number followed by d/h/m/s for days/hours/minutes/seconds.\n"
                f"Example: `{self.bot.command_prefix}reminder 1h20m your message here`"
            )
        else:
            raise error

    @viewreminders.error
    async def viewreminders_error(self, ctx, error):
        if isinstance(error, commands.CommandInvokeError):
            await ctx.send("Here are your active reminders:\nNo reminders found.")
        else:
            raise error

    @deletereminder.error
    async def deletereminder_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(
                "You need to specify which reminder to delete. "
                f"View all of your active reminders with `{self.bot.command_prefix}viewreminders`"
            )
        elif isinstance(error, commands.CommandInvokeError):
            await ctx.send("You have no active reminders to delete.")
        else:
            raise error


async def setup(bot):
    await bot.add_cog(Reminder(bot))
    print("Reminder cog loaded")

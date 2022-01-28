import discord
from discord.ext import commands, tasks
import json
import random
import datetime
import asyncio
from utils.time import convert_time
import utils.logger

#
#this file here contains the new reminder system
#

class Reminder(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.reminder_loop.start()


    def cog_unload(self):
        self.reminder_loop.cancel()


    #saves a new reminder
    @commands.command(aliases=['remindme', "newreminder", "newremindme"])
    async def reminder(self, ctx, time, *, reminder_message):
        seconds, reminder_time = convert_time(time)

        if seconds < 30:
            await ctx.send("Duration is too short! I'm sure you can remember that yourself.")
            return
        #30 days, chosen at will. maybe increase it to a year or so in the future
        if seconds > 2592000:
            await ctx.send("Duration is too long! Maximum duration is 30 days.")
            return

        #i think 200 chars is enough for a reminder message, have to keep discord max message length in mind for viewreminders
        if len(reminder_message[200:]) > 0:
            reminder_message = reminder_message[:200]

        reminder_message = discord.utils.remove_markdown(reminder_message)

        #if the duration is fairly short, i wont bother writing it to the file, a sleep statement will do
        if seconds < 299:
            message_dt = datetime.datetime.fromtimestamp(discord.utils.utcnow().timestamp() + seconds)

            await ctx.send(f"{ctx.author.mention}, I will remind you about `{reminder_message}` in {reminder_time}! ({discord.utils.format_dt(message_dt, style='f')})")

            await asyncio.sleep(seconds)

            await ctx.send(f"{ctx.author.mention}, you wanted me to remind you of `{reminder_message}`, {reminder_time} ago.")
        #otherwise it will get saved in the file
        else:
            with open(r'./json/reminder.json', 'r') as f:
                reminders = json.load(f)

            reminder_id = random.randint(1000000, 9999999)
            reminder_date = discord.utils.utcnow().timestamp() + seconds

            try:
                reminders[f'{ctx.author.id}'][reminder_id] = {'channel': ctx.channel.id, 'date': reminder_date, 'read_time': reminder_time, 'message': reminder_message}
            except KeyError:
                reminders[f'{ctx.author.id}'] = {}
                reminders[f'{ctx.author.id}'][reminder_id] = {'channel': ctx.channel.id, 'date': reminder_date, 'read_time': reminder_time, 'message': reminder_message}

            with open(r'./json/reminder.json', 'w') as f:
                json.dump(reminders, f, indent=4)

            message_dt = datetime.datetime.fromtimestamp(discord.utils.utcnow().timestamp() + seconds)

            await ctx.send(f"{ctx.author.mention}, I will remind you about `{reminder_message}` in {reminder_time}! ({discord.utils.format_dt(message_dt, style='f')})\nView all of your active reminders with `%viewreminders`")



    #view your reminders
    @commands.command(aliases=['reminders', 'myreminders', 'viewreminder', 'listreminders'])
    async def viewreminders(self, ctx):
        with open(r'./json/reminder.json', 'r') as f:
            reminders = json.load(f)

        reminder_list = []

        for reminder in reminders[f'{ctx.author.id}']:
            dt = reminders[f'{ctx.author.id}'][reminder]['date']
            dt_now = discord.utils.utcnow().timestamp()
            timediff = str(datetime.timedelta(seconds=(dt - dt_now))).split('.')[0]
            #in a unfortunate case of timing, a user could view their reminder when it already "expired" but the loop has not checked yet. this here prevents a dumb number displaying
            if (dt - dt_now) <= 30:
                timediff = "Less than a minute..."
            reminder_list.append(f"**ID:** {reminder} - **Time remaining:** {timediff} - **Message:** `{reminders[f'{ctx.author.id}'][reminder]['message']}`\n")

        if len(reminder_list) == 0:
            reminder_list = ["No reminders found."]

        try:
            await ctx.send(f"Here are your active reminders:\n{''.join(reminder_list)}")
        #if the message is too long, this error gets triggered
        except discord.errors.HTTPException:
            #should be max ~300 chars per reminder so we can fit in 6 in the worst case. discord message char limit being at 2000
            shortened_reminder_list = reminder_list[:6]
            await ctx.send(f"Your reminders are too long to list in a single message. Here are your first 6 reminders:\n{''.join(shortened_reminder_list)}")



    #just deletes a reminder
    @commands.command(aliases=['delreminder', 'rmreminder', 'delreminders', 'deletereminders'])
    async def deletereminder(self, ctx, reminder_id):
        with open(r'./json/reminder.json', 'r') as f:
            reminders = json.load(f)

        if reminder_id in reminders[f'{ctx.author.id}']:
            del reminders[f'{ctx.author.id}'][reminder_id]
            await ctx.send(f"Deleted reminder ID {reminder_id}.")
        else:
            await ctx.send("I could not find any reminder with this ID. \nView all of your active reminders with `%viewreminders`")

        with open(r'./json/reminder.json', 'w') as f:
            json.dump(reminders, f, indent=4)



    #the loop that checks if a reminder has already passed
    @tasks.loop(seconds=60)
    async def reminder_loop(self):
        with open(r'./json/reminder.json', 'r') as f:
            reminders = json.load(f)

        tbd_reminders = []

        logger = utils.logger.get_logger("bot.reminder")

        for user in reminders:
            for reminder_id in reminders[user]:
                reminder_date = reminders[user][reminder_id]['date']
                date_now = discord.utils.utcnow().timestamp()
                if reminder_date < date_now:
                    logger.info(f"Reminder #{reminder_id} from user {user} has passed. Notifying user and deleting reminder...")

                    message = reminders[user][reminder_id]['message']
                    time = reminders[user][reminder_id]['read_time']
                    try:
                        channel = await self.bot.fetch_channel(reminders[user][reminder_id]['channel'])
                        await channel.send(f"<@!{user}>, you wanted me to remind you of `{message}`, {time} ago.")
                    #the channel could get deleted in the meantime
                    except discord.errors.NotFound:
                        #unfortunately we need a second try/except block because people can block your bot and this would throw an error otherwise, and we dont wanna interrupt the loop
                        try:
                            member = await self.bot.fetch_user(user)
                            await member.send(f"<@!{user}>, you wanted me to remind you of `{message}`, {time} ago, in a deleted channel.")
                        except:
                            pass

                    #need to append these first, then delete them. otherwise we'll get an error saying our loop changed or whatever
                    tbd_reminders.append((user, reminder_id))

        for i in tbd_reminders:
            del reminders[i[0]][i[1]]
            logger.info(f"Successfully deleted Reminder #{i[1]}")

        with open(r'./json/reminder.json', 'w') as f:
            json.dump(reminders, f, indent=4)


    @reminder_loop.before_loop
    async def before_reminder_loop(self):
        await self.bot.wait_until_ready()





    #error handling
    @reminder.error
    async def reminder_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("You need to specify an amount of time and the reminder message!")
        elif isinstance(error, commands.CommandInvokeError):
            await ctx.send("Invalid time format! Please use a number followed by d/h/m/s for days/hours/minutes/seconds.\nExample: `%reminder 1h20m your message here`")
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
        if isinstance(error, commands.CommandInvokeError):
            await ctx.send("You have no active reminders to delete.")
        else:
            raise error

    @deletereminder.error
    async def deletereminder_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("You need to specify which reminder to delete. View all of your active reminders with `%viewreminders`")
        else:
            raise error



def setup(bot):
    bot.add_cog(Reminder(bot))
    print("Reminder cog loaded")
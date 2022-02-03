import discord
from discord.ext import commands
import json
import asyncio
from utils.ids import GuildNames, GuildIDs, TGArenaChannelIDs, TGMatchmakingRoleIDs
import utils.logger


class Ranking(commands.Cog):
    """
    Contains the ranked portion of our matchmaking system.
    """

    def __init__(self, bot):
        self.bot = bot

    async def get_recent_ranked_pings(self, timestamp: float):
        """
        Gets a list with all the recent ranked pings.
        We need a different approach than unranked here because we also store the rank role here.
        """
        with open(r"./json/rankedpings.json", "r") as f:
            user_pings = json.load(f)

        list_of_searches = []

        for ping in user_pings:
            ping_rank = user_pings[f"{ping}"]["rank"]
            ping_channel = user_pings[f"{ping}"]["channel"]
            ping_timestamp = user_pings[f"{ping}"]["time"]

            difference = timestamp - ping_timestamp

            minutes = round(difference / 60)

            if minutes < 31:
                list_of_searches.append(
                    f"<@&{ping_rank}> | <@!{ping}>, in <#{ping_channel}>, {minutes} minutes ago\n"
                )

        list_of_searches.reverse()
        searches = "".join(list_of_searches)

        if len(searches) == 0:
            searches = "Looks like no one has pinged recently :("

        return searches

    @commands.command(aliases=["rankedmm", "rankedmatchmaking", "rankedsingles"])
    @commands.cooldown(1, 120, commands.BucketType.user)
    async def ranked(self, ctx):
        """
        Used for 1v1 ranked matchmaking.
        Pings your ranked role.
        """
        if ctx.channel.id not in TGArenaChannelIDs.RANKED_ARENAS:
            await ctx.send(
                "Please only use this command in the ranked matchmaking arenas."
            )
            ctx.command.reset_cooldown(ctx)
            return

        timestamp = discord.utils.utcnow().timestamp()

        with open(r"./json/ranking.json", "r") as f:
            ranking = json.load(f)

        # gets your elo score and the according value
        try:
            elo = ranking[f"{ctx.author.id}"]["elo"]
            if elo < 800:
                pingrole = discord.utils.get(
                    ctx.guild.roles, id=TGMatchmakingRoleIDs.ELO_800_ROLE
                )
            if elo < 950 and elo > 799:
                pingrole = discord.utils.get(
                    ctx.guild.roles, id=TGMatchmakingRoleIDs.ELO_950_ROLE
                )
            if elo < 1050 and elo > 949:
                pingrole = discord.utils.get(
                    ctx.guild.roles, id=TGMatchmakingRoleIDs.ELO_1050_ROLE
                )
            if elo < 1200 and elo > 1049:
                pingrole = discord.utils.get(
                    ctx.guild.roles, id=TGMatchmakingRoleIDs.ELO_1200_ROLE
                )
            if elo < 1300 and elo > 1199:
                pingrole = discord.utils.get(
                    ctx.guild.roles, id=TGMatchmakingRoleIDs.ELO_1300_ROLE
                )
            if elo > 1299:
                pingrole = discord.utils.get(
                    ctx.guild.roles, id=TGMatchmakingRoleIDs.ELO_MAX_ROLE
                )
        except:
            # default elo role, in case someone isnt in the database
            pingrole = discord.utils.get(
                ctx.guild.roles, id=TGMatchmakingRoleIDs.ELO_1050_ROLE
            )

        with open(r"./json/rankedpings.json", "r") as fp:
            rankedusers = json.load(fp)

        # stores your ping
        rankedusers[f"{ctx.author.id}"] = {}
        rankedusers[f"{ctx.author.id}"] = {
            "rank": pingrole.id,
            "channel": ctx.channel.id,
            "time": timestamp,
        }

        with open(r"./json/rankedpings.json", "w") as fp:
            json.dump(rankedusers, fp, indent=4)

        # gets all of the other active pings
        searches = await self.get_recent_ranked_pings(timestamp)

        embed = discord.Embed(
            title="Ranked pings in the last 30 Minutes:",
            description=searches,
            colour=discord.Colour.blue(),
        )

        mm_message = await ctx.send(
            f"{ctx.author.mention} is looking for ranked matchmaking games! {pingrole.mention}",
            embed=embed,
        )
        mm_thread = await mm_message.create_thread(
            name=f"Ranked Arena of {ctx.author.name}", auto_archive_duration=60
        )
        await mm_thread.add_user(ctx.author)
        await mm_thread.send(
            f"Hi there, {ctx.author.mention}! Please use this thread for communicating with your opponent and for reporting matches."
        )

        # waits 30 mins and deletes the ping afterwards
        await asyncio.sleep(1800)

        with open(r"./json/rankedpings.json", "r") as fp:
            rankedusers = json.load(fp)

        try:
            del rankedusers[f"{ctx.message.author.id}"]
        except KeyError:
            logger = utils.logger.get_logger("bot.mm")
            logger.warning(
                f"Tried to delete a ranked ping by {str(ctx.message.author)} but the ping was already deleted."
            )

        with open(r"./json/rankedpings.json", "w") as fp:
            json.dump(rankedusers, fp, indent=4)

    @commands.command(aliases=["reportgame"], cooldown_after_parsing=True)
    @commands.cooldown(1, 41, commands.BucketType.user)
    @commands.guild_only()
    async def reportmatch(self, ctx, user: discord.Member):
        """
        The winner of the match uses this to report a ranked set.
        Updates the elo values and ranked roles of the players automatically.
        """

        # since only threads have a parent_id, we need a special case for these to not throw any errors.
        if str(ctx.channel.type) == "public_thread":
            if ctx.channel.parent_id not in TGArenaChannelIDs.RANKED_ARENAS:
                await ctx.send(
                    "Please only use this command in the ranked matchmaking arenas or the threads within."
                )
                ctx.command.reset_cooldown(ctx)
                return
        else:
            if ctx.channel.id not in TGArenaChannelIDs.RANKED_ARENAS:
                await ctx.send(
                    "Please only use this command in the ranked matchmaking arenas or the threads within."
                )
                ctx.command.reset_cooldown(ctx)
                return

        # to prevent any kind of abuse
        if user is ctx.author:
            await ctx.send("Don't report matches with yourself please.")
            ctx.command.reset_cooldown(ctx)
            return

        # same here
        if user.bot:
            await ctx.send("Are you trying to play a match with bots?")
            ctx.command.reset_cooldown(ctx)
            return

        def check(message):
            return (
                message.content.lower() == "y"
                and message.author == user
                and message.channel == ctx.channel
            )

        await ctx.send(
            f"The winner of the match {ctx.author.mention} vs. {user.mention} is: {ctx.author.mention}! \n{user.mention} do you agree with the results? **Type y to verify.**"
        )
        try:
            await self.bot.wait_for("message", timeout=40.0, check=check)
        except asyncio.TimeoutError:
            await ctx.send(
                "You took too long to respond! Please try reporting the match again."
            )
            return

        with open(r"./json/ranking.json", "r+") as f:
            ranking = json.load(f)

        # if someone does not exist in the file, it'll create a "profile"
        if not f"{ctx.author.id}" in ranking:
            ranking[f"{ctx.author.id}"] = {}
            ranking[f"{ctx.author.id}"]["wins"] = 0
            ranking[f"{ctx.author.id}"]["losses"] = 0
            ranking[f"{ctx.author.id}"]["elo"] = 1000
            ranking[f"{ctx.author.id}"]["matches"] = []

        if not f"{user.id}" in ranking:
            ranking[f"{user.id}"] = {}
            ranking[f"{user.id}"]["wins"] = 0
            ranking[f"{user.id}"]["losses"] = 0
            ranking[f"{user.id}"]["elo"] = 1000
            ranking[f"{user.id}"]["matches"] = []

        def expected(A, B):
            """
            The expected outcome of the match.
            """
            return 1 / (1 + 10 ** ((B - A) / 400))

        def elo(old, exp, score, k=32):
            """
            The classic elo formula.
            """
            return old + k * (score - exp)

        winnerexpected = expected(
            ranking[f"{ctx.author.id}"]["elo"], ranking[f"{user.id}"]["elo"]
        )
        loserexpected = expected(
            ranking[f"{user.id}"]["elo"], ranking[f"{ctx.author.id}"]["elo"]
        )

        # 1 is a win, 0 is a loss. 0.5 would be a draw but there are no draws here
        winnerupdate = round(elo(ranking[f"{ctx.author.id}"]["elo"], winnerexpected, 1))
        loserupdate = round(elo(ranking[f"{user.id}"]["elo"], loserexpected, 0))

        ranking[f"{ctx.author.id}"]["wins"] += 1
        ranking[f"{user.id}"]["losses"] += 1

        ranking[f"{ctx.author.id}"]["matches"].append("W")
        ranking[f"{user.id}"]["matches"].append("L")

        winnerdiff = winnerupdate - ranking[f"{ctx.author.id}"]["elo"]
        loserdiff = ranking[f"{user.id}"]["elo"] - loserupdate

        ranking[f"{ctx.author.id}"]["elo"] = winnerupdate
        ranking[f"{user.id}"]["elo"] = loserupdate

        with open(r"./json/ranking.json", "w") as f:
            json.dump(ranking, f, indent=4)

        async def updaterankroles(user):
            """
            Checks the elo of the user, and assigns the elo role based on that.
            """
            elo = ranking[f"{user.id}"]["elo"]
            elo800role = discord.utils.get(
                ctx.guild.roles, id=TGMatchmakingRoleIDs.ELO_800_ROLE
            )
            elo950role = discord.utils.get(
                ctx.guild.roles, id=TGMatchmakingRoleIDs.ELO_950_ROLE
            )
            elo1050role = discord.utils.get(
                ctx.guild.roles, id=TGMatchmakingRoleIDs.ELO_1050_ROLE
            )
            elo1200role = discord.utils.get(
                ctx.guild.roles, id=TGMatchmakingRoleIDs.ELO_1200_ROLE
            )
            elo1300role = discord.utils.get(
                ctx.guild.roles, id=TGMatchmakingRoleIDs.ELO_1300_ROLE
            )
            elomaxrole = discord.utils.get(
                ctx.guild.roles, id=TGMatchmakingRoleIDs.ELO_MAX_ROLE
            )

            elo_roles = [
                elo800role,
                elo950role,
                elo1050role,
                elo1200role,
                elo1300role,
                elomaxrole,
            ]

            # the role change only triggers if the user does not have their current elo role, so its fine to remove ALL others first and then give the new one out
            if elo < 800:
                if elo800role not in user.roles:
                    for role in elo_roles:
                        if role in user.roles:
                            await user.remove_roles(role)
                    await user.add_roles(elo800role)
            if elo < 950 and elo > 799:
                if elo950role not in user.roles:
                    for role in elo_roles:
                        if role in user.roles:
                            await user.remove_roles(role)
                    await user.add_roles(elo950role)
            if elo < 1050 and elo > 949:
                if elo1050role not in user.roles:
                    for role in elo_roles:
                        if role in user.roles:
                            await user.remove_roles(role)
                    await user.add_roles(elo1050role)
            if elo < 1200 and elo > 1049:
                if elo1200role not in user.roles:
                    for role in elo_roles:
                        if role in user.roles:
                            await user.remove_roles(role)
                    await user.add_roles(elo1200role)
            if elo < 1300 and elo > 1199:
                if elo1300role not in user.roles:
                    for role in elo_roles:
                        if role in user.roles:
                            await user.remove_roles(role)
                    await user.add_roles(elo1300role)
            if elo > 1299:
                if elomaxrole not in user.roles:
                    for role in elo_roles:
                        if role in user.roles:
                            await user.remove_roles(role)
                    await user.add_roles(elomaxrole)

        # only assigns these roles after 5 games
        if (
            ranking[f"{ctx.author.id}"]["wins"] + ranking[f"{ctx.author.id}"]["losses"]
            > 4
        ):
            await updaterankroles(ctx.author)

        if ranking[f"{user.id}"]["wins"] + ranking[f"{user.id}"]["losses"] > 4:
            await updaterankroles(user)

        await ctx.send(
            f"Game successfully reported!\n{ctx.author.mention} won!\nUpdated Elo score: {ctx.author.mention} = {winnerupdate} (+{winnerdiff}) | {user.mention} = {loserupdate} (-{loserdiff})"
        )

    @commands.command(aliases=["forcereportgame"], cooldown_after_parsing=True)
    @commands.has_permissions(administrator=True)
    @commands.cooldown(1, 41, commands.BucketType.user)
    async def forcereportmatch(self, ctx, user1: discord.Member, user2: discord.Member):
        """
        Used by mods for forcefully reporting a match, in case someone abandons it or fails to report.
        Mostly the same as reportmatch up above, with a few small tweaks.
        """

        if ctx.guild.id != GuildIDs.TRAINING_GROUNDS:
            await ctx.send(
                f"This command is only available on the {GuildNames.TRAINING_GROUNDS} Server."
            )
            return

        def check(message):
            return (
                message.content.lower() == "y"
                and message.author == ctx.author
                and message.channel == ctx.channel
            )

        await ctx.send(
            f"The winner of the match {user1.mention} vs. {user2.mention} is: {user1.mention}! \n{ctx.author.mention}, is that result correct? **Type y to verify.**"
        )
        try:
            await self.bot.wait_for("message", timeout=40.0, check=check)
        except asyncio.TimeoutError:
            await ctx.send(
                "You took too long to respond! Please try reporting the match again."
            )
            return

        with open(r"./json/ranking.json", "r+") as f:
            ranking = json.load(f)

        # if someone does not exist in the file, it'll create a "profile"
        if not f"{user1.id}" in ranking:
            ranking[f"{user1.id}"] = {}
            ranking[f"{user1.id}"]["wins"] = 0
            ranking[f"{user1.id}"]["losses"] = 0
            ranking[f"{user1.id}"]["elo"] = 1000
            ranking[f"{user1.id}"]["matches"] = []

        if not f"{user2.id}" in ranking:
            ranking[f"{user2.id}"] = {}
            ranking[f"{user2.id}"]["wins"] = 0
            ranking[f"{user2.id}"]["losses"] = 0
            ranking[f"{user2.id}"]["elo"] = 1000
            ranking[f"{user2.id}"]["matches"] = []

        def expected(A, B):
            """
            The expected outcome of the match.
            """
            return 1 / (1 + 10 ** ((B - A) / 400))

        def elo(old, exp, score, k=32):
            """
            The classic elo formula.
            """
            return old + k * (score - exp)

        winnerexpected = expected(
            ranking[f"{user1.id}"]["elo"], ranking[f"{user2.id}"]["elo"]
        )
        loserexpected = expected(
            ranking[f"{user2.id}"]["elo"], ranking[f"{user1.id}"]["elo"]
        )

        # 1 is a win, 0 is a loss. 0.5 would be a draw but there are no draws here
        winnerupdate = round(elo(ranking[f"{user1.id}"]["elo"], winnerexpected, 1))
        loserupdate = round(elo(ranking[f"{user2.id}"]["elo"], loserexpected, 0))

        winnerdiff = winnerupdate - ranking[f"{user1.id}"]["elo"]
        loserdiff = ranking[f"{user2.id}"]["elo"] - loserupdate

        ranking[f"{user1.id}"]["wins"] += 1
        ranking[f"{user2.id}"]["losses"] += 1

        ranking[f"{user1.id}"]["matches"].append("W")
        ranking[f"{user2.id}"]["matches"].append("L")

        ranking[f"{user1.id}"]["elo"] = winnerupdate
        ranking[f"{user2.id}"]["elo"] = loserupdate

        with open(r"./json/ranking.json", "w") as f:
            json.dump(ranking, f, indent=4)

        async def updaterankroles(user):
            """
            Checks the elo of the user, and assigns the elo role based on that.
            """
            elo = ranking[f"{user.id}"]["elo"]
            elo800role = discord.utils.get(
                ctx.guild.roles, id=TGMatchmakingRoleIDs.ELO_800_ROLE
            )
            elo950role = discord.utils.get(
                ctx.guild.roles, id=TGMatchmakingRoleIDs.ELO_950_ROLE
            )
            elo1050role = discord.utils.get(
                ctx.guild.roles, id=TGMatchmakingRoleIDs.ELO_1050_ROLE
            )
            elo1200role = discord.utils.get(
                ctx.guild.roles, id=TGMatchmakingRoleIDs.ELO_1200_ROLE
            )
            elo1300role = discord.utils.get(
                ctx.guild.roles, id=TGMatchmakingRoleIDs.ELO_1300_ROLE
            )
            elomaxrole = discord.utils.get(
                ctx.guild.roles, id=TGMatchmakingRoleIDs.ELO_MAX_ROLE
            )

            elo_roles = [
                elo800role,
                elo950role,
                elo1050role,
                elo1200role,
                elo1300role,
                elomaxrole,
            ]

            if elo < 800:
                if elo800role not in user.roles:
                    for role in elo_roles:
                        if role in user.roles:
                            await user.remove_roles(role)
                    await user.add_roles(elo800role)
            if elo < 950 and elo > 799:
                if elo950role not in user.roles:
                    for role in elo_roles:
                        if role in user.roles:
                            await user.remove_roles(role)
                    await user.add_roles(elo950role)
            if elo < 1050 and elo > 949:
                if elo1050role not in user.roles:
                    for role in elo_roles:
                        if role in user.roles:
                            await user.remove_roles(role)
                    await user.add_roles(elo1050role)
            if elo < 1200 and elo > 1049:
                if elo1200role not in user.roles:
                    for role in elo_roles:
                        if role in user.roles:
                            await user.remove_roles(role)
                    await user.add_roles(elo1200role)
            if elo < 1300 and elo > 1199:
                if elo1300role not in user.roles:
                    for role in elo_roles:
                        if role in user.roles:
                            await user.remove_roles(role)
                    await user.add_roles(elo1300role)
            if elo > 1299:
                if elomaxrole not in user.roles:
                    for role in elo_roles:
                        if role in user.roles:
                            await user.remove_roles(role)
                    await user.add_roles(elomaxrole)

        if ranking[f"{user1.id}"]["wins"] + ranking[f"{user1.id}"]["losses"] > 4:
            await updaterankroles(user1)

        if ranking[f"{user2.id}"]["wins"] + ranking[f"{user2.id}"]["losses"] > 4:
            await updaterankroles(user2)

        await ctx.send(
            f"Game successfully reported!\n{user1.mention} won!\nUpdated Elo score: {user1.mention} = {winnerupdate} (+{winnerdiff}) | {user2.mention} = {loserupdate} (-{loserdiff})\nGame was forcefully reported by: {ctx.author.mention}"
        )

    @commands.command(aliases=["rankedstats"])
    async def rankstats(self, ctx, member: discord.User = None):
        """
        Gets you the ranked stats of a member, or your own if you dont specify a member.
        If you get your own, you get a choice of removing/adding your ranked role.
        """
        selfcheck = False
        if member is None:
            member = ctx.author
            selfcheck = True

        with open(r"./json/ranking.json", "r") as f:
            ranking = json.load(f)

        eloscore = ranking[f"{member.id}"]["elo"]
        wins = ranking[f"{member.id}"]["wins"]
        losses = ranking[f"{member.id}"]["losses"]
        # gets the last 5 games played and reversed that list
        last5games = ranking[f"{member.id}"]["matches"][-5:]
        gamelist = "".join(last5games[::-1])

        embed = discord.Embed(title=f"Ranked stats of {str(member)}", colour=0x3498DB)
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.add_field(name="Elo score", value=eloscore, inline=True)
        embed.add_field(name="Wins", value=wins, inline=True)
        embed.add_field(name="Losses", value=losses, inline=True)
        embed.add_field(name="Last Matches", value=gamelist, inline=True)
        if (
            selfcheck is True
            and ctx.guild is not None
            and ctx.guild.id == GuildIDs.TRAINING_GROUNDS
        ):
            # i have to add the ctx.guild is not None check, otherwise we get an error in DMs
            embed.set_footer(
                text="React within 120s to turn ranked notifications on or off until the next match"
            )

        embed_message = await ctx.send(embed=embed)

        # same here
        if (
            selfcheck is True
            and ctx.guild is not None
            and ctx.guild.id == GuildIDs.TRAINING_GROUNDS
        ):
            await embed_message.add_reaction("🔔")
            await embed_message.add_reaction("🔕")

            def reaction_check(reaction, member):
                return (
                    member.id == ctx.author.id
                    and reaction.message.id == embed_message.id
                    and str(reaction.emoji) in ["🔔", "🔕"]
                )

            try:
                reaction, member = await self.bot.wait_for(
                    "reaction_add", timeout=120.0, check=reaction_check
                )
            except asyncio.TimeoutError:
                return
            else:
                if str(reaction.emoji) == "🔔":
                    elo = ranking[f"{ctx.author.id}"]["elo"]
                    if elo < 800:
                        pingrole = discord.utils.get(
                            ctx.guild.roles, id=TGMatchmakingRoleIDs.ELO_800_ROLE
                        )
                    if elo < 950 and elo > 799:
                        pingrole = discord.utils.get(
                            ctx.guild.roles, id=TGMatchmakingRoleIDs.ELO_950_ROLE
                        )
                    if elo < 1050 and elo > 949:
                        pingrole = discord.utils.get(
                            ctx.guild.roles, id=TGMatchmakingRoleIDs.ELO_1050_ROLE
                        )
                    if elo < 1200 and elo > 1049:
                        pingrole = discord.utils.get(
                            ctx.guild.roles, id=TGMatchmakingRoleIDs.ELO_1200_ROLE
                        )
                    if elo < 1300 and elo > 1199:
                        pingrole = discord.utils.get(
                            ctx.guild.roles, id=TGMatchmakingRoleIDs.ELO_1300_ROLE
                        )
                    if elo > 1299:
                        pingrole = discord.utils.get(
                            ctx.guild.roles, id=TGMatchmakingRoleIDs.ELO_MAX_ROLE
                        )
                    await ctx.author.add_roles(pingrole)
                elif str(reaction.emoji) == "🔕":
                    elo800role = discord.utils.get(
                        ctx.guild.roles, id=TGMatchmakingRoleIDs.ELO_800_ROLE
                    )
                    elo950role = discord.utils.get(
                        ctx.guild.roles, id=TGMatchmakingRoleIDs.ELO_950_ROLE
                    )
                    elo1050role = discord.utils.get(
                        ctx.guild.roles, id=TGMatchmakingRoleIDs.ELO_1050_ROLE
                    )
                    elo1200role = discord.utils.get(
                        ctx.guild.roles, id=TGMatchmakingRoleIDs.ELO_1200_ROLE
                    )
                    elo1300role = discord.utils.get(
                        ctx.guild.roles, id=TGMatchmakingRoleIDs.ELO_1300_ROLE
                    )
                    elomaxrole = discord.utils.get(
                        ctx.guild.roles, id=TGMatchmakingRoleIDs.ELO_MAX_ROLE
                    )
                    roles = [
                        elo800role,
                        elo950role,
                        elo1050role,
                        elo1200role,
                        elo1300role,
                        elomaxrole,
                    ]
                    for role in roles:
                        if role in ctx.author.roles:
                            await ctx.author.remove_roles(role)
                else:
                    pass

    @commands.command()
    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    async def leaderboard(self, ctx):
        """
        The Top 10 Players saved in the file, sorted by elo value.
        """
        with open(r"./json/ranking.json", "r") as f:
            ranking = json.load(f)

        all_userinfo = []

        for user in ranking:
            eloscore = ranking[f"{user}"]["elo"]
            wins = ranking[f"{user}"]["wins"]
            lose = ranking[f"{user}"]["losses"]
            userinfo = (user, eloscore, wins, lose)
            all_userinfo.append(userinfo)

        # sorts them by their elo score, reverses the list and gets the top 10
        all_userinfo.sort(key=lambda x: x[1])
        all_userinfo.reverse()
        all_userinfo = all_userinfo[:10]

        rawstats = []

        rank = 1

        for i in all_userinfo:
            user = i[0]
            elo = i[1]
            wins = i[2]
            lose = i[3]
            rawstats.append(f"{rank} | <@!{user}> | {elo} | {wins}/{lose}\n")
            rank += 1

        embedstats = "".join(rawstats)

        embed = discord.Embed(
            title=f"Top 10 Players of {GuildNames.TRAINING_GROUNDS} Ranked Matchmaking",
            description=f"**Rank | Username | Elo score | W/L**\n{embedstats}",
            colour=discord.Colour.blue(),
        )
        embed.set_thumbnail(url=ctx.guild.icon.url)
        embed.timestamp = discord.utils.utcnow()
        await ctx.send(embed=embed)

    # some basic error handling
    @reportmatch.error
    async def reportmatch_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.send(
                f"You are on cooldown! Try again in {round(error.retry_after)} seconds."
            )
        elif isinstance(error, commands.NoPrivateMessage):
            await ctx.send(
                f"Please only use this command in the {GuildNames.TRAINING_GROUNDS} Discord Server."
            )
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Please mention the member that you beat in the match.")
        elif isinstance(error, commands.MemberNotFound):
            await ctx.send("Please mention the member that you beat in the match.")
        else:
            raise error

    @forcereportmatch.error
    async def forcereportmatch_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("Nice try, but you don't have the permissions to do that!")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(
                "Please mention the 2 members that have played in this match. First mention the winner, second mention the loser."
            )
        elif isinstance(error, commands.MemberNotFound):
            await ctx.send(
                "Please mention the 2 members that have played in this match. First mention the winner, second mention the loser."
            )
        elif isinstance(error, commands.CommandOnCooldown):
            await ctx.send(
                f"You are on cooldown! Try again in {round(error.retry_after)} seconds."
            )
        else:
            raise error

    @rankstats.error
    async def rankstats_error(self, ctx, error):
        if isinstance(error, commands.CommandInvokeError):
            await ctx.send("This user hasn't played a ranked match yet.")
        elif isinstance(error, commands.UserNotFound):
            await ctx.send(
                "I couldn't find this member, make sure you have the right one or just leave it blank."
            )
        else:
            raise error

    @ranked.error
    async def ranked_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            if ctx.channel.id not in TGArenaChannelIDs.RANKED_ARENAS:
                await ctx.send(
                    "Please only use this command in the ranked matchmaking arenas."
                )
                return

            timestamp = discord.utils.utcnow().timestamp()

            searches = await self.get_recent_ranked_pings(timestamp)

            embed = discord.Embed(
                title="Ranked pings in the last 30 Minutes:",
                description=searches,
                colour=discord.Colour.blue(),
            )

            await ctx.send(
                f"{ctx.author.mention}, you are on cooldown for another {round((error.retry_after)/60)} minutes to use this command. \nIn the meantime, here are the most recent ranked pings:",
                embed=embed,
            )
        else:
            raise error

    @leaderboard.error
    async def leaderboard_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("Nice try, but you don't have the permissions to do that!")
        else:
            raise error


def setup(bot):
    bot.add_cog(Ranking(bot))
    print("Ranking cog loaded")

# Here is the place where the unique IDs are stored.
# Change them as you wish, but keep the names and the types.
from typing import Optional

import discord


class GetIDFunctions:
    """Contains functions for getting the correct role or channel IDs, given a guild ID."""

    @staticmethod
    def get_muted_role(guild_id: int) -> Optional[int]:
        """Gets you the muted role of a given guild."""

        if guild_id == GuildIDs.TRAINING_GROUNDS:
            return TGRoleIDs.MUTED_ROLE
        elif guild_id == GuildIDs.BATTLEGROUNDS:
            return BGRoleIDs.MUTED_ROLE
        else:
            return None

    @staticmethod
    def get_logchannel(guild_id: int) -> Optional[int]:
        """Gets you the Log Channel ID of a given guild."""

        if guild_id == GuildIDs.TRAINING_GROUNDS:
            return TGChannelIDs.LOGCHANNEL

        elif guild_id == GuildIDs.BATTLEGROUNDS:
            return BGChannelIDs.LOGCHANNEL
        else:
            return None


class GuildNames:
    """Contains strings for the Server names."""

    TRAINING_GROUNDS = "SSBU Training Grounds"
    # Just an abbreviation, used in some places.
    TG = "TG"
    BATTLEGROUNDS = "SSBU Battlegrounds"
    BG = "BG"


class GuildIDs:
    """The unique Server IDs."""

    TRAINING_GROUNDS = 739299507795132486
    BATTLEGROUNDS = 915395890775216188
    # This is done for application commands, we need a list of guild objects.
    ALL_GUILDS = [discord.Object(id=TRAINING_GROUNDS), discord.Object(id=BATTLEGROUNDS)]
    # The list of guilds where mutes/timeouts etc. carry over.
    # This is its own list, since you might want to add the bot to guilds where mutes do not apply.
    MOD_GUILDS = [TRAINING_GROUNDS, BATTLEGROUNDS]
    # This is the guild with the Mee6 Leaderboard enabled.
    # Make sure to set the visibility to public in the Mee6 Dashboard.
    LEADERBOARD_GUILD = 739299507795132486


class AdminVars:
    """Admin specific strings, like the Server Owner and Head Moderators."""

    # Used in the warn/mute/kick messages, it says: "..contact {GROUNDS_GENERALS}", thats why its worded like that.
    GROUNDS_GENERALS = "Tabuu#0720, Phxenix#1104, Parz#5811, or Fahim#2800"
    # Google doc with ban records, leave an empty string if you dont have one.
    BAN_RECORDS = "https://docs.google.com/spreadsheets/d/1EZhyKa69LWerQl0KxeVJZuLFFjBIywMRTNOPUUKyVCc/"
    # Google form for ban appeals, this will get sent to users before they get banned so they know where to appeal.
    APPEAL_FORM = "https://forms.gle/kLcpkenBDSWzCYq56"


class TournamentReminders:
    """Contains variables used in the Tournament Reminder Pings."""

    # Change this to False to disable pings.
    PING_ENABLED = True
    # The timezone the other times are based on.
    TIMEZONE = "US/Eastern"
    # The weekday as an int, keep in mind weeks start at 0 = Monday. Which means that 4 = Friday.
    SMASH_OVERSEAS_DAY = 4
    # This is set to 1 hour & 5 mins before the tournaments.
    SMASH_OVERSEAS_HOUR = 12
    SMASH_OVERSEAS_MINUTE = 55

    TRIALS_OF_SMASH_DAY = 5
    TRIALS_OF_SMASH_HOUR = 17
    TRIALS_OF_SMASH_MINUTE = 55

    DESIGN_TEAM_DAY = 6
    DESIGN_TEAM_HOUR = 12
    DESIGN_TEAM_MINUTE = 55

    LINK_REMINDER_DAY = 0
    LINK_REMINDER_HOUR = 12
    LINK_REMINDER_MINUTE = 55


class TGChannelIDs:
    """Contains Channel IDs used throughout the code, specific to the Training Grounds Server."""

    GENERAL_CHANNEL = 739299507937738849
    RULES_CHANNEL = 739299507937738843
    HELP_CHANNEL = 739299507937738847
    GENERAL_VOICE_CHAT = 765625841861394442
    ANNOUNCEMENTS_CHANNEL = 739299507937738844
    # Private channels for our Teams.
    STREAM_TEAM = 766721811962396672
    TOURNAMENT_TEAM = 812433498013958205
    DESIGN_TEAM = 762475241514991687
    # Channel for general logs.
    LOGCHANNEL = 739299509670248504
    # Channel for logging warnings specifically.
    INFRACTION_LOGS = 785970832572678194
    # The channels where the invite link filtering doesn't check.
    INVITE_LINK_WHITELIST = (
        739299509670248502,
        739299508902559811,
        739299508403437623,
        739299508197917060,
        739299509670248505,
    )
    # Channel where starboard messages get posted.
    STARBOARD_CHANNEL = 788921409648066610
    # The channels where the bot checks for reactions to put on the starboard.
    STARBOARD_LISTENING_CHANNELS = (1037574984882724895,)
    # Channel to post modmails in.
    MODMAIL_CHANNEL = 806860630073409567


class TGArenaChannelIDs:
    """Contains just the IDs of the Matchmaking Channels on the Training Grounds Server."""

    # Normal arenas, like #arena-1, etc.
    PUBLIC_ARENAS = (739299508403437626, 739299508403437627, 742190378051960932)
    # Private arenas, like #champions-arena, etc.
    PRIVATE_ARENAS = (
        801176498274172950,
        764882596118790155,
        739299509670248503,
        831673163812569108,
    )
    # Openly accessible ranked arenas, like #ranked-matchmaking-1 etc.
    OPEN_RANKED_ARENAS = (835582101926969344, 835582155446681620, 836018137119850557)
    # The ranked arenas that are closed off to certain skill ranges.
    CLOSED_RANKED_ARENAS = (
        1017912840134328411,
        1017912905498370188,
        1017912968480051250,
        1017913062591828058,
    )


class BGChannelIDs:
    """Contains Channel IDs used throughout the code, specific to the Battlegrounds Server."""

    OFF_TOPIC_CHANNEL = 915395890775216191
    LOGCHANNEL = 923018569128763482
    RULES_CHANNEL = 923018112729759794


class TGRoleIDs:
    """Contains the Role IDs used throughout the code, specific to the Training Grounds Server."""

    MOD_ROLE = 739299507816366106
    MUTED_ROLE = 739391329779581008
    # The role you get when you join the General VC.
    VOICE_ROLE = 824258210101198889
    # Role for Server Boosters.
    BOOSTER_ROLE = 739344833738571868
    # Role for Premium Members of the Server.
    PREMIUM_ROLE = 943261906238603264
    # The colour roles, reserved for server boosters.
    COLOUR_ROLES = (
        774290821842862120,
        774290823340359721,
        774290825927458816,
        774290826896605184,
        774290829128105984,
        774290831271002164,
        794726232616206378,
        794726234231013437,
        794726235518795797,
    )
    # Team roles.
    STREAMER_ROLE = 752291084058755192
    TOURNAMENT_OFFICIAL_ROLE = 739299507816366104
    TOURNAMENT_HEAD_ROLE = 1020426587251953804
    DESIGN_TEAM_ROLE = 801640022423371776
    TRIAL_DESIGN_ROLE = 974001606184017980
    PROMOTER_ROLE = 739299507799326847


class TGLevelRoleIDs:
    """Contains only the Level Role IDs, which are used to hand out Level Roles according to the Mee6 API."""

    # The default role you recieve when joining the server.
    RECRUIT_ROLE = 739299507799326843
    # Roles you get when you reach X level.
    LEVEL_10_ROLE = 827473860936990730
    LEVEL_25_ROLE = 827473868766707762
    LEVEL_50_ROLE = 827473874413289484
    LEVEL_75_ROLE = 827583894776840212
    LEVEL_100_ROLE = 927706002831323166


class TGMatchmakingRoleIDs:
    """Contains the Matchmaking Role IDs, ranked and unranked."""

    # Normal Matchmaking roles.
    SINGLES_ROLE = 739299507799326842
    DOUBLES_ROLE = 739299507799326841
    FUNNIES_ROLE = 739299507795132495
    RANKED_ROLE = 1017073005714743396
    # Ranked matchmaking roles.
    ONE_STAR = 835559992965988373
    TWO_STAR = 835559996221554728
    THREE_STAR = 835560000658341888
    FOUR_STAR = 835560003556999199
    FIVE_STAR = 835560006907985930
    GROUNDS_MASTER = 835560009810444328


class BGRoleIDs:
    """Contains the Role IDs used throughout the code, specific to the Battlegrounds Server."""

    MOD_ROLE = 915402610926825553
    MUTED_ROLE = 928985750505140264
    # The default role you recieve when joining the server.
    TRAVELLER_ROLE = 915403426811244585


class Emojis:
    """Contains some Custom Emojis."""

    # Emoji/role pairs for profile badges.
    PROFILE_BADGES = {
        "<a:tg_Singles_Winner:955967054878478367>": 739299507816366102,
        "<a:tg_Doubles_Winner:955968025570447460>": 739299507816366101,
        "<a:tg_Casual_Winner:955969250676334632>": 739299507816366100,
        "<a:tg_Crew_Winner:955969969751990362>": 753049385457287268,
        "<a:tg_MVP:959179485310230598>": 753048972947488880,
        "<a:tg_TGL:959178568468926534>": 923024434862911518,
        "<a:tg_TGL_MVP:959178568640905316>": 933441986583740456,
    }

    # Win/lose emojis for rankstats.
    # If you dont want any, just use "W" & "L".
    WIN_EMOJI = "<:rs_W:956192092454023198>"
    LOSE_EMOJI = "<:rs_L:956193883098853507>"

    # Emojis for the leaderboard ranks, make sure to have 8 with an empty one at the end.
    LEADERBOARD_EMOJIS = ["🥇", "🥈", "🥉", "💎", "💠", "🌸", "🏵️", "💮", ""]

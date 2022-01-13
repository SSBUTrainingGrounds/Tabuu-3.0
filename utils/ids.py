#this is the place where the unique IDs are stored. 
#if you are planning on running the bot yourself, you should probably change them to suit your needs

class GuildIDs:
    #the training grounds server, the "main" server
    TRAINING_GROUNDS = 739299507795132486
    #battlegrounds is the smaller spin-off server
    BATTLEGROUNDS = 915395890775216188

class TGChannelIDs:
    #general chat
    GENERAL_CHANNEL = 739299507937738849
    #rules and info
    RULES_CHANNEL = 739299507937738843
    #the general voice chat
    GENERAL_VOICE_CHAT = 765625841861394442
    #the announcements channel
    ANNOUNCEMENTS_CHANNEL = 739299507937738844
    #channel for our streamers
    STREAM_TEAM = 766721811962396672
    #channel for our tournament officials
    TOURNAMENT_TEAM = 812433498013958205
    #the channel for the logs
    LOGCHANNEL = 739299509670248504
    #log channel specifically for warnings
    INFRACTION_LOGS = 785970832572678194
    #the channels where the invite link filtering doesnt check
    INVITE_LINK_WHITELIST = (739299509670248502, 739299508902559811, 739299508403437623, 739299508197917060, 739299509670248505)
    #the starboard channel
    STARBOARD_CHANNEL = 788921409648066610
    #the channels where the bot checks for reactions to put on the starboard
    STARBOARD_LISTENING_CHANNELS = (783120161992605706)
    #channel to post modmails in
    MODMAIL_CHANNEL = 806860630073409567

class TGArenaChannelIDs:
    #the normal arenas
    PUBLIC_ARENAS = (739299508403437626, 739299508403437627, 742190378051960932)
    #private arenas, like tgl arena
    PRIVATE_ARENAS = (801176498274172950, 764882596118790155, 739299509670248503, 831673163812569108)
    #ranked matchmaking arenas
    RANKED_ARENAS = (835582101926969344, 835582155446681620, 836018137119850557)

class BGChannelIDs:
    #off-topic channel on bg
    OFF_TOPIC_CHANNEL = 915395890775216191
    #logchannel for bg
    LOGCHANNEL = 923018569128763482

class TGRoleIDs:
    #the grounds warrior role
    MOD_ROLE = 739299507816366106
    #muted role on tg
    MUTED_ROLE = 739391329779581008
    #the role you get when you join the general VC
    VOICE_ROLE = 824258210101198889
    #role server boosters get automatically
    BOOSTER_ROLE = 739344833738571868
    #the colour roles, reserved for server boosters
    COLOUR_ROLES = (774290821842862120, 774290823340359721, 774290825927458816, 774290826896605184, 774290829128105984, 774290831271002164, 794726232616206378, 794726234231013437, 794726235518795797)
    #role for our streamers
    STREAMER_ROLE = 752291084058755192
    #role for tournament officials
    TOURNAMENT_OFFICIAL_ROLE = 739299507816366104
    #role for promoters
    PROMOTER_ROLE = 739299507799326847

class TGLevelRoleIDs:
    #the default level 0 role you get when you join tg
    RECRUIT_ROLE = 739299507799326843
    #roles you get when you reach X level
    LEVEL_10_ROLE = 827473860936990730
    LEVEL_25_ROLE = 827473868766707762
    LEVEL_50_ROLE = 827473874413289484
    LEVEL_75_ROLE = 827583894776840212

class TGMatchmakingRoleIDs:
    #the normal matchmaking roles
    SINGLES_ROLE = 739299507799326842
    DOUBLES_ROLE = 739299507799326841
    FUNNIES_ROLE = 739299507795132495
    #the ranked matchmaking roles
    ELO_800_ROLE = 835559992965988373
    ELO_950_ROLE = 835559996221554728
    ELO_1050_ROLE = 835560000658341888
    ELO_1200_ROLE = 835560003556999199
    ELO_1300_ROLE = 835560006907985930
    ELO_MAX_ROLE = 835560009810444328

class BGRoleIDs:
    #the muted role
    MUTED_ROLE = 928985750505140264
    #the default role you get when you join bg
    TRAVELLER_ROLE = 915403426811244585
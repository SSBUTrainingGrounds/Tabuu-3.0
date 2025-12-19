import random
from math import floor

import discord
from discord import app_commands
from discord.ext import commands

from utils.ids import GuildIDs


class Funcommands(commands.Cog):
    """Contains the "funny" commands."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.parz_coin_value = None

    @commands.hybrid_command(aliases=["uwu"])
    @app_commands.guilds(*GuildIDs.ALL_GUILDS)
    async def tabuwu(self, ctx: commands.Context) -> None:
        """Well..."""

        messages = [
            "Stop this, you're making a fool of yourself",
            "Take a break from the internet",
            "Why do you exist?",
        ]
        await ctx.send(random.choice(messages))

    @commands.hybrid_command(aliases=["tabuujoke"])
    @app_commands.guilds(*GuildIDs.ALL_GUILDS)
    async def joke(self, ctx: commands.Context) -> None:
        """Jokes. May or may not make you laugh."""

        messages = [
            "I invented a new word! Plagiarism!",
            "?v cloud bair",
            "What's the best thing about Switzerland?\nI don't know, but the flag is a big plus.",
            "It takes guts to be an organ donor.",
            "What do you call a band of Tabuus?\nThe Blue Man Group! I'm sorry.",
            "What do you call a belt made of watches?\nA waist of time",
            "Did you hear about the new high-tech broom?\nIt's sweeping the nation!",
            "You know, working in a mirror factory is something I could really see myself doing",
            "I broke my hand last week, but on the other hand, I'm ok",
            "Did you hear about the new restaurant on the moon?\nThe food is great, but it has no atmosphere!",
            "What do sprinters eat before a race?\nNothing, they fast",
            "What's the difference between a regular joke and a dad joke?\nIt should be a-parent",
            "I took the shell off my racing snail to try to make him go faster.\nIt just made him more slug-ish",
            "Why did the chicken go to the seance?\nTo get to the other side",
            "When does a joke become a dad joke?\nWhen the punchline becomes a parent",
            "I recently bought some perfume, but it didn't smell like anything.\nIt made no scents.",
            "Why does a clock break when it gets hungry?\nIt goes back four seconds.",
            "What's the problem with eating a clock?\nIt's very time consuming!",
            "I used to love my job collecting leaves.\nI was raking it in!",
            "To the person who invented 0: Thanks for nothing!",
            "What do you call a magic dog?\nA Labra-cadabra-dor.",
            "Whats a windmill's favorite music?\nI don't know, but it's a big metal fan.",
            "How do rabbits travel?\nBy Hareplane!",
            "Where do sharks like to go on vacation?\nFinland!",
            "Where do hamsters like to go on vacation?\nHamsterdam!",
            "Where do bees like to go on vacation?\nStingapore!",
            "Where do sheep like to go on vacation?\nThe Baa-hamas!",
            "Where do cows like to go on vacation?\nMoo York!",
            "That car looks nice, but the muffler seems exhausted.",
            "What country's capital is growing the fastest?\nIreland, every day it's Dublin!",
            "I made a pencil with two erasers.\nIt was pointless.",
            "How do celebs stay cool in the summer?\nThey have many fans!",
            "What kind of car do sheep drive?\nA lamb-orghini!",
            "What did the accountants say while auditing?\nThis is taxing!",
            "Where do kings get crowned?\nOn their head!",
            "Why did king arthur go to the dentist?\nTo get his teeth crowned!",
            "Did you hear about the restaurant on the moon?\nThe food is good, but there's no atmosphere!",
            "Did you hear about the antennas that got married?\nThe wedding was good, but the reception was amazing!",
            "What is corn's favorite day?\nNew ears day!",
            "What is a cow's favorite day?\nMoo years eve!",
            "Who performs surgery underwater?\nA Sturgeon!",
            "A Friend of mine dug a hole in the garden and filled it with water.\nI think he meant well.",
            "I Ordered a chicken and an egg. I'll let you know which comes first.",
            "Did you know Cheese is the most humble of dairy products?\nIt's the most grate-ful!",
            "I was going to tell a joke about pizza, but it's a little cheesy.",
            "Singing in the shower is fun until you get soap in your mouth.\nThen it's a soap opera!",
            "I know some jokes about umbrellas, but they usually go over people's heads.",
            "What did the raindrop feel when it hit the window?\nThe Pane!",
            "What is drinking water's favorite dance?\nTap!",
            "I'm reading a book about anti-gravity.\nIt's impossible to put it down!",
            "How do we know flowers are friendly in the spring?\nThey have a lot of new buds!",
            "Can bees fly in the rain?\nNot without their yellow jacket!",
            "What is a rabbit's favorite bedtime story?\nOne with a hoppy ending!",
            "What did the doctor say to the skeleton with a temperature of 102?\nLooks like you're running a femur!",
            "Why don't skeletons like spicy food?\nThey don't have the stomach for it!",
            "How much fun is it to wash clothes?\nLoads!",
            "Why are poker players good at laundry?\nThey know how to fold em!",
            "What detergent does the little mermaid use?\nTide!",
            "How much does the combined laundry of white house weigh?\nA Washing-ton!",
            "A child saw her dad fall over while he was carrying laundry. She watched it all unfold.",
            "What's the best music for fishing?\nSomething catchy!",
            "How did the pirate get his ship so cheap?\nIt was on sail!",
            "What's the best kind of bird to work for construction?\nA crane!",
            "Do you know what cows read every day?\nThe moos-paper!",
            "Do you know what the apple said to the kangaroo?\nNothing, apples can't talk."
            "A woman Spilled her scrabble set on the road. She turned and asked me 'What's the word on the street?,",
            "What do chickens drive?\nA Coop!",
            "Where do Dogs park?\nIn the barking lot!",
            "Motherhood is a fairy tale in reverse. You start in a beautiful gown and end up cleaning up everyone's messes.",
            "Why did the cookie cry?\nHis mom was a wafer too long!",
            "What is a parade of bunnies hopping backwards called?\nA receding hare-line!",
            "What did the wind turbine say to the engineer?\nI'm a big fan of your work!",
            "How do you stop newspapers from flying away?\nUse a news anchor!",
            "Why is there so much wind in the sports stadium?\nBecause of all the fans!",
            "Why are basketball  players afraid of summer vacation?\nThey don't want to get called for travelling!",
            "What did the bees say during the heatwave?\nBoy it's swarm!",
            "What do you do if you get rejected when trying to get a job at the sunscreen company?\nReapply!",
            "What do you call a funny mountain?\nHill-arious!",
            "How does the moon cut his hair?\nE-clips-it!",
            "The baby corn asked the mama corn 'Where's pop-corn?'",
            "The waiter asked me 'Do you wanna box for your leftovers?'\nI said 'No, but I'll arm wrestle you for them.'",
            "Did you know it's illegal to laugh loudly in Hawaii?\nYou have to keep it to a-low-ha!",
            "How much room does it take for fungi to grow?\nAs mush space as necessary!",
            "||Help I'm trapped in a joke command!||",
            "Why couldn't the sesame seed leave the casino?\nIt was on a roll!",
            "How fast is milk?\nIt's pasteurize before you know it!",
            "What kind of music are balloons afraid of?\nPop music!",
            "What do you call a nervous tree?\nA sweaty palm!",
            "What role does a baby plant have in the army?\nInfant-tree!",
            "I can cut down a tree just by looking at it.\nI saw it with my own eyes!",
            "What did the loaf of bread say after helping a friend?\nIt's the yeast I could do!",
            "What did the slice of bread say to the slice of cheese?\nYou're the best thing since me!",
            "How can you spot a radical baker?\nThey always go against the grain!",
            "Why did the students go on the boat?\nTo get their scholar-ship!",
            "Why couldn't the sailors play cards?\nThe captain was standing on the deck!",
            "What do you do with a sick boat?\nTake it to the Doc!",
            "What do you call a factory that makes ok products?\nA satis-factory!",
            "Did you hear about the chocolate record player?\nIt sounds pretty sweet!",
            "I asked my Dog \"What's 2 minus 2?\nShe said nothing!",
        ]
        await ctx.send(random.choice(messages))

    @commands.hybrid_command()
    @app_commands.guilds(*GuildIDs.ALL_GUILDS)
    async def john(self, ctx: commands.Context) -> None:
        """Random excuse why you lost the last Game of Smash."""

        messages = [
            "I only lost cause my router called me mean names",
            "I only lost cause I dont care for this stupid game anymore",
            "There is no johns, I lost fair and square",
            "I only lost cause Tabuu gave me second hand smoke",
            "I only lost cause I put my foot on the desk again and it disconnected my lan",
            "I only lost cause Arto burned down my freaking house mid-set",
            "I only lost because i got weirdganted",
            "I only lost cause my slime controller got drift",
            "I only lost cause I got muted mid-set",
            "I only lost because I was trying to get pinned in #number-chain",
            "I only lost cause arto accidentally banned me from this server",
            "I only lost because I didn't DI away from plats",
            "I only lost cause spoon pinged everyone again",
            "I only lost because someone pinged %singles in our arena midmatch",
            "I only lost cause ewans bald head was blinding me",
            "I only lost cause i was distracted by ewan explaining scottish independence to me",
        ]
        await ctx.send(random.choice(messages))

    @commands.hybrid_command()
    @app_commands.guilds(*GuildIDs.ALL_GUILDS)
    async def hypemeup(self, ctx: commands.Context) -> None:
        """Hypes you up for the next Game of Smash."""

        messages = [
            "Whose better than you? \nNobody. That's who.",
            "This is your day to shine!",
            "Get ready to clip this one!",
            "Nobody does it like you!",
            "If you wanna be the best you gotta beat the best!",
            "If anyone can do it, it's you!",
            "Never back down from a challenge!",
            "Make this game legendary!",
            "Go out there and GET. THOSE. CLIPS. 👏",
            "See you in grand finals!",
            "Whoa now, leave some stocks for the rest of us!",
            "They're gonna remember this one!",
        ]
        await ctx.send(random.choice(messages))

    @commands.hybrid_command()
    @app_commands.guilds(*GuildIDs.ALL_GUILDS)
    async def slander(self, ctx: commands.Context) -> None:
        """Gives you a true story about the individual known as 'parz'."""

        messages = [
            "Fun parz fact: He has sent an email to wrigley every day for the past year and a half request “Hot dog flavored gum”",
            "Parz keeps asking me to commission a drawing of the hamburger helper glove “Sensually” choking out the pillsbury doughboy",
            "Fun Parz Fact, due to the “Toxic chemicals” in traditional soap, parz will scrub himself with hamburger helper Cheeburger maracaroni in the the shower as “It is a good cleaning agent and tastes good too”",
            "I was walking down the street with parz when we saw a kid wearing a shirt with ninja turtles on it. I tried to signal to the kid to turn and run away but it was no use. Parz already saw. He asked the kid “Who is your favorite ninja turtle?” and the kid said “Leonardo”. I quivered knowing what was about to happen. Parzs eyes went bloodshot red, veins popping out of his head. “Fuck you you little bitch.” parz shouted. And then ranted for about 10 minutes a out how Leonardo is the most racist ninja turtle.",
            "Time for some 2 sentence horror: Me and parz are at the empire state building when I see him start pressing all of the elevator buttons. “Heres how Micheal bay ruined ninja turtles” says parz.",
            "Parz spoke at my church today. He got up on stage and said “Do you think the ninja turtles saved new york all by themselves?”",
            "Parz bought a time machine on ali Express, he says he is going “Go back in time, to the first thanksgiving to put hotdogs ON the menu”",
            'Was at parzs birthday yesterday when he said "there is no reason a hot dog needs too be in a hot dog shape" before pulling out a slab of hotdog with some candles in it',
            'Parz was at a local bar trying to rizz up some women last night. Unfortunately things went south when she asked what his astrological sign was and said she was a leo. He insisted he was a "Mikey" and told her to get the fuck out of his face because he hates leo.',
            'Parz brought a controller to the mario movie and was loudly clicking it and every time mario took damage in the movie he would yell "FUCK!”',
            'In a cold sweat parz awakes. Immediately he runs to the doomsday bunker that has been hidden under his laundry corner for years and calls his therapist. "Its ok parz" says his therapist. "It was just a dream, hotcats are not real”',
            'Parz is always so energetic in the mornings and i asked him what is secret is. That\'s when parz offered me what he referred to as a "snow dog", a hot dog covered in cocaine. He insists that 3 a day combined with a glob of peter pan peanut butter is all he needs to get his daily nutrients, but when it comes to hot dogs he is still a pack a day kind of guy.',
            "Dont call a hot dog a frankfurter in front of parz though because he will make sure to let you know it was actually frankfurters monster",
            'I had to call my insurance company today and ask for a quote and the agent sounded suspiciously like parz. I provided my information and answered every question and I heard some typing noises over the span of 10 minutes of otherwise silence. Finally, the agent spoke to me about the cost I was to pay. "That will cost you the land promised to me over 2000 years ago" My heart sunk, as my fears were confirmed. Parzival owns insurance now and the fee will cost me everything',
            'I climbed the summit of a great mountain, at the peak The wisest man in the world is said to be. I walk up to him only to realize that it\'s Parzival. "It\'s you. How can it be you? Why are you up here?" I said. "Well." Parz said. "In order to main cloud one to must be like a cloud." Then he took a big puff of his teenage mutant Ninja turtle vape and said one more thing. "I see great confliction in your heart. What answer do you seek." I then ask. "Why is it that every time I eat a hotdog, my head tells me to use mustard. But my heart wants to use mayo." "That\'s because you are ignoring what the soul wants." Parz exclaims with childlike joy, clapping his hands together like a kid on Christmas. As He pulls out a jar of peter pan peanut butter and spreads it all over a hotdog. Consuming it in one bite.',
            'I was talking to Parz (also known as big P / P Omega / P daddy / phxenix alt) this morning and he asked me a important question, "Dont you love it when the shower hits just right and doesnt get your hot dog all soggy?" "What the fuck are you talking about parz" I exclaimed. But parz cant hear me because he still has his "hot dog earplugs" in.',
            'Parz looked down today and i asked him whats bugging him and he wouldnt tell me. asked his mom if she was aware of parzs recent depression and she told me that he recently took a buzzfeed quiz "Which Ninja turtle are you" and got leonardo. He hasnt been the same since.',
            "when parx heard that my fish had died, he dm’d me and told me to hop on a video call. I was hesitant at first, but he insisted he had something important to say but could only do it on call. I reluctantly agreed. As soon as I joined he was right up to the camera shoving goldfish crackers into his mouth, chewing with his mouth open so he could mouth breathe. But his fingers looked kinda weird? Almost like, they were hot dogs??? And all I could see in the background were multiple stacks of Pizza boxes and hot dog packet wrappers",
            'One day I asked Parz who was the greater painter, Leonardo or Michelangelo. "I don\'t know" said parz. "But next time I stop by the sewer I\'ll ask.”',
            "Parz the typa guy to ask for hotdog water at the local breakfast spot (they don't serve hotdogs) and when he doesn't get it go onto yelp and leave a 1 star review",
            'I asked parz why he liked hot dogs so much and he responded with: "when i was seven years old i sat on a banana and that changed my life forever”',
            "I asked Parz what the meaning of life is. He smiled, leaned back and said. \"Some of us were born to eat hotdogs. Others were born to make them. It's up to you to decide which you are. “",
            'Every time Parz makes a hot dog he insists it\'s a waste to throw the flavorful hot dog water out so he pours some swiss miss packets in and has "Hot Dog Chocolate" He likes it so much sometimes he will ask for it at restaurants but he usually just gets confused looks.',
            'Parz invited me over to his house to watch an "HD movie" on his new 4K tv. Unfortunately when i got there I realized "HD" didn\'t mean high definition and we watched a movie that was just hot dogs on a grill for 4 hours.',
            'I asked parz if he wanted to go get some baja blast pie from taco bell to which he said "My father died in a baja Blast you son of a bitch" then crawled under his bed and wont come out',
            "The Monster mash came on at my Halloween party and parz with tears in his eyes said “My father died in a monster mash you son of a bitch” and slithered away.",
            "Was driving with parz when “Rock you like a hurricane” came on the radio, Parz looked and me and said “My father Died being rocked like a hurricane you son of a bitch” then crashed the car.",
            "Partnersville that sick bastard. Finally did it. He's been talking about doing it for years but I never thought he'd actually go through with it. He finally got the surgery to turn his fingers into hot dogs, just so he can say that a glizzy is never out of arms reach for him. Please think about his wife and children in this trying time.",
            '"Faster" parz says, pointing a gun at a cashier in a 7/11. "Cant you do this yourself?" the cashier asks, slowly cutting up a hot dog and putting it in a slurpee.',
            'I noticed that parz evils diet has changed substantially in the last few months. I went to his house the other day to visit his brother and I ended up walking into his room to check if the laundry corner still existed. It did not. In its place was a large pile of pizza boxes and hot dog containers. I asked him why hot dogs and pizza. He turned to me with a smirk on his face that I knew meant no good. "Mikey doesn\'t eat his pizza without hot dogs in the crust." He said as he slipped into his Ninja turtle costume',
            'I tried to wingman parz at the bar last night, I told him how you can talk yourself up a bit and maybe stretch the truth a little and he kept trying to tell people he was "Really good friends with the ninja turtles." which didn\'t work out for him. At the end of the night he said "I know the issue" and started shaving his head because "The ninja turtles are bald”',
            'Yesterday parz was telling me about his new startup company which will make "Emergency Hot dogs" Its a cold hot dog but then you snap it like a glow stick and it heats itself up',
            'Although he claims to be a "Smart Fella" My sources show that parz is actually a "Fart Smella”',
            'Today I was driving down a small country road, when I spotted something through the trees, it was parz, eating a recently killed turkey raw. I pulled over and yelled towards him asking what in the world he was doing. He motioned like he couldn\'t hear me, and pulled out his phone. My phone buzzed and I realized he must have sent me a text, it read " proximity voice chat must not go this far. You should join me for lunch!" Seemingly from thin air parz plucked a hot dog and offered it to me. That\'s when I saw it. Parts\' back pocket was stuffed with hotdogs. What in the world! I exclaimed. "Theirs one thing you don\'t know about me, the reason I never get lunch." Parz said. "Why\'s that." I said nervously. "Why go out to eat when lunch is right here." As he swallowed 4 hotdogs whole, buns and all.',
            'I have an omelette for lunch today and parz just texted me, "I laid that egg for you". I haven\'t seen him in weeks how the fuck did he know I was eating an omelette',
            "I heard parz thought that megamind vs the doom syndicate was better than the original, and even called it the greatest movie ever.",
            'today parz told me that he would not go back in time to the first thanksgiving to take turkeys off the menu because and i quote, "It reminds me of Lunch, and i hate that shit.”',
            "In the middle of the nights i heard a scream, it was parz who woke up from a nightmare and was drenched in sweat, I asked him what happened and he told me about how for the past week he has been having nightmares where the hamburger helper was a sock rather than a glove",
            "This isnt even slander this is just parzs home address: 521 N Main St, Tonopah, NV 89049",
            'Parz Loves bananas, one time i was in his room and i thought it smelled a bit... off. I looked up in horror at hundreds, if not thousands of banana peels on the ceiling above his bed. I asked parz about this monstrosity, he said when he eats a banana he doesn\'t want to go all the way to the trash can so he throws it and it sticks to his ceiling. He calls it his "Banandelier".',
            "Big P hates Italians more than he hates helping poor people in a small east Asian village",
            "Touche and Lethal have asked parz if he wants to get mexican so many times. However, parz always says he can't go. Logically speaking, this would indicate that parz does not like Mexicans but he always insists he doesn't hate them.",
            "This recurring event has brought out the latest parzsona. I'd like you all to meet Páez, parz's Mexican Sona born out of the desire to prove he doesn't hate mexicans",
            "Quick parz lore fact, his first alternate parzonality, was an Irishman named Paddy Mcloud. He was killed in the second parz war after Miles baited him into a fortnite spike trap with a Guinness.",
            'Parz thinks he is persona 5 Joker irl because one time his grandma told him he looked like persona 5 joker. Yesterday i watched as he walked into a Walmart and yelled "ARSEN" and then lit the cushions aisle on fire. I asked him if he meant "Arson" and he said "Looking cool Parzival" and scurried off.',
            'Parz came over to my house to play smash the other night and asked to borrow my controller. He then dipped his hands in dorito dust for "Extra Grip".',
            'Today Parz "Parz" Parzival told me that he likes to put dry cereal on an extra large spoon, douse it in 1% milk, and I quote "eat that shit in one bite, cause I\'m a man.”',
            "Parz deserves to be slandered for millions of reasons, but at least he likes Bowser party",
            "This morning I snapped parz to say happy father's day to father parz and he replied with \"I ain't ya father boy, but I am your daddy\" and sent me phallic images thereafter",
            'I walk into the theater, and I look too my right. There he is, eyes bloodshot, bags under his eyes. Its Parzival. I ask parz how many times he has seen live action how to train your dragon, "None of your damn business" he replies as a stack of 13 movie tickets fall out of his pocket.',
            "Parz kept me in a straight jacket in his laundry corner, and when I awoke he told me this. \"I wasn't sure you'd wake up. I hoped you would. I wanted to show you. I don't...have anyone else. I think a lot about meteors. The purity of them. Boom! The end. Start again. The world made clean for the new man to rebuild. I was meant to be new. I was meant to be beautiful. The world would have looked to the sky and seen hope. Seen mercy. Instead they'll look up in horror because of you. You've wounded me. I give you full marks for that. But, like the man said, what doesn't kill you... just makes me stronger!\" Then he started shotgunning caprisuns",
            'Today parz told me that he had successfully merged all of his 8 parzonalities into a machine body, And with this new body he would finally bring peace. "Do you see the beauty of it? The inevitability? You rise, only to fall. You, Parz Slanderers, you are my meteor. My swift and terrible sword and the Earth will crack with the weight of your failure. Purge me from your computers; turn my own flesh against me. It means nothing! When the dust settles, the only thing living in this world, will be metal.”',
            'Parz cancelled our local to watch live action how to train your dragon because, and i quote, "This is the closest I will ever get to getting a gummer from toothless”',
            '"This tastes like toast." Touche said, mouth full of burnt toast. Oblivious as he ate his last meal. "That would be because it\'s burnt bread," Parz responded as he pulled the pin on the grenade and slid it across the floor.',
            'Everyday at lunch parz goes to the local elementary school and stands outside of the fence at recess throwing rocks at kids while standing just out of their throwing range. He says "He has to practice proper spacing in and out for the game.”',
            "Everytime parz goes to McDonald's he tries to order a hot dog because \"If they get enough requests it will get on the menu”",
            "Parzs favorite actor is jared leto",
            "Parz once curb stomped my mate for asking if he was the kazuya parz",
            'I went to church with parz on sunday and i guess he skipped breakfast because he asked me "Are you gonna eat your body of Christ" and then stole my communion cracker',
            'In 9th grade Parz got a crippling addiction to Kraft™ mac and cheese. He sat behind me in math class and everyday would chant "Kraft™ Kraft™ you\'re the Mac, You\'re the Mac for meee" before whipping out a thermos of Kraft™ mac and cheese. At the peak he would also snort about 3 Kraft™ mac and cheese dust packets a day because "Everything will taste like Kraft™ Mac and cheese". Those days are now past us but the other day at the local somebody was talking about steve crafting and parzs head snapped to look direct at them, he shuddered started drooling a little and said "DID SOMEBODY SAY, KRRAFFFTTT™?”',
            'I made the critical mistake of forgetting a controller to the local last Friday. I asked parz if I could borrow his since we are on opposite sides of the bracket (He seeded it and he was afraid of running into me after the gannon incident) he said "sure" and pulled out a controller covered in Vaseline. "What the hell" I exclamed and he said "The Vaseline removes friction allowing for tighter controls and faster reaction times. How else would i hit link downthrow into frame perfect turn around uptilt?" I informed him that he has never hit that and he DQd me for "Unsportsmanlike conduct".',
            '"I hate Parz." I said to myself Peering out the car window, I realized we were approaching the Parz factory…',
            'Me and parz went to smash con 2 years ago and when we got to the hotel I noticed his suitcase was dripping and i was like "parz why the hell is you suitcase dripping" and he said "dont you mean, my *soupcase*" as he opened it and like 15 gallons of chilli spilled out',
            'I got onto parzs computer when he wasnt around because i needed to google something and realized he has 17 different bookmarks of rule 34 of gearmo from mario galaxy. When i asked him about it he mumbled "Atleast he didnt find the body pillow" and scurried away',
            'it was a dark and stormy night, a sickening dread crept up on me like a tiger. At my window, *knock*. the vent, *knock*. My closet door, *knock* I closed my eyes, my mind and body overtaken with fear, " This is it." I thought. He\'d **found **me. After hours of driving, taking twisting turns down narrow streets, driving well past the speed limit. and even switching cars several times. I had neglected to remember one thing, he had been to my house before. "Stupid" I thought. It was then I heard it. A voice barely louder than a whisper say, " Link\'s Uptilt only barely combos out of downthrow, but you have to do a frame perfect turnaround uptilt.”',
            'Parz wears a jumbo shrimp around his wrist like a watch at all times and if you ask him what time it is he will put it up to his ear and the shrimp will "Whisper the time to him". Sometimes he will be like an hour off and he always just says "Ya Most shrimps just kinda guestimate”',
            'I got breakfast with parz at McDonald\'s yesterday, He ordered a "Sausage egg McMuffin with no ranch or tomato". I asked him why he specified not to put on ranch and tomato and he pulled out a bottle of hidden valley and a tomato from his pocket and said "I brought my own" as he soaked his sandwich in ranch',
            'Fun Parz fact, He doesnt like to compliment people or insult them which leads to some ambiguous statements so that the person he is talking to can decide wether to be offended or complimented. Yesterday When we went to an authentic Italian restaurant he walked up to some kid and said "Well well well, look who smells like muffin mix" and the kid started crying out of confusion.',
            'Today when I was at lunch getting Italian with touche and Parz, I said these words to parzival. "Longing, Rusted, Seventeen, Daybreak, Furnace, Nine, Benign, Homecoming, One, Freight Car" And he responded in Russian, and bought me lunch.',
            'Last Halloween me and parz went to a haunted house and he "Didnt piss himself". A wet spot appeared on his pants and he just continually shouted "DID DRACULA POUR WATER ON ANYBODY ELSE!??" Louder and louder until we left',
            'The other day parz was speeding through a school zone and I yelled, "Parz look out for those kids!!" He looked at me and said "dont worry touche, I know how tech" as he lightly tapped the brake petal each time he hit somebody',
            'Yesterday I was at breakfast with parz and the waiter asked how he wants his eggs done and he said "Gorilla style" and when asked what he meant by that he started running around on all fours making monkey noises',
            'Today parz was talking to me In his native language of Japanese,and he said that he was going to, and I quote. "Start burning more fossil fuels and dogs to speed up global warming, because this place too cold for someone like me.”',
            "Parz abbreviated Cyberpunk",
            'The other day parz and i went to an Italian restaurant and sent back his lasagna because "It didnt have raisins in it like his moms lasagna”',
            'Was walking through town today when parz slithered out of a storm drain and stabbed me in the foot with a pencil. I kicked him away and he complained that his "tipper dair" should have froze me or something. Weird guy.',
            "Mirror Mirror on the wall, whos the worst cloud main of them all? it isnt spargo, or MkFuego. his hair isnt blond, his eyes arent blue. But this Cloud main is sure as hell Forward Airing you. his name is Parz as you can tell. The Cloud main straight outta hell.",
            "Parz (Staring at a hotdog): i think i always knew it Would be you that killed me hotdog: *cocks gun*: it wasn't supposed to be this way",
            "Its finally over, Parz is officially dead as of 4:21 today after trying out his “Hot Dog Bong”",
            "She loves me, Parz says, taking a bite of a hot dog. She loves me not, he says taking another.",
            "Parz once had the idea to open a hot dog buffet, Unfortunately it closed after 24 hours because parz just sat at the buffet eating all the hot dogs.",
            "Went to outback steakhouse with parz where he requested a Bone in hot dog in the shape of a tbone steak. Surprisingly, they actually had it and parz ate it in 3 bites.",
            "Parz slams a 20$ bill down and says “How about something with a little more Pep” The pianist at the funeral is confused.",
            "I asked parz if he stole 20$ from my wallet. “No he says sipping a 3$ cup of coffee. I open the glove box and 17$ worth of hot dogs fall out.",
            "Parz made me his famous 7 layer chip dip today, here are all 7 layers if you want to try it yourself: waffles, bacon, hot sauce, blood of the innocent, butter, cream cheese and tomato bisque.",
            "I dated parz once. I could never get through to him, past his defences you could say. He would always win arguments through such cruel measures like <:InputRight:814136798074765313> <:InputA:740288923418493008> or <:InputUp:814132654361411635> <:InputB:740288923368161407>. He would NEVER let ANYONE get close to him, always pushing even his closest family members back to ledge and into what he liked to call “optimal back air range”. I think the final straw in our relationship was when i thought that i had finally won, finally gotten through to him. Turns out he did have limits and boy did i break them. I had broken his limit, his limit break, his limit was all broken. He went blue with rage and did want he called a “ztd” and i “got clipped on his twitch”. That was the last time i spoke to parz, he needs some serious help and i wish him the best.",
            "Sometimes feel like a piece of shit, But then reminded myself that by age 7 parz was in jail for burning down 3 McDonald's restaurants because, and i quote, \"they didn't have cloud bair on the menu\" and then didn't feel so bad about myself.",
        ]

        await ctx.send(random.choice(messages))

    @commands.hybrid_command(name="8ball")
    @app_commands.guilds(*GuildIDs.ALL_GUILDS)
    @app_commands.describe(question="Your question to the magic 8ball.")
    async def _8ball(self, ctx: commands.Context, *, question: str = None) -> None:
        """Ask the magic 8ball."""

        if question is None:
            await ctx.send("Please input a question for the magic 8-ball.")
            return

        messages = [
            "It is certain.",
            "It is decidedly so.",
            "Without a doubt.",
            "Yes - definitely.",
            "You may rely on it.",
            "As I see it, yes.",
            "Most likely.",
            "Outlook good.",
            "Yes.",
            "Signs point to yes.",
            "Reply hazy, try again.",
            "Ask again later.",
            "Better not tell you now.",
            "Cannot predict now.",
            "Concentrate and ask again.",
            "Don't count on it.",
            "My reply is no.",
            "My sources say no.",
            "Outlook not so good.",
            "Very doubtful.",
        ]

        question = discord.utils.remove_markdown(question)

        try:
            await ctx.send(
                f"{ctx.author.mention} asked: `{question}`:\n{random.choice(messages)}"
            )
        # This is in the case if a user inputs a question with more than 2000 chars in length,
        # the bot cant respond with the question.
        except discord.HTTPException:
            await ctx.send(random.choice(messages))

    @commands.hybrid_command()
    @app_commands.guilds(*GuildIDs.ALL_GUILDS)
    @app_commands.describe(question="Your question.")
    async def who(self, ctx: commands.Context, *, question: str = None) -> None:
        """Returns a random online member of the server as a response."""

        if ctx.guild is None:
            await ctx.send("You cannot use this command in my DM channel.")
            return

        if question is None:
            await ctx.send("Please input a question so I can look for the right user.")
            return

        question = discord.utils.remove_markdown(question)

        # Only gets online members.
        online_members = [
            member
            for member in ctx.guild.members
            if member.status != discord.Status.offline
        ]
        user = random.choice(online_members)
        try:
            await ctx.send(
                f"{ctx.author.mention} asked: `Who {question}`:\n{discord.utils.escape_markdown(str(user))}"
            )
        except discord.HTTPException:
            await ctx.send(discord.utils.escape_markdown(str(user)))

    @commands.hybrid_command(aliases=["ship", "relationship"])
    @app_commands.guilds(*GuildIDs.ALL_GUILDS)
    @app_commands.describe(
        user1="The first user.",
        user2="The second user, leave empty to compare to yourself.",
    )
    async def friendship(
        self, ctx: commands.Context, user1: discord.User, user2: discord.User = None
    ) -> None:
        """The friendship status between two users."""
        if not user2:
            user2 = ctx.author

        # The relationship between you and yourself should always be 100, of course.
        rating = 100 if user1.id == user2.id else (user1.id + user2.id) % 100

        message = ("█" * floor(rating / 5)).ljust(20, "░")

        emojis = [
            "😡",
            "😠",
            "🙄",
            "😒",
            "😐",
            "🙂",
            "😀",
            "😄",
            "😁",
            "🥰",
            "😍",
        ]

        await ctx.send(
            f"The friendship status of {discord.utils.escape_markdown(user1.name)} "
            f"and {discord.utils.escape_markdown(user2.name)} is...\n"
            f"**{message} - {rating}%** {emojis[floor(rating / 10)] * 3}"
        )

    @commands.hybrid_command()
    @app_commands.guilds(*GuildIDs.ALL_GUILDS)
    async def parzcoin(self, ctx: commands.Context) -> None:
        """The current value of Parz Coin."""

        # It will reset every time the bot is restarted, not bothering with persistent storage.
        if not self.parz_coin_value:
            self.parz_coin_value = 500.0

        floor = -75
        ceiling = 150

        if self.parz_coin_value > 999.0:
            ceiling = -40
        elif self.parz_coin_value < 100:
            floor = 80

        # Need the weights for an even distribution of ups and downs
        weights = [2 if i < 0 else 1 for i in range(floor, ceiling + 1)]

        percent = random.choices(range(floor, ceiling + 1), weights=weights, k=1)[0]

        self.parz_coin_value *= 1 + (percent / 100.0)

        if percent > 0:
            print_message = f"UP 📈 {percent}%"
        elif percent < 0:
            print_message = f"DOWN 📉 {abs(percent)}%"
        else:
            print_message = "UNCHANGED 😐"

        await ctx.send(
            f"Parz Coin is **{print_message}** since the last time!\nCurrent value: 0.{self.parz_coin_value:015.0f} USD"
        )


async def setup(bot) -> None:
    await bot.add_cog(Funcommands(bot))
    print("Funcommands cog loaded")

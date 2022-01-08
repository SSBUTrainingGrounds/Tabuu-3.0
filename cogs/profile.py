import discord
from discord.ext import commands, tasks
import json

#
#this file here contains the various new profile commands
#


class Profile(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    #matches the input to one or multiple characters and returns their emoji
    def match_character(self, input):
        with open(r'./files/characters.json', 'r') as f:
            characters = json.load(f)

        output_characters = []

        if input is None:
            return output_characters

        input = input.lower()
        input_characters = input.split(",")
        
        for i_char in input_characters:
            #this strips leading and trailing whitespaces
            i_char = i_char.lstrip()

            for match_char in characters["Characters"]:
                if i_char == match_char["name"] or i_char == match_char["id"] or i_char in match_char["aliases"]:
                    if match_char["emoji"] not in output_characters:
                        output_characters.append(match_char["emoji"])

        return output_characters
        

    def make_new_profile(self, user: discord.User):
        with open(r'./json/profile.json', 'r') as f:
            profiles = json.load(f)

        if not f'{user.id}' in profiles:
            profiles[f'{user.id}'] = {}
            profiles[f'{user.id}']['tag'] = f"{str(user)}"
            profiles[f'{user.id}']['region'] = ""
            profiles[f'{user.id}']['mains'] = []
            profiles[f'{user.id}']['secondaries'] = []
            profiles[f'{user.id}']['pockets'] = []
            profiles[f'{user.id}']['note'] = ""
            profiles[f'{user.id}']['colour'] = 0

            with open(r'./json/profile.json', 'w') as f:
                json.dump(profiles, f, indent=4)


    @commands.command(aliases=["smashprofile", "profileinfo", "userprofile"])
    async def profile(self, ctx, user: discord.User = None):
        if user is None:
            user = ctx.author

        with open(r'./json/profile.json', 'r') as f:
            profiles = json.load(f)

        if not f'{user.id}' in profiles:
            await ctx.send("This user did not set up their profile yet.")
            return

        tag = profiles[f'{user.id}']['tag']
        region = profiles[f'{user.id}']['region']
        mains = " ".join(profiles[f'{user.id}']['mains'])
        secondaries = " ".join(profiles[f'{user.id}']['secondaries'])
        pockets = " ".join(profiles[f'{user.id}']['pockets'])
        note = profiles[f'{user.id}']['note']
        colour = profiles[f'{user.id}']['colour']

        embed = discord.Embed(title=f"Smash profile of {str(user)}", colour=colour)
        embed.set_thumbnail(url=user.display_avatar.url)

        embed.add_field(name="Tag", value=tag, inline=True)

        if region != "":
            embed.add_field(name="Region", value=region, inline=True)
        if mains != "":
            embed.add_field(name="Mains", value=mains, inline=True)
        if secondaries != "":
            embed.add_field(name="Secondaries", value=secondaries, inline=True)
        if pockets != "":
            embed.add_field(name="Pockets", value=pockets, inline=True)
        if note != "":
            embed.add_field(name="Note", value=note, inline=True)

        await ctx.send(embed=embed)
        

    #deletes your profile from the json file
    @commands.command()
    async def deleteprofile(self, ctx):
        with open(r'./json/profile.json', 'r') as f:
            profiles = json.load(f)

        if not f'{ctx.author.id}' in profiles:
            await ctx.send("You have no profile saved.")
            return

        del profiles[f'{ctx.author.id}']
        
        with open(r'./json/profile.json', 'w') as f:
            json.dump(profiles, f, indent=4)

        await ctx.send(f"{ctx.author.mention}, I have successfully deleted your profile.")

    #deletes another users profile, just in case
    @commands.command()
    @commands.has_permissions(administrator=True)  
    async def forcedeleteprofile(self, ctx, user: discord.User):
        with open(r'./json/profile.json', 'r') as f:
            profiles = json.load(f)
        
        if not f'{user.id}' in profiles:
            await ctx.send("This user has no profile saved.")
            return

        del profiles[f'{user.id}']

        with open(r'./json/profile.json', 'w') as f:
            json.dump(profiles, f, indent=4)

        await ctx.send(f"{ctx.author.mention}, I have successfully deleted the profile of {str(user)}.")


    #these commands set your characters in your profile
    @commands.command(aliases=["main", "setmain", "spmains", "profilemains"])
    async def mains(self, ctx, *, input = None):
        #only getting the first 7 chars, think thats a very generous cutoff
        chars = self.match_character(input)[:7]

        self.make_new_profile(ctx.author)

        with open(r'./json/profile.json', 'r') as f:
            profiles = json.load(f)

        profiles[f'{ctx.author.id}']['mains'] = chars
        
        with open(r'./json/profile.json', 'w') as f:
            json.dump(profiles, f, indent=4)

        if input is None:
            await ctx.send(f"{ctx.author.mention}, I have deleted your mains.")
        else:
            await ctx.send(f"{ctx.author.mention}, I have set your mains to: " + " ".join(chars))

    @commands.command(aliases=["secondary", "setsecondary", "spsecondaries", "profilesecondaries"])
    async def secondaries(self, ctx, *, input = None):
        chars = self.match_character(input)[:7]

        self.make_new_profile(ctx.author)

        with open(r'./json/profile.json', 'r') as f:
            profiles = json.load(f)

        profiles[f'{ctx.author.id}']['secondaries'] = chars
        
        with open(r'./json/profile.json', 'w') as f:
            json.dump(profiles, f, indent=4)

        if input is None:
            await ctx.send(f"{ctx.author.mention}, I have deleted your secondaries.")
        else:
            await ctx.send(f"{ctx.author.mention}, I have set your secondaries to: " + " ".join(chars))

    @commands.command(aliases=["pocket", "setpocket", "sppockets", "profilepockets"])
    async def pockets(self, ctx, *, input = None):
        #since you can have some more pockets, i put it at 10 max. there could be a max of around 25 per embed field however
        chars = self.match_character(input)[:10]

        self.make_new_profile(ctx.author)

        with open(r'./json/profile.json', 'r') as f:
            profiles = json.load(f)

        profiles[f'{ctx.author.id}']['pockets'] = chars
        
        with open(r'./json/profile.json', 'w') as f:
            json.dump(profiles, f, indent=4)

        if input is None:
            await ctx.send(f"{ctx.author.mention}, I have deleted your pockets.")
        else:
            await ctx.send(f"{ctx.author.mention}, I have set your pockets to: " + " ".join(chars))


    #sets your tag in your profile
    @commands.command(aliases=["smashtag", "sptag", "settag"])
    async def tag(self, ctx, *, input = None):
        #the default tag is just your discord tag
        if input is None:
            input = str(ctx.author)
        
        #think 30 chars for a tag is fair
        input = input[:30]

        self.make_new_profile(ctx.author)

        with open(r'./json/profile.json', 'r') as f:
            profiles = json.load(f)

        profiles[f'{ctx.author.id}']['tag'] = input
        
        with open(r'./json/profile.json', 'w') as f:
            json.dump(profiles, f, indent=4)

        await ctx.send(f"{ctx.author.mention}, I have set your tag to: `{input}`")


    #matches your input to a general region
    @commands.command(aliases=["setregion", "spregion", "country"])
    async def region(self, ctx, *, input = None):
        if input is None:
            input = ""

        #tried to be as broad as possible here, hope thats enough
        if input.lower() in ("na", "north america", "usa", "us", "canada", "latin america", "america"):
            input = "North America"
        elif input.lower() in ("east coast", "us east", "east", "midwest", "na east", "canada east"):
            input = "NA East"
        elif input.lower() in ("west coast", "us west", "west", "na west", "canada west"):
            input = "NA West"
        elif input.lower() in ("mexico", "south", "us south", "na south", "texas", "southern"):
            input = "NA South"
        elif input.lower() in ("sa", "brazil", "argentina", "south america", "chile", "peru"):
            input = "South America"
        elif input.lower() in ("eu", "europe", "uk", "england", "france", "germany"):
            input = "Europe"
        elif input.lower() in ("asia", "sea", "china", "japan", "india", "middle east"):
            input = "Asia"
        elif input.lower() in ("africa", "south africa", "egypt"):
            input = "Africa"
        elif input.lower() in ("australia", "new zealand", "nz", "au", "oceania"):
            input = "Oceania"
        elif input == "":
            pass
        else:
            await ctx.send("Please choose a valid region. Example: `%region Europe`")
            return

        self.make_new_profile(ctx.author)

        with open(r'./json/profile.json', 'r') as f:
            profiles = json.load(f)

        profiles[f'{ctx.author.id}']['region'] = input
        
        with open(r'./json/profile.json', 'w') as f:
            json.dump(profiles, f, indent=4)

        if input == "":
            await ctx.send(f"{ctx.author.mention}, I have deleted your region.")
        else:
            await ctx.send(f"{ctx.author.mention}, I have set your region to: `{input}`")


    #sets up a note on your profile
    @commands.command(aliases=["setnote", "spnote"])
    async def note(self, ctx, *, input = None):
        if input is None:
            input = ""

        #for a note, 150 chars seem enough to me
        input = input[:150]

        self.make_new_profile(ctx.author)

        with open(r'./json/profile.json', 'r') as f:
            profiles = json.load(f)

        profiles[f'{ctx.author.id}']['note'] = input
        
        with open(r'./json/profile.json', 'w') as f:
            json.dump(profiles, f, indent=4) 

        if input == "":
            await ctx.send(f"{ctx.author.mention}, I have deleted your note.")
        else:
            await ctx.send(f"{ctx.author.mention}, I have set your note to: `{input}`")


    #sets a colour for their profile in a hex value format
    @commands.command(aliases=["color", "spcolour", "spcolor", "setcolour", "setcolor"])
    async def colour(self, ctx, input):
        #hex colour codes are 7 digits long and start with #
        if not input.startswith("#") or not len(input) == 7:
            await ctx.send("Please choose a valid hex colour code. Example: `%colour #8a0f84`")
            return

        input = input.replace("#", "0x")

        try:
            colour = int(input, 16)
        except ValueError:
            await ctx.send("Please choose a valid hex colour code. Example: `%colour #8a0f84`")
            return

        self.make_new_profile(ctx.author)
        
        with open(r'./json/profile.json', 'r') as f:
            profiles = json.load(f)

        profiles[f'{ctx.author.id}']['colour'] = colour
        
        with open(r'./json/profile.json', 'w') as f:
            json.dump(profiles, f, indent=4) 

        await ctx.send(f"{ctx.author.mention}, I have set your colour to: `{input}`")


    #some basic error handling for the above
    @profile.error
    async def profile_error(self, ctx, error):
        if isinstance(error, commands.UserNotFound):
            await ctx.send("I couldn't find this user, make sure you have the right one or just leave it blank.")
        else:
            raise error

    @forcedeleteprofile.error
    async def forcedeleteprofile_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("Nice try, but you don't have the permissions to do that!")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Please specify which profile to delete.")
        elif isinstance(error, commands.UserNotFound):
            await ctx.send("I couldn't find this user, make sure you have the right one.")
        else:
            raise error
        

    @colour.error
    async def colour_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Please choose a valid hex colour code. Example: `%colour #8a0f84`")
        else:
            raise error



def setup(bot):
    bot.add_cog(Profile(bot))
    print("Profile cog loaded")
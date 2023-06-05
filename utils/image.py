import io

import discord
from colorthief import ColorThief


async def get_dominant_colour(image: discord.Asset) -> discord.Colour:
    """Gets the dominant colour of an image, and returns it as a discord.Colour object."""
    img_bytes = await image.read()

    colour_thief = ColorThief(io.BytesIO(img_bytes))

    dominant_colour = colour_thief.get_color(quality=1)

    colour = discord.Colour.from_rgb(*dominant_colour)

    return colour

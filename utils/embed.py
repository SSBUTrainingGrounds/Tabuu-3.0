import discord


def add_attachments_to_embed(embed: discord.Embed, message: discord.Message):
    """
    Adds the message message attachments to the embed in a neat way.
    """
    if message.attachments:
        if len(message.attachments) == 1:
            if message.attachments[0].url.endswith((".jpg", ".png", ".jpeg", ".gif")):
                embed.set_image(url=message.attachments[0].proxy_url)
                embed.add_field(name="Attachment:", value="See below.", inline=False)
            else:
                embed.add_field(
                    name="Attachment:",
                    value=message.attachments[0].url,
                    inline=False,
                )
        else:
            for i, x in enumerate(message.attachments, start=1):
                if not embed.image:
                    if x.url.endswith((".jpg", ".png", ".jpeg", ".gif")):
                        embed.set_image(url=x.proxy_url)

                embed.add_field(
                    name=f"Attachment ({i}/{len(message.attachments)}):",
                    value=x.url,
                    inline=False,
                )

    if message.stickers:
        if not embed.image:
            embed.set_image(url=message.stickers[0].url)
            embed.add_field(name="Sticker:", value="See below.", inline=False)
        else:
            embed.add_field(name="Sticker:", value=f"{message.stickers[0].url}")

    return embed

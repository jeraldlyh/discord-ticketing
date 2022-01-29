import discord
import os
import string


def format_name(author: discord.abc.User):
    """Remove readable ASCII characters"""

    name = author.name
    updated_name = ""

    for letter in name:
        if letter in string.ascii_letters + string.digits:
            updated_name += letter

    if not updated_name:
        updated_name = "null"

    updated_name += f" - {author.discriminator}"
    return updated_name


def format_info(guild: discord.Guild, message: discord.Message):
    """Retrieves information about a member of a guild"""

    user = message.author
    member = guild.get_member(user.id)
    print(user, member)
    avatar_url = user.avatar_url
    color = 0

    if member:
        roles = sorted(member.roles, key=lambda r: r.position)
        role_names = (
            ", ".join([r.name for r in roles if r.name != "@everyone"]) or "None"
        )
        member_number = (
            sorted(guild.members, key=lambda m: m.joined_at).index(member) + 1
        )

        for role in roles:
            if str(role.color) != "#000000":
                color = role.color

    embed = discord.Embed(colour=color, description="Modmail thread started.")
    embed.set_thumbnail(url=avatar_url)
    embed.set_author(name=user, icon_url=guild.icon_url)

    if member:
        embed.add_field(name="Member No.", value=str(member_number), inline=True)
        embed.add_field(name="Nickname", value=member.mention, inline=True)
        embed.add_field(name="Roles", value=role_names, inline=True)
    else:
        embed.add_field(
            name="Something went wrong",
            value="Unable to retrieve information about user in server",
        )

    return embed

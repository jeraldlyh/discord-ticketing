import discord
import datetime

from typing import Union


def command_embed(description="", error=False):
    embed = discord.Embed(title="❌ Command Error" if error else "✅ Command Processed")
    embed.description = description
    embed.color = discord.Colour.red() if error else discord.Colour.green()
    return embed


def award_embed(description="", error=False):
    embed = discord.Embed(title="❌ Points Rejected" if error else "✅ Points Processed")
    embed.description = description
    embed.color = discord.Colour.red() if error else discord.Colour.green()
    return embed


def blocked_embed():
    embed = discord.Embed(title="Message not processed!", color=discord.Color.red())
    embed.description = "You have been blocked from using modmail."
    return embed


def close_modmail_embed(user: str, moderator: Union[discord.User, discord.Member], timestamp: datetime.datetime, is_log=False):
    title = f"{user}'s Thread Closed" if is_log else "Thread Closed"

    embed = discord.Embed(title=title)
    embed.description = f"{moderator} has closed this modmail session."
    embed.color = discord.Color.red() if is_log else discord.Color(0xFFD700)
    embed.timestamp = timestamp
    return embed

def insufficient_points_embed(user: discord.Member):
    embed = command_embed(description=f"{user.mention} does not have sufficient points", error=True)

    return embed

def warning_embed(user: discord.Member):
    embed = discord.Embed(color=discord.Color.red())
    embed.description = f"{user.mention} attempted to share a flag"

    return embed
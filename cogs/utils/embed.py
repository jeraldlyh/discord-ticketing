import discord


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


def close_modmail_embed(user, moderator, is_log=False):
    title = f"{user}'s Thread Closed" if is_log else "Thread Closed"

    embed = discord.Embed(title=title)
    embed.description = f"{moderator} has closed this modmail session."
    embed.color = discord.Color.red() if is_log else discord.Color(0xFFD700)
    return embed

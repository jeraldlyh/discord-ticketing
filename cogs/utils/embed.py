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

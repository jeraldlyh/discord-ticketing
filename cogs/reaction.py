import discord
import os
import asyncio

from discord.ext import commands
from typing import Union
from cogs.utils.embed import command_embed, insufficient_points_embed
from cogs.firebase import Firestore


class Reaction(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.firestore = Firestore()

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def react(self, ctx: commands.Context):
        guild = discord.utils.get(self.bot.guilds, id=int(os.getenv("GUILD_ID")))
        embed = discord.Embed(title=f"{guild.name}'s Modmail", color=discord.Color.gold())
        roles = await self.firestore.get_all_roles()

        description = ""
        for role in roles:
            role_mention = discord.utils.get(ctx.guild.roles, id=int(role["id"])).mention
            description += f"React with {role['emoji']} to raise a ticket for {role_mention}\n"

        embed.description = description
        message = await ctx.send(embed=embed)

        await asyncio.gather(*[message.add_reaction(role["emoji"]) for role in roles])
        await self.firestore.register_reaction_message(str(message.id))

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction: discord.Reaction, user: Union[discord.Member, discord.User]):
        message = reaction.message
        reaction_message = await self.firestore.get_reaction_message(str(message.id))

        if reaction_message is None or user.bot:
            print("Exiting", reaction_message, user.bot)
            return

        await message.remove_reaction(reaction.emoji, user)
        
        embed = discord.Embed(title="Thanks for the message!")
        embed.description = "You've just requested"
        embed.color = discord.Color.green()
        role = await self.firestore.get_role_by_emoji(reaction.emoji)

        embed.add_field(name="Category", value=role["name"])
        embed.add_field(name="Time Limit", value=60)

        return await user.send(embed=embed)

# Adding the cog to main script
def setup(bot):
    bot.add_cog(Reaction(bot))

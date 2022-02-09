import discord
import os

from discord.ext import commands
from emoji import UNICODE_EMOJI
from typing import List
from cogs.utils.embed import command_embed, insufficient_points_embed
from cogs.firebase import Firestore


class Role(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.firestore = Firestore()

    @commands.has_any_role("Server Support")
    @commands.command()
    async def add_role(self, ctx: commands.Context, role: discord.Role, emoji: str):
        role_id = str(role.id)
        role_doc = await self.firestore.get_role_doc(role_id)

        if role_doc is not None:
            embed = command_embed(description=f"{role.name} role already exists with a reaction of {role_doc['emoji']}", error=True)
            return await ctx.send(embed=embed)
        
        if emoji not in UNICODE_EMOJI["en"]:
            embed = command_embed(description=f"{emoji} is not an emoji", error=True)
            return await ctx.send(embed=embed)
        
        await self.firestore.create_role(role_id, role.name, emoji)
        embed = command_embed(description=f"Successfully created a role reaction with {emoji}")
        return await ctx.send(embed=embed)

    @commands.has_any_role("Server Support")
    @commands.command()
    async def delete_role(self, ctx: commands.Context, role: discord.Role):
        role_id = str(role.id)
        role_doc = await self.firestore.get_role_doc(role_id)

        if role_doc is None:
            embed = command_embed(description=f"{role.name} role does not exist", error=True)
            return await ctx.send(embed=embed)
        
        await self.firestore.delete_role(role_id)
        embed = command_embed(description=f"Successfully deleted {role.name}")
        return await ctx.send(embed=embed)



# Adding the cog to main script
def setup(bot):
    bot.add_cog(Role(bot))

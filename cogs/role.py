import discord
import os

from discord.ext import commands
from discord.commands import slash_command
from emoji import UNICODE_EMOJI
from typing import List
from cogs.utils.embed import command_embed, insufficient_points_embed
from cogs.firebase import Firestore


class Role(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.firestore = Firestore()

    @slash_command(
        guild_ids=[int(os.getenv("GUILD_ID"))],
        name="add_role",
        description="Register a role with specified emoji that listens to reaction",
    )
    @commands.has_any_role("Server Support")
    async def add_role(self, ctx: commands.Context, role: discord.Role, emoji: str):
        role_id = str(role.id)
        role_docs = await self.firestore.get_all_roles()

        for role_doc in role_docs:
            if role_doc["id"] == role_id or role_doc["emoji"] == emoji:
                role_mention = discord.utils.get(
                    ctx.guild.roles, id=int(role_doc["id"])
                ).mention
                embed = command_embed(
                    description=f"{role_mention} already exists with a reaction of {role_doc['emoji']}",
                    error=True,
                )
                return await ctx.send(embed=embed)

        if emoji not in UNICODE_EMOJI["en"]:
            embed = command_embed(description=f"{emoji} is not an emoji", error=True)
            return await ctx.send(embed=embed)

        await self.firestore.create_role(role_id, role.name, emoji)
        embed = command_embed(
            description=f"Successfully created a role reaction with {emoji}"
        )
        return await ctx.send(embed=embed)

    @slash_command(
        guild_ids=[int(os.getenv("GUILD_ID"))],
        name="remove_role",
        description="Delete a role that listens to reaction",
    )
    @commands.has_any_role("Server Support")
    async def delete_role(self, ctx: commands.Context, role: discord.Role):
        role_id = str(role.id)
        role_doc = await self.firestore.get_role_doc(role_id)

        if role_doc is None:
            embed = command_embed(
                description=f"{role.name} role does not exist", error=True
            )
            return await ctx.send(embed=embed)

        await self.firestore.delete_role(role_id)
        embed = command_embed(description=f"Successfully deleted {role.name}")
        return await ctx.send(embed=embed)


# Adding the cog to main script
def setup(bot):
    bot.add_cog(Role(bot))

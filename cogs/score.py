import discord
import os

from discord.ext import commands
from cogs.utils.embed import command_embed, insufficient_points_embed
from cogs.firebase import Firestore


class Score(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.firestore = Firestore()

    @commands.has_any_role("Sponsor")
    @commands.command()
    async def add(self, ctx: commands.Context, user: discord.Member):
        username = user.name
        is_user_exist = await self.firestore.is_user_exist(username)

        if not is_user_exist:
            await self.firestore.create_user(username)
        
        await self.firestore.add_points(username)
        embed = command_embed(
            description=f"Successfully added 1 point to {user.mention}"
        )
        return await ctx.send(embed=embed)

    @commands.has_any_role("Sponsor")
    @commands.command()
    async def minus(self, ctx: commands.Context, user: discord.Member):
        try:
            username = user.name
            is_user_exist = await self.firestore.is_user_exist(username)

            if not is_user_exist:
                await self.firestore.create_user(username)
                return await ctx.send(embed=insufficient_points_embed(user))

            await self.firestore.minus_points(username)
            embed = command_embed(
                description=f"Successfully deducted 1 point from {user.mention}"
            )
            return await ctx.send(embed=embed)
        except ValueError:
            return await ctx.send(embed=insufficient_points_embed(user))
    
    @commands.command()
    @commands.has_any_role("Server Support")
    async def help(self, ctx: commands.Context):
        if ctx.message.channel.name != os.getenv("LOGGING_CHANNEL"):
            logs = discord.utils.get(ctx.message.guild.channels, name=os.getenv("LOGGING_CHANNEL"))
            embed = command_embed(
                description=f"{ctx.message.author.mention} Commands can only be used in {logs.mention}",
                error=True
            )
            return await ctx.send(embed=embed)
        
        embed = discord.Embed(
            title="Available Commands",
            color=0xA53636,
        )
        for command in self.bot.commands:
            print(command, command.help, command.name)

        embed.description=("\n".join([str(command) + " - " + str(command.help) for command in self.bot.commands]))
        await ctx.send(embed=embed)


# Adding the cog to main script
def setup(bot):
    bot.add_cog(Score(bot))

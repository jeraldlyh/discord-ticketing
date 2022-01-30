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
    
    @commands.command()
    async def list(self, ctx: commands.Context):
        user_data = await self.firestore.get_all_users()
        field_value_count = 0
        username_value = ""
        points_value = ""
        index = 0

        while (index < len(user_data)):
            user = user_data[index]
            username = str(user["username"])
            points = str(user["points"])

            field_value_count += max(len(username), len(points))

            # Reset if it exceeds embed field value limit of 1024 characters
            if (field_value_count >= 1000):
                self.send_scoreboard(ctx, username_value, points_value)
                username_value = ""
                points_value = ""
                index -= 1

            username_value += username
            points_value += points
            index += 1

        # Send leftover buffer
        await self.send_scoreboard(ctx, username_value, points_value)
    
    async def send_scoreboard(self, ctx: commands.Context, usernames, points):
        embed = discord.Embed(title="Scoreboard")

        embed.add_field(name="Username", value=usernames, inline=True)
        embed.add_field(name="Points", value=points, inline=True)
        return await ctx.send(embed=embed)



# Adding the cog to main script
def setup(bot):
    bot.add_cog(Score(bot))

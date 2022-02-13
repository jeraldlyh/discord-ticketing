import discord
import os

from discord.ext import commands
from discord.commands import slash_command
from cogs.utils.embed import command_embed, insufficient_points_embed
from cogs.firebase import Firestore


class Score(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.firestore = Firestore()

    @slash_command(
        guild_ids=[int(os.getenv("GUILD_ID"))],
        name="add",
        description="Award a user up to 5 points",
    )
    @commands.has_any_role("Sponsor")
    async def _add(self, ctx, user: discord.Member, points: int = 1):
        """Award a user with points up to 5 points"""

        try:
            username = user.name
            is_user_exist = await self.firestore.is_user_exist(username)

            if not is_user_exist:
                await self.firestore.create_user(username)

            await self.firestore.add_points(username, points)
            embed = command_embed(
                description=f"Successfully added {points} point to {user.mention}"
            )
            return await ctx.send(embed=embed)
        except SyntaxError as e:
            embed = command_embed(description=str(e), error=True)
            return await ctx.send(embed=embed)

    @slash_command(
        guild_ids=[int(os.getenv("GUILD_ID"))],
        name="minus",
        description="Deduct points from a user",
    )
    @commands.has_any_role("Sponsor")
    async def _minus(self, ctx, user: discord.Member, points: int = 1):
        try:
            username = user.name
            is_user_exist = await self.firestore.is_user_exist(username)

            if not is_user_exist:
                await self.firestore.create_user(username)
                return await ctx.send(embed=insufficient_points_embed(user))

            await self.firestore.minus_points(username, points)
            embed = command_embed(
                description=f"Successfully deducted {points} point from {user.mention}"
            )
            return await ctx.send(embed=embed)
        except ValueError:
            return await ctx.send(embed=insufficient_points_embed(user))
        except SyntaxError as e:
            embed = command_embed(description=str(e), error=True)
            return await ctx.send(embed=embed)

    @slash_command(
        guild_ids=[int(os.getenv("GUILD_ID"))],
        name="help",
        description="Display available commands",
    )
    @commands.has_any_role("Server Support")
    async def _help(self, ctx):
        await ctx.defer()

        if ctx.interaction.channel != os.getenv("LOGGING_CHANNEL"):
            logs = discord.utils.get(
                ctx.guild.channels, name=os.getenv("LOGGING_CHANNEL")
            )
            print(logs)
            embed = command_embed(
                description=f"{ctx.user.mention} Commands can only be used in {logs.mention}",
                error=True,
            )
            return await ctx.respond(embed=embed)

        embed = discord.Embed(
            title="Available Commands",
            color=0xA53636,
        )
        for command in self.bot.commands:
            print(command, command.help, command.name)

        embed.description = "\n".join(
            [str(command) + " - " + str(command.help) for command in self.bot.commands]
        )
        await ctx.respond(embed=embed)

    # @commands.command()
    # @commands.has_any_role("Sponsor")
    # async def list(self, ctx):
    #     user_data = await self.firestore.get_all_users()
    #     field_value_count = 0
    #     username_value = ""
    #     points_value = ""
    #     index = 0

    #     while (index < len(user_data)):
    #         user = user_data[index]
    #         username = str(user["username"])
    #         points = str(user["points"])

    #         field_value_count += max(len(username), len(points))

    #         # Reset if it exceeds embed field value limit of 1024 characters
    #         if (field_value_count >= 1000):
    #             self.send_scoreboard(ctx, username_value, points_value)
    #             username_value = ""
    #             points_value = ""
    #             index -= 1

    #         username_value += username
    #         points_value += points
    #         index += 1

    #     # Send leftover buffer
    #     await self.send_scoreboard(ctx, username_value, points_value)

    @slash_command(
        guild_ids=[int(os.getenv("GUILD_ID"))],
        name="list",
        description="Display user points",
    )
    async def _list(self, ctx):
        username = ctx.message.author.name
        user_doc = await self.firestore.get_user_doc(username)

        return await self.send_scoreboard(
            ctx, username, 0 if user_doc is None else user_doc["points"]
        )

    async def send_scoreboard(self, ctx, usernames, points):
        # embed = discord.Embed(title="Scoreboard")
        embed = discord.Embed(color=discord.Color.random())

        embed.add_field(name="Username", value=usernames, inline=True)
        embed.add_field(name="Points", value=points, inline=True)
        return await ctx.send(embed=embed)


# Adding the cog to main script
def setup(bot):
    bot.add_cog(Score(bot))

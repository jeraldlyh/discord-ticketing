import discord
import os

from discord.ext import commands
from discord.commands import slash_command, Option
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
    async def _add(
        self,
        ctx,
        user: discord.Member,
        points: Option(int, "Enter a number between 1 to 5", required=False, default=1),
    ):
        """Award a user with points up to 5 points"""

        try:
            username = str(user)

            await self.firestore.get_user_doc(username)
            await self.firestore.add_points(username, points)
            return await ctx.respond(
                embed=command_embed(
                    description=f"Successfully added {points} point to {user.mention}"
                )
            )
        except SyntaxError as e:
            return await ctx.respond(embed=command_embed(description=str(e), error=True))

    @slash_command(
        guild_ids=[int(os.getenv("GUILD_ID"))],
        name="minus",
        description="Deduct points from a user",
    )
    @commands.has_any_role("Sponsor")
    async def _minus(
        self,
        ctx,
        user: discord.Member,
        points: Option(int, "Enter a positive number", required=False, default=1),
    ):
        try:
            if points < 0:
                return await ctx.respond(
                    embed=command_embed("Kindly enter a positive number!", error=True)
                )

            username = str(user)

            await self.firestore.get_user_doc(username)
            await self.firestore.minus_points(username, points)

            return await ctx.respond(
                embed=command_embed(
                    description=f"Successfully deducted {points} point from {user.mention}"
                )
            )
        except ValueError:
            return await ctx.respond(embed=insufficient_points_embed(user))
        except SyntaxError as e:
            return await ctx.respond(embed=command_embed(description=str(e), error=True))

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
        username = str(ctx.author)
        user_doc = await self.firestore.get_user_doc(username)

        return await self.send_scoreboard(
            ctx, username, 0 if user_doc is None else user_doc["points"]
        )

    async def send_scoreboard(self, ctx, usernames, points):
        # embed = discord.Embed(title="Scoreboard")
        embed = discord.Embed(color=discord.Color.random())

        # embed.add_field(name="Username", value=usernames, inline=True)
        embed.add_field(name="Points", value=points, inline=True)
        return await ctx.respond(embed=embed)


# Adding the cog to main script
def setup(bot):
    bot.add_cog(Score(bot))

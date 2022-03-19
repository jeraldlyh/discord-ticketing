import discord
import os

from discord.ext import commands
from discord.commands import slash_command, Option
from cogs.utils.embed import command_embed
from cogs.exception import InsufficientPointsError, MaxPointsError, NotFoundError
from cogs.firebase import Firestore


MAX_POINTS = int(os.getenv("MAX_POINTS"))


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
        user: Option(discord.Member, "Enter a Discord user", required=True),
        points: Option(
            int,
            f"Enter a number between 1 to {MAX_POINTS}",
            min_value=1,
            max_value=MAX_POINTS,
            required=False,
            default=1,
        ),
    ):
        try:
            await ctx.interaction.response.defer(ephemeral=True)

            username = str(user)
            role = [
                role
                for role in ctx.author.roles
                if role.name != ctx.guild.default_role.name and role.name != "Sponsor"
            ][0]

            await self.firestore.add_points(username, points, str(role))
            return await ctx.respond(
                embed=command_embed(
                    description=f"Successfully added {points} point to {user.mention}"
                ),
            )
        except MaxPointsError as e:
            return await ctx.respond(
                embed=command_embed(description=str(e), error=True)
            )
        except Exception as e:
            return await ctx.respond(str(e))

    @slash_command(
        guild_ids=[int(os.getenv("GUILD_ID"))],
        name="minus",
        description="Deduct points from a user",
    )
    @commands.has_any_role("Sponsor")
    async def _minus(
        self,
        ctx,
        user: Option(discord.Member, "Enter a Discord user", required=True),
        points: Option(
            int,
            f"Enter a number between 1 to {MAX_POINTS}",
            min_value=1,
            max_value=MAX_POINTS,
            required=False,
            default=1,
        ),
    ):
        try:
            await ctx.interaction.response.defer(ephemeral=True)

            username = str(user)
            role = [
                role
                for role in ctx.author.roles
                if role.name != ctx.guild.default_role.name and role.name != "Sponsor"
            ][0]

            await self.firestore.minus_points(username, points, str(role))

            return await ctx.respond(
                embed=command_embed(
                    description=f"Successfully deducted {points} point from {user.mention}"
                )
            )
        except InsufficientPointsError as e:
            return await ctx.respond(
                embed=command_embed(description=str(e), error=True)
            )

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

        embed = discord.Embed(color=discord.Color.random())
        embed.add_field(name="Username", value=ctx.author.mention, inline=False)

        if user_doc["points"]:
            for key, value in user_doc["points"].items():
                embed.add_field(name=key, value=value, inline=True)
        else:
            embed.add_field(name="Points", value=0, inline=True)

        return await ctx.respond(embed=embed, ephemeral=True)

    @slash_command(
        guild_ids=[int(os.getenv("GUILD_ID"))],
        name="create_flag",
        description=f"Create {os.getenv('TYPE')} flag",
    )
    @commands.has_permissions(administrator=True)
    async def _create_flag(
        self,
        ctx,
        flag: Option(str, f"Enter a {os.getenv('TYPE')} flag", required=True),
        points: Option(
            int, "Enter number of points for flag", min_value=1, required=True
        ),
    ):
        await self.firestore.create_flag(flag, points)
        return await ctx.respond(
            embed=command_embed(
                description=f"Successfully created `{flag}` with `{points} points`"
            )
        )

    @slash_command(
        guild_ids=[int(os.getenv("GUILD_ID"))],
        name="delete_flag",
        description=f"Delete {os.getenv('TYPE')} flag",
    )
    @commands.has_permissions(administrator=True)
    async def _delete_flag(
        self,
        ctx,
        flag: Option(str, f"Enter a {os.getenv('TYPE')} flag", required=True),
    ):
        flag_data = await self.firestore.get_flag_doc(flag)
        if flag_data is None:
            return await ctx.respond(
                embed=command_embed(description=f"`{flag}` does not exist"), error=True
            )

        await self.firestore.delete_flag(flag)
        return await ctx.respond(
            embed=command_embed(description=f"Successfully deleted `{flag}`")
        )

    @slash_command(
        guild_ids=[int(os.getenv("GUILD_ID"))],
        name="flag",
        description=f"Submit {os.getenv('TYPE')} flag",
    )
    async def _flag(
        self, ctx, flag: Option(str, f"Enter a {os.getenv('TYPE')} flag", required=True)
    ):
        await ctx.interaction.response.defer(ephemeral=True)

        flag_data = await self.firestore.get_flag_doc(flag)

        if flag_data is None:
            return await ctx.respond(
                embed=command_embed(description=f"`{flag}` is invalid", error=True),
                ephemeral=True,
            )

        username = str(ctx.author)
        user_data = await self.firestore.get_user_doc(username)

        if flag in user_data["points"]:
            return await ctx.respond(
                embed=command_embed(
                    description=f"{ctx.author.mention} has already claimed this flag",
                    error=True,
                ),
                ephemeral=True,
            )

        await self.firestore.add_points(str(ctx.author), flag_data["points"], flag)
        return await ctx.respond(
            embed=command_embed(
                description=f"{ctx.author.mention} has successfully claimed `{flag}` for `{flag_data['points']} points`"
            ),
            ephemeral=True,
        )

    @slash_command(
        guild_ids=[int(os.getenv("GUILD_ID"))],
        name="generate",
        description=f"Generate scores into a JSON file",
    )
    @commands.has_permissions(administrator=True)
    async def _generate(self, ctx):
        await ctx.interaction.response.defer()

        await self.firestore.generate_scores()
        return await ctx.respond(
            embed=command_embed(
                description=f"{ctx.author.mention} has successfully generated `scores.json`"
            ),
        )


# Adding the cog to main script
def setup(bot):
    bot.add_cog(Score(bot))

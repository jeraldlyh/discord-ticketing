import os

from discord.ext import commands
from cogs.utils.embed import command_embed
from discord.commands import slash_command, Option


class Util(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @slash_command(
        guild_ids=[int(os.getenv("GUILD_ID"))],
        name="enable_cog",
        description=f"Enable a cog",
    )
    @commands.has_permissions(administrator=True)
    async def _enable_cog(
        self, ctx, cog: Option(str, "Enter a cog name", required=True)
    ):
        is_cog_exist = any(filename[:-3] == cog for filename in os.listdir("./cogs"))

        if not is_cog_exist:
            return await ctx.send(
                embed=command_embed(
                    description=f"`{cog}` cog does not exist", error=True
                )
            )
        self.bot.add_cog(f"cogs.{cog}")
        return await ctx.send(
            embed=command_embed(description=f"Successfully enabled `{cog}` cog")
        )

    @slash_command(
        guild_ids=[int(os.getenv("GUILD_ID"))],
        name="disable_cog",
        description=f"Disable a cog",
    )
    @commands.has_permissions(administrator=True)
    async def _disable_cog(
        self, ctx, cog: Option(str, "Enter a cog name", required=True)
    ):
        is_cog_exist = any(filename[:-3] == cog for filename in os.listdir("./cogs"))

        if not is_cog_exist:
            return await ctx.send(
                embed=command_embed(
                    description=f"`{cog}` cog does not exist", error=True
                )
            )
        self.bot.remove_cog(f"cogs.{cog}")
        return await ctx.send(
            embed=command_embed(description=f"Successfully disabled `{cog}` cog")
        )


# Adding the cog to main script
def setup(bot):
    bot.add_cog(Util(bot))

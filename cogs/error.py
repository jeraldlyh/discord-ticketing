from discord.ext import commands
from cogs.utils.embed import command_embed


class Error(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, error: commands.CommandError):
        if (isinstance(error, commands.MissingAnyRole)):
            embed = command_embed(str(error), error=True)
            return await ctx.send(embed=embed)

        embed = command_embed("Something went wrong with the server. Kindly contact an adminstrator.", error=True)
        return await ctx.send(embed=command_embed)


# Adding the cog to main script
def setup(bot):
    bot.add_cog(Error(bot))

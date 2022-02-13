from discord.ext import commands
from cogs.utils.embed import command_embed


class Error(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error: commands.CommandError):
        if isinstance(error, commands.MissingAnyRole):
            return await ctx.send(
                embed=command_embed(description=str(error), error=True)
            )
        print(str(error))
        return await ctx.send(
            embed=command_embed(
                description="Something went wrong with the server. Kindly contact an adminstrator.",
                error=True,
            )
        )

    @commands.Cog.listener()
    async def on_application_command_error(self, ctx, error: commands.CommandError):
        print(str(error))
        if isinstance(error, commands.MissingPermissions) or isinstance(
            error, commands.MissingAnyRole
        ):
            return await ctx.interaction.response.send_message(
                "You do not have access to this command!", ephemeral=True
            )
        return await ctx.interaction.response.send_message(
            "Something went wrong, contact the admins!", ephemeral=True
        )


# Adding the cog to main script
def setup(bot):
    bot.add_cog(Error(bot))

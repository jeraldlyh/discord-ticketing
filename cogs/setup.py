import os
import discord


from discord.ext import commands
from cogs.utils.embed import command_embed


class Setup(commands.Cog):
    def __init__(self):
        super().__init__()

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def setup(self, ctx: commands.Context):
        """Sets up a server for ticketing system"""

        if discord.utils.get(ctx.guild.categories, name=os.getenv("SUPPORT_CATEGORY")):
            return await ctx.send("Server has already been set up.")

        try:
            support = await ctx.guild.create_role(
                name="Server Support", color=discord.Color(0x72E4B2)
            )
            overwrite = {
                ctx.guild.default_role: discord.PermissionOverwrite(
                    read_messages=False
                ),
                support: discord.PermissionOverwrite(read_messages=True),
            }
            category = await ctx.guild.create_category(
                name=os.getenv("SUPPORT_CATEGORY"), overwrites=overwrite
            )
            # await categ.edit(position=0)
            channel = await ctx.guild.create_text_channel(
                name=os.getenv("LOGGING_CHANNEL"), category=category
            )

            embed = command_embed(
                description=f"Channels have been setup. Please do not tamper with any roles/channels created by {self.bot.user.name}."
            )
            return await ctx.send(embed=embed)
        except:
            embed = command_embed(
                description="Do not have administrator permissions to setup the server.",
                error=True,
            )
            return await ctx.send(embed=embed)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def disable(self, ctx: commands.Context):
        """Close all threads and disable modmail."""

        if ctx.message.channel.name != os.getenv("LOGGING_CHANNEL"):
            logs_channel = discord.utils.get(
                ctx.message.guild.channels, name=os.getenv("LOGGING_CHANNEL")
            )

            if logs_channel is None:
                logs_channel = "#" + os.getenv("LOGGING_CHANNEL")
            else:
                logs_channel = logs_channel.mention

            embed = command_embed(
                description=f"{ctx.message.author.mention} Commands can only be used in {logs_channel}",
                error=True,
            )
            return await ctx.send(embed=embed)

        support_category = discord.utils.get(
            ctx.guild.categories, name=os.getenv("SUPPORT_CATEGORY")
        )
        if not support_category:
            embed = command_embed(description="Server has not been setup.", error=True)
            return await ctx.send(embed=embed)

        for channel in support_category.text_channels:
            if channel.name != os.getenv("LOGGING_CHANNEL"):
                await channel.delete()

        await support_category.delete()
        await ctx.send(embed=command_embed(description="Disabled Modmail."))

    def load_cogs(self):
        for filename in os.listdir("./cogs"):
            try:
                if filename.endswith(".py") and filename[:-3] not in self.IGNORE_FILES:
                    cog = f"cogs.{filename[:-3]}"
                    self.load_extension(cog)
                    print(f"Loaded {cog}")
            except Exception as e:
                print(e)

# Adding the cog to main script
def setup(bot):
    bot.add_cog(Setup(bot))
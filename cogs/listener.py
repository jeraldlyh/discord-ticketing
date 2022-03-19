import re
import os

from discord.ext import commands
from discord.commands import slash_command, Option
from cogs.utils.embed import command_embed, warning_embed


class Listener(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Store regex in buffer because it's too costly to store regex patterns in
        # firestore due to listener watching over every single message sent in the server
        self.regex_buffer = []

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        if self.regex_buffer:
            for regex in self.regex_buffer:
                if bool(re.search(regex, message.content)):
                    author = message.author

                    await message.delete()
                    await message.channel.send(embed=warning_embed(author))
    
    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if before.author.bot or after.author.bot:
            return

        if self.regex_buffer:
            for regex in self.regex_buffer:
                if bool(re.search(regex, after.content)):
                    author = after.author

                    await after.delete()
                    await after.channel.send(embed=warning_embed(author))

    @slash_command(
        guild_ids=[int(os.getenv("GUILD_ID"))],
        name="add_regex",
        description="Add a regex pattern to detect blacklisted words",
    )
    @commands.has_permissions(administrator=True)
    async def _add_regex(
        self,
        ctx,
        regex: Option(str, "Enter a regex pattern", required=True),
    ):
        try:
            await ctx.interaction.response.defer()
            regex_input = re.compile(regex)
            self.regex_buffer.append(regex_input)

            return await ctx.respond(
                embed=command_embed(
                    description=f"Successfully added `{regex}` into buffer"
                )
            )
        except Exception:
            return await ctx.respond(
                embed=command_embed(description=f"`{regex}` is not a valid regex")
            )


# Adding the cog to main script
def setup(bot):
    bot.add_cog(Listener(bot))

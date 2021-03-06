import discord
import os

from discord.ext import commands
from discord.commands import slash_command
from cogs.view import TicketSupportView
from cogs.firebase import Firestore


class Reaction(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.firestore = Firestore()

    @slash_command(
        guild_ids=[int(os.getenv("GUILD_ID"))],
        name="react",
        description="Sends a message that listens to button interactions",
    )
    @commands.has_permissions(administrator=True)
    async def react(self, ctx):
        guild = ctx.guild
        roles = await self.firestore.get_all_roles()
        roles = sorted(roles, key=lambda x: int(x['order']))
        view = TicketSupportView(ctx, roles, guild, self.firestore)

        description = f"""
Welcome to the **{guild.name}** Support Channel!\n
If you have any questions or inquiries regarding the {str(os.getenv('TYPE'))}, please select the appropriate option below to contact the respective challenge setters!\n
        """

        for role in roles:
            role_name = role["name"]
            role_emoji = role["emoji"]

            role_mention = discord.utils.get(guild.roles, id=int(role["id"])).mention
            description += f"• Press `{role_emoji} {role_name}` to raise a ticket for {role_mention}\n"

        response = await ctx.respond(
            embed=discord.Embed(title=f"{guild.name} Support", description=description),
            view=view,
        )
        message = await response.original_message()

        await self.firestore.register_ticket(str(message.id), True, str(ctx.author), "")
        self.bot.add_view(view)


# Adding the cog to main script
def setup(bot):
    bot.add_cog(Reaction(bot))

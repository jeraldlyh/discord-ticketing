import discord
import os

from discord.ext import commands
from discord.ui import Button, View
from typing import Union
from cogs.utils.embed import command_embed, insufficient_points_embed
from cogs.firebase import Firestore


class TicketView(View):
    def __init__(self):
        super().__init__()

    @discord.ui.button(
        label="Claim",
        style=discord.ButtonStyle.green,
        custom_id="persistent_view:claim",
        emoji="🔗",
    )
    async def claim(self, button: Button, interaction: discord.Interaction):
        user_role = interaction.user
        message = interaction.message
        pass


class CustomButton(Button):
    def __init__(self, ctx, label: str, emoji: str, guild: discord.Guild):
        super().__init__(
            label=label,
            style=discord.ButtonStyle.secondary,
            emoji=emoji,
            custom_id=f"persisent_view:{label}",
        )
        self.guild = guild
        self.ctx = ctx

    async def callback(self, interaction: discord.Interaction):
        support_category = discord.utils.get(self.guild.categories, name="📋 Support")
        channel = await self.guild.create_text_channel(
            name=str(interaction.user), category=support_category
        )
        embed = self.ticket_embed
        # TODO - CREATE VIEW HERE
        await self.ctx.send(embed=embed)

    def ticket_embed(self, user: discord.Member, role: discord.Role):
        embed = discord.Embed()
        description = f"""
Hey {user.mention}, thanks for reaching out to {role.mention}

```fix Kindly explain your issue or query in detail so that we can better assist you further```

We'll respond to your ticket as soon as possible, however at times, there may be a surge in tickets which will result in delayed responses.

Please refrain from pinging {role.mention} to speed up the request as this goes against our rules. {role.mention} has already received a ping upon the creation of this ticket.


If you have accidentally opened a ticket or wish to close this ticket, kindly click on the `🔒 Close` button.
"""
        embed.description = description
        return embed


class Reaction(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.firestore = Firestore()

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def react(self, ctx):
        guild = discord.utils.get(self.bot.guilds, id=int(os.getenv("GUILD_ID")))
        embed = discord.Embed(title=f"{guild.name} Support")
        roles = await self.firestore.get_all_roles()
        view = View(timeout=None)

        description = f"""
Welcome to the **{guild.name}** Support Channel!\n
If you have any questions or inquiries regarding the {str(os.getenv('TYPE'))}, please select the appropriate option below to contact the respective challenge setters!\n
        """

        for role in roles:
            role_name = role["name"]
            role_emoji = role["emoji"]
            role_mention = discord.utils.get(guild.roles, id=int(role["id"])).mention
            description += f"• Press `{role_emoji} {role_name}` to raise a ticket for {role_mention}\n"
            button = CustomButton(
                ctx=ctx, label=role_name, emoji=role_emoji, guild=guild
            )
            view.add_item(button)

        embed.description = description

        message = await ctx.send(embed=embed, view=view)
        await self.firestore.register_reaction_message(str(message.id))
        self.bot.add_view(view)


# Adding the cog to main script
def setup(bot):
    bot.add_cog(Reaction(bot))

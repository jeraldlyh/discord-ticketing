import discord

from discord.ui import Button, View
from typing import Union
from cogs.firebase import Firestore


class TicketView(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="Claim",
        style=discord.ButtonStyle.green,
        custom_id="claim",
        emoji="🔓",
    )
    async def claim(self, button: Button, interaction: discord.Interaction):
        user = interaction.user
        print(user, user.roles)

        message = interaction.message
        pass

    @discord.ui.button(
        label="Close",
        style=discord.ButtonStyle.red,
        custom_id="close",
        emoji="🔓",
    )
    async def close(self, button: Button, interaction: discord.Interaction):
        user_role = interaction.user
        message = interaction.message
        pass


class CustomButton(Button):
    def __init__(
        self,
        ctx,
        id: str,
        label: str,
        emoji: str,
        guild: discord.Guild,
        firestore: Firestore,
    ):
        super().__init__(
            label=label,
            style=discord.ButtonStyle.secondary,
            emoji=emoji,
            custom_id=f"{label}",
        )
        self.id = id
        self.ctx = ctx
        self.guild = guild
        self.firestore = firestore

    async def callback(self, interaction: discord.Interaction):
        user = interaction.user
        user_doc = await self.firestore.get_user_doc(str(user))

        # Ignore blocked users
        if user_doc is not None and user_doc["is_blocked"]:
            return await user.send(embed=self.blocked_embed())

        channel = discord.utils.get(
            self.guild.channels,
            name=str(user).replace("#", "").lower(),
        )  # i.e. xDevolution#3059 -> xdevolution3059

        # Verifies if existing channel has been created
        if channel is not None:
            # Retrieve ticket role ID in channel topic
            role = discord.utils.get(self.guild.roles, id=int(channel.topic))
            return await channel.send(embed=self.error_embed(role))

        role = discord.utils.get(self.guild.roles, id=int(self.id))
        support_category = discord.utils.get(self.guild.categories, name="📋 Support")
        support_role = discord.utils.get(self.guild.roles, name="Server Support")

        # Disable @everyone to access the channels except @Server Support ticket user
        permission = {
            self.guild.default_role: discord.PermissionOverwrite(read_messages=False),
            support_role: discord.PermissionOverwrite(read_messages=True),
            user: discord.PermissionOverwrite(read_messages=True),
        }

        channel = await self.guild.create_text_channel(
            name=str(user), category=support_category, overwrites=permission
        )
        await channel.edit(topic=role.id)  # Set ticket role ID in channel topic
        embed = self.ticket_embed(user, role)
        message = await channel.send(embed=embed, view=TicketView())
        return await self.firestore.register_reaction_message(str(message.id), False)

    def ticket_embed(
        self, user: Union[discord.Member, discord.User], role: discord.Role
    ):
        embed = discord.Embed()
        embed.description = f"""
Hey {user.mention}, thanks for reaching out to {role.mention}

```fix
Kindly explain your issue or query in detail so that we can better assist you further```

We'll respond to your ticket as soon as possible, however at times, there may be a surge in tickets which will result in delayed responses.

Please refrain from pinging {role.mention} to speed up the request as this goes against our rules. {role.mention} has already received a ping upon the creation of this ticket.


If you have accidentally opened a ticket or wish to close this ticket, kindly click on the `🔒 Close` button.
"""
        return embed

    def error_embed(self, role: discord.Role):
        embed = discord.Embed(color=discord.Color.red())
        embed.description = f"""
You currently have an open ticket for {role.mention}!

Kindly click on the `🔒 Close` button to close the current ticket first!
"""
        return embed

    def blocked_embed(self):
        embed = discord.Embed(title="Ticket not raised!", color=discord.Color.red())
        embed.description = "You have been blocked from using modmail."
        embed.set_footer(text="Kindly contact a server support regarding this issue")
        return embed


class TicketSupportView(View):
    def __init__(self, ctx, roles, guild: discord.Guild, firestore: Firestore):
        super().__init__(timeout=None)
        self.roles = roles
        self.ctx = ctx
        self.guild = guild
        self.firestore = firestore

        for role in self.roles:

            button = CustomButton(
                ctx=self.ctx,
                id=role["id"],
                label=role["name"],
                emoji=role["emoji"],
                guild=self.guild,
                firestore=firestore,
            )
            self.add_item(button)

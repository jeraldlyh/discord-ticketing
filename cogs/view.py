from pprint import pprint
import discord
import os

from typing import Union
from cogs.firebase import Firestore


# class ConfirmationView(discord.ui.View):
#     def __init__(self, firestore: Firestore):
#         super().__init__(timeout=3)
#         self.firestore = firestore

#     @discord.ui.button(
#         label="Yes",
#         style=discord.ButtonStyle.green,
#         custom_id="yes",
#     )
#     async def accept(self, button: discord.ui.Button, interaction: discord.Interaction):
#         user = interaction.user
#         channel = interaction.channel

#         role = discord.utils.get(interaction.guild.roles, id=int(channel.topic))

#         log_channel = discord.utils.get(
#             interaction.guild.channels, name=os.getenv("LOGGING_CHANNEL")
#         )

#         await log_channel.send(
#             embed=self.ticket_log_embed(user.name, role=role, is_log=True)
#         )
#         await user.send(embed=self.ticket_log_embed(user.name, role=role, is_log=False))
#         await self.firestore.delete_ticket(str(user))
#         await channel.delete()

#     @discord.ui.button(
#         label="No",
#         style=discord.ButtonStyle.red,
#         custom_id="no",
#     )
#     async def cancel(self, button: discord.ui.Button, interaction: discord.Interaction):
#         await interaction.message.delete(delay=5)

#     async def on_timeout(self):
#         raise Exception("here")
    
#     async def on_error(self, error, item, interaction):
#         # print(str(error))
#         await interaction.response.send_message(str(error))
#         pass

#     def ticket_log_embed(self, user: str, role: str, is_log=False):
#         return discord.Embed(
#             title=f"{user}'s Ticket Closed" if is_log else "Ticket Closed",
#             description=f"The ticket for {role} has just been closed.",
#             color=discord.Color.red() if is_log else discord.Color(0xFFD700),
#         )


class TicketView(discord.ui.View):
    def __init__(self, role_id: int, firestore: Firestore):
        super().__init__(timeout=None)
        self.role_id = role_id
        self.is_claimed = False
        self.firestore = firestore

    @discord.ui.button(
        label="Claim",
        style=discord.ButtonStyle.green,
        custom_id="claim",
        emoji="🔓",
    )
    async def claim(self, button: discord.ui.Button, interaction: discord.Interaction):
        user = interaction.user

        # Validates if user have support role to access claim functionality or ticket has previously been claimed
        if not self.is_interaction_allowed(user) or self.is_claimed:
            return

        channel = interaction.channel

        # Ticket user does not have any other roles except @everyone
        for member in channel.members:
            if len(member.roles) == 1:
                ticket_user = member
                break

        self.is_claimed = True
        return await channel.send(
            content=ticket_user.mention, embed=self.claim_embed(user)
        )

    @discord.ui.button(
        label="Close",
        style=discord.ButtonStyle.red,
        custom_id="close",
        emoji="🔒",
    )
    async def close(self, button: discord.ui.Button, interaction: discord.Interaction):
        user = interaction.user
        channel = interaction.channel

        if (
            not self.is_interaction_allowed(user)
            and channel.name != str(user).replace("#", "").lower()
        ):
            return
        
        role = discord.utils.get(interaction.guild.roles, id=int(channel.topic))

        log_channel = discord.utils.get(
            interaction.guild.channels, name=os.getenv("LOGGING_CHANNEL")
        )

        await log_channel.send(
            embed=self.ticket_log_embed(user.name, role=role, is_log=True)
        )
        await user.send(embed=self.ticket_log_embed(user.name, role=role, is_log=False))
        await self.firestore.delete_ticket(str(user))
        return await channel.delete()

        # return await channel.send(
        #     content=user.mention,
        #     embed=self.confirmation_embed(),
        #     view=ConfirmationView(self.firestore),
        # )

    def is_interaction_allowed(self, user: Union[discord.User, discord.Member]):
        # Validates if user have support role to access claim functionality
        return any(
            os.getenv("SUPPORT_ROLE") == role.name or self.role_id == role.id
            for role in user.roles
        )

    def claim_embed(self, user: Union[discord.User, discord.Member]):
        return discord.Embed(
            description=f"{user.mention} will be assisting you on the issue!",
            color=discord.Color.green(),
            title="Ticket Claimed",
        )

    def confirmation_embed(self):
        return discord.Embed(description="Are you sure you want to close this ticket?")
    
    def ticket_log_embed(self, user: str, role: str, is_log=False):
        return discord.Embed(
            title=f"{user}'s Ticket Closed" if is_log else "Ticket Closed",
            description=f"The ticket for {role} has just been closed.",
            color=discord.Color.red() if is_log else discord.Color(0xFFD700),
        )


class CustomButton(discord.ui.Button):
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
        message = await channel.send(
            content=f"{user.mention} {role.mention}",
            embed=embed,
            view=TicketView(role.id, self.firestore),
        )
        return await self.firestore.register_ticket(
            str(message.id), False, str(user), str(role.id)
        )

    def ticket_embed(
        self, user: Union[discord.Member, discord.User], role: discord.Role
    ):
        return discord.Embed(
            description=f"""
Hey {user.mention}, thanks for reaching out to {role.mention}

```fix
Kindly explain your issue or query in detail so that we can better assist you further```

We'll respond to your ticket as soon as possible, however at times, there may be a surge in tickets which will result in delayed responses.

Please refrain from pinging {role.mention} to speed up the request as this goes against our rules. {role.mention} has already received a ping upon the creation of this ticket.


If you have accidentally opened a ticket or wish to close this ticket, kindly click on the `🔒 Close` button.
"""
        )

    def error_embed(self, role: discord.Role):
        return discord.Embed(
            description=f"""
You currently have an open ticket for {role.mention}!

Kindly click on the `🔒 Close` button to close the current ticket first!
""",
            color=discord.Color.red(),
        )

    def blocked_embed(self):
        embed = discord.Embed(
            title="Ticket not raised!",
            description="You have been blocked from using modmail.",
            color=discord.Color.red(),
        )
        embed.set_footer(text="Kindly contact a server support regarding this issue")
        return embed


class TicketSupportView(discord.ui.View):
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

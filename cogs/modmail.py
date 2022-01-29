import os
from typing import Union
import discord
import re

from discord.ext import commands
from urllib.parse import urlparse

from discord.errors import NotFound
from cogs.utils.embed import command_embed, blocked_embed
from cogs.utils.format import format_info, format_name


class Modmail(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def setup(self, ctx, *, modrole: discord.Role = "Server Support"):
        """Sets up a server for modmail"""
        if discord.utils.get(ctx.guild.categories, name="📋 Support"):
            return await ctx.send("Server has already been set up.")
        else:
            try:
                support = await ctx.guild.create_role(name="Server Support", color=discord.Color(0x72E4B2))
                overwrite = {
                    ctx.guild.default_role: discord.PermissionOverwrite(read_messages=False),
                    support: discord.PermissionOverwrite(read_messages=True),
                }
                category = await ctx.guild.create_category(name="📋 Support", overwrites=overwrite)
                # await categ.edit(position=0)
                channel = await ctx.guild.create_text_channel(name=os.getenv("LOGGING_CHANNEL"), category=category)
                await channel.edit(topic="-block <userID> to block users.\n\n" "Blocked\n-------\n\n")

                embed = command_embed(
                    description=f"**Channels have been setup. Please do not tamper with any roles/channels created by {self.bot.user.name}.**"
                )
                return await ctx.send(embed=embed)
            except:
                embed = command_embed(description="**Do not have administrator permissions to setup the server.**", error=True)
                return await ctx.send(embed=embed)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def disable(self, ctx):
        """Close all threads and disable modmail."""

        if ctx.message.channel.name != os.getenv("LOGGING_CHANNEL"):
            logs_channel = discord.utils.get(ctx.message.guild.channels, name=os.getenv("LOGGING_CHANNEL"))

            if logs_channel is None:
                logs_channel = "#" + os.getenv("LOGGING_CHANNEL")
            else:
                logs_channel = logs_channel.mention

            embed = command_embed(
                description=f"**{ctx.message.author.mention} Commands can only be used in {logs_channel}**"
            )
            return await ctx.send(embed=embed)
    
        support_category = discord.utils.get(ctx.guild.categories, name="📋 Support")
        if not support_category:
            embed = command_embed(description="**Server has not been setup.**", error=True)
            return await ctx.send(embed=embed)

        embed_message = discord.Embed(title="Thread Closed")
        embed_message.description = "**{ctx.author}** has closed this modmail session."
        embed_message.color = discord.Color.red()

        for channel in support_category.text_channels:
            channel_topic = str(channel.topic)

            if "User ID:" in channel_topic:
                user_id = channel_topic.split(": ")[1]
                user = self.get_user(user_id)
                await user.send(embed=embed_message)
            await channel.delete()
        await support_category.delete()

        try:
            embed = command_embed(description="**Disabled Modmail.**")
            await ctx.send(embed=embed)
        except NotFound as e:
            pass

    @commands.command(name="close")
    @commands.has_any_role("Server Support")
    async def _close(self, ctx):
        """Close the current thread."""

        if "User ID:" not in str(ctx.channel.topic):
            eembed = command_error(description="This is not a modmail thread.")
            return await ctx.send(embed=eembed)
        user_id = int(ctx.channel.topic.split(": ")[1])
        user = self.bot.get_user(user_id)
        em = discord.Embed(title="Thread Closed")
        em.description = "**{0}** has closed this modmail session.".format(ctx.author)
        em.color = discord.Color.red()
        try:
            logs = discord.utils.get(ctx.message.guild.channels, name=os.getenv("LOGGING_CHANNEL"))
            log_em = discord.Embed(title="{0}'s Thread Closed".format(user))
            log_em.color = discord.Color(0xFFD700)
            log_em.description = "**{0}** has closed this modmail session.".format(
                ctx.author
            )
            await logs.send(embed=log_em)
            await user.send(embed=em)
        except Exception as e:
            print(e)
        await ctx.channel.delete()

    async def send_mail(self, message: discord.Message, channel: Union[discord.TextChannel,discord.DMChannel], is_moderator: bool):
        """Sends message to modmail channel for specific user"""

        author = message.author
        embed = discord.Embed()
        embed.description = message.content
        embed.timestamp = message.created_at
        embed.set_author(name=str(author), icon_url=author.avatar_url)
        urls = re.findall(r"(https?://[^\s]+)", message.content)

        types = [".png", ".jpg", ".gif", ".jpeg", ".webp"]

        for url in urls:
            if any(urlparse(url).path.endswith(x) for x in types):
                embed.set_image(url=url)
                break

        if is_moderator:
            embed.color = discord.Color.green()
            embed.set_footer(text="Moderator")
        else:
            embed.color = discord.Color.gold()
            embed.set_footer(text="User")

        if message.attachments:
            embed.set_image(url=message.attachments[0].url)

        await channel.send(embed=embed)

    async def process_reply(self, message: discord.Message):
        try:
            await message.delete()
        except NotFound:
            pass

        await self.send_mail(message, message.channel, is_moderator=True)

        user_id = int(message.channel.topic.split(": ")[1])
        user = self.bot.get_user(user_id)

        await self.send_mail(message, user, is_moderator=True)

    async def validate_blocked_user(self, message, category):
        bot_info_channel = category.channels[0]  # By default, bot-info
        blocked = bot_info_channel.topic.split("Blocked\n-------")[1].strip().split("\n")
        blocked = [x.strip() for x in blocked]

        if str(message.author.id) in blocked:
            return await message.author.send(embed=blocked_embed)

    async def process_modmail(self, message: discord.Message):
        """Processes messages sent to the bot, creates a thread with requested user."""

        await message.add_reaction("✅")

        guild = discord.utils.get(self.bot.guilds, id=os.getenv("GUILD_ID"))
        support_category = discord.utils.get(guild.categories, name="📋 Support")
        await self.validate_blocked_user(message, support_category)
        
        author = message.author
        topic = f"User ID: {author.id}"
        channel = discord.utils.get(guild.text_channels, topic=topic)

        embed = discord.Embed(title="Thanks for the message!")
        embed.description = "The moderation team will get back to you as soon as possible!"
        embed.color = discord.Color.green()

        if channel is not None:
            await self.send_mail(message, channel, mod=False)
        else:
            await message.author.send(embed=embed)
            # overwrite={
            # message.author: discord.PermissionOverwrite(read_messages=True),
            # guild.default_role: discord.PermissionOverwrite(read_messages=False)
            # }
            modmail_channel = await guild.create_text_channel(
                name=self.format_name(author),
                # overwrites=overwrite,
                category=support_category,
            )

            await modmail_channel.edit(topic=topic)
            support = discord.utils.get(guild.roles, name="Server Support")

            await modmail_channel.send(
                f"{support.mention}",
                embed=self.format_info(message)
            )
            await self.send_mail(message, modmail_channel, mod=False)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return

        if isinstance(message.channel, discord.DMChannel):
            await self.process_modmail(message)

    @commands.command()
    @commands.has_any_role("Server Support")
    async def reply(self, ctx, *, message):
        """Reply to users using this command."""

        category = discord.utils.get(ctx.guild.categories, id=ctx.channel.category_id)
        if category is not None:
            if category.name == "📋 Support":
                if "User ID:" in ctx.channel.topic:
                    ctx.message.content = message
                    await self.process_reply(ctx.message)

    @commands.command()
    @commands.has_any_role("Server Support")
    async def block(self, ctx, user=Union[discord.Member, int, str, None]):
        """Block a user from using modmail."""

        if user is None and "User ID:" not in str(ctx.channel.topic):
            embed = command_embed(description="**Kindly provide a user ID or tag a user.**", error=True)
            return await ctx.send(embed=embed)
        elif isinstance(user, discord.Member):
            id = user.id
        else:
            id = ctx.channel.topic.split("User ID: ")[1].strip() or user

        category = discord.utils.get(ctx.guild.categories, name="📋 Support")
        bot_info_channel = category.channels[0]  # bot-info

        if id in bot_info_channel.topic:
            embed = command_embed(description="**User is already blocked.**", error=True)
            return await ctx.send(embed=embed)

        topic = str(bot_info_channel.topic)
        topic += "\n" + id

        await bot_info_channel.edit(topic=topic)
        member = self.get_user(id)

        embed = command_embed(description=f"**Sucessfully blocked {member.mention}.**")
        await ctx.send(embed=embed)

    @commands.command()
    @commands.has_any_role("Server Support")
    async def unblock(self, ctx, user=Union[discord.Member, int, str, None]):
        """Unblocks a user from using modmail."""

        if user is None and "User ID:" not in str(ctx.channel.topic):
            embed = command_embed(description="**Kindly provide a user ID or tag a user.**", error=True)
            return await ctx.send(embed=embed)
        elif isinstance(user, discord.Member):
            id = user.id
        else:
            id = ctx.channel.topic.split("User ID: ")[1].strip() or user

        category = discord.utils.get(ctx.guild.categories, name="📋 Support")
        bot_info_channel = category.channels[0]  # bot-info

        if id not in bot_info_channel.topic:
            embed = command_embed(description="**User is not already blocked.**", error=True)
            return await ctx.send(embed=embed)

        topic = str(bot_info_channel.topic)
        topic = topic.replace("\n" + id, "")

        await bot_info_channel.edit(topic=topic)
        member = self.get_user(id)

        embed = command_embed(description=f"**Sucessfully unblocked {member.mention}.**")
        return await ctx.send(embed=embed)

    @commands.command()
    @commands.has_any_role("Server Support")
    async def help(self, ctx):
        if ctx.message.channel.name != os.getenv("LOGGING_CHANNEL"):
            logs = discord.utils.get(ctx.message.guild.channels, name=os.getenv("LOGGING_CHANNEL"))
            embed = command_embed(
                description=f"**{ctx.message.author.mention} Commands can only be used in {logs.mention}**",
                error=True
            )
            return await ctx.send(embed=embed)
        
        embed = discord.Embed(
            title="Available Commands",
            color=0xA53636,
        )
        embed.description=("\n".join([command for command in self.bot.commands]))
        await ctx.send(embed=embed)


# Adding the cog to main script
def setup(bot):
    bot.add_cog(Modmail(bot))

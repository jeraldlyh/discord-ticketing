import os
import discord
import pytz
import datetime
import firebase_admin

from dotenv import load_dotenv
from cogs.firebase import Firestore
from cogs.view import TicketSupportView, TicketView
from discord.ext import commands


class ModMail(commands.Bot):
    def __init__(self):
        intents = discord.Intents.all()
        intents.members = True
        super().__init__(
            command_prefix=commands.when_mentioned_or("-"), intents=intents
        )
        self.IGNORE_FILES = ["firebase", "modmail", "view"]

    def load_cogs(self):
        for filename in os.listdir("./cogs"):
            try:
                if filename.endswith(".py") and filename[:-3] not in self.IGNORE_FILES:
                    cog = f"cogs.{filename[:-3]}"
                    self.load_extension(cog)
                    print(f"Loaded {cog}")
            except Exception as e:
                print(e)

    async def on_ready(self):
        self.remove_command("help")
        self.load_cogs()
        await self.change_presence(activity=discord.Activity(name="Your PMs", type=2))
        # await self.sync_commands()

        # Reloads persistent view upon relaunching
        db = Firestore()
        tickets = await db.get_available_tickets()
        roles = await db.get_all_roles()
        guild = discord.utils.get(self.guilds, id=int(os.getenv("GUILD_ID")))

        if tickets:
            for ticket in tickets:
                if ticket["is_root"]:
                    print(f"Adding persistent root view to {ticket['id']}")
                    self.add_view(
                        view=TicketSupportView(self, roles, guild, db),
                        message_id=int(ticket["id"]),
                    )
                else:
                    print(f"Adding persistent view to {ticket['id']}")
                    self.add_view(
                        view=TicketView(ticket["role_id"]),
                        message_id=int(ticket["id"]),
                    )

        time_now = datetime.datetime.now(tz=pytz.timezone("Asia/Singapore"))
        login_time = time_now.strftime("%d-%m-%Y %I:%M %p")
        print("-----------------")
        print("Logged in as {0} at {1}".format(self.user.name, login_time))
        print("-----------------")


os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "./google-credentials.json"
load_dotenv()
firebase_admin.initialize_app()
bot = ModMail()
bot.run(os.getenv("BOT_TOKEN"))

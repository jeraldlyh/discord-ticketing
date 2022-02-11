import os
import discord
import pytz
import datetime
import firebase_admin

from dotenv import load_dotenv
from discord.ext import commands


class ModMail(commands.Bot):
    def __init__(self):
        intents = discord.Intents.all()
        intents.members = True
        super().__init__(command_prefix=commands.when_mentioned_or("-"), intents=intents)
        self.IGNORE_FILES = ["firebase", "modmail"]

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
        await self.change_presence(
            activity=discord.Activity(name="Your PMs", type=2)
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

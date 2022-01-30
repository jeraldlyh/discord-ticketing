import os
import discord
import pytz
import datetime
import firebase_admin
import config

from firebase_admin import credentials
from discord.ext import commands

os.environ["GOOGLE_APPLICATION_CREDENTIALS"]="./whitehacks-key.json"
extensions = ["cogs.modmail", "cogs.score"]#, "cogs.error"]

credential = credentials.Certificate(config.FIREBASE_CREDENTIALS)
firebase_admin.initialize_app(credential)

intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix="-", intents=intents)
bot.remove_command("help")

@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Activity(name="Your PMs", type=2))
    time_now = datetime.datetime.now(tz=pytz.timezone("Asia/Singapore"))
    login_time = time_now.strftime("%d-%m-%Y %I:%M %p")
    print("-----------------")
    print("Logged in as {0} at {1}".format(bot.user.name, login_time))
    print("-----------------")


if __name__ == "__main__":
    for extension in extensions:
        try:
            bot.load_extension(extension)
            print("Loaded {0}".format(extension))
        except Exception as e:
            print(e)


bot.run(config.BOT_TOKEN)

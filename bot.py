import os
import discord
import pytz
import datetime
import firebase_admin

from dotenv import load_dotenv
from discord.ext import commands


os.environ["GOOGLE_APPLICATION_CREDENTIALS"]="./google-credentials.json"
load_dotenv()
firebase_admin.initialize_app()

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
    ignore = ["firebase", "modmail"]
    for filename in os.listdir("./cogs"):
        try:
            if filename.endswith(".py") and filename[:-3] not in ignore:
                cog = f"cogs.{filename[:-3]}"
                bot.load_extension(cog)
                print(f"Loaded {cog}")
        except Exception as e:
            print(e)


bot.run(os.getenv("BOT_TOKEN"))

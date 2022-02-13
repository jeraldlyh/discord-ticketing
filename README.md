## Overview
This is a rewrite version of [discord-modmail](https://github.com/jeraldlyh/discord-modmail) due to the breaking changes released by Discord where all bots are expected to migrate over to Slash Commands by April 2022. Discord modmail serves as a shared inbox for server moderators to communicate with users in a seamless way.

## How does it work?
User is able to raise a ticket by interacting with the buttons on a support message which consists of various support categories configured by the server. A subsequent text channel will be created between both the user and support staffs that has the corresponding role belonging to the support category.

## Commands Usage
-   **Server Administrators**
    -   `/setup` - Automatically sets up the ticketing module in the server
    -   `/disable` - Close all current threads and disable ticketing
    -   `/react` - Sends a message that listens for interactions with the buttons
-   **Moderators**
    -   `-block <user>` - Blocks specified user and prevent them from utilising ticketing system
    -   `-unblock <user>` - Unblocks specified user
-   **Sponsors**
    -   `/add <user> <points>` - Awards point(s) (default = 1) to specified user
    -   `/minus <user> <points>` - Deducts point(s) (default = 1) from specified user

## Notes
-   Moderators must be assigned a support role (specified in environment variables) to access the commands.

## Environment Variables
| Name                 | Description                                                                             |
| -------------------- | --------------------------------------------------------------------------------------- |
| `BOT_TOKEN`          | Discord bot [token](https://discord.com/developers/docs/intro)                          |
| `GUILD_ID`           | Discord server ID                                                                       |
| `LOGGING_CHANNEL`    | Name of logging channel (recommended: mail-logs)                                        |
| `GOOGLE_CREDENTIALS` | Firebase service [account](https://firebase.google.com/support/guides/service-accounts) |
| `TYPE`               | Type of support that the server is providing (i.e. CTF, Hackathons)                     |
| `SUPPORT_ROLE`       | Name of support role to access the bot                                                  |
| `SUPPORT_CATEGORY`   | Name of support category to for ticket logs                                             |


## Local Deployment
```bash
git clone https://github.com/jeraldlyh/discord-ticketing.git
cd discord-ticketing

# Usage of Virtual Env
python3 -m venv .
source venv/bin/activate

# Installs dependencies
pip3 install -r requirements.txt

# Launch bot
python3 bot.py
```

## Heroku Deployment
```bash
heroku create <nameOfApp>

heroku config:set BOT_TOKEN=<botToken>
heroku config:set GUILD_ID=<guildID>
heroku config:set LOGGING_CHANNEL=<loggingChannel>
heroku config:set GOOGLE_CREDENTIALS=<googleCreds>
heroku config:set TYPE=<type>
heroku config:set SUPPORT_ROLE=<supportRole>
heroku config:set SUPPORT_CATEGORY=<supportCategory>

heroku buildpacks:set heroku/python
heroku buildpacks:add --index 1 https://github.com/buyersight/heroku-google-application-credentials-buildpack.git

git add .
git commit -m "Initial commit"
git push heroku master
```
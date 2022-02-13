## Overview
This is a rewrite version of [discord-modmail](https://github.com/jeraldlyh/discord-modmail). Discord modmail serves as a shared inbox for server moderators to communicate with users in a seamless way. It currently supports both text and image messages (.png, .jpg, .gif, .jpeg, .webp).

## How does it work?
Whenever a user sends a direct message to the bot, a channel/thread will be created in the designated category named `📋 Support`. Moderators are able to respond to the user via the text channel which users will receive moderator(s)' replies from their DMs thereafter.

## Commands Usage
-   **Server Administrators**
    -   `-setup` - Automatically sets up the modmail module in the server
    -   `-disable` - Close all current threads and disable modmail
-   **Moderators**
    -   `-reply <message>` - Replies the user with a message
    -   `-close` - Resolve and close the current threaed
    -   `-block <userID / userMention>` - Blocks specified user and prevent them from utilising modmail
    -   `-unblock <userID / userMention>` - Unblocks specified user
    -   `-help` - Display available commands for moderators
-   **Sponsors**
    -   `-add <userMention>` - Awards one point to specified user
    -   `-minus <userMention>` - Deducts one point from specified user

## Notes
-   Moderators must be assigned a support role (specified in environment variables) to access the commands.
-   Tweak and configure the category name accordingly to your preference in the script by replacing the default name stated above in the script.

## Environment Variables
| Name                 | Description                                                                             |
| -------------------- | --------------------------------------------------------------------------------------- |
| `BOT_TOKEN`          | Discord bot [token](https://discord.com/developers/docs/intro)                          |
| `GUILD_ID`           | Discord server ID                                                                       |
| `LOGGING_CHANNEL`    | Name of logging channel (recommended: mail-logs)                                        |
| `GOOGLE_CREDENTIALS` | Firebase service [account](https://firebase.google.com/support/guides/service-accounts) |
| `TYPE`               | Type of support that the server is providing (i.e. CTF, Hackathons)                     |
| `SUPPORT_ROLE`       | Name of support role to access the bot                                                  |


## Local Deployment
```bash
git clone https://github.com/jeraldlyh/discord-modmail.git
cd discord-modmail

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

heroku buildpacks:set heroku/python
heroku buildpacks:add --index 1 https://github.com/buyersight/heroku-google-application-credentials-buildpack.git

git add .
git commit -m "Initial commit"
git push heroku master
```
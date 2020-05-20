# Markov Bot
A Discord bot to generate Markov sentences from a model based on your server chat logs.

## Setup
Running the bot for your own server is pretty simple. You first will need a bot token from Discord. The bot expects this token to be available via the environmental variable DISCORD_BOT_TOKEN

If running in a development environment, install dev dependencies.

`
$ pip install -r requirements/dev.txt
`

If running in a non-dev environment, install base dependencies.

`
$ pip install -r requirements/base.txt
`

To start the bot:
`
$ python bot.py
`



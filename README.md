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

### Run via Docker
Download the Docker Image from Docker Hub and Run it via this Command:

`
$ docker run -rm -it --env DISCORD_BOT_TOKEN=BOT_TOKEN_HERE sheldonburks/discord-markov-bot:latest
`

Note: discord-markov-bot uses an embedded document database called TinyDB. You will either need to mount a docker volume and set the environment variable DB_PATH.
If this variable is not set the DB will be created inside of the application directory and will only last as long as the container does. Meaning your data will be lost if the container is deleted.



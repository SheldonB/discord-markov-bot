# Markov Bot
A Discord bot to generate Markov sentences from a model based on your server chat logs.

## Commands

- `!markov say` generates a sentence from the entire server's chain.
- `!markov say @user` generates a sentence from that user's messages in the current server.
- `!markov say 123456789012345678` selects a user by their numeric Discord ID, including someone who has left the server.
- `!markov learn` rebuilds the server chain and separate chains for every human author with eligible messages.

Training scans all available history in readable text channels, excluding bots, one-word messages, and messages starting with `!`. Initial training builds both server and user chains. Existing server-only databases keep working; run `!markov learn` to add user chains.

Anyone who can use `say` can select a trained author. Each user's chain belongs to the server where it was trained. Both server and user sentences must be 125–500 characters and pass the existing originality checks, so users with little training text may be unable to generate a sentence. Missing or unsuccessful user chains return an error without falling back to the server chain.

As before, `learn` deletes saved chains before rebuilding. A failed or empty rebuild leaves no saved chains. Authors whose text cannot train a model are skipped; training details are recorded in the logs.

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



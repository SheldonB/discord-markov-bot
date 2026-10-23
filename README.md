# Markov Bot
A Discord bot to generate Markov sentences from a model based on your server chat logs.

## Commands

- `!markov say` generates a sentence from the entire server's chain.
- `!markov say @user` generates a sentence from that user's messages in the current server.
- `!markov say 123456789012345678` selects a user by their numeric Discord ID, including someone who has left the server.
- `!markov learn` rebuilds the server chain and separate chains for every human author with eligible messages.

Training scans all available history in readable text channels, excluding bots, one-word messages, and messages starting with `!`. Initial training builds both server and user chains. Existing server-only databases keep working; run `!markov learn` to add user chains.

Anyone who can use `say` can select a trained author. Each user's chain belongs to the server where it was trained. By default, both server and user sentences must be 20–500 characters and pass the existing originality checks, so users with little training text may still be unable to generate a sentence. Missing or unsuccessful user chains return an error without falling back to the server chain.

Training preserves user mentions (`<@ID>` and `<@!ID>`), plain user IDs, slang, and ordinary emoji. Generated mentions can still tag people. It removes URLs, fenced and inline code, timestamped/severity-prefixed log lines, and Python tracebacks. Markdown link labels remain; channel mentions are removed and custom emoji become `:name:` without their IDs. Whitespace and curly quotes are normalized. Quotes, parentheses, brackets, and emoticons are accepted as training text.

Each message and newline establishes a training boundary. Sentence punctuation also separates lowercase sentences, without requiring capitalization or adding a period to unpunctuated replies. Cleaned sentences with fewer than two words are skipped.

Server models default to two preceding words of context; user models default to one, allowing more recombination from smaller collections of messages. Both can be configured from one to three words. One word gives more varied combinations; three preserves longer phrases and generally needs more training text. User models always train exclusively on the selected author's messages in that server.

Generation makes at most 300 candidate attempts by default. Each walk stops when it would exceed the character or word limit, and incomplete walks are discarded. Reconstructed models are compiled and cached in memory, with up to 128 recently used server/user models retained. Saving or deleting a guild's chains invalidates its cached models; originals remain available for the existing originality checks.

Existing saved models remain usable. Run `!markov learn` to apply the new preprocessing and context sizes to their training data.

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

### Markov settings

Set these environment variables before starting the bot:

| Variable | Default | Meaning |
| --- | --- | --- |
| `MARKOV_MIN_CHARS` | `20` | Minimum output length; zero or greater, and no greater than the maximum. |
| `MARKOV_MAX_CHARS` | `500` | Maximum output length, from 1 to 2000 characters. |
| `MARKOV_GENERATION_TRIES` | `300` | Maximum candidate attempts per request; must be positive. |
| `MARKOV_MAX_WORDS` | `100` | Maximum words in a candidate; must be positive. |
| `MARKOV_STATE_SIZE` | `2` | Server model context size, from 1 to 3 words. |
| `MARKOV_USER_STATE_SIZE` | `1` | User model context size, from 1 to 3 words. |

Context settings take effect when training; rebuild existing models with `!markov learn` after changing them. Length and attempt settings apply when generating sentences.

### Run via Docker
Download the Docker Image from Docker Hub and Run it via this Command:

`
$ docker run -rm -it --env DISCORD_BOT_TOKEN=BOT_TOKEN_HERE sheldonburks/discord-markov-bot:latest
`

Note: discord-markov-bot uses an embedded document database called TinyDB. You will either need to mount a docker volume and set the environment variable DB_PATH.
If this variable is not set the DB will be created inside of the application directory and will only last as long as the container does. Meaning your data will be lost if the container is deleted.



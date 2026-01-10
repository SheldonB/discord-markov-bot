# Agent Guidelines

## Architecture Overview
- **Entrypoint:** `bot.py` initializes logging, loads `DISCORD_BOT_TOKEN`, and runs the Discord bot via `markovbot.run(...)`.
- **Bot core:** `markovbot/core.py` defines `MarkovBot`, a `discord.ext.commands.Bot` subclass that manages lifecycle events and presence updates while delegating guild management to `Supervisor`.
- **Commands:** `markovbot/commands.py` registers the `say` and `learn` commands that generate sentences or rebuild the Markov chain.
- **Supervisor & seeding:** `markovbot/supervisor.py` tracks connected guilds and kicks off seeding. `markovbot/seeder.py` downloads channel history, filters messages, and rebuilds chains.
- **Markov model:** `markovbot/markov.py` defines a `CustomMarkovText` wrapper around `markovify` and generates sentences from persisted chains.
- **Persistence:** `markovbot/persistence.py` stores Markov chains in TinyDB (`markov_db.json`), keyed by guild ID.
- **Tests:** `test/` contains unittest-based coverage for persistence and supervisor behavior.

## Agent Instructions
- When you make a change, **always run the tests and ensure they pass** before finalizing your work.
  - Suggested command: `python -m unittest`

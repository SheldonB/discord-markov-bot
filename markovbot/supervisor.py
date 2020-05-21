import logging

from discord import Guild

from markovbot import markov, persistence
from markovbot.seeder import seeder


log = logging.getLogger(__name__)


class Supervisor:
    def __init__(self):
        self.guilds = {}

    async def add(self, guild: Guild):
        self.guilds[guild.id] = guild
        await seeder.seed(guild)

    def remove(self, guild: Guild, delete_data=False): # TODO: Ugly, clean up later.
        try:
            self.guilds.pop(guild.id)

            if delete_data:
                persistence.delete_chain(guild)
        except KeyError:
            log.warning('Guild=%s:%s asked to be removed, but was not in connected guilds map', guild.id, guild.name)

    def connected_guild_count(self):
        return len(self.guilds)

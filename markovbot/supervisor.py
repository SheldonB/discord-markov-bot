import logging

from discord import Guild

from markovbot import markov
from markovbot.seeder import Seeder


log = logging.getLogger(__name__)


class Supervisor:
    def __init__(self):
        self.guilds = {}
        self.seeder = Seeder()

    async def add(self, guild: Guild):
        self.guilds[guild.id] = guild
        await self.seeder.seed(guild)

    def remove(self, guild: Guild):
        try:
            self.guilds.pop(guild.id)
            # TODO: Write to disk
        except KeyError:
            log.warning('Guild=%s:%s asked to be removed, but was not in connected guilds map', guild.id, guild.name)
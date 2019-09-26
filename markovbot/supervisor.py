import logging

from discord import Guild


log = logging.getLogger(__name__)


class Supervisor:
    def __init__(self):
        self.guilds = {}

    def add(self, guild: Guild):
        self.guilds[guild.id] = guild

    def remove(self, guild: Guild):
        try:
            self.guilds.pop(guild.id)
        except KeyError:
            log.warning('Guild=%s:%s asked to be removed, but was not in connected guilds map', guild.id, guild.name)

    # def _seed(self, guild: Guild):

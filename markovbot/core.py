import logging

from discord import Guild, Game, CustomActivity
from discord.ext.commands import Bot

from markovbot.supervisor import Supervisor

log = logging.getLogger(__name__)

description = """Generate sentences based off of a Markov model of the text chat of your discord server"""


class MarkovBot(Bot):
    """
    Extends the discord.py Bot implementation and
    overrides events for custom logic and handling.
    """
    def __init__(self):
        super().__init__(command_prefix='!markov ', description=description)

        self.is_connected = False
        self.supervisor = Supervisor()

    @property
    def connect_guild_count(self) -> int:
        """
        Get the number of connected guilds the bot is a member of.
        :return: int
        """
        return len(self.guilds)

    async def on_ready(self):
        await self.update_presence()
        log.info("Markov Bot is connected and ready.")

    async def on_guild_join(self, guild: Guild):
        """
        Event that is fired when the bot is added to a new server.

        This will hand off the management of the Guild of to the supervisor
        where seeding can begin.

        :param guild: Discord Guild (Server) that has joined.
        :return: None
        """
        log.info("New Guild(id=%s, name=%s) has joined the mix.", guild.id, guild.name)
        await self.supervisor.add(guild)
        await self.update_presence()

    async def on_guild_remove(self, guild: Guild):
        log.info("Guild(id=%s, name=%s) has been removed.", guild.id, guild.name)
        self.supervisor.remove(guild)
        await self.update_presence()

    async def on_guild_available(self, guild: Guild):
        log.info("Guild(id=%s, name=%s) is now available.", guild.id, guild.name)
        await self.supervisor.add(guild)
        await self.update_presence()

    async def on_guild_unavailable(self, guild: Guild):
        log.info("Guild(id=%s, name=%s) is now unavailable.", guild.id, guild.name)
        self.supervisor.remove(guild, True)
        await self.update_presence()

    async def update_presence(self):
        game_activity = Game("on {} servers.".format(self.supervisor.connected_guild_count()))
        await self.change_presence(activity=game_activity)


markovbot = MarkovBot()
import os
import sys
import logging

import discord

from discord.ext.commands import Bot, core

from markovbot import datastore
from markovbot.server import ServerManager

log = logging.getLogger(__name__)

description = """Generate sentences based off of a Markov model of the text chat of your discord server"""

class CustomCommand(core.Command):
    def __init__(self, name, callback, **kwargs):
        super().__init__(name, callback, **kwargs)

    async def invoke(self, ctx):
        ctx.server_context = markovbot.server_manager.get_server_context(ctx.message.server)
        await super().invoke(ctx)


class CustomBotClient(Bot):
    """
    Extends the discord.py Bot implementation and
    overrides events for custom logic and handeling.
    """
    def __init__(self):
        #TODO: Make Command Prefix configurable
        super().__init__(command_prefix='!cancer ', description=description)

        self._server_manager = ServerManager(self)

    @property
    def server_manager(self):
        return self._server_manager

    async def on_message(self, message: discord.Message):
        """
        This event is fired whenever a new message comes to 
        any server that the bot is a member of.

        Right now there is really nothing to be done here
        other than forward this on to the discord.py implementation
        to allow for command processing.

        :param message: The discord.py Message object
        """
        await self.process_commands(message)

    async def on_server_join(self, server: discord.Server):
        """
        This event is fired whenever the bot joins a new server.

        When a new server is added, it is added to the manager.

        Note: This is not fired when the bot comes online, see 
        on_server_available for that.

        :param server: The discord.py Server object representing the
        new server the bot has joined.
        """
        log.info('A new server %s has joined', server.name)
        await self.server_manager.add(server)

    async def on_server_remove(self, server: discord.Server):
        """
        This event is fired when a server removes the bot as a member.

        When the bot is removed, the server is removed from the server
        manager.

        :param server: The discord.py Server object representing the
        server being removed.
        """
        log.info('Server %s has been removed', server.name)
        self.server_manager.remove(server)

    async def on_server_update(self, server: discord.Server):
        """
        TODO: This might or might not need to be handled.
                I need to have a better understanding of how
                the discord client updates this. Like, does it return
                a new object or does it just modify the reference?
        """
        log.info('Server %s has been updated')

    async def on_server_available(self, server: discord.Server):
        """
        This event is fired when ever a server has
        existed in the server cache, but has become available
        again.

        For example, when the bot has been restarted this is called
        for all previously connected servers.

        :param server: The discord.py Server object representing the
        server that has become available.
        """
        log.info('The server %s has become available', server.name)
        await self.server_manager.add(server)

    async def on_server_unavailable(self, server: discord.Server):
        """
        Event fired when a server had become unavailable for use.

        The server will be removed from the server manager when this event
        it fired.

        :param server: The discord.py Server object representing the
        server that has become unavailable.
        """
        log.info('The server %s has become unavailable', server.name)
        self.server_manager.remove(server)

    def command(self, *args, **kwargs):
        """
        Override the command decorator that is exposed by discord.py
        so that we can inject our own CustomCommand class into it,
        which adds the server context to the context of the command.
        """
        kwargs['cls'] = CustomCommand
        return super().command(*args, **kwargs)


markovbot = CustomBotClient()
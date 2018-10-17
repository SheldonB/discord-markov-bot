# pylint: disable=W0612

import os
import sys
import logging

import discord

from cancerbot.server import ServerManager

log = logging.getLogger(__name__)

class CancerBotClient:

    def __init__(self):
        # The Discord Client
        self.client = discord.Client()

        # The Bot Client Token
        self.token: str = None

        self.server_manager = ServerManager()

        self.events = []

        self._register_discord_events()

    def _register_discord_events(self):
        client = self.client

        @client.event
        async def on_message(message: discord.Message):
            log.debug('Received Message')

        @client.event
        async def on_server_join(server: discord.Server):
            log.debug('A new server %s has been joined', server.name)
            self.server_manager.add(server)

        @client.event
        async def on_server_remove(server: discord.Server):
            log.debug('Server %s has been removed', server.name)
            self.server_manager.remove(server)

        @client.event
        async def on_server_update(server: discord.Server):
            # TODO: This might or might not need to be handled.
            #       I need to have a better understanding of how
            #       the discord client updates this. Like, does it return
            #       a new object or does it just modify the reference?
            log.debug('Server %s has been updated')

        @client.event
        async def on_server_available(server: discord.Server):
            """
            This event is fired when ever a server has
            existed in the server cache, but has become available
            again.

            For Example: When the bot has been restarted this is called
            for all previously connected servers.
            """
            log.debug('The server %s has become available', server.name)
            self.server_manager.add(server)

        async def on_server_unavailable(server: discord.Server):
            log.debug('The server %s has become unavailable', server.name)
            self.server_manager.remove(server)

    def run(self, token: str):
        self.token = token

        self.client.run(token)

    def event(self, func, *args, **kwargs):
        """
        Decorator for cancer bot events.
        Any event that should be executed by 
        the bot should be decorated with this.

        The discord client will then be available to the event,
        on event execution.

        TODO: I dont think an event needs the entire client available
        to them, but if it does, the event needs some better context
        on the server the event is happening on.
        """
        def new_func():
            return func(self.client)

        self.events.append(new_func)

        return new_func
# pylint: disable=W0612

import os
import sys
import logging

import discord

log = logging.getLogger(__name__)

class CancerBotClient:

    def __init__(self):
        # The Discord Client
        self.client = discord.Client()

        # The Bot Client Token
        self.token = None

        # TODO: This needs to be with the ServerContext
        self.cancer_level = 1

        self.events = []

        self._register_discord_events()

    def _register_discord_events(self):
        client = self.client

        @client.event
        async def on_message(message: discord.Message):
            log.debug('Received Message')

        @client.event
        async def on_server_join(server: discord.Server):
            # TODO Add Server join impl
            log.debug('New Server Added')

        @client.event
        async def on_server_remove(server: discord.Server):
            # TODO Add Server remove impl
            log.debug('Server Removed')

        @client.event
        async def on_server_update(server: discord.Server):
            # TODO Add server update impl
            log.debug('Server Updated')

        @client.event
        async def on_server_available(server: discord.Server):
            """
            This event is fired when ever a server has
            existed in the server cache, but has become available
            again.

            For Example: When the bot has been restarted this is called
            for all previously connected servers.

            # TODO: Impl
            """
            log.debug('Server Now Available')

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
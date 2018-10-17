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

        self.server_manager = ServerManager(self.client)

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
            # Temporarily Pass Events here
            self.server_manager.add(server, self.events)

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
            # Temporarily Pass Events here
            await self.server_manager.add(server, self.events)

        async def on_server_unavailable(server: discord.Server):
            log.debug('The server %s has become unavailable', server.name)
            self.server_manager.remove(server)

    def run(self, token: str):
        self.token = token

        self.client.run(token)

    def event(self, cancer_level, schedule):
        """
        Decorator for cancer bot events.
        Any event that should be executed by 
        the bot should be decorated with this.

        The discord client will then be available to the event,
        on event execution.
        """

        def decorated(func):
            # Hack for now to try and make this 
            # prototype work
            # test = {
            #     'func': func,
            #     'cancer_level': cancer_level,
            #     'schedule': schedule
            # }
            self.events.append((func, schedule))

        return decorated
        #     def wrapper(*args, **kwargs):
        #         func(self.client, None)
        #     return wrapper

        # self.events.append(decorated)

        # return decorated
        #     return func(self.client)

        # self.events.append(new_func)

        # return new_func
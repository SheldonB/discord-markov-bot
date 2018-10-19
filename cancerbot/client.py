# pylint: disable=W0612

import os
import sys
import logging

import discord
from discord.ext.commands import Bot as BotClient

from cancerbot.server import ServerManager
from cancerbot.event_manager import EventManager

log = logging.getLogger(__name__)

description = """This is a bot that perpetuates cancer to your Discord Server"""


class CancerBotClient:

    def __init__(self):

        # The Discord Client
        self.client = BotClient(command_prefix='!cancer ', description=description)

        # The Bot Client Token
        self.token: str = None

        self.server_manager = ServerManager(self)

        self.event_manager = EventManager(self)

        self._register_discord_events()


    def _register_discord_events(self):
        client = self.client

        @client.event
        async def on_message(message: discord.Message):
            await client.process_commands(message)

        @client.event
        async def on_server_join(server: discord.Server):
            log.info('A new server %s has been joined', server.name)
            await self.server_manager.add(server)

        @client.event
        async def on_server_remove(server: discord.Server):
            log.info('Server %s has been removed', server.name)
            self.server_manager.remove(server)

        @client.event
        async def on_server_update(server: discord.Server):
            """
            TODO: This might or might not need to be handled.
                  I need to have a better understanding of how
                  the discord client updates this. Like, does it return
                  a new object or does it just modify the reference?
            """
            log.info('Server %s has been updated')

        @client.event
        async def on_server_available(server: discord.Server):
            """
            This event is fired when ever a server has
            existed in the server cache, but has become available
            again.

            For example, when the bot has been restarted this is called
            for all previously connected servers.
            """
            log.info('The server %s has become available', server.name)
            await self.server_manager.add(server)

        @client.event
        async def on_server_unavailable(server: discord.Server):
            log.info('The server %s has become unavailable', server.name)
            self.server_manager.remove(server)
        
        @client.command()
        async def level(level: int):
            # TODO Impl
            await client.say('Blah')

        @client.command()
        async def start():
            # TODO Impl
            print('Starting')

        @client.command()
        async def stop():
            #TODO Impl
            print('Stopping')

    def get_discord_client(self):
        return self.client

    def get_server_manager(self):
        return self.server_manager

    def get_event_manager(self):
        return self.event_manager

    def run(self, token: str):
        """
        Run the Cancer Bot.

        :param token: The token provided by the discord application api.
        """
        self.token = token

        self.client.run(token)

    def event(self, cancer_level, schedule):
        """
        Decorator for cancer bot events.
        Any event that should be executed by 
        the bot should be decorated with this.

        The discord client object, and the server object
        will then be available to the event function.
        """

        def decorated(func):
            self.event_manager.register((func, schedule, cancer_level))

        return decorated
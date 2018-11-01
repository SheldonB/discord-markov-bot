import time
import asyncio
import logging
import threading

import discord

from cancerbot import datastore, markov

log = logging.getLogger(__name__)


class ServerContext:
    """
    The Server Context with the client this server is 
    using to communicate, and the server itself.

    :param client: The CancerBotClient the server is using, doing this
    could allow for multiple clients to be spun up in the future, but
    we are only using one right now.

    :param server: The server this context is pertaining too.
    """
    def __init__(self, client, server):
        self.client = client

        self.server = server

        self.markov_manager = markov.MarkovManager()

    # TODO: This is going to be temporary till
    # a better way to handle server initialization
    # is determined, cant really do this in the
    # constructor since is it async
    async def init(self):

        if self.is_new_server():
            datastore.update_server(self.server)

            for user in self.server.members:
                datastore.add_user(user)

            log.debug('New Server [%s]. Downloading last 10,000 messages', self.server.name)
            await self._seed_messages()
            
        else:
            datastore.update_server(self.server)

            for user in self.server.members:
                datastore.add_user(user)

    def is_new_server(self):
        return datastore.does_server_exist(self.server)

    async def _seed_messages(self):
        # TODO: Figure out better way to handle channels
        # This will just get the first text channel in the channel list, which the user
        # could not want.
        channel = discord.utils.get(self.server.channels, type=discord.ChannelType.text)
        discord_client = self.client.get_discord_client()

        async for message in discord_client.logs_from(channel, limit=10000):
            datastore.add_message(message)

    def get_server(self):
        return self.server


class ServerManager:
    def __init__(self, client):
        """
        The client that is using this server manager
        instance.
        """
        self.client = client

        """
        A map that represents all connected servers for
        this instance of a server manager.

        The map uses the id of the server as the key, and the
        server context is the value.
        """
        self.connected_servers = {}

    def get_server_context(self, server):
        return self.connected_servers.get(server.id)

    async def add(self, server):
        """
        Create a new server context object and add it
        to the connected_servers map.

        :param server: The discord server object.
        """
        context = ServerContext(self.client, server)

        self.connected_servers[server.id] = context

        await context.init()

    def remove(self, server):
        """
        
        """
        if server.id in self.connected_servers:
            del self.connected_servers[server.id]

import time
import asyncio
import logging
import threading

from discord import Server

import cancerbot.schedule as schedule

log = logging.getLogger(__name__)


class ServerContext:
    def __init__(self, server: Server, discord_client):
        self.discord_client = discord_client

        self.server = server

    def get_server(self):
        return self.server


class ServerManager:
    def __init__(self, client):
        # this is the client that is using the server manager
        self.client = client

        # Store the ServerContext as a map from the
        # server id to the context object.
        self.servers = {}

    def get_server_context(self, server: Server):
        return self.servers.get(server.id)

    def add(self, server: Server):
        context = ServerContext(server, self.client.get_discord_client())
        self.servers[server.id] = context

    def remove(self, server: Server):
        if server.id in self.servers:
            del self.servers[server.id]

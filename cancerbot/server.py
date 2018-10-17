import time
import logging
import threading

from discord import Server

import cancerbot.schedule as schedule

log = logging.getLogger(__name__)

class ServerContext:
    def __init__(self, server: Server, client, cancer_lvl=1, events=[]):
        self.client = client

        self.server = server

        self._cancer_level = cancer_lvl

        self.events = events

        for event in events:
            async def wrapper():
                await event[0](self.client, self.server)
            test = wrapper
            event[1].do(test)

    # Each server will have a schedule of events that are
    # registered to it on creation or level change
    async def _run_schedule(self, interval=1):
        while True:
            await schedule.run_pending_async()
            # time.sleep(interval)

    def getServer(self):
        return self.server

    @property
    def cancer_level(self):
        return self._cancer_level


class ServerManager:
    def __init__(self, client):
        self.client = client

        self.servers: list = []

    async def add(self, server: Server, events: list):
        context = ServerContext(server, self.client, events=events)
        self.servers.append(context)

        await context._run_schedule()


    def remove(self, server: Server):
        for context in self.servers:
            # I think this will work?
            if context.getServer() == server:
                self.servers.remove(context)

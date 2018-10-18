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
            func =  event[0]
            schedule = event[1]

            schedule.do(self._gen_wrapper(func))

    def _gen_wrapper(self, func):
        """
        This is a temporary function that is used to 
        generate the async wrapper function that is
        going to be scheduled. So its really a wrapper
        for our wrapper. But I would just declare this
        anonymously in the event scheduling but for some
        reason the references get weird, and it always
        wants to use a reference to the most recently created function.

        We might be able to handle this in the event wrapper itself,
        but this will work for now.
        """
        async def wrapper():
            await func(self.client, self.server)
        return wrapper

    # Each server will have a schedule of events that are
    # registered to it on creation or level change
    async def _run_schedule(self, interval=1):
        while True:
            await schedule.run_pending_async()
            time.sleep(interval)

    def get_server(self):
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
            if context.get_server() == server:
                self.servers.remove(context)

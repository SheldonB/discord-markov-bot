import time
import logging
import threading

import schedule

from discord import Server

log = logging.getLogger(__name__)

class ServerContext:
    def __init__(self, server: Server, client, cancer_lvl=1, events=[]):
        self.client = client

        self.server = server

        self._cancer_level = cancer_lvl

        self.events = events

        # for event in events:
            # async def wrapper():
            #     await event['func'](self.client, self.server)

            # event['schedule'].do(wrapper)


    # Each server will have a schedule of events that are
    # registered to it on creation or level change
    async def _run_schedule(self, interval=10):
        # cease_run = threading.Event()

        # class ScheduleThread(threading.Thread):
        #     @classmethod
        #     async def run(cls):
        #         while not cease_run.is_set():
        #             # schedule.run_pending()
        #             await self.events[0]['func'](self.client, self.server)
        #             time.sleep(interval)
        
        # continuous_thread = ScheduleThread()
        # await continuous_thread.start()

        # return cease_run
        await self.events[0]['func'](self.client, self.server)

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

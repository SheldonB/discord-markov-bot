import time
import asyncio
import logging
import threading

from discord import Server

import cancerbot.schedule as schedule

log = logging.getLogger(__name__)


class ServerContext:
    def __init__(self, server: Server, discord_client, event_manager, cancer_lvl=1):
        self.discord_client = discord_client

        self.server = server

        self.event_manager = event_manager

        self._cancer_level = cancer_lvl

        self.events = self.event_manager.get_events(cancer_lvl)

        self._schedule_events()

        self.should_cancel = False

    def _schedule_events(self):
        for event in self.events:
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
            await func(self.discord_client, self.server)
        return wrapper

    async def start_async(self, interval=1):
        while True:
            # If the sever had been stopped,
            # cancel the loop, and reset the stopped flag.
            if self.should_cancel:
                self.should_cancel = False
                break

            await schedule.run_pending_async()
            await asyncio.sleep(interval)

    def stop(self):
        schedule.clear()
        self.should_cancel = True

    def get_server(self):
        return self.server

    def get_cancer_level(self):
        return self._cancer_level

    def set_cancer_level(self, value):
        """
        Change the cancer level of the bot.

        Note: this function has side effects right now,
        it will cancel all currently running events and 
        reschedule events at the new cancer level.
        """

        if value == self._cancer_level:
            return

        self._cancer_level = value

        # Clear all scheduled jobs as we 
        # are going to reschedule at a new level.
        schedule.clear()
        self.events = self.event_manager.get_events(value)
        self._schedule_events()


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
        context = ServerContext(server, self.client.get_discord_client(), event_manager=self.client.get_event_manager())
        self.servers[server.id] = context

    def remove(self, server: Server):
        if server.id in self.servers:
            del self.servers[server.id]

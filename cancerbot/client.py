import os
import sys
import logging

import discord

log = logging.getLogger(__name__)

class CancerBotClient:

    def __init__(self):
        # The Discord Client
        self.client = None

        # The Bot Client Token
        self.token = None

        self.cancer_level = 1

        self.events = []

    def _register_discord_events(self):
        client = self.client

        @client.event
        async def on_message(message: discord.Message):
            log.debug('Received Message')

    def run(self, token: str):
        self.token = token

        self.client = discord.Client()

        self._register_discord_events()

        self.client.run(token)

    def event(self, func, *args, **kwargs):
        """
        Decorator for cancer bot events.
        Any event that should be executed by 
        the bot should be decorated with this.

        The discord client will then be available to the event,
        on event execution.
        """
        def new_func():
            return func(self.client)

        self.events.append(new_func)

        return new_func
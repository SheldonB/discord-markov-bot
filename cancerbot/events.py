import logging
import asyncio

import schedule

from discord import Message, Client, Server

from cancerbot import cancerbot

log = logging.getLogger(__name__)

# This is simply a placeholder event showing what I went event creation
# to look like, this event will not work right now, and it only used for testing/debugging
@cancerbot.event(cancer_level=1, schedule=schedule.every(10).seconds)
async def test_event(client: Client, server: Server):
    for channel in server.channels:
        if channel.name == 'general':
            await client.send_message(channel, content='This is a test')
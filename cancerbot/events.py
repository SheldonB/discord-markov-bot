import logging
import asyncio

from discord import Message, Client, Server

from cancerbot import cancerbot
import cancerbot.schedule as schedule

log = logging.getLogger(__name__)

"""
 This is simply an example event showing how to create an event.

 To create an event simply create a function with the signature (client, server).
 And decorate it with the @cancerbot.event decorator. The decorator takes two arguments (cancer_level and schedule).
 The cancer_level is the level of cancer this event is and will only be ran at this level. The schedule is the schedule
 object you want this to run on. 

 The bot is using a modified version of this library: https://schedule.readthedocs.io
 Documentation for a schedule can be found there. The actual running of the event is handled
 by the bots scheduler.

@cancerbot.event(cancer_level=1, schedule=schedule.every(10).seconds)
async def test_event(client: Client, server: Server):
    for channel in server.channels:
        if channel.name == 'general':
            await client.send_message(channel, content='This is a test 1')
"""
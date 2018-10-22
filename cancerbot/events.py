import logging
import asyncio
import random

from discord import Message, Client, Server, ChannelType

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

def get_voice_channels(server: Server):
    """
    Get all voice channels for a server.
    """
    return [channel for channel in server.channels if channel.type == ChannelType.voice]


@cancerbot.event(cancer_level=1, schedule=schedule.every(5).minutes)
async def move_user_channel(client: Client, server: Server):
    """
    This event will move a random user from a random voice channel,
    to another random voice channel then move them back.

    Preconditions: Must have at least 2 voice channels on the server.
    """
    log.info('Running move user channel event on server(%s)', server.name)

    all_voice_channels = get_voice_channels(server)

    if len(all_voice_channels) < 2:
        log.debug('Their are not enough voice channels to execute this event on server(%s)', server.name)
        return

    non_empty_voice_channels = [voice_channel for voice_channel in all_voice_channels if len(voice_channel.voice_members) > 0]

    if len(non_empty_voice_channels) == 0:
        log.debug('No active voice channels to execute this event on server(%s)', server.name)
        return

    candidate_voice_channel = random.choice(non_empty_voice_channels)
    
    # TODO: Make sure that the member is not the bot, or is not a bot in general
    candidate_member = random.choice(candidate_voice_channel.voice_members)

    # Create a two sets of voice channels and take
    # the intersection to we dont transfer to the
    # same voice channel
    channels_to_transfer =  list(set(all_voice_channels) - set([candidate_voice_channel]))

    transfer_voice_channel = random.choice(channels_to_transfer)

    await client.move_member(candidate_member, transfer_voice_channel)

    await asyncio.sleep(3)

    await client.move_member(candidate_member, candidate_voice_channel)


@cancerbot.event(cancer_level=3, schedule=schedule.every(15).minutes)
async def flood_voice_channel(client: Client, server: Server):
    """
    This event will choose a random voice channel that
    has users currently connected to it, and then pop in
    and out of that channel a random amount of times.
    """
    log.debug('Running flood voice channel event on server (%s)', server.name)

    # Get all channels in the server that are voice channels.
    voice_channels = get_voice_channels(server)

    # Get all voice channels that at least has one person in it.
    non_empty_voice_channels = [voice_channel for voice_channel in voice_channels if len(voice_channel.voice_members) > 0]

    if len(non_empty_voice_channels) == 0:
        log.debug('Tried flooding the voice channels, but no users were connected.')
        return

    # Chose a random voice channel with people in it.
    candidate = random.choice(non_empty_voice_channels)

    num_times = random.randint(1, 10)

    log.debug('Flooding the channel %d times', num_times)

    times_tried = 0
    while times_tried < num_times:
        voice_client = await client.join_voice_channel(candidate)

        await asyncio.sleep(1)

        await voice_client.disconnect()

        await asyncio.sleep(1)

        times_tried = times_tried + 1

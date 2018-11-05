import asyncio
import logging

import markovify

from cancerbot import cancerbot

log = logging.getLogger(__name__)

"""
Just getting the discord client here so
that events can be registered against it.

Ultimately I would just like to add a wrapper command
in the CancerBotClient class, but I was having a little 
trouble getting that to work initially. That way we can
hide the actual discord client implementation from this.
"""
client = cancerbot.discord_client

def get_server_context_from_client_context(context):
    return cancerbot.server_manager.get_server_context(context.message.server)

@client.command(pass_context=True, help='The bot will say something')
async def say(context, user: str = None):
    server_context = get_server_context_from_client_context(context)

    if user is None:
        log.debug('Bot issued say command on server %s', server_context.server.name)

        sentence = server_context.markov.make_sentence_server()
    else:
        sentence = server_context.markov.make_sentence_user(user)

    if user is not None and sentence is None:
        await client.say('Unable to generate message. This user either does not exist, or has not sent enough messages.')
        return

    if sentence is None:
        await client.say('Unable to generate message. This is probably due to a lack of seed data.')
        return

    await client.say(sentence)



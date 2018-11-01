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
client = cancerbot.get_discord_client()

def get_server_context_from_client_context(context):
    return cancerbot.get_server_manager().get_server_context(context.message.server)

# Temporarily exposing this here so
# so the file wont be read every time the
# command is called
with open('./sanatized_data.txt') as f:
    text = f.read()

model = markovify.Text(text)

@client.command(help='The bot will say something')
async def say():
    sentence = model.make_sentence()
    await client.say(sentence)



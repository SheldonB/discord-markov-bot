import asyncio
import logging

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

MAX_LEVEL = 3
MIN_LEVEL = 1

def get_server_context_from_client_context(context):
    return cancerbot.get_server_manager().get_server_context(context.message.server)


@client.command(pass_context=True, help='Set the bot cancer level.')
async def level(context, level: int):
    server = context.message.server
    server_context = get_server_context_from_client_context(context)

    if level < MIN_LEVEL or level > MAX_LEVEL:
        await client.say('Cancer level must be between {} and {}'.format(MIN_LEVEL, MAX_LEVEL))
        return

    log.debug('Setting level for %s to %d', server.name, level)
    server_context.set_cancer_level(level)


@client.command(pass_context=True, help='Start the bot. Do this at your own risk.')
async def start(context):
    server_context = get_server_context_from_client_context(context)

    await client.say('Cancer Bot initiated. Hope you are ready ;)')

    await server_context.start_async()


@client.command(pass_context=True, help='Tired of the cancer? Stop it with this command.')
async def stop(context):
    server_context = get_server_context_from_client_context(context)

    server_context.stop()

    await client.say('Cancer Bot stopped. See you next time.')


@client.command(help='Get sung a lovely song.')
async def sing():
    await client.say('Im going to sing you a song :)')
    await asyncio.sleep(4)

    await client.say('Country Roads')
    await asyncio.sleep(2)
    await client.say('Take me home')
    await asyncio.sleep(2)
    await client.say('To the place I belong')
    await asyncio.sleep(2)
    await client.say('WEST VIRGINIA')
    await asyncio.sleep(2)
    await client.say('Mountain Momma')
    await asyncio.sleep(2)
    await client.say('Take me home')
    await asyncio.sleep(2)
    await client.say('Country Roads')



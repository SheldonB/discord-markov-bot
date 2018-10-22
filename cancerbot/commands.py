import asyncio
from cancerbot import cancerbot

client = cancerbot.get_discord_client()

@client.command()
async def level(level: int):
    print('Setting level')

@client.command()
async def start():
    await client.say('Cancer Bot initiated. Hope you are ready ;)')

@client.command()
async def stop():
    await client.say('Cancer Bot stopped. See you next time.')

@client.command()
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



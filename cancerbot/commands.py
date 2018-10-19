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
import os
import discord

client = discord.Client()

@client.event
async def on_message(message: discord.Message):
    if message.content.startswith('test'):
        await client.send_message(message.channel, 'TESTING')

token = os.environ['DISCORD_BOT_TOKEN']
client.run(token)
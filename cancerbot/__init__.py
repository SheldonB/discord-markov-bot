import os
import sys

import discord

from cancerbot import context, events

"""
This is the discord client that will be using to connect to the servers with.
This client should not be used directly, but if access is needed, it should be
done through the context object.
"""
_client = discord.Client()


"""
The overlying context of what our app is, this will have access to the client,
and any other information that could be important about our application.
"""
context = context.BotContext(_client)


"""
Register our events against the client.
"""
events.init(_client)


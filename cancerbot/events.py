import logging

from discord import Message, Client

log = logging.getLogger(__name__)

def init(client: Client):
	@client.event
	async def on_message(message: Message):
		if message.content.startswith('!cancer-level'):
			await client.send_message(message.channel, 'TESTING')

class Event:
	def __init__(self):
		self.trigger_level = 1

	def run(self):
		raise NotImplementedError


def TestEvent(Event):
	def __init__(self):
		self.trigger_level = 1
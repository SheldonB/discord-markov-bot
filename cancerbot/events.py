import logging

from discord import Message, Client
from cancerbot import cancerbot

log = logging.getLogger(__name__)

@cancerbot.event
def test_event(client: Client):
	log.info('Hello World')
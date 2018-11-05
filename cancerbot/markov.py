import logging

import markovify

from cancerbot import datastore

log = logging.getLogger(__name__)

class CustomMarkovText(markovify.Text):

    def _prepare_text(self, text):
        text = text.strip()

        if not text.endswith(('.', '?', '!')):
            text += '.'

        return text

    def sentence_split(self, text):
        lines = text.splitlines()

        text = ' '.join([self._prepare_text(line) for line in lines if line.strip()])

        return markovify.split_into_sentences(text)

class MarkovManager:

    ALL_KEY = '__ALL__'

    def __init__(self, server_context):
        self.server_context = server_context

        self.cache_chain = {}

    def make_sentence_server(self):
        log.debug('Generating Markov Sentence based off entire server text')

        if self.ALL_KEY not in self.cache_chain:
            log.debug('Markov Chain for server %s not found in cache. Generating it.', self.server_context.server.name)

            messages = datastore.get_messages_by_server(self.server_context.server)

            bot_user = self.server_context.client.discord_client.user

            # Get Messages that are a certain length, not a command, and not from the bot itself.
            content = [message['content'] for message in messages
                if message['user_id'] != bot_user.id and len(message['content']) > 15 and not message['content'].startswith('!')]

            chain = CustomMarkovText(content)

            self.cache_chain[self.ALL_KEY] = chain

        return self.cache_chain[self.ALL_KEY].make_sentence()


    def make_sentence_user(self, user):
        log.debug('Generating Markov Sentence for user %s', user)
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

    def __init__(self, server):
        self.server = server

        self.cache_chain = {}

    def make_sentence_server(self):
        log.debug('Generating Markov Sentence based off entire server text')

        if self.ALL_KEY not in self.cache_chain:
            messages = datastore.get_messages_by_server(self.server)

            content = [message['content'] for message in messages]            

            chain = CustomMarkovText(content)

            self.cache_chain[self.ALL_KEY] = chain

        return self.cache_chain[self.ALL_KEY].make_sentence()



    def make_sentence_user(self, user):
        log.debug('Generating Markov Sentence for user %s', user)
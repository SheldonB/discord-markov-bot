import random
import logging

import markovify

from markovbot import datastore

log = logging.getLogger(__name__)


class CustomMarkovText(markovify.Text):

    def _prepare_text(self, text):
        text = text.strip()

        if not text.endswith(('.', '?', '!')):
            text += '.'

        return text

    def sentence_split(self, text):
        text = self._prepare_text(text)

        return markovify.split_into_sentences(text)


class MarkovManager:

    ALL_KEY = '__ALL__'
    MAX_CACHE_SIZE = 3

    def __init__(self, server_context):
        self.server_context = server_context

        self.server_cache = None

        self.user_cache_chain = {}

        random.seed()

    def _manage_cache(self):
        num_cache_entries = len(self.user_cache_chain)

        if num_cache_entries >= self.MAX_CACHE_SIZE:
            # Chose a random entry from the cache to evict.
            # This will probably be LRU eventually.
            eviction_candidate = random.choice(list(self.user_cache_chain.keys()))
            log.info('User cache has exceeded max size of %d, evicting chain for user id %s',
                     self.MAX_CACHE_SIZE, eviction_candidate)

            del self.user_cache_chain[eviction_candidate]

    def make_sentence_server(self):
        log.debug('Generating Markov Sentence based off entire server text')

        if self.server_cache is None:
            log.debug('Markov Chain for server %s not found in cache. Generating it.', self.server_context.server.name)

            messages = datastore.get_messages_by_server(server_id=self.server_context.server.id)

            content = [message['content'] for message in messages]

            chain = CustomMarkovText(content)

            self.server_cache = chain

        return self.server_cache.make_short_sentence(500, min_chars=100, tries=150)

    def make_sentence_user(self, user):
        user_id = user['id']

        if user_id not in self.user_cache_chain:
            log.debug('Markov Chain for user %s from server %s not found in cache. Generating it.', user['name'], self.server_context.server.name)

            self._manage_cache()

            messages = datastore.get_messages_by_user(user_id=user_id)

            content = [message['content'] for message in messages]

            if len(content) == 0:
                return None

            chain = CustomMarkovText(content)

            self.user_cache_chain[user_id] = chain

        return self.user_cache_chain[user_id].make_short_sentence(500, min_chars=100, tries=150)

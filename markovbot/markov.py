import random
import logging

from typing import List

import markovify
from discord import Message, Guild

from markovbot import persistence

log = logging.getLogger(__name__)


class MarkovGenerationException(Exception):
    pass

class CustomMarkovText(markovify.Text):

    def _prepare_text(self, text):
        text = text.strip()

        if not text.endswith(('.', '?', '!')):
            text += '.'

        return text

    def sentence_split(self, text):
        text = self._prepare_text(text)

        return markovify.split_into_sentences(text)


def make_sentence(guild: Guild) -> str:
    chain_as_dict = persistence.get_chain(guild)
    chain = CustomMarkovText.from_dict(chain_as_dict)
    
    sentence = chain.make_short_sentence(500, min_chars=125, tries=300)

    if not sentence:
        log.warn('Sentence was unable to be generated for Guild(id=%s, name=%s). Probably not enough data', guild.id, guild.name)
        raise MarkovGenerationException

    return sentence


def generate_chain(messages: List[Message]) -> markovify.Text:
    log.info('Generating new Markov Chain')
    content = [message.content for message in messages]
    return CustomMarkovText(content)


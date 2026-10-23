import logging

from typing import List

import markovify
from discord import Message, Guild

from markovbot import persistence

log = logging.getLogger(__name__)


class MarkovGenerationException(Exception):
    pass


class MarkovTrainingException(Exception):
    """The input contains no text that can train a Markov model."""


class CustomMarkovText(markovify.Text):

    def _prepare_text(self, text):
        text = text.strip()

        if not text.endswith(('.', '?', '!')):
            text += '.'

        return text

    def sentence_split(self, text):
        text = self._prepare_text(text)

        return markovify.split_into_sentences(text)

    def generate_corpus(self, text):
        corpus = list(super().generate_corpus(text))
        if not corpus:
            raise MarkovTrainingException('No trainable sentences in the supplied messages.')
        return corpus


def make_sentence(guild: Guild, user_id: int = None) -> str:
    chain_as_dict = persistence.get_chain(guild, user_id)
    if chain_as_dict is None:
        raise MarkovGenerationException('No saved chain for the requested server or user.')

    chain = CustomMarkovText.from_dict(chain_as_dict)

    sentence = chain.make_short_sentence(500, min_chars=125, tries=300)

    if not sentence:
        log.warning(
            'Sentence was unable to be generated for Guild(id=%s, name=%s), '
            'user_id=%s. Probably not enough data',
            guild.id, guild.name, user_id,
        )
        raise MarkovGenerationException

    return sentence


def generate_chain(messages: List[Message]) -> markovify.Text:
    log.info('Generating new Markov Chain')
    content = [message.content for message in messages]
    return CustomMarkovText(content)

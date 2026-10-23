import logging
import os
import re
import unicodedata
from collections import OrderedDict
from typing import List

import markovify
from discord import Message, Guild
from markovify.splitters import is_sentence_ender
from markovify.text import DEFAULT_MAX_OVERLAP_RATIO, DEFAULT_MAX_OVERLAP_TOTAL

from markovbot import persistence

log = logging.getLogger(__name__)

_CODE_BLOCK = re.compile(r'```.*?(?:```|\Z)|~~~.*?(?:~~~|\Z)', re.DOTALL)
_INLINE_CODE = re.compile(r'`[^`\n]*`')
_MARKDOWN_LINK = re.compile(r'\[([^\]\n]+)\]\(https?://[^\s)]+\)', re.IGNORECASE)
_URL = re.compile(r'<(?:https?://|www\.)[^\s<>]+>|(?:https?://|www\.)[^\s<>]+', re.IGNORECASE)
_CUSTOM_EMOJI = re.compile(r'<a?:([A-Za-z0-9_]+):[0-9]+>')
_CHANNEL_MENTION = re.compile(r'<#[0-9]+>')
_LOG_LINE = re.compile(
    r'^\s*(?:\[?\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}'
    r'|\[?\d{2}:\d{2}:\d{2}(?:[.,]\d+)?\]?\s+'
    r'|\[(?:DEBUG|INFO|WARN(?:ING)?|ERROR|CRITICAL|TRACE)\]'
    r'|(?:DEBUG|INFO|WARN(?:ING)?|ERROR|CRITICAL|TRACE)\s*[:|]'
    r'|File "[^"]+", line \d+)'
)
_SENTENCE_END = re.compile(r'''(\S*?[.!?])(["')\]]*)[^\S\n]+''')
_PUNCTUATION = str.maketrans({
    '\u2018': "'", '\u2019': "'", '\u201c': '"', '\u201d': '"',
    '\u2026': '...', '\u200b': '', '\ufeff': '',
})
_MODEL_CACHE_SIZE = 128
_model_cache = OrderedDict()


def _int_setting(name, default, minimum=1, maximum=None):
    value = int(os.environ.get(name, default))
    if value < minimum or (maximum is not None and value > maximum):
        raise ValueError(f'{name} must be at least {minimum}' + (
            f' and at most {maximum}.' if maximum is not None else '.'
        ))
    return value


def clear_model_cache():
    _model_cache.clear()


class MarkovGenerationException(Exception):
    pass


class MarkovTrainingException(Exception):
    """The input contains no text that can train a Markov model."""


class CustomMarkovText(markovify.Text):

    def _prepare_text(self, text):
        text = unicodedata.normalize('NFC', text).translate(_PUNCTUATION)
        text = _CODE_BLOCK.sub('\n', text)
        text = _INLINE_CODE.sub(' ', text)
        text = _MARKDOWN_LINK.sub(r'\1', text)
        # Keep punctuation after a bare URL so removing it does not join sentences.
        text = _URL.sub(lambda match: (
            ' ' if match.group().startswith('<') else
            ' ' + match.group()[len(match.group().rstrip('.,!?;:')):]
        ), text)
        text = re.sub(r'[^\S\n]+([.!?,;])', r'\1', text)
        text = _CUSTOM_EMOJI.sub(r':\1:', text)
        text = _CHANNEL_MENTION.sub(' ', text)

        lines = []
        in_traceback = False
        for line in text.splitlines():
            if line.strip().startswith('Traceback (most recent call last):'):
                in_traceback = True
                lines.append('')
                continue
            if not line.strip():
                in_traceback = False
            if in_traceback or _LOG_LINE.match(line):
                lines.append('')
            else:
                lines.append(' '.join(line.split()))

        return '\n'.join(lines).strip()

    def sentence_split(self, text):
        text = self._prepare_text(text)
        sentences = []
        for line in text.splitlines():
            start = 0
            for match in _SENTENCE_END.finditer(line):
                word = match.group(1)
                if len(word) == 1 or is_sentence_ender(word):
                    end = match.end(2)
                    sentences.append(line[start:end].strip())
                    start = match.end()
            if line[start:].strip():
                sentences.append(line[start:].strip())
        return sentences

    def test_sentence_input(self, sentence):
        # Chat punctuation is valid training data, including quotes and emoticons.
        return len(sentence.split()) > 1

    def generate_corpus(self, text):
        corpus = list(super().generate_corpus(text))
        if not corpus:
            raise MarkovTrainingException('No trainable sentences in the supplied messages.')
        return corpus

    def make_short_sentence(self, max_chars, min_chars=0, *, tries=300, max_words=100):
        """Bound both candidate count and walk length, retaining originality checks."""
        for _ in range(tries):
            words = []
            length = 0
            for word in self.chain.gen():
                length += len(word) + bool(words)
                if length > max_chars or len(words) >= max_words:
                    break
                words.append(word)
            else:
                if words and length >= min_chars and self.test_sentence_output(
                    words, DEFAULT_MAX_OVERLAP_RATIO, DEFAULT_MAX_OVERLAP_TOTAL,
                ):
                    return self.word_join(words)
        return None


def _get_model(guild, user_id):
    key = (guild.id, user_id)
    revision = persistence.get_chain_revision(guild)
    cached = _model_cache.get(key)
    if cached is not None and cached[0] == revision:
        _model_cache.move_to_end(key)
        return cached[1]

    _model_cache.pop(key, None)
    chain_as_dict = persistence.get_chain(guild, user_id)
    if chain_as_dict is None:
        raise MarkovGenerationException('No saved chain for the requested server or user.')

    chain = CustomMarkovText.from_dict(chain_as_dict)
    chain.compile(inplace=True)
    _model_cache[key] = (revision, chain)
    if len(_model_cache) > _MODEL_CACHE_SIZE:
        _model_cache.popitem(last=False)
    return chain


def make_sentence(guild: Guild, user_id: int = None) -> str:
    min_chars = _int_setting('MARKOV_MIN_CHARS', 20, minimum=0)
    max_chars = _int_setting('MARKOV_MAX_CHARS', 500, maximum=2000)
    if min_chars > max_chars:
        raise ValueError('MARKOV_MIN_CHARS must not exceed MARKOV_MAX_CHARS.')
    tries = _int_setting('MARKOV_GENERATION_TRIES', 300)
    max_words = _int_setting('MARKOV_MAX_WORDS', 100)
    chain = _get_model(guild, user_id)
    sentence = chain.make_short_sentence(
        max_chars, min_chars=min_chars, tries=tries, max_words=max_words,
    )

    if not sentence:
        log.warning(
            'Sentence was unable to be generated for Guild(id=%s, name=%s), '
            'user_id=%s. Probably not enough data',
            guild.id, guild.name, user_id,
        )
        raise MarkovGenerationException

    return sentence


def generate_chain(messages: List[Message], *, user_model=False) -> markovify.Text:
    log.info('Generating new Markov Chain')
    setting = 'MARKOV_USER_STATE_SIZE' if user_model else 'MARKOV_STATE_SIZE'
    state_size = _int_setting(setting, 1 if user_model else 2, maximum=3)
    content = [message.content for message in messages]
    return CustomMarkovText(content, state_size=state_size)

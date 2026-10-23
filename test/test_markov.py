import os
import unittest
from random import Random
from types import SimpleNamespace
from unittest import mock

import markovify

from markovbot import markov, persistence
from markovbot.markov import CustomMarkovText, MarkovGenerationException, MarkovTrainingException, generate_chain, make_sentence
from .utils import MockGuild, get_guild, isolate_persistence


CHAT = [
    'we should play the new game together after dinner tonight',
    'we could watch the new movie together before lunch tomorrow',
    'they should watch the old game together before dinner tomorrow',
    'they could play the old movie together after lunch tonight',
    'our friends want to play the new game before lunch today',
    'your friends want to watch the old movie after dinner today',
]

LONG_CHAT = [
    '<@123456789012345678> Every morning we gather near the ancient oak tree before we wander through '
    'the bustling marketplace to find fresh vegetables and share our stories about the changing seasons.',
    '<@123456789012345678> Every evening we gather near the peaceful river bank before we wander through '
    'the quiet village to find warm bread and share our dreams about the distant mountains.',
]

LOWERCASE_CHAT = [
    'every morning we gather near the ancient oak tree. then we wander through the bustling marketplace '
    'to find fresh vegetables. finally we share our stories about the changing seasons.',
    'every evening we gather near the peaceful river bank. then we wander through the quiet village '
    'to find warm bread. finally we share our dreams about the distant mountains.',
]


def train(texts=CHAT, **kwargs):
    return generate_chain([SimpleNamespace(content=text) for text in texts], **kwargs)


class GenerationStyleTest(unittest.TestCase):
    def setUp(self):
        isolate_persistence(self)
        markov.clear_model_cache()
        self.addCleanup(markov.clear_model_cache)
        environment = mock.patch.dict(os.environ, {}, clear=True)
        environment.start()
        self.addCleanup(environment.stop)
        self.guild = get_guild()

    def save_models(self, texts):
        persistence.create_chain(self.guild, train(texts).to_dict(), {
            456: train(texts, user_model=True).to_dict(),
        })

    def test_default_server_and_user_replies_keep_the_previous_length_floor(self):
        self.save_models(CHAT + LONG_CHAT)
        for user_id in (None, 456):
            with self.subTest(user_id=user_id):
                with mock.patch('markovify.chain.random', Random(42)):
                    replies = [make_sentence(self.guild, user_id) for _ in range(50)]
                self.assertTrue(all(125 <= len(reply) <= 500 for reply in replies))
                self.assertTrue(all(reply not in CHAT + LONG_CHAT for reply in replies))

    def test_user_models_keep_two_words_of_context_by_default(self):
        self.save_models(LONG_CHAT)
        self.assertEqual(persistence.get_chain(self.guild)['state_size'], 2)
        self.assertEqual(persistence.get_chain(self.guild, 456)['state_size'], 2)

    def test_lowercase_clauses_can_still_generate_long_recombined_replies(self):
        self.save_models(LOWERCASE_CHAT)
        for user_id in (None, 456):
            with self.subTest(user_id=user_id):
                with mock.patch('markovify.chain.random', Random(42)):
                    sentence = make_sentence(self.guild, user_id)
                self.assertGreaterEqual(len(sentence), 125)
                self.assertNotIn(sentence, LOWERCASE_CHAT)

    def test_sparse_models_do_not_silently_return_short_replies_by_default(self):
        self.save_models(CHAT)
        for user_id in (None, 456):
            with self.subTest(user_id=user_id):
                with self.assertRaises(MarkovGenerationException):
                    make_sentence(self.guild, user_id)

    def test_shorter_replies_and_one_word_context_remain_explicit_options(self):
        with mock.patch.dict(os.environ, {'MARKOV_MIN_CHARS': '20', 'MARKOV_USER_STATE_SIZE': '1'}):
            self.save_models(CHAT)
            with mock.patch('markovify.chain.random', Random(42)):
                sentence = make_sentence(self.guild, 456)
        self.assertGreaterEqual(len(sentence), 20)
        self.assertLess(len(sentence), 125)
        self.assertEqual(persistence.get_chain(self.guild, 456)['state_size'], 1)


class MarkovTest(unittest.TestCase):

    def setUp(self):
        markov.clear_model_cache()
        self.addCleanup(markov.clear_model_cache)
        self.settings_patch = mock.patch.dict(os.environ, {
            'MARKOV_MIN_CHARS': '125', 'MARKOV_MAX_CHARS': '500',
            'MARKOV_GENERATION_TRIES': '300', 'MARKOV_MAX_WORDS': '100',
            'MARKOV_STATE_SIZE': '2', 'MARKOV_USER_STATE_SIZE': '2',
            'MARKOV_SPLIT_LOWERCASE': '0',
        })
        self.settings_patch.start()
        self.addCleanup(self.settings_patch.stop)

    def test_prepare_text_trims_whitespace_without_adding_punctuation(self):
        text = "  Hello world  "

        result = CustomMarkovText(["seed text"])._prepare_text(text)

        self.assertEqual(result, "Hello world")

    def test_prepare_text_keeps_trailing_punctuation(self):
        text = "Hello world!"

        result = CustomMarkovText(["seed text"])._prepare_text(text)

        self.assertEqual(result, "Hello world!")

    def test_lowercase_splitting_is_optional_and_keeps_quotes_and_newline_boundaries(self):
        model = train()
        text = (
            'hello world. are you online? i am ready\n'
            'she said "good game!" let us play\nDr. Smith likes games'
        )
        self.assertEqual(model.sentence_split(text), [
            'hello world. are you online? i am ready',
            'she said "good game!" let us play', 'Dr. Smith likes games',
        ])
        with mock.patch.dict(os.environ, {'MARKOV_SPLIT_LOWERCASE': '1'}):
            self.assertEqual(model.sentence_split(text), [
                'hello world.', 'are you online?', 'i am ready',
                'she said "good game!"', 'let us play', 'Dr. Smith likes games',
            ])
        with mock.patch.dict(os.environ, {'MARKOV_SPLIT_LOWERCASE': '2'}):
            with self.assertRaises(ValueError):
                model.sentence_split(text)

    def test_cleanup_keeps_user_mentions_ids_slang_and_emoji(self):
        model = train([
            '  hey\t<@123456789012345678> <@!234567890123456789> '
            '345678901234567890 you’re “ready” (right)? 😂 <:party:456789012345678901> '
            '<#567890123456789012> [the guide](https://example.com/guide) '
            'https://example.com/data www.example.org <https://example.net>\n'
            '```python\nprint("do not learn this")\n```\n'
            '`some_code()`\n'
            '2026-10-22 12:34:56 ERROR noisy service log\n'
            '[INFO] another noisy log\n'
            'Traceback (most recent call last):\n'
            '  File "app.py", line 1\n'
            '    failing_code()\n'
            'ValueError: broken\n\n'
            'lol   let’s go',
        ])
        text = '\n'.join(' '.join(words) for words in model.parsed_sentences)
        self.assertEqual(text,
            'hey <@123456789012345678> <@!234567890123456789> '
            '345678901234567890 you\'re "ready" (right)?\n😂 :party: the guide\n'
            "lol let's go"
        )

    def test_cleanup_keeps_sentence_punctuation_after_urls(self):
        self.assertEqual(train().sentence_split(
            'read https://example.com. Then play games'
        ), ['read.', 'Then play games'])

    def test_parentheses_quotes_and_emoticons_are_trainable(self):
        texts = ['that works (usually)', 'she said "good game"', 'this is fine :)']
        self.assertEqual(train(texts).parsed_sentences, [text.split() for text in texts])

    def test_messages_remain_separate_training_sequences(self):
        self.assertEqual(train(['first message', 'second message']).parsed_sentences,
                         [['first', 'message'], ['second', 'message']])

    def test_generate_chain_returns_custom_markov_text(self):
        messages = [SimpleNamespace(content="Hello there")]

        result = generate_chain(messages)

        self.assertIsInstance(result, CustomMarkovText)

    def test_generate_chain_rejects_empty_or_unusable_corpora(self):
        for messages in ([], [SimpleNamespace(content='```no usable code```')],
                         [SimpleNamespace(content='https://example.com www.example.org')]):
            with self.subTest(messages=messages):
                with self.assertRaises(MarkovTrainingException):
                    generate_chain(messages)

    def test_generate_chain_does_not_hide_unexpected_errors(self):
        with mock.patch.object(CustomMarkovText, 'sentence_split', side_effect=RuntimeError('Unexpected failure')):
            with self.assertRaises(RuntimeError):
                generate_chain([SimpleNamespace(content='Some valid text')])

    def test_make_sentence_success(self):
        guild = get_guild()
        chain_dict = {"state": "data"}
        chain_mock = mock.Mock()
        chain_mock.make_short_sentence.return_value = "Generated sentence"

        with mock.patch("markovbot.markov.persistence.get_chain", return_value=chain_dict):
            with mock.patch.object(CustomMarkovText, "from_dict", return_value=chain_mock) as from_dict_mock:
                result = make_sentence(guild)

        from_dict_mock.assert_called_once_with(chain_dict)
        chain_mock.compile.assert_called_once_with(inplace=True)
        chain_mock.make_short_sentence.assert_called_once_with(500, min_chars=125, tries=300, max_words=100)
        self.assertEqual(result, "Generated sentence")

    def test_make_sentence_failure_raises_exception(self):
        guild = get_guild()
        chain_dict = {"state": "data"}
        chain_mock = mock.Mock()
        chain_mock.make_short_sentence.return_value = None

        with mock.patch("markovbot.markov.persistence.get_chain", return_value=chain_dict):
            with mock.patch.object(CustomMarkovText, "from_dict", return_value=chain_mock):
                with self.assertRaises(MarkovGenerationException):
                    make_sentence(guild)

        chain_mock.make_short_sentence.assert_called_once_with(500, min_chars=125, tries=300, max_words=100)

    def test_make_sentence_selects_server_or_user_without_changing_generation_settings(self):
        guild = get_guild()
        for user_id in (None, 456):
            with self.subTest(user_id=user_id):
                model = mock.Mock()
                model.make_short_sentence.return_value = 'A generated sentence'
                with mock.patch('markovbot.markov.persistence.get_chain', return_value={'model': 'data'}) as get_chain:
                    with mock.patch.object(CustomMarkovText, 'from_dict', return_value=model):
                        self.assertEqual(make_sentence(guild, user_id), 'A generated sentence')
                get_chain.assert_called_once_with(guild, user_id)
                model.make_short_sentence.assert_called_once_with(500, min_chars=125, tries=300, max_words=100)

    def test_missing_chain_is_a_controlled_error(self):
        for user_id in (None, 456):
            with self.subTest(user_id=user_id):
                with mock.patch('markovbot.markov.persistence.get_chain', return_value=None) as get_chain:
                    with mock.patch.object(CustomMarkovText, 'from_dict') as from_dict:
                        with self.assertRaises(MarkovGenerationException):
                            make_sentence(get_guild(), user_id)
                get_chain.assert_called_once_with(get_guild(), user_id)
                from_dict.assert_not_called()

    def test_generation_retries_are_linear_and_reject_copied_training_text(self):
        model = train(['a single isolated training sentence'])
        with mock.patch.object(model.chain, 'gen', wraps=model.chain.gen) as generate:
            self.assertIsNone(model.make_short_sentence(500, min_chars=0, tries=7))
        self.assertEqual(generate.call_count, 7)

    def test_walks_stop_at_word_and_character_limits_even_without_an_end(self):
        model = train()
        for max_chars, max_words, moves in ((1000, 4, 15), (7, 100, 6)):
            with self.subTest(max_chars=max_chars, max_words=max_words):
                with mock.patch.object(model.chain, 'move', return_value='loop') as move:
                    self.assertIsNone(model.make_short_sentence(
                        max_chars, tries=3, max_words=max_words,
                    ))
                self.assertEqual(move.call_count, moves)

    def test_short_novel_sentences_generate_after_json_roundtrip(self):
        model = CustomMarkovText.from_json(train().to_json())
        with mock.patch('markovify.chain.random', Random(42)):
            sentence = model.make_short_sentence(100, min_chars=20)
        self.assertIsNotNone(sentence)
        self.assertGreaterEqual(len(sentence), 20)
        self.assertLessEqual(len(sentence), 100)
        self.assertNotIn(sentence, CHAT)

    def test_server_and_user_context_sizes_are_independently_configurable(self):
        self.assertEqual(train().state_size, 2)
        self.assertEqual(train(user_model=True).state_size, 2)
        with mock.patch.dict(os.environ, {'MARKOV_STATE_SIZE': '3', 'MARKOV_USER_STATE_SIZE': '1'}):
            self.assertEqual(CustomMarkovText.from_json(train().to_json()).state_size, 3)
            self.assertEqual(train(user_model=True).state_size, 1)
        for value in ('0', '4', 'invalid'):
            with self.subTest(value=value):
                with mock.patch.dict(os.environ, {'MARKOV_STATE_SIZE': value}):
                    with self.assertRaises(ValueError):
                        train()

    def test_generation_settings_are_configurable_and_validate_limits(self):
        with mock.patch.dict(os.environ, {
            'MARKOV_MIN_CHARS': '10', 'MARKOV_MAX_CHARS': '200',
            'MARKOV_GENERATION_TRIES': '25', 'MARKOV_MAX_WORDS': '30',
        }):
            with mock.patch('markovbot.markov._get_model') as get_model:
                make_sentence(get_guild())
        get_model.return_value.make_short_sentence.assert_called_once_with(
            200, min_chars=10, tries=25, max_words=30,
        )
        for settings in (
            {'MARKOV_MIN_CHARS': '501'}, {'MARKOV_MAX_CHARS': '2001'},
            {'MARKOV_GENERATION_TRIES': '0'}, {'MARKOV_MAX_WORDS': '0'},
        ):
            with self.subTest(settings=settings):
                with mock.patch.dict(os.environ, settings):
                    with self.assertRaises(ValueError):
                        make_sentence(get_guild())


class ModelCacheTest(unittest.TestCase):
    def setUp(self):
        isolate_persistence(self)
        markov.clear_model_cache()
        self.addCleanup(markov.clear_model_cache)
        self.guild = get_guild()
        self.chain = train(LONG_CHAT).to_dict()
        persistence.create_chain(self.guild, self.chain, {456: self.chain})

    def test_legacy_server_only_records_still_generate_with_originality_checks(self):
        guild = MockGuild(id=987)
        texts = LONG_CHAT
        legacy_chain = markovify.Text(texts).to_dict()
        persistence.ChainDB.insert({'guild_id': guild.id, 'chain': legacy_chain})
        sentence = make_sentence(guild)
        self.assertNotIn(sentence, texts)
        self.assertLessEqual(set(sentence.split()), set(' '.join(texts).split()))
        with self.assertRaises(MarkovGenerationException):
            make_sentence(guild, 456)

    def test_model_is_loaded_and_compiled_once_until_replaced(self):
        with mock.patch.object(CustomMarkovText, 'from_dict', wraps=CustomMarkovText.from_dict) as restore:
            with mock.patch.object(persistence, 'get_chain', wraps=persistence.get_chain) as read:
                make_sentence(self.guild)
                make_sentence(self.guild)
                self.assertEqual(restore.call_count, 1)
                self.assertEqual(read.call_count, 1)
                replacement_text = [text.replace('vegetables', 'fruit').replace('bread', 'cake') for text in LONG_CHAT]
                persistence.create_chain(self.guild, train(replacement_text).to_dict())
                sentence = make_sentence(self.guild)
                self.assertEqual(restore.call_count, 2)
                self.assertEqual(read.call_count, 2)
        self.assertLessEqual(set(sentence.split()), set(' '.join(replacement_text).split()))
        self.assertTrue(next(iter(markov._model_cache.values()))[1].chain.compiled)

    def test_cache_is_scoped_to_guild_and_user_and_deletion_invalidates_it(self):
        other_guild = MockGuild(id=789)
        persistence.create_chain(other_guild, self.chain)
        with mock.patch.object(CustomMarkovText, 'from_dict', wraps=CustomMarkovText.from_dict) as restore:
            for guild, user_id in ((self.guild, None), (self.guild, 456), (other_guild, None)):
                make_sentence(guild, user_id)
                make_sentence(guild, user_id)
            self.assertEqual(restore.call_count, 3)
        persistence.delete_chain(self.guild)
        for user_id in (None, 456):
            with self.assertRaises(MarkovGenerationException):
                make_sentence(self.guild, user_id)
        self.assertIsInstance(make_sentence(other_guild), str)

    def test_replacing_user_models_drops_cached_stale_authors(self):
        make_sentence(self.guild, 456)
        persistence.create_chain(self.guild, self.chain)
        with self.assertRaises(MarkovGenerationException):
            make_sentence(self.guild, 456)

    def test_cache_evicts_the_least_recently_used_model(self):
        with mock.patch('markovbot.markov._MODEL_CACHE_SIZE', 2):
            for guild_id in (1, 2, 1, 3):
                guild = MockGuild(id=guild_id)
                if not persistence.chain_exists(guild):
                    persistence.create_chain(guild, self.chain)
                make_sentence(guild)
        self.assertEqual(list(markov._model_cache), [(1, None), (3, None)])


if __name__ == '__main__':
    unittest.main()

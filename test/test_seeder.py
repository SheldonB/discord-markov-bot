import unittest
from random import Random
from types import SimpleNamespace
from unittest.mock import Mock, patch

from markovbot import markov, persistence
from markovbot.seeder import Seeder
from .utils import MockGuild, isolate_persistence


def message(user_id, content, bot=False):
    return SimpleNamespace(author=SimpleNamespace(id=user_id, bot=bot), content=content)


def channel(messages, readable=True, error=None):
    async def history(limit):
        for item in messages:
            yield item
        if error:
            raise error

    return SimpleNamespace(
        name='test-channel',
        permissions_for=Mock(return_value=SimpleNamespace(read_messages=readable)),
        history=Mock(side_effect=history),
    )


def sentences(chain):
    return [' '.join(words) for words in chain['parsed_sentences']]


class SeederTest(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        isolate_persistence(self)
        self.seeder = Seeder()
        self.guild = MockGuild(me=object())

    async def test_saved_user_model_generates_a_novel_sentence_from_that_author(self):
        texts = [
            'Every morning we gather near the ancient oak tree before we wander through '
            'the bustling marketplace to find fresh vegetables and share our stories '
            'about the changing seasons.',
            'Every evening we gather near the peaceful river bank before we wander '
            'through the quiet village to find warm bread and share our dreams '
            'about the distant mountains.',
        ]
        self.guild.text_channels = [channel([
            *(message(111, text) for text in texts),
            message(222, 'Penguins swim underneath the frozen ocean'),
        ])]

        await self.seeder.seed(self.guild)
        with patch('markovify.chain.random', Random(42)):
            sentence = markov.make_sentence(self.guild, 111)

        self.assertGreaterEqual(len(sentence), 125)
        self.assertLessEqual(len(sentence), 500)
        self.assertNotIn(sentence, texts)
        self.assertLessEqual(set(sentence.split()), {word for text in texts for word in text.split()})

    async def test_one_history_scan_builds_combined_and_separate_author_models(self):
        first = channel([
            message(111, 'Alice drinks a cup of tea'),
            message(222, 'Bob plays music before dinner'),
            message(333, 'A robot should be ignored', bot=True),
            message(444, 'hello'),
            message(555, '!markov say something'),
        ])
        second = channel([message(111, 'Alice walks around the garden')])
        hidden = channel([message(666, 'A hidden message stays hidden')], readable=False)
        self.guild.text_channels = [first, second, hidden]

        await self.seeder.seed(self.guild)

        self.assertEqual(sentences(persistence.get_chain(self.guild)), [
            'Alice drinks a cup of tea.',
            'Bob plays music before dinner.',
            'Alice walks around the garden.',
        ])
        self.assertEqual(sentences(persistence.get_chain(self.guild, 111)), [
            'Alice drinks a cup of tea.', 'Alice walks around the garden.',
        ])
        self.assertEqual(sentences(persistence.get_chain(self.guild, 222)), ['Bob plays music before dinner.'])
        for user_id in (333, 444, 555, 666):
            self.assertIsNone(persistence.get_chain(self.guild, user_id))
        first.history.assert_called_once_with(limit=None)
        second.history.assert_called_once_with(limit=None)
        hidden.history.assert_not_called()

    async def test_existing_legacy_or_modern_record_skips_automatic_training(self):
        source = channel([message(111, 'Some new training text')])
        self.guild.text_channels = [source]
        for user_chains in (None, {'111': {'old': True}}):
            with self.subTest(user_chains=user_chains):
                persistence.ChainDB.truncate()
                record = {'guild_id': self.guild.id, 'chain': {'legacy': True}}
                if user_chains is not None:
                    record['user_chains'] = user_chains
                persistence.ChainDB.insert(record)

                await self.seeder.seed(self.guild)

                self.assertEqual(persistence.get_chain(self.guild), {'legacy': True})
                source.history.assert_not_called()

    async def test_reseed_replaces_legacy_data_and_removes_stale_authors(self):
        self.guild.text_channels = [channel([message(111, 'Fresh training text for Alice')])]
        for old_record in (
            {'guild_id': self.guild.id, 'chain': {'legacy': True}},
            {'guild_id': self.guild.id, 'chain': {'old': True}, 'user_chains': {'222': {'old': True}}},
        ):
            with self.subTest(old_record=old_record):
                persistence.ChainDB.truncate()
                persistence.ChainDB.insert(old_record)

                await self.seeder.reseed(self.guild)

                self.assertEqual(sentences(persistence.get_chain(self.guild)), ['Fresh training text for Alice.'])
                self.assertEqual(sentences(persistence.get_chain(self.guild, 111)), ['Fresh training text for Alice.'])
                self.assertIsNone(persistence.get_chain(self.guild, 222))

    async def test_author_with_untrainable_text_is_skipped_without_failing_other_models(self):
        self.guild.text_channels = [channel([
            message(111, '(no usable text)'),
            message(222, 'This author has usable text'),
        ])]

        await self.seeder.seed(self.guild)

        self.assertTrue(persistence.chain_exists(self.guild))
        self.assertIsNone(persistence.get_chain(self.guild, 111))
        self.assertEqual(sentences(persistence.get_chain(self.guild, 222)), ['This author has usable text.'])

    async def test_empty_or_untrainable_rebuild_leaves_no_models(self):
        for messages in ([], [message(111, 'hello')], [message(111, '(no usable text)')]):
            with self.subTest(messages=messages):
                persistence.create_chain(self.guild, {'old': True}, {111: {'old': True}})
                self.guild.text_channels = [channel(messages)]

                await self.seeder.reseed(self.guild)

                self.assertFalse(persistence.chain_exists(self.guild))
                self.assertIsNone(persistence.get_chain(self.guild, 111))

    async def test_missing_bot_member_does_not_download_history(self):
        source = channel([message(111, 'Some training text')])
        self.guild.me = None
        self.guild.text_channels = [source]

        await self.seeder.seed(self.guild)

        source.history.assert_not_called()
        self.assertFalse(persistence.chain_exists(self.guild))

    async def test_history_failure_removes_old_models_without_publishing_new_ones(self):
        persistence.create_chain(self.guild, {'old': True}, {111: {'old': True}})
        self.guild.text_channels = [channel([message(111, 'Some new text')], error=RuntimeError('History failed'))]

        with self.assertLogs('markovbot.seeder', level='ERROR'):
            with self.assertRaisesRegex(RuntimeError, 'History failed'):
                await self.seeder.reseed(self.guild)

        self.assertFalse(persistence.chain_exists(self.guild))
        self.assertIsNone(persistence.get_chain(self.guild, 111))

    async def test_unexpected_training_failure_does_not_publish_partial_models(self):
        persistence.create_chain(self.guild, {'old': True}, {111: {'old': True}})
        self.guild.text_channels = [channel([
            message(111, 'Some text for Alice'), message(222, 'Some text for Bob'),
        ])]
        generate_chain = markov.generate_chain

        def generate(messages):
            if len(messages) == 1 and messages[0].author.id == 222:
                raise RuntimeError('Training failed')
            return generate_chain(messages)

        with patch('markovbot.seeder.markov.generate_chain', side_effect=generate):
            with self.assertLogs('markovbot.seeder', level='ERROR'):
                with self.assertRaisesRegex(RuntimeError, 'Training failed'):
                    await self.seeder.reseed(self.guild)

        self.assertFalse(persistence.chain_exists(self.guild))
        self.assertIsNone(persistence.get_chain(self.guild, 111))

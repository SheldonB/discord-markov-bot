import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from tinydb import TinyDB

from markovbot import persistence
from .utils import MockGuild, get_guild, isolate_persistence


class PersistenceTest(unittest.TestCase):

    def setUp(self):
        isolate_persistence(self)

    def test_create_chain(self):
        guild = get_guild()

        persistence.create_chain(guild, { 'prop': 123 })
        self.assertIs(persistence.chain_exists(guild), True)

    def test_delete_chain(self):
        guild = get_guild()

        persistence.create_chain(guild, { 'prop': 123 })
        persistence.delete_chain(guild)

        self.assertIs(persistence.chain_exists(guild), False)
    
    def test_get_chain(self):
        guild = get_guild()
        chain = { 'prop': 123 }
        persistence.create_chain(guild, chain)

        result = persistence.get_chain(guild)

        self.assertEqual(result, chain)

    def test_get_chain_not_exists(self):
        result = persistence.get_chain(get_guild())

        self.assertIsNone(result)

    def test_user_models_roundtrip_through_json(self):
        guild = get_guild()
        server_chain = {'server': 'model'}
        user_chain = {'user': 'model'}
        with TemporaryDirectory() as directory:
            path = Path(directory) / 'models.json'
            with TinyDB(path) as database:
                with patch.object(persistence, 'ChainDB', database.table('Chain')):
                    persistence.create_chain(guild, server_chain, {456: user_chain})
            with TinyDB(path) as database:
                with patch.object(persistence, 'ChainDB', database.table('Chain')):
                    self.assertEqual(persistence.get_chain(guild), server_chain)
                    self.assertEqual(persistence.get_chain(guild, 456), user_chain)
                    self.assertIsNone(persistence.get_chain(guild, 789))

    def test_legacy_record_keeps_server_model_and_has_no_user_models(self):
        guild = get_guild()
        persistence.ChainDB.insert({'guild_id': guild.id, 'chain': {'legacy': True}})

        self.assertTrue(persistence.chain_exists(guild))
        self.assertEqual(persistence.get_chain(guild), {'legacy': True})
        self.assertIsNone(persistence.get_chain(guild, 456))

    def test_models_are_isolated_by_guild_and_author(self):
        first, second = MockGuild(id=123), MockGuild(id=456)
        persistence.create_chain(first, {'guild': 'first'}, {789: {'user': 'first'}, 987: {'user': 'other'}})
        persistence.create_chain(second, {'guild': 'second'}, {789: {'user': 'second'}})

        self.assertEqual(persistence.get_chain(first, 789), {'user': 'first'})
        self.assertEqual(persistence.get_chain(first, 987), {'user': 'other'})
        self.assertEqual(persistence.get_chain(second, 789), {'user': 'second'})
        self.assertIsNone(persistence.get_chain(second, 987))

    def test_replacing_models_removes_stale_authors(self):
        guild = get_guild()
        persistence.create_chain(guild, {'old': True}, {456: {'old': True}, 789: {'old': True}})
        persistence.create_chain(guild, {'new': True}, {456: {'new': True}})

        self.assertEqual(persistence.get_chain(guild), {'new': True})
        self.assertEqual(persistence.get_chain(guild, 456), {'new': True})
        self.assertIsNone(persistence.get_chain(guild, 789))

    def test_omitted_or_empty_user_map_clears_old_models(self):
        guild = get_guild()
        for user_chains in (None, {}):
            with self.subTest(user_chains=user_chains):
                persistence.create_chain(guild, {'old': True}, {456: {'old': True}})
                persistence.create_chain(guild, {'new': True}, user_chains)
                self.assertIsNone(persistence.get_chain(guild, 456))

    def test_deleting_guild_removes_all_its_models_only(self):
        first, second = MockGuild(id=123), MockGuild(id=456)
        for guild in (first, second):
            persistence.create_chain(guild, {'server': True}, {789: {'user': True}})

        persistence.delete_chain(first)

        self.assertFalse(persistence.chain_exists(first))
        self.assertIsNone(persistence.get_chain(first))
        self.assertIsNone(persistence.get_chain(first, 789))
        self.assertTrue(persistence.chain_exists(second))
        self.assertEqual(persistence.get_chain(second, 789), {'user': True})


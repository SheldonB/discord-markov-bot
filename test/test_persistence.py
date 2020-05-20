import unittest

from markovbot import persistence
from .utils import get_guild


class PersistenceTest(unittest.TestCase):

    def tearDown(self):
        persistence.ChainDB.truncate()


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


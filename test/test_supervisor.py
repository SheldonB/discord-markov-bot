import asyncio
import unittest
from unittest import mock

from markovbot.supervisor import Supervisor
from .utils import get_guild


class SupervisorTest(unittest.TestCase):

    def test_can_add_guild(self):
        supervisor = Supervisor()

        guild = get_guild()

        asyncio.run(supervisor.add(guild))

        self.assertIn(guild.id, supervisor.guilds)

    def test_can_remove_guild(self):
        supervisor = Supervisor()
        guild = get_guild()

        asyncio.run(supervisor.add(guild))

        supervisor.remove(guild)

        self.assertNotIn(guild.id, supervisor.guilds)

    def test_connected_guild_count_after_add_remove(self):
        supervisor = Supervisor()
        guild = get_guild()

        self.assertEqual(supervisor.connected_guild_count(), 0)

        asyncio.run(supervisor.add(guild))

        self.assertEqual(supervisor.connected_guild_count(), 1)

        supervisor.remove(guild)

        self.assertEqual(supervisor.connected_guild_count(), 0)


if __name__ == '__main__':
    unittest.main()

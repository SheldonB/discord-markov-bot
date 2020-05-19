import unittest
from unittest.mock import Mock

import asyncio
from asyncio import coroutine

from markovbot.supervisor import Supervisor
from .utils import get_guild


class SupervisorTest(unittest.TestCase):
    def test_can_add_guild(self):
        supervisor = Supervisor()
        supervisor.seeder.seed = Mock(side_effect=coroutine(Mock()))

        guild = get_guild()

        loop = asyncio.get_event_loop()
        loop.run_until_complete(supervisor.add(guild))

        self.assertIn(guild.id, supervisor.guilds)

    def test_can_remove_guild(self):
        supervisor = Supervisor()
        supervisor.seeder.seed = Mock(side_effect=coroutine(Mock()))
        guild = get_guild()

        loop = asyncio.get_event_loop()
        loop.run_until_complete(supervisor.add(guild))

        supervisor.remove(guild)

        self.assertNotIn(guild.id, supervisor.guilds)


if __name__ == '__main__':
    unittest.main()

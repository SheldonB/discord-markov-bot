import unittest

from markovbot.supervisor import Supervisor
from .utils import get_guild


class SupervisorTest(unittest.TestCase):
    def test_can_add_guild(self):
        supervisor = Supervisor()
        guild = get_guild()

        supervisor.add(guild)

        self.assertIn(guild.id, supervisor.guilds)

    def test_can_remove_guild(self):
        supervisor = Supervisor()
        guild = get_guild()

        supervisor.add(guild)
        supervisor.remove(guild)

        self.assertNotIn(guild.id, supervisor.guilds)


if __name__ == '__main__':
    unittest.main()

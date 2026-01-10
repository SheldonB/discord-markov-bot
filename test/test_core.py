import asyncio
import unittest
from unittest.mock import AsyncMock, patch

from discord import Game

from markovbot.core import MarkovBot
from .utils import get_guild


class MarkovBotTest(unittest.TestCase):

    def test_on_guild_join_adds_and_updates_presence(self):
        with patch("markovbot.core.Supervisor") as supervisor_factory:
            supervisor = supervisor_factory.return_value
            bot = MarkovBot()
            bot.update_presence = AsyncMock()

            guild = get_guild()

            asyncio.run(bot.on_guild_join(guild))

            supervisor.add.assert_awaited_once_with(guild)
            bot.update_presence.assert_awaited_once()

    def test_on_guild_remove_removes_and_updates_presence(self):
        with patch("markovbot.core.Supervisor") as supervisor_factory:
            supervisor = supervisor_factory.return_value
            bot = MarkovBot()
            bot.update_presence = AsyncMock()

            guild = get_guild()

            asyncio.run(bot.on_guild_remove(guild))

            supervisor.remove.assert_called_once_with(guild)
            bot.update_presence.assert_awaited_once()

    def test_on_guild_available_adds_and_updates_presence(self):
        with patch("markovbot.core.Supervisor") as supervisor_factory:
            supervisor = supervisor_factory.return_value
            bot = MarkovBot()
            bot.update_presence = AsyncMock()

            guild = get_guild()

            asyncio.run(bot.on_guild_available(guild))

            supervisor.add.assert_awaited_once_with(guild)
            bot.update_presence.assert_awaited_once()

    def test_on_guild_unavailable_removes_with_delete_and_updates_presence(self):
        with patch("markovbot.core.Supervisor") as supervisor_factory:
            supervisor = supervisor_factory.return_value
            bot = MarkovBot()
            bot.update_presence = AsyncMock()

            guild = get_guild()

            asyncio.run(bot.on_guild_unavailable(guild))

            supervisor.remove.assert_called_once_with(guild, True)
            bot.update_presence.assert_awaited_once()

    def test_update_presence_sets_game_activity_from_supervisor_count(self):
        with patch("markovbot.core.Supervisor") as supervisor_factory:
            supervisor = supervisor_factory.return_value
            supervisor.connected_guild_count.return_value = 3
            bot = MarkovBot()
            bot.change_presence = AsyncMock()

            asyncio.run(bot.update_presence())

            bot.change_presence.assert_awaited_once()
            activity = bot.change_presence.call_args.kwargs["activity"]
            self.assertIsInstance(activity, Game)
            self.assertEqual(activity.name, "on 3 servers.")


if __name__ == '__main__':
    unittest.main()

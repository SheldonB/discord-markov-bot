import logging

from discord import Guild

from markovbot import markov


log = logging.getLogger(__name__)


class Supervisor:
    def __init__(self):
        self.guilds = {}

    async def add(self, guild: Guild):
        self.guilds[guild.id] = guild
        # TODO: Write to disk
        await self._seed()

    def remove(self, guild: Guild):
        try:
            self.guilds.pop(guild.id)
            # TODO: Write to disk
        except KeyError:
            log.warning('Guild=%s:%s asked to be removed, but was not in connected guilds map', guild.id, guild.name)

    async def _seed(self, guild: Guild):
        """
        Start the seeding process for a new Guild.
        All messages for each Channel that the bot has access
        to will be used for the seeding process.

        On initial seeding a chain will be created for the server.

        :param guild:
        :return:
        """
        channels = guild.text_channels

        messages = []

        for channel in channels:
            async for message in channel.history(limit=None):
                author = message.author
                content = message.content

                # Conditions for us to insert a message into the database.
                # 1. The author is not a bot.
                # 2. The message is more than one word.
                # 3. The message does not start with '!' (This should weed out most commands)
                # 4. The message is not a link.
                if not author.bot and len(content.split()) > 1 and not content.startswith(('!', 'http')):
                    messages.append(message)

        chain = markov.generate_chain(messages)
        # Save chain as json
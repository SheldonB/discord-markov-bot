import logging

from discord import Guild

from markovbot import markov, persistence

log = logging.getLogger(__name__)

class Seeder:
    async def seed(self, guild: Guild):
        log.info("Seeding chain for Guild(id=%s, name=%s)", guild.id, guild.name)

        channels = guild.text_channels
        messages = []

        for channel in channels:
            async for message in channel.history(limit=None):
                author = message.author
                content = message.content

                # Conditions to insert a message into the database.
                # 1. The author is not a bot.
                # 2. The message is more than one word.
                # 3. The message does not start with '!' (This should weed out most commands)
                # 4. The message is not a link.
                if not author.bot and len(content.split()) > 1 and not content.startswith(('!', 'http')):
                    messages.append(message)

        chain = markov.generate_chain(messages)
        persistence.create_chain(guild, chain.to_dict())

        log.info("Successfully seeded chain with %d messages for Guild(id=%s, %s)", len(messages), guild.id, guild.name)
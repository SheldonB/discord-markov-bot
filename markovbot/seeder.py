import logging
from collections import defaultdict
from typing import List

from discord import Guild, TextChannel

from markovbot import markov, persistence

log = logging.getLogger(__name__)


class Seeder:
    async def seed(self, guild: Guild):
        try:
            await self._seed(guild)
        except Exception:
            log.exception('Failed to seed chains for Guild(id=%s, name=%s)', guild.id, guild.name)
            raise

    async def _seed(self, guild: Guild):

        if persistence.chain_exists(guild):
            log.debug('Skipping seeding chain for Guild(id=%s, name=%s). It already exists.', guild.id, guild.name)
            return

        log.debug("Seeding chain for Guild(id=%s, name=%s)", guild.id, guild.name)

        channels: List[TextChannel] = guild.text_channels
        messages = []
        messages_by_author = defaultdict(list)

        for channel in channels:
            member = guild.me
            if member is None:
                log.warning('Skipping channel permissions check for Guild(id=%s) because bot member is unavailable.', guild.id)
                continue

            if channel.permissions_for(member).read_messages:
                log.debug('Downloading channel history for Channel(name=%s)', channel.name)
                async for message in channel.history(limit=None):
                    author = message.author
                    content = message.content

                    # Conditions to insert a message into the database.
                    # 1. The author is not a bot.
                    # 2. The message is more than one word.
                    # 3. The message does not start with '!' (This should weed out most commands)
                    if not author.bot and len(content.split()) > 1 and not content.startswith('!'):
                        messages.append(message)
                        messages_by_author[author.id].append(message)

        if not messages:
            log.info('No eligible messages to seed chains for Guild(id=%s, name=%s)', guild.id, guild.name)
            return

        try:
            chain = markov.generate_chain(messages)
        except markov.MarkovTrainingException:
            log.info(
                'No trainable text to seed chains for Guild(id=%s, name=%s); skipping %d authors',
                guild.id, guild.name, len(messages_by_author),
            )
            return

        user_chains = {}
        skipped_authors = 0
        for user_id, user_messages in messages_by_author.items():
            try:
                user_chain = markov.generate_chain(user_messages)
            except markov.MarkovTrainingException:
                skipped_authors += 1
                log.info('Skipping untrainable author User(id=%s) for Guild(id=%s)', user_id, guild.id)
                continue
            user_chains[user_id] = user_chain.to_dict()

        persistence.create_chain(guild, chain.to_dict(), user_chains)

        log.info(
            'Successfully seeded server chain and %d user chains with %d messages '
            'for Guild(id=%s, name=%s); skipped %d authors',
            len(user_chains), len(messages), guild.id, guild.name, skipped_authors,
        )

    async def reseed(self, guild: Guild):
        log.info("Starting re-seeding for Guild(id=%s, name=%s)", guild.id, guild.name)
        persistence.delete_chain(guild)
        await self.seed(guild)


seeder = Seeder()

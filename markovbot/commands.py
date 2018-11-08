import asyncio
import logging

import markovify

from discord.ext.commands import core

from markovbot import markovbot, datastore

log = logging.getLogger(__name__)


class CustomCommand(core.Command):
    def __init__(self, name, callback, **kwargs):
        super().__init__(name, callback, **kwargs)

    async def invoke(self, ctx):
        ctx.server_context = markovbot.server_manager.get_server_context(ctx.message.server)
        await super().invoke(ctx)


# TODO: I wonder if there is a way to extend the way the context is passed in, and we could add our server
# context as a property on that context object.
@markovbot.command(cls=CustomCommand, pass_context=True, help='Generate a Markov sentence based on the server chat history.')
async def say(context, user: str = None):
    server_context = context.server_context

    if not server_context.is_ready:
        await markovbot.say('I am still learning from all your messages. Try again later.')
        return

    if user is None:
        log.debug('Bot issued say command on server %s', server_context.server.name)
        sentence = server_context.markov.make_sentence_server()

        if sentence is None:
            await markovbot.say('Unable to generate message. This is probably due to a lack of messages on the server.')
            return

    else:
        db_user = datastore.get_server_user(server_context.server.id, user)

        if db_user is None:
            await markovbot.say('The user {} does not exist. Check your spelling and try again.'.format(user))
            return

        sentence = server_context.markov.make_sentence_user(db_user)

        if sentence is None:
            await markovbot.say('Unable to generate message for {}. This is probably because they have not sent enough messages.'.format(user))
            return

    await markovbot.say(sentence)



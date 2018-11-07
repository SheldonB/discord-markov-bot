import asyncio
import logging

import markovify

from cancerbot import cancerbot, datastore

log = logging.getLogger(__name__)

def get_server_context_from_client_context(context):
    return cancerbot.server_manager.get_server_context(context.message.server)

# TODO: I wonder if there is a way to extend the way the context is passed in, and we could add our server
# context as a property on that context object.
@cancerbot.command(pass_context=True, help='Generate a Markov sentence based on the server chat history.')
async def say(context, user: str = None):
    server_context = get_server_context_from_client_context(context)

    if not server_context.is_ready:
        await cancerbot.say('I am still learning from all your messages. Try again later.')
        return

    if user is None:
        log.debug('Bot issued say command on server %s', server_context.server.name)
        sentence = server_context.markov.make_sentence_server()

        if sentence is None:
            await cancerbot.say('Unable to generate message. This is probably due to a lack of messages on the server.')
            return

    else:
        db_user = datastore.get_server_user(server_context.server.id, user)

        if db_user is None:
            await cancerbot.say('The user {} does not exist. Check your spelling and try again.'.format(user))
            return

        sentence = server_context.markov.make_sentence_user(db_user)

        if sentence is None:
            await cancerbot.say('Unable to generate message for {}. This is probably because they have not sent enough messages.'.format(user))
            return



    await cancerbot.say(sentence)



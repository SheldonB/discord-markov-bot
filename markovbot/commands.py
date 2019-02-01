import asyncio
import logging
import random
import math

import markovify

from discord.ext.commands import core

from markovbot import markovbot, datastore

log = logging.getLogger(__name__)


# TODO: I wonder if there is a way to extend the way the context is passed in, and we could add our server
# context as a property on that context object.
@markovbot.command(pass_context=True, help='Generate a Markov sentence based on the server chat history.')
async def say(context, user: str = None):
    server_context = context.server_context

    if not server_context.is_ready:
        await markovbot.say('I am still learning from all your messages. Try again later.')
        return

    if user is None:
        log.debug('Bot issued say command on server %s',
                  server_context.server.name)
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


@markovbot.command(pass_context=True, help='Mock the last specified user message.')
async def mock(context, user: str = None):
    server_context = context.server_context
    targeted_user = server_context.server.get_member_named(user)
    logs_by_user = list()

    # Get messages from user in current channel
    async for message in markovbot.logs_from(context.message.channel, limit=500):
        if message.author.id == targeted_user.id:
            logs_by_user.append(message)

    # Get latest message from user
    logs_by_user.sort(key=lambda message: message.timestamp, reverse=True)

    targeted_message = logs_by_user[0]
    sentence = mock_string(targeted_message.content)

    await markovbot.say(sentence)


def mock_string(sentence: str):
    if sentence is None:
        return

    # TODO: Might end up changing this to handle smaller strings.
    mock_count = math.ceil(len(sentence) - len(sentence) / 2)
    sentence_mock = list(sentence.lower())

    # TODO: Make a comparator array?
    # elements = getRandomElements(sentence_mock, mock_count)
    # TODO: Probably need to rename these for clarity.
    i = 0
    j = 0
    k = 3
    while j in range(0, mock_count) and k > 0:
        # TODO: This could end up being too random and not get any chars.
        capitalize = bool(random.getrandbits(1))
        val = str(sentence_mock[i])
        # Don't want to count a char mutation for spaces / integers / capitals.
        if capitalize and sentence_mock[i] != ' ' and not (val.isdigit() or val.isupper()):
            sentence_mock[i] = sentence_mock[i].upper()
            j += 1
        i += 1
        # Restart at beginning of string if mock_count is not met.
        # Only allow k runs
        if i == len(sentence_mock):
            i = 0
            k -= 1
    sentence = ''.join(str(e) for e in sentence_mock)
    return sentence

# Leaving this for now since I'm working off master.
# def getRandomElements(sentence_mock, mock_count):
#     result = []
#     i = 0
#     while i in range(0, mock_count):
#         result.append(sentence_mock[math.floor(
#             random.random() * sentence_mock.length)])
#         i += 1
#     return result

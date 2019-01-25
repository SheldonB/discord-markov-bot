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
        logs = markovbot.logs_from(server_context.message.channel, limit=20):
        sentence = logs[-1]
        
    await markovbot.say(sentence)


def mockString(sentence):
    if sentence is None:
        return

    # TODO: Might end up changing this to handle smaller strings.
    print(len(sentence))
    mockCount = random.randint(0, math.ceil(
        len(sentence) - len(sentence) / 2))
    sentenceMock = list(sentence.lower())

    # TODO: Make a comparator array?
    # elements = getRandomElements(sentenceMock, mockCount)
    # TODO: Probably need to rename these for clarity.
    i = 0
    j = 0
    k = 3
    while j in range(0, mockCount) and k > 0:
        # TODO: This could end up being too random and not get any chars.
        capitalize = bool(random.getrandbits(1))
        val = str(sentenceMock[i])
        # Don't want to count a char mutation for spaces / integers / capitals.
        if capitalize and sentenceMock[i] != ' ' and not (val.isdigit() or val.isupper()):
            sentenceMock[i] = sentenceMock[i].upper()
            j += 1
        i += 1
        # Restart at beginning of string if mockCount is not met.
        # Only allow k runs
        if i == len(sentenceMock):
            i = 0
            k -= 1
    sentence = ''.join(str(e) for e in sentenceMock)
    return sentence

# Leaving this for now since I'm working off master.
# def getRandomElements(sentenceMock, mockCount):
#     result = []
#     i = 0
#     while i in range(0, mockCount):
#         result.append(sentenceMock[math.floor(
#             random.random() * sentenceMock.length)])
#         i += 1
#     return result

import os

from cancerbot import client, logger

if __name__ == '__main__':
    token = os.environ.get('DISCORD_BOT_TOKEN')

    if token is None:
        logger.error('DISCORD_BOT_TOKEN env variable not set. Set it before running the bot.')
        exit(-1)

    logger.info('Starting Discord Cancer Bot')
    client.run(token)
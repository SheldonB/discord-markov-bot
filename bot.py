import os
import sys
import logging

from markovbot import markovbot


class CustomFormatter(logging.Formatter):
    LEVEL_MAP = {logging.FATAL: 'F', logging.ERROR: 'E', logging.WARN: 'W', logging.INFO: 'I', logging.DEBUG: 'D'}

    def format(self, record):
        record.levelletter = self.LEVEL_MAP[record.levelno]
        return super(CustomFormatter, self).format(record)


def init_logging():
    fmt = '%(levelletter)s %(asctime)s.%(msecs).03d %(process)d %(filename)s:%(lineno)d] %(message)s'
    date_format = '%m-%d-%y %H:%M:%S'
    formatter = CustomFormatter(fmt, date_format)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(formatter)

    file_handler = logging.FileHandler('log.txt')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    root = logging.getLogger()
    root.setLevel(logging.DEBUG)
    root.addHandler(console_handler)
    root.addHandler(file_handler)

    # Explicitly tell these libraries to shut up
    logging.getLogger('discord').setLevel(logging.WARN)
    logging.getLogger('websockets').setLevel(logging.WARN)


if __name__ == '__main__':
    init_logging()

    log = logging.getLogger(__name__)

    token = os.environ.get('DISCORD_BOT_TOKEN')

    if token is None:
        log.error('DISCORD_BOT_TOKEN env variable not set. Set it before running the bot.')
        exit(-1)

    log.info('Starting Discord Cancer Bot')

    try:
        markovbot.run(token)
    except:
        log.error("Something went wrong during execution. Exiting....", exc_info=1)

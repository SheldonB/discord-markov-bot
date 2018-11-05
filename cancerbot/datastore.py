import logging
import datetime

from tinydb import TinyDB, Query

log = logging.getLogger(__name__)

db = TinyDB('bot_db.json')

def does_server_exist(server):
    table = db.table('Server')

    server_query = Query()
    record = table.search(server_query.id == server.id)

    return len(record) > 0


def update_server(server):
    table = db.table('Server')

    log.debug('Updating Server Info for %s(%s)', server.name, server.id)

    server_query = Query()
    table.upsert({'id': server.id, 'name': server.name, 'last_connected': str(datetime.datetime.now())}, server_query.id == server.id)


def add_user(user):
    table = db.table('User')

    log.debug('Updating user %s(%s)', user.name, user.id)

    table.upsert({ 'id': user.id, 'name': user.name}, Query().id == user.id)


def add_message(message):
    table = db.table('Message')

    server = message.server
    user = message.author

    log.debug('Inserting new message(%s) from %s(%s) for server %s(%s)', message.id, user.name, user.id, server.name, server.id)

    table.insert({'server_id': server.id, 'user_id': user.id, 'content': message.content})


def get_messages_by_server(server):
    table = db.table('Message')

    query = Query()
    records = table.search(query.server_id == server.id)

    return records

# def get_messages_by_user(user):
#     return



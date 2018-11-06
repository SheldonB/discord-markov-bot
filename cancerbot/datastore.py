import logging
import datetime

from tinydb import TinyDB, Query

log = logging.getLogger(__name__)

db = TinyDB('bot_db.json')

def does_server_exist(server):
    table = db.table('Server')

    record = table.get(Query().id == server.id)

    return record is not None


def update_server(server):
    table = db.table('Server')

    log.debug('Updating Server Info for %s(%s)', server.name, server.id)

    server_query = Query()
    table.upsert({'id': server.id, 'name': server.name, 'last_connected': str(datetime.datetime.now())}, server_query.id == server.id)


def add_user(user):
    table = db.table('User')

    log.debug('Updating user %s(%s)', user.name, user.id)

    table.upsert({'id': user.id, 'name': user.name.lower()}, Query().id == user.id)


def get_user_by_username(username):
    table = db.table('User')

    return table.get(Query().name == username)


def add_message(message):
    table = db.table('Message')

    server = message.server
    user = message.author

    log.debug('Inserting new message(%s) from %s(%s) for server %s(%s)', message.id, user.name, user.id, server.name, server.id)

    table.insert({'server_id': server.id, 'user_id': user.id, 'content': message.content})


def add_messages(messages):
    table = db.table('Message')

    formatted_messages = [{'server_id': message.server.id, 'user_id': message.author.id, 'content': message.content} for message in messages]

    log.debug('Inserting %d messages.', len(formatted_messages))

    table.insert_multiple(formatted_messages)


def get_messages_by_server(server):
    table = db.table('Message')

    query = Query()
    records = table.search(query.server_id == server.id)

    return records


def get_messages_by_user_id(user_id):
    table = db.table('Message')

    return table.search(Query().user_id == user_id)


def get_messages_by_username(username):
    user = get_user_by_username(username)

    if user is None:
        log.debug('User with username=%s not found in database', username)
        return []

    return get_messages_by_user_id(user['id'])




import logging
import datetime

from tinydb import TinyDB, Query

log = logging.getLogger(__name__)

db = TinyDB('bot_db.json')


def update_server(server):
    table = db.table('Server')

    log.debug('Updating Server Info for %s(%s)', server.name, server.id)

    record = {
        'id': server.id,
        'name': server.name,
        'last_connected': str(datetime.datetime.now()),
        'members': [{
            'id': member.id,
            'name': member.name.lower(),
            'nickname': member.nick.lower() if member.nick is not None else member.nick
        } for member in server.members]
    }

    table.upsert(record, Query().id == server.id)


def get_server(id):
    table = db.table('Server')
    return table.get(Query().id == id)


def get_server_user(server_id, username):
    server = get_server(server_id)

    # This will actually match on username and nickname,
    # which is kind of wierd. 
    for member in server['members']:
        if member['name'] == username.lower() or member['nickname'] == username.lower():
            return member


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


def get_messages_by_server(server_id):
    table = db.table('Message')

    query = Query()
    records = table.search(query.server_id == server_id)

    return records


def get_messages_by_user(user_id):
    table = db.table('Message')

    return table.search(Query().user_id == user_id)

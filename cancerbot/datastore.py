import datetime

from google.cloud import datastore

client = datastore.Client()

def does_server_exist(server):
    key = client.key('Server', server.id)

    entity = client.get(key)

    return entity is None


def add_user(user):
    server_key = client.key('Server', user.server.id)
    user_key = client.key('User', user.id, parent=server_key)

    entity = datastore.Entity(key=user_key)

    entity['name'] = user.name

    client.put(entity)


def update_server(server):
    key = client.key('Server', server.id)

    entity = datastore.Entity(key=key)

    entity['name'] = server.name

    entity['last_connected'] = datetime.datetime.now()

    client.put(entity)


def add_message(message):
    server_key = client.key('User', message.author.id)
    message_key = client.key('Message', message.id, parent=server_key)

    msg = datastore.Entity(key=message_key)

    msg['content'] = message.content

    client.put(msg)


import logging

from tinydb import TinyDB, Query
from discord import Guild

log = logging.getLogger(__name__)

db = TinyDB('markov_db.json')

ChainDB = db.table('Chain')


def create_chain(guild: Guild, chain: dict):
    record = {
        'guild_id': guild.id,
        'chain': chain
    }

    log.info("Persisting Chain for Guild(id=%s, name=%s)", guild.id, guild.name)

    Chain = Query()
    ChainDB.upsert(record, Chain.guild_id == guild.id)


def get_chain(guild: Guild) -> dict:
    log.debug("Retreiving Chain for Guild(id=%s, name=%s)", guild.id, guild.name)
    Chain = Query()

    record = ChainDB.get(Chain.guild_id == guild.id)

    if not record:
        return None

    return dict(record['chain'])


def delete_chain(guild: Guild):
    log.info("Deleting Chain for Guild(id=%s, name=%s)", guild.id, guild.name)

    Chain = Query()
    ChainDB.remove(Chain.guild_id == guild.id)


def chain_exists(guild: Guild) -> bool:
    Chain = Query()
    return ChainDB.contains(Chain.guild_id == guild.id)

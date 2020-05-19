
import logging

from tinydb import TinyDB, Query
from discord import Guild

log = logging.getLogger(__name__)

db = TinyDB('markov_db.json')

def create_chain(guild: Guild, chain: dict):
    table = db.table('Chain')

    record = {
        'guild_id': guild.id,
        'chain': chain
    }

    log.info("Persisting Chain for Guild(id=%s, name=%s)", guild.id, guild.name)
    table.upsert(record, Query().guild_id == guild.id)
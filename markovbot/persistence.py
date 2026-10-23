import os
import logging

from tinydb import TinyDB, Query
from discord import Guild

log = logging.getLogger(__name__)

db = TinyDB(os.environ.get('DB_PATH', './') + 'markov_db.json')

ChainDB = db.table('Chain')
_chain_revisions = {}


def get_chain_revision(guild: Guild) -> int:
    """Track writes in this process so cached models can skip database reads."""
    return _chain_revisions.get(guild.id, 0)


def create_chain(guild: Guild, chain: dict, user_chains: dict = None):
    record = {
        'guild_id': guild.id,
        'chain': chain,
        'user_chains': {str(user_id): model for user_id, model in (user_chains or {}).items()}
    }

    log.info("Persisting Chain for Guild(id=%s, name=%s)", guild.id, guild.name)

    Chain = Query()
    ChainDB.upsert(record, Chain.guild_id == guild.id)
    _chain_revisions[guild.id] = get_chain_revision(guild) + 1


def get_chain(guild: Guild, user_id: int = None) -> dict:
    log.debug("Retrieving Chain for Guild(id=%s, name=%s), user_id=%s", guild.id, guild.name, user_id)
    Chain = Query()

    record = ChainDB.get(Chain.guild_id == guild.id)

    if not record:
        return None

    chain = record['chain'] if user_id is None else record.get('user_chains', {}).get(str(user_id))
    return dict(chain) if chain is not None else None


def delete_chain(guild: Guild):
    log.info("Deleting Chain for Guild(id=%s, name=%s)", guild.id, guild.name)

    Chain = Query()
    ChainDB.remove(Chain.guild_id == guild.id)
    _chain_revisions[guild.id] = get_chain_revision(guild) + 1


def chain_exists(guild: Guild) -> bool:
    Chain = Query()
    return ChainDB.contains(Chain.guild_id == guild.id)

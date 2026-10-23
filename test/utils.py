from dataclasses import dataclass
from unittest.mock import patch

from tinydb import TinyDB
from tinydb.storages import MemoryStorage


def isolate_persistence(test_case):
    database = TinyDB(storage=MemoryStorage)
    test_case.addCleanup(database.close)
    table_patch = patch('markovbot.persistence.ChainDB', database.table('Chain'))
    table_patch.start()
    test_case.addCleanup(table_patch.stop)


@dataclass
class MockGuild:
    id: int = 123
    name: str = "Test Guild"
    text_channels: list = None
    me: object = None

    def __post_init__(self):
        if self.text_channels is None:
            self.text_channels = []


def get_guild():
    return MockGuild()

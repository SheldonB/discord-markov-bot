from discord import Guild


class MockState:
    def __init__(self):
        self.shard_count = 1


def get_guild():
    return Guild(data={'id': 123}, state=MockState())

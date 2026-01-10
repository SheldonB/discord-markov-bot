from dataclasses import dataclass


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

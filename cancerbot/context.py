import discord

class BotContext():

    def __init__(self, client: discord.Client):
        self.client = client
        self.cancer_level = 1

    def getClient(self) -> discord.Client:
        return self.client

    def setCancerLevel(self, level):
        self.cancer_level = level

    def getCancerLevel(self):
        return self.cancer_level

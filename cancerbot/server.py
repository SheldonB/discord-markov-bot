from discord import Server

class ServerContext:
    def __init__(self, server: Server, cancer_lvl=1):
        self.server = server
        self._cancer_level = cancer_lvl

    def getServer(self):
        return self.server

    @property
    def cancer_level(self):
        return self._cancer_level


class ServerManager:
    def __init__(self):
        self.servers: list = []

    def add(self, server: Server):
        self.servers.append(ServerContext(server))

    def remove(self, server: Server):
        for context in self.servers:
            # I think this will work?
            if context.getServer() == server:
                self.servers.remove(context)

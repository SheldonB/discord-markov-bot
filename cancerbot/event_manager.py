
class EventManager:

    def __init__(self, client):
        # This is the client that is using the event manager
        self.client = client

        self.events = []

    def register(self, event):
        self.events.append(event)

    def get_events(self, cancer_level=1):
        return [i for i in self.events if i[2] == cancer_level]

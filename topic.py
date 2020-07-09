from datetime import datetime

class Topic:
    def __init__(self, name, publisher):
        self.name = name
        self.publisher = publisher
        self.messages = {}

    def add_message(self, message):
        self.messages[str(datetime.now())] = message

    def get_name(self):
        return self.name

    def get_publisher(self):
        return self.publisher

    def get_messages(self):
        return self.messages

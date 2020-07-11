from datetime import datetime

class Topic:
    def __init__(self, name, publisher):
        self.name = name
        self.publisher = publisher
        self.subscribers = []
        self.messages = {}
        self.is_active = True

    def add_message(self, message):
        self.messages[str(datetime.now())] = message

    def subscribe_subscriber(self, subscriber):
        self.subscribers.append(subscriber)

    def get_name(self):
        return self.name

    def get_publisher(self):
        return self.publisher

    def get_subscribers(self):
        return self.subscribers

    def get_messages(self):
        return self.messages

    def get_is_active(self):
        return self.is_active

    def set_is_active(self, status):
        self.is_active = status

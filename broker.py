import socket
from datetime import datetime
import os
from _thread import start_new_thread
from topic import Topic

HOST = '127.0.0.1'
PORT = 65432
ThreadCount = 0

class Broker:
    def __init__(self):
        self.topics = {}
        self.publishers = {}
        self.subscribers = {}
        self.clients = []

        self.run_server()

    def run_server(self):
        socket_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            socket_server.bind((HOST, PORT))
        except socket.error as e:
            print('Error setting up socket server: {}'.format(e))

        print('Waitiing for a Connection..')
        socket_server.listen(5)

        while True:
            client, address = socket_server.accept()
            self.clients.append(client)
            print('Connected to: ' + address[0] + ':' + str(address[1]))
            start_new_thread(self.threaded_client, (client, ))
            global ThreadCount
            ThreadCount += 1
            print('Thread Number: ' + str(ThreadCount))

        socket_server.close()

    def threaded_client(self, connection):
        connection.sendall(str.encode('Server: What do you want to do?'))
        self.determine_what_to_do(connection)

        while True:
            data = connection.recv(1024)
            message = data.decode('utf-8')
            print(connection)
            reply = 'Server: recieved \'' + message + '\''
            if not data:
                connection.sendall(str.encode('Server: Ending communication.\n'))
                break
            connection.sendall(str.encode(reply))
            result = self.determine_what_to_do(connection, message)
            print(result)
            connection.sendall(str.encode(result))
        connection.close()

    def determine_what_to_do(self, connection):
        data = connection.recv(1024)
        message = data.decode('utf-8')

        if 'Publish' in message:
            self.handle_publisher(connection, message)
            return
        elif 'Subscribe' in message:
            self.handle_subscriber(connection, message)
            self.subscribers[str(datetime.now())] = connection
            connection.sendall(str.encode("You are a subscriber."))

    def handle_publisher(self, connection, message):
        self.publishers[str(datetime.now())] = connection

        new_topic = Topic(' '.join(self.separate_str_by_space(message)[1:]).rstrip('\n'), connection)
        self.topics[str(datetime.now())] = new_topic

        reply = "Server: topic \'" + new_topic.get_name() + "\' has been published."
        print(reply)
        connection.sendall(str.encode(reply + '\n'))

        self.receive_topic_messages_and_respond(connection)
        return

    def receive_topic_messages_and_respond(self, connection):
        specified_topic = None
        for topic in self.topics.values():
            if topic.get_publisher() == connection:
                specified_topic = topic

        while True:
            data = connection.recv(1024)
            message = data.decode('utf-8')
            reply = 'Server: recieved \'' + message + '\' to be published under topic \'' + specified_topic.get_name() + '\'.'
            if not data:
                reply = 'Server: Ending communication.\n'
                connection.sendall(str.encode(reply))
                break
            print(reply)
            connection.sendall(str.encode(reply + '\n'))

            specified_topic.add_message(message)
            print(specified_topic.get_name() + ' messages: ',end='')
            print(str(specified_topic.get_messages().values()))
            print()

        connection.close()

    def handle_subscriber(self, connection, message):
        pass

    def separate_str_by_space(self, message):
        return message.split(' ')

# def serialize_dict_of_objects(dictionary):
#     serialized_objects = { key:topic.__dict__ for (key,topic) in dictionary.items() }
#     return json.dumps(serialized_objects)

def main():
    Broker()

if __name__ == "__main__":
    main()

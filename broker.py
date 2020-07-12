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
            print('Thread Number: ' + str(ThreadCount) + '.\n')

        socket_server.close()

    def threaded_client(self, connection):
        connection.sendall(str.encode('Server: What do you want to do?'))
        self.determine_what_to_do(connection)

    def determine_what_to_do(self, connection):
        try:
            data = connection.recv(1024)
            message = data.decode('utf-8')
        except:
            print('Connection to ' + ':'.join(map(str,connection.getpeername())) + ' lost.\n')

            self.remove_client_from_clients_list(connection)

            return

        if 'Publish' in message:
            self.handle_publisher(connection, message)
        elif 'active topics' in message:
            self.handle_subscriber(connection)
        else:
            print("\'" + message + "\' is not a valid option. Ending communications with " + ':'.join(map(str,connection.getpeername())) + ".\n")

            self.remove_client_from_clients_list(connection)

            connection.close()

            return
        
        self.remove_client_from_clients_list(connection)

        return

    def handle_publisher(self, connection, message):
        self.publishers[str(datetime.now())] = connection

        new_topic = Topic(' '.join(self.separate_str_by_space(message)[1:]).rstrip('\n'), connection)
        self.topics[str(datetime.now())] = new_topic

        reply = "Server: topic \'" + new_topic.get_name() + "\' has been published."
        print(reply)

        try:
            connection.sendall(str.encode(reply + '\n'))

            self.receive_topic_messages_and_respond(connection)
        except:
            print('Connection to ' + ':'.join(map(str,connection.getpeername())) + ' lost.\n')

            for topic in self.topics.values():
                if topic.get_publisher() == connection:
                    topic.set_is_active(False)

                    self.send_inactive_topic_message_to_subs(topic)

            self.remove_client_from_clients_list(connection)
            self.remove_client_from_publishers_list(connection)

        return

    def receive_topic_messages_and_respond(self, connection):
        specified_topic = None
        for topic in self.topics.values():
            if topic.get_publisher() == connection:
                specified_topic = topic

        while True:
            try: 
                data = connection.recv(1024)
                message = data.decode('utf-8')
            
                if not data:
                    reply = 'Server: Ending communication.\n'
                    connection.sendall(str.encode(reply))
                    break
                
                specified_topic.add_message(message)
                self.send_topic_message_to_subscribers(specified_topic, message)

                reply = 'Server: message \'' + message + '\' has been published under topic \'' + specified_topic.get_name() + '\'.'
                print(reply)
                connection.sendall(str.encode(reply + '\n'))

                print(specified_topic.get_name() + ' messages: ',end='')
                print(str(specified_topic.get_messages().values()))
                print()
            except:
                print('Connection to ' + ':'.join(map(str,connection.getpeername())) + ' lost.\n')

                for topic in self.topics.values():
                    if topic.get_publisher() == connection:
                        topic.set_is_active(False)

                        self.send_inactive_topic_message_to_subs(topic)

                self.remove_client_from_clients_list(connection)
                self.remove_client_from_publishers_list(connection)

                break

        connection.close()

    def handle_subscriber(self, connection):
        try:
            active_topics_list = self.get_active_topics()

            if not active_topics_list:
                message = 'No active topics found.'
                print(message)
                connection.sendall(str.encode(message))
            else:
                print('Active topics: ' + ", ".join(active_topics_list))
                connection.sendall(str.encode('Topics: ' + ", ".join(active_topics_list)))

                topics_list =  self.subscribe_subscriber_to_topics(connection)
                if type(topics_list) is str:
                    print('Connection to ' + ':'.join(map(str,connection.getpeername())) + ' lost.\n')
                    print('Unsubscribing ' + ':'.join(map(str,connection.getpeername())) + ' from any topics and removing from server.\n')

                    self.remove_client_from_clients_list(connection)
                    self.remove_client_from_subscribers_list(connection)
                    self.remove_client_from_topics(connection)

                    return
                elif not topics_list:
                    message = 'No matching topics found. Ending communication'
                    print(message + 'with ' + ':'.join(map(str,connection.getpeername())) + '.\n')
                    connection.sendall(str.encode(message + '.'))

                    self.remove_client_from_clients_list(connection)
                else:
                    message = 'Client \'' + ':'.join(map(str,connection.getpeername())) + '\' has been subscribed to ' + ', '.join(topics_list) + '.'
                    print(message + '\n')
                    connection.sendall(str.encode(message))

                    self.subscribers[str(datetime.now())] = connection
        except:
            print('Connection to ' + ':'.join(map(str,connection.getpeername())) + ' lost.\n')
            
            self.remove_client_from_clients_list(connection)

        while True:
            try:
                data = connection.recv(1024)
                message = data.decode('utf-8')
                print('Client \'' + ':'.join(map(str,connection.getpeername())) + '\': ' + message)

                if 'Unsub from' in message:
                    unsubed_topics_list = self.unsubscribe_sub_from_topic(connection, message.split(' ')[2:])

                    if not unsubed_topics_list:
                        reply = 'No topics with any of the specified names found.'
                    else:
                        reply = 'Client \'' + ':'.join(map(str,connection.getpeername())) + '\' will be unsubscribed from: ' + ', '.join(unsubed_topics_list) + '.'
                    
                    print(reply + '\n')
                    connection.sendall(str.encode(reply))
                elif 'Get active topics' in message:
                    active_topics_list = self.get_active_topics()

                    print('Active topics: ' + ", ".join(active_topics_list) + '\n')
                    connection.sendall(str.encode('Topics: ' + ", ".join(active_topics_list)))
                elif 'stop' in message.lower():
                    reply= 'Client \'' + ':'.join(map(str,connection.getpeername())) + '\' will be set to only receive messages.'
                    print(reply + '\n')
                    
                    connection.sendall(str.encode(reply))
                    break
                else:
                    reply = 'Unrecognized command.'
                    print(reply + '\n')
                    connection.sendall(str.encode(reply))

            except:
                print('Connection to ' + ':'.join(map(str,connection.getpeername())) + ' lost.\n')
                print('Unsubscribing ' + ':'.join(map(str,connection.getpeername())) + ' from any topics and removing from server.\n')

                self.remove_client_from_clients_list(connection)
                self.remove_client_from_subscribers_list(connection)
                self.remove_client_from_topics(connection)
                break

    def subscribe_subscriber_to_topics(self, connection):
        try:
            data = connection.recv(1024)
            message = data.decode('utf-8')

            found_topics = []

            if not message == 'No topics specified.':
                for topic_name in self.separate_str_by_space(message):
                    for topic in self.topics.values():
                        if topic_name == topic.get_name() and topic.get_is_active():
                            topic.subscribe_subscriber(connection)
                            found_topics.append(topic_name)

            return found_topics
        except:
            return 'Connection failure'

    def send_topic_message_to_subscribers(self, topic, message):
        for subscriber in self.subscribers.values():
            if subscriber in topic.get_subscribers():
                try:
                    subscriber.sendall(str.encode('\'' + topic.get_name() + '\': ' + message))
                except:
                    print('Cannot connect to ' + ':'.join(map(str,subscriber.getpeername())) + '.')
                    print('Unsubscribing ' + ':'.join(map(str,subscriber.getpeername())) + ' from any topics and removing from server.\n')

                    self.remove_client_from_clients_list(subscriber)
                    self.remove_client_from_subscribers_list(subscriber)
                    self.remove_client_from_topics(subscriber)

    def unsubscribe_sub_from_topic(self, connection, topic_list):
        unsubed_topic_list = []

        for topic_name in topic_list:
            for actual_topic in self.topics.values():
                if topic_name.lower() == actual_topic.get_name().lower():
                    if connection in actual_topic.get_subscribers():
                        actual_topic.subscribers.remove(connection)
                        unsubed_topic_list.append(actual_topic.get_name())

        return unsubed_topic_list

    def remove_client_from_clients_list(self, connection):
        if connection in self.clients:
            self.clients.remove(connection)

    def remove_client_from_subscribers_list(self, connection):
        for key,client in self.subscribers.copy().items():
            if client == connection:
                del self.subscribers[key]

    def remove_client_from_publishers_list(self, connection):
        for key,client in self.publishers.copy().items():
            if client == connection:
                del self.publishers[key]

    def remove_client_from_topics(self, connection):
        for topic in self.topics.values():
            if connection in topic.get_subscribers():
                topic.subscribers.remove(connection)

    def send_inactive_topic_message_to_subs(self, topic):
        for subscriber in topic.get_subscribers():
            try:
                subscriber.sendall(str.encode('Topic \'' + topic.get_name() + '\' has become inactive.'))
            except:
                print('Cannot connect to ' + ':'.join(map(str,subscriber.getpeername())) + '.')
                print('Unsubscribing ' + ':'.join(map(str,subscriber.getpeername())) + ' from any topics and removing from server.\n')

                self.remove_client_from_clients_list(subscriber)
                self.remove_client_from_subscribers_list(subscriber)
                self.remove_client_from_topics(subscriber)

    def get_active_topics(self):
        topics_list = [ topic.name for topic in self.topics.values() if topic.get_is_active() ]
        return topics_list

    def separate_str_by_space(self, message):
        return message.split(' ')

def main():
    Broker()

if __name__ == "__main__":
    main()

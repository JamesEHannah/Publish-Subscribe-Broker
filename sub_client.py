import socket
import threading

HOST = '127.0.0.1'
PORT = 65432

class Subscriber:
    def __init__(self):
        self.subscribe()

    def subscribe(self):
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        print('Waiting for connection.')
        try:
            client_socket.connect((HOST, PORT))
        except socket.error as e:
            print(str(e))

        try:
            response = client_socket.recv(1024)
            print(response.decode('utf-8'))

            message = 'Get active topics.'
            print(message + '\n')

            client_socket.send(str.encode(message))
            response = client_socket.recv(1024).decode('utf-8')
            print('Server: ' + response)

            if not 'No active topics found.' in response:
                self.subscribe_to_topics_and_listen_for_messages(client_socket)
        except:
            print('Connection to server lost.\n')

    def subscribe_to_topics_and_listen_for_messages(self, client_socket):
        topics_to_subscribe_to = self.get_topics_input()

        if not topics_to_subscribe_to:
            message = 'No topics specified.'
            print(message)
            try:
                client_socket.sendall(str.encode(message))

                response = client_socket.recv(1024)
                print('Server: ' + response.decode('utf-8') + '\n')
            except:
                print('Connection to server lost.\n')
        else:
            try:
                client_socket.send(str.encode(" ".join(topics_to_subscribe_to)))

                response = client_socket.recv(1024)
                print('Server: ' + response.decode('utf-8') + '\n')
            except:
                print('Connection to server lost.\n')
                return

            threading.Thread(target=self.listen_for_messages, args=(client_socket,)).start()

            while True:
                try:
                    message = input('What do you want to do now? (Options: \'Unsub from A B\' / \'Get active topics\' / \'Stop\')\n')

                    client_socket.send(str.encode(message))

                    response = client_socket.recv(1024)
                    print('Server: ' + response.decode('utf-8') + '\n')

                    if message.lower() == 'stop':
                        break

                except:
                    print('Connection to server lost.\n')
                    break
        
        return

    def listen_for_messages(self, client_socket):
        while True:
            try:
                response = client_socket.recv(1024)
                print('Server: ' + response.decode('utf-8') + '\n')
            except:
                print('Connection to server lost.\n')
                break

    def get_topics_input(self):
        topics_to_subscribe_to = []

        topic = input('What topic do you want to subscribe to? (reply \'Exit\' when done) ')
        while not topic.lower() == 'exit':
            topics_to_subscribe_to.append(topic.rstrip('\n'))

            topic = input('What other topic do you want to subscribe to? (reply \'Exit\' when done) ')

        print()
        return topics_to_subscribe_to

test_sub = Subscriber()

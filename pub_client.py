import socket
import time
import random
import string

HOST = '127.0.0.1'
PORT = 65432

class Publisher:
    def __init__(self):
        self.publish()

    def publish(self):
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.topic = input('What is your topic? ')

        print('Waiting for connection')
        try:
            client_socket.connect((HOST, PORT))
        except socket.error as e:
            print(str(e))

        response = client_socket.recv(1024)
        print(response.decode('utf-8'))
        print('Publisher: publish ' + self.topic + '\'.')

        client_socket.send(str.encode('Publish ' + self.topic))
        response = client_socket.recv(1024)
        print(response.decode('utf-8'))

        # while True:
        #     # message = input('Say Something: ')

        #     client_socket.send(str.encode(message))
        #     response = client_socket.recv(1024)
        #     print(response.decode('utf-8'))
        self.send_messages(client_socket)

        client_socket.close()

    def send_messages(self, client_socket):
        while True:
            message = ''.join(random.choices(string.ascii_uppercase + string.digits, k=random.randint(10, 30)))
            print('Publisher: publish \'' + message + '\' to topic \'' + self.topic + '\'.')

            client_socket.send(str.encode(message))
            response = client_socket.recv(1024)
            print(response.decode('utf-8'))
            time.sleep(random.randint(30, 60))

test_pub = Publisher()
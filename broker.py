import socket
import datetime
import os
from _thread import start_new_thread

HOST = '127.0.0.1'
PORT = 65432
ThreadCount = 0

class Broker:
    def __init__(self):
        self.topics = {}
        self.publishers = {}
        self.subscribers = {}

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
            print('Connected to: ' + address[0] + ':' + str(address[1]))
            start_new_thread(self.threaded_client, (client, ))
            global ThreadCount
            ThreadCount += 1
            print('Thread Number: ' + str(ThreadCount))

        socket_server.close()

    def threaded_client(self, connection):
        connection.send(str.encode('Welcome to the Server\n'))
        while True:
            data = connection.recv(1024)
            reply = 'Server Says: ' + data.decode('utf-8')
            if not data:
                break
            connection.sendall(str.encode(reply))
        connection.close()

def main():
    sub_pub_broker = Broker()
    print(sub_pub_broker)

if __name__ == "__main__":
    main()

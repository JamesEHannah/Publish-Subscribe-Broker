import socket

HOST = '127.0.0.1'
PORT = 65432

class Subscriber:
    def __init__(self):
        self.subscribe()

    def subscribe(self):
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        print('Waiting for connection')
        try:
            client_socket.connect((HOST, PORT))
        except socket.error as e:
            print(str(e))

        response = client_socket.recv(1024)
        print(response.decode('utf-8'))

        client_socket.send(str.encode('Subscribe'))
        response = client_socket.recv(1024)
        print(response.decode('utf-8'))

        while True:
            message = input('Say Something: ')
            client_socket.send(str.encode(message))
            response = client_socket.recv(1024)
            print(response.decode('utf-8'))
            response = client_socket.recv(1024)
            print(response.decode('utf-8'))

        client_socket.close()

test_sub = Subscriber()

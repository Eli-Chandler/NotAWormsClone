import socket
import threading
from src.multiplayer.message import Message, Ping
import json

class Server:
    def __init__(self):
        self.host = '127.0.0.1'
        self.port = 5000
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((self.host, self.port))
        self.clients = []
        self.nicknames = []

    def broadcast(self, author, message):
        for client in self.clients:
            if client != author:
                self.send_message(client, message)

    def handle_client(self, client):
        while True:
            #try:
            message = self.recieve_message(client)
            self.broadcast(client, message)
            #self.send_message(client, Ping())
            '''except:
                print('Big error')
                index = self.clients.index(client)
                self.clients.remove(client)
                client.close()
                nickname = self.nicknames[index]
                self.nicknames.remove(nickname)

                message = Message('server', 'player_leave', nick=nickname)
                self.broadcast(message)
                break'''

    def send_message(self, client, message):
        client.send(message.to_message())


    def recieve_message(self, client):

        message = client.recv(1024).decode('utf-8')
        message = Message.from_str(message)
        #print(message.author, message.action, message.body)
        return message

    def receive(self):
        while True:
            print('test')
            client, address = self.server.accept()
            print(f"Connected with {str(address)}")

            self.send_message(client, Message('server', 'request_nickname'))
            message = self.recieve_message(client)
            self.send_message(client, Message('server', 'nickname_approved'))

            self.nicknames.append(message.author)
            self.clients.append(client)

            print(f"Nickname of client is {message.author}!")

            thread = threading.Thread(target=self.handle_client, args=(client,))
            thread.start()

    def start(self):
        print("Server is listening...")
        self.server.listen()
        self.receive()

if __name__ == '__main__':
    s = Server()
    s.start()
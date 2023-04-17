import socket
import threading
import json
from src.multiplayer.message import Message, SendNickname, UpdatePlayer, Pong
from src.sprites import player

responses = {
    'request_username': SendNickname,
    'ping': Pong
}

players = {}


class Client:
    def __init__(self, nickname, window):
        self.window = window
        self.host = '127.0.0.1'
        self.port = 5000
        self.nickname = nickname
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect((self.host, self.port))
        self.unread_data = b''

    def receive(self):
        while True:
            while not b'n' in self.unread_data:
                chunk = self.client.recv(1024)
                self.unread_data += chunk

            message, _, self.unread_data = self.unread_data.partition(b'\n')

            if message:
                try:
                    message = message.decode('utf-8')
                    message = Message.from_str(message)
                    self.handle_server_message(message)
                except json.decoder.JSONDecodeError:
                    print('Json decode error')

    def handle_server_message(self, message):
        if message.action == 'update_player':
            if message.author not in players:
                players[message.author] = player.Player(
                    message.body['center_x'],
                    message.body['center_y'],
                    message.author
                )
                self.window.player_list.append(players[message.author])
            else:
                players[message.author].center_x = message.body['center_x']
                players[message.author].center_y = message.body['center_y']

        if message.action in responses:
            response = responses[message.action](self)
            self.send_message(response)

    def send_message(self, message):
        self.client.send(message.to_message())

    def start(self):
        receive_thread = threading.Thread(target=self.receive)
        receive_thread.start()

    def send_client_info(self):
        message = UpdatePlayer(self)
        self.send_message(message)
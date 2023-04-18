import queue
import random

import arcade
from src.game import game
from src.sprites import block, bullet, explosion, player, weapon
from queue import Queue
from threading import Thread
from src.multiplayer.message import Message, GivePosition, GivePositions, CreateExplosion
import struct

import socket

class Server(game.MyGame):
    def __init__(self, settings, host='127.0.0.1', port=5000):
        self.nickname = 'server'
        self.is_client = False

        super().__init__(settings)
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.start()
        self.clients = {}
        self.players = {}
        self.setup()

    def start(self):
        self.server_socket.bind((self.host, self.port))
        self.server_socket.setblocking(False)
        self.server_socket.listen()



    def setup(self):
        arcade.set_background_color(arcade.color.SKY_BLUE)

        self.player_list = arcade.SpriteList()
        self.block_list = arcade.SpriteList(use_spatial_hash=True)
        self.bullet_list = arcade.SpriteList()
        self.explosion_list = arcade.SpriteList()

        self.sprite_list_append_queue = queue.Queue()
        block.Block(self.SCREEN_WIDTH / 2, self.SCREEN_HEIGHT / 2)

    def on_update(self, delta_time):
        for i in range(2):
            self.receive_data_and_handle_messages()

        for b in self.bullet_list:
            b.update(delta_time)

        for e in self.explosion_list:
            e.update(delta_time)

        self.send_server_info()

    def on_draw(self):
        arcade.start_render()
        self.block_list.draw()
        self.player_list.draw()
        self.bullet_list.draw()
        self.explosion_list.draw()

    def send_server_info(self):
        self.broadcast_message(GivePositions(self.player_list))

    def receive_data_and_handle_messages(self):
        self.recieve_and_handle_new_clients()

        for nickname, client in self.clients.items():
            message = self.recieve_message(client)
            if message is None:
                continue
            self.handle_message(client, message)

    def handle_message(self, client, message):
        handlers= {
            'get_position': self.handle_get_position,
            'give_position': self.handle_give_position,
            'create_explosion': self.handle_create_explosion
        }

        return handlers[message.action](client, message)

    def handle_create_explosion(self, client, message):
        source = message.body['source']
        center_x = message.body['center_x']
        center_y = message.body['center_y']
        diameter = message.body['diameter']
        e = explosion.Explosion(source, center_x, center_y, diameter)
        self.explosion_list.append(e)

        self.broadcast_message(CreateExplosion(e))

    def handle_give_position(self, client, message):
        nickname = message.author
        p = self.players[nickname]
        p.center_x = message.body['center_x']
        p.center_y = message.body['center_y']
        p.angle = message.body['angle']

    def handle_get_position(self, client, message):
        nickname = message.body['nickname']
        p = self.players[nickname]
        self.send_message(client, GivePosition(p.center_x, p.center_y, p.angle))


    def send_message(self, client, message):
        client.send(message.to_message())

    def broadcast_message(self, message):
        for client in self.clients.values():
            self.send_message(client, message)

    def recieve_message(self, client):
        try:
            length_bytes = client.recv(4)
        except BlockingIOError:
            return None

        length = struct.unpack('!I', length_bytes)[0]
        message_bytes = b''
        while len(message_bytes) < length:
            chunk = client.recv(length - len(message_bytes))
            message_bytes += chunk
        return Message.from_message(message_bytes)

    def recieve_and_handle_new_clients(self):
        try:
            client_socket, client_address = self.server_socket.accept()

            message = self.recieve_message(client_socket)
            if message.action == 'update_nickname':
                nickname = message.body['nickname']
                p = player.Player(random.randint(50, self.SCREEN_WIDTH-50), random.randint(50, self.SCREEN_HEIGHT-50), nickname)
                self.player_list.append(p)
                self.clients[nickname] = client_socket
                self.players[nickname] = p

        except BlockingIOError:
            pass
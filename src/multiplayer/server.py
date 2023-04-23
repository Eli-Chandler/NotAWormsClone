import queue
import random

import arcade
from src.game import game
from src.sprites import block, bullet, explosion, player, weapon
from queue import Queue
from threading import Thread
from src.multiplayer.message import Message, GivePosition, GivePositions, CreateExplosion, GivePreviousExplosions
import struct

import socket

class Server(game.MyGame):
    def __init__(self, settings, host='0.0.0.0', port=25561):
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

        self.previous_explosions = []

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
        #self.player_list.draw()
        self.bullet_list.draw()
        for player in self.player_list:
            player.draw()
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
            'create_explosion': self.handle_create_explosion,
            'create_bullet': self.handle_create_bullet
        }

        return handlers[message.action](client, message)

    def handle_create_explosion(self, client, message):
        source = message.body['source']
        center_x = message.body['center_x']
        center_y = message.body['center_y']
        diameter = message.body['diameter']
        self.previous_explosions.append(message.body)
        e = explosion.Explosion(source, center_x, center_y, diameter)
        self.explosion_list.append(e)

        self.broadcast_message(message)

    def handle_create_bullet(self, client, message):
        center_x = message.body['center_x']
        center_y = message.body['center_y']
        angle = message.body['angle']
        scale = message.body['scale']
        change_x = message.body['change_x']
        change_y = message.body['change_y']
        weapon_name = message.body['weapon_name']

        b = bullet.ServerBullet(center_x, center_y, change_x, change_y, weapon_name, angle, scale)
        self.bullet_list.append(b)

        self.broadcast_message(message)

    def handle_give_position(self, client, message):
        nickname = message.author
        p = self.players[nickname]
        p.center_x = message.body['center_x']
        p.center_y = message.body['center_y']
        if p.current_weapon is None:
            p.current_weapon = weapon.AK47(p)
        if p.current_weapon.name != message.body['weapon_name']:
            if message.body['weapon_name'] == 'ak47':
                p.current_weapon = weapon.AK47(p)
            if message.body['weapon_name'] == 'p90':
                p.current_weapon = weapon.P90(p)
        p.current_weapon.angle = message.body['weapon_angle']
        p.current_weapon.scale = message.body['weapon_scale']

        p.current_weapon.center_x = p.center_x
        p.current_weapon.center_y = p.center_y
        p.health = message.body['health']

    def handle_get_position(self, client, message):
        nickname = message.body['nickname']
        p = self.players[nickname]
        self.send_message(client, GivePosition(p.center_x, p.center_y, 'none', 'none', 'none', 100))
        self.send_message(client, GivePreviousExplosions(self.previous_explosions))

    def send_message(self, client, message):
        try:
            client.send(message.to_message())
        except BlockingIOError:
            pass

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
        client.setblocking(True)
        while len(message_bytes) < length:
            chunk = client.recv(length - len(message_bytes))
            message_bytes += chunk
        client.setblocking(False)
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
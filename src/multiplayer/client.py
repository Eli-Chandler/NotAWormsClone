import queue

import arcade
from src.game import game
from src.sprites import block, bullet, explosion, player, weapon
from src.game import physics_engine
from src.utils import utils
from queue import Queue
from threading import Thread
import struct

from src.multiplayer.message import Message, UpdateNickname, GetPosition, GivePosition

import socket


class Client(game.MyGame):
    def __init__(self, username, settings, server_host='127.0.0.1', server_port=5000):
        self.nickname = username
        self.is_client = True

        super().__init__(settings)
        self.server_host = server_port
        self.server_port = server_host
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


        start_x, start_y = self.connect_to_server()

        self.mouse_x = 0
        self.mouse_y = 0


        self.setup(start_x, start_y)

    def connect_to_server(self):
        self.client_socket.connect(('127.0.0.1', 5000))
        print('Connected')
        self.send_message(UpdateNickname(self.nickname))
        self.send_message(GetPosition(nickname=self.nickname))
        while True:
            message = self.recieve_message()
            if message and message.action == 'give_position':
                break
        start_x = message.body['center_x']
        start_y = message.body['center_y']
        self.client_socket.setblocking(False)

        return start_x, start_y

    def setup(self, start_x, start_y):
        arcade.set_background_color(arcade.color.SKY_BLUE)

        self.player_list = arcade.SpriteList()
        self.block_list = arcade.SpriteList(use_spatial_hash=True)
        self.bullet_list = arcade.SpriteList()
        self.explosion_list = arcade.SpriteList()

        self.other_players = {}

        self.sprite_list_append_queue = queue.Queue()
        block.Block(self.SCREEN_WIDTH / 2, self.SCREEN_HEIGHT / 2)
        self.player = player.Player(start_x, start_y, self.nickname, True)
        self.player_list.append(self.player)

        self.physics_engine = physics_engine.PhysicsEngine(self.player, self.block_list, self.settings.get('GRAVITY', 2))

    def send_message(self, message):
        self.client_socket.send(message.to_message())

    def recieve_message(self):
        try:
            length_bytes = self.client_socket.recv(4)
        except BlockingIOError:
            return None

        length = struct.unpack('!I', length_bytes)[0]
        message_bytes = b''
        while len(message_bytes) < length:
            chunk = self.client_socket.recv(length - len(message_bytes))
            message_bytes += chunk
        return Message.from_message(message_bytes)

    def on_update(self, delta_time):
        for i in range(2):
            self.recieve_and_handle_messages()


        self.player.update(delta_time)
        self.physics_engine.update(delta_time)

        for b in self.bullet_list:
            b.update(delta_time)

        for e in self.explosion_list:
            e.update(delta_time)

    def on_draw(self):
        arcade.start_render()
        self.block_list.draw()
        self.bullet_list.draw()
        self.player_list.draw()
        self.player.weapon_list.draw()
        self.explosion_list.draw()


    def send_explosion(self, explosion):
        self.send_message()


    def recieve_and_handle_messages(self):
        message = self.recieve_message()
        if message:
            if message.author == self.nickname:
                return

            handlers= {
                'give_positions': self.handle_give_positions,
                'create_explosion': self.handle_create_explosion
            }

            return handlers[message.action](message)

    def handle_create_explosion(self, message):
        source = message.body['source']

        center_x = message.body['center_x']
        center_y = message.body['center_y']
        diameter = message.body['diameter']
        e = explosion.Explosion(source, center_x, center_y, diameter)
        self.explosion_list.append(e)


    def handle_give_positions(self, message):
        positions = message.body['positions']

        for nickname, position in positions.items():
            print(nickname, position)
            if nickname == self.player.nickname:
                continue

            if nickname not in self.other_players:
                p = player.Player(position['center_x'], position['center_y'], nickname)
                self.other_players[nickname] = p
                self.player_list.append(p)
            else:
                self.other_players[nickname].center_x = position['center_x']
                self.other_players[nickname].center_y = position['center_y']



    def on_key_press(self, symbol: int, modifiers: int):
        if symbol == arcade.key.F:
            self.set_fullscreen(not self.fullscreen)

        self.player.on_key_press(symbol, modifiers)

    def on_key_release(self, symbol: int, modifiers: int):
        self.player.on_key_release(symbol, modifiers)

    def on_mouse_motion(self, x: int, y: int, dx: int, dy: int):
        self.mouse_x = x
        self.mouse_y = y

    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int):
        x, y = utils.convert_viewport_position_to_global_position(x, y)
        self.player.on_mouse_press(button, modifiers)

    def on_mouse_release(self, x: int, y: int, button: int, modifiers: int):
        self.player.on_mouse_release(button, modifiers)

    def test_subdivide(self, x, y):
        hits = arcade.get_sprites_at_point((x, y), self.block_list)
        for hit in hits:
            hit.subdivide()
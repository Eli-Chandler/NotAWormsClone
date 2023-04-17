import arcade
from src.sprites import player, block, explosion
from src.game import physics_engine
from src.utils import utils
from src.multiplayer import client
import json

class MyGame(arcade.Window):
    def __init__(self, username, settings):
        self.nickname = username
        self.settings = settings
        self.SCREEN_WIDTH = self.settings.get('SCREEN_WIDTH')
        self.SCREEN_HEIGHT =  self.settings.get('SCREEN_HEIGHT')
        super().__init__(self.SCREEN_WIDTH, self.SCREEN_HEIGHT, 'NotAWormsClone')

        self.set_update_rate(1/self.settings.get('FPS', 144))
        self.client = client.Client(username, self)
        self.setup()
        self.client.start()



    def setup(self):
        arcade.set_background_color(arcade.color.SKY_BLUE)

        self.fps = 0
        self.mouse_x = 0
        self.mouse_y = 0
        self.block_list = arcade.SpriteList(use_spatial_hash=True)
        self.explosion_list = arcade.SpriteList()
        self.player_list = arcade.SpriteList()
        self.bullet_list = arcade.SpriteList()

        block.Block(self.SCREEN_WIDTH / 2, self.SCREEN_HEIGHT / 2)
        self.player = player.Player(500, 500, self.nickname, True) # Create initial objects
        self.player_list.append(self.player)


        self.physics_engine = physics_engine.PhysicsEngine(self.player, self.block_list, self.settings.get('GRAVITY', 2))

    def on_draw(self):
        arcade.start_render()
        self.block_list.draw()
        self.player_list.draw()
        self.explosion_list.draw()
        self.player.weapon_list.draw()
        self.bullet_list.draw()




    def on_update(self, delta_time: float):
        self.physics_engine.update(delta_time)

        self.player.update(delta_time)

        for bullet in self.bullet_list:
            bullet.update(delta_time)

        for explosion in self.explosion_list:
            explosion.update(delta_time)

        self.client.send_client_info()

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

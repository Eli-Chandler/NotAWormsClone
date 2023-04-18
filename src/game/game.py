import arcade
from src.sprites import player, block, explosion
from src.game import physics_engine
from src.utils import utils
import json

class MyGame(arcade.Window):
    def __init__(self, settings):
        self.settings = settings

        self.SCREEN_WIDTH = self.settings.get('SCREEN_WIDTH')
        self.SCREEN_HEIGHT =  self.settings.get('SCREEN_HEIGHT')
        self.set_update_rate(1 / self.settings.get('FPS', 144))

        super().__init__(self.SCREEN_WIDTH, self.SCREEN_HEIGHT, 'NotAWormsClone')



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
        self.time += delta_time
        self.physics_engine.update(delta_time)

        self.player.update(delta_time)

        for bullet in self.bullet_list:
            bullet.update(delta_time)

        for explosion in self.explosion_list:
            explosion.update(delta_time)

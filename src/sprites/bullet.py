import arcade
import math

from src.sprites import explosion
from src.multiplayer.message import CreateBullet

class ServerBullet(arcade.Sprite):
    def __init__(self, center_x, center_y, change_x, change_y, weapon_name, angle, scale):
        self.is_server_bullet = True
        self.window = arcade.get_window()
        texture = f'assets/images/weapons/{weapon_name}/{weapon_name}_bullet.png'
        super().__init__(filename=texture,
                         center_x=center_x,
                         center_y=center_y,
                         scale=scale,
                         angle=angle)

        self.weapon_name = weapon_name

        self.change_x = change_x
        self.change_y = change_y
        self.already_hit = []

    def update(self, delta_time):
        self.center_x += self.change_x * delta_time
        self.center_y += self.change_y * delta_time

        if arcade.check_for_collision_with_list(self, self.window.block_list):
            self.explode()

    def explode(self):
        self.kill()


class Bullet(arcade.Sprite):
    def __init__(self, weapon, speed, explosion_diameter, scale=0.05):
        self.window = arcade.get_window()
        self.weapon = weapon
        self.weapon_name = weapon.name
        self.speed = speed
        self.explosion_diameter = explosion_diameter
        self.is_server_bullet = False

        texture = f'assets/images/weapons/{self.weapon.name}/{self.weapon.name}_bullet.png'
        super().__init__(filename=texture,
                         center_x=self.weapon.center_x,
                         center_y=self.weapon.center_y,
                         angle=self.weapon.angle,
                         scale=scale)
        self.set_hit_box([(-1, -1), (-1, 1), (1, 1), (1, -1)])

        self.window.bullet_list.append(self)

        self.change_x = math.cos(math.radians(self.angle)) * self.speed
        self.change_y = math.sin(math.radians(self.angle)) * self.speed

        self.window.send_message(CreateBullet(self))

    def update(self, delta_time):
        self.center_x += self.change_x * delta_time
        self.center_y += self.change_y * delta_time

        if arcade.check_for_collision_with_list(self, self.window.block_list):
            self.explode()

    def explode(self):
        if self.window.is_client:
            e = explosion.ClientExplosion(self.weapon.owner.nickname, self.center_x, self.center_y, self.explosion_diameter)
            self.window.explosion_list.append(e)
        self.kill()


class AK47Bullet(Bullet):
    def __init__(self, weapon):
        super().__init__(weapon, 200, 25)

class P90Bullet(Bullet):
    def __init__(self, weapon):
        super().__init__(weapon, 150, 5)
import arcade
import math

from src.sprites import explosion

class Bullet(arcade.Sprite):
    def __init__(self, weapon, speed, explosion_diameter, scale=0.05):
        self.window = arcade.get_window()
        self.weapon = weapon
        self.speed = speed
        self.explosion_diameter = explosion_diameter

        texture = f'assets/images/weapons/{self.weapon.name}/{self.weapon.name}_bullet.png'
        super().__init__(filename=texture,
                         center_x=self.weapon.center_x,
                         center_y=self.weapon.center_y,
                         angle=self.weapon.angle,
                         scale=scale)

        self.window.bullet_list.append(self)

        self.change_x = math.cos(math.radians(self.angle)) * self.speed
        self.change_y = math.sin(math.radians(self.angle)) * self.speed

    def update(self, delta_time):
        self.center_x += self.change_x * delta_time
        self.center_y += self.change_y * delta_time

        if arcade.check_for_collision_with_list(self, self.window.block_list):
            self.explode()

    def explode(self):
        e = explosion.Explosion(self.center_x, self.center_y, self.explosion_diameter)
        self.window.explosion_list.append(e)
        self.kill()


class AK47Bullet(Bullet):
    def __init__(self, weapon):
        super().__init__(weapon, 200, 25)
import arcade
from src.utils import utils
from src.sprites import bullet
import numpy as np

sounds = {}

class Weapon(arcade.Sprite):
    def __init__(self, owner, name, recoil_amount, fire_rate, rapid_fire, bullet, scale=1):
        self.owner = owner
        self.name = name
        self.window = arcade.get_window()

        self.recoil_amount = recoil_amount
        self.fire_rate = fire_rate
        self.rapid_fire = rapid_fire
        self.bullet = bullet

        self.recoil = 0
        self.time_since_last_shot = 0

        self.has_fired_single_shot = False

        texture = f'assets/images/weapons/{name}/{name}.png'
        if self.name not in sounds:
            sounds[self.name] = arcade.load_sound(f'assets/sounds/weapons/ak47_shoot.wav')
        self.sound = sounds[self.name]

        super().__init__(texture, center_x=owner.center_x, center_y=owner.center_y, scale=scale)


    def update_position_and_angle(self):
        self.center_x = self.owner.center_x
        self.center_y = self.owner.center_y

        actual_angle = utils.get_angle_between_two_points(
            utils.convert_viewport_position_to_global_position(self.window.mouse_x, self.window.mouse_y),
            (self.owner.center_x, self.owner.center_y)
        )

        self.angle = actual_angle + self.recoil
        self.recoil = self.recoil * 0.9 if abs(self.recoil) > 0.1 else 0

    def update(self, delta_time):
        self.update_position_and_angle()
        self.time_since_last_shot += delta_time

        if self.owner.want_to_shoot:
            self.shoot()
        else:
            self.has_fired_single_shot = False

    def shoot(self):
        if self.time_since_last_shot < 1 / self.fire_rate:
            return
        if not self.rapid_fire and self.has_fired_single_shot:
            return

        self.bullet(self)
        recoil_sample = np.random.normal(loc=0, scale=self.recoil_amount / 3)  # loc is the mean and scale is the standard deviation
        recoil_effect = (self.recoil_amount / 2) - abs(recoil_sample)
        self.recoil += recoil_effect
        self.time_since_last_shot = 0
        self.has_fired_single_shot = True
        arcade.play_sound(self.sound)

class AK47(Weapon):
    def __init__(self, owner):
        name = 'ak47'
        super().__init__(owner, name, 90, 4, True, bullet.AK47Bullet, scale=0.5)

class P90(Weapon):
    def __init__(self, owner):
        name = 'p90'
        super().__init__(owner, name, 25, 5.5, True, bullet.P90Bullet, scale=0.5)
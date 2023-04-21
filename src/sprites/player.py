import arcade
from src.sprites import explosion
from src.sprites import weapon
from src.multiplayer.message import GivePosition
import random


class Player(arcade.Sprite):
    def __init__(self, center_x, center_y, name, is_controlled=False):
        self.weapon_list = arcade.SpriteList()
        self.current_weapon = None

        self.pressed_keys = set()

        self.window = arcade.get_window()
        self.speed = self.window.settings.get('PLAYER_MOVE_SPEED', 50)
        self.jump_speed = self.window.settings.get('PLAYER_JUMP_SPEED', 100)
        self.ground_distance_threshold_for_jump = self.window.settings.get('PLAYER_JUMP_THRESHOLD', 5)
        self.want_to_jump = False
        self.want_to_shoot = False
        self.nickname = name
        self.health = 100
        self.max_health = 100
        self.regen_rate = 5
        self.health_bar_width = 50
        self.health_bar_height = 5

        super().__init__('assets/images/player/player.png', center_x=center_x, center_y=center_y, scale=0.5, hit_box_algorithm='Detailed')
        self.is_controlled = is_controlled
        if is_controlled:
            self.spawn()
            self.add_weapon()

    def add_weapon(self):
        ak47 = weapon.AK47(self)
        self.weapon_list.append(ak47)
        self.current_weapon = ak47

    def update(self, delta_time):
        self.update_movement(delta_time)
        self.update_actions()
        self.update_viewport()
        self.current_weapon.update(delta_time)
        if self.health < self.max_health:
            self.health += self.regen_rate * delta_time
        if self.health > self.max_health:
            self.health = self.max_health

        if self.is_controlled:
            if self.health <= 0:
                self.respawn()
            if self.center_y < -1000:
                self.respawn()

    def draw(self):
        super().draw()
        if self.current_weapon:
            #print('Drawing weapon')
            self.current_weapon.draw()
        self.draw_health_bar()



    def draw_health_bar(self):
        # Draw the health bar background

        # Draw the health bar
        health_ratio = self.health / self.max_health
        health_width = self.health_bar_width * health_ratio

        color = arcade.color.GREEN if health_ratio > 0.5 else arcade.color.YELLOW if health_ratio > 0.25 else arcade.color.RED

        arcade.draw_rectangle_filled(self.center_x, self.center_y - 16, health_width, self.health_bar_height, color)



    def update_viewport(self):
        self.window.set_viewport(self.center_x - 160, self.center_x + 160, self.center_y - 90, self.center_y + 90)

    def update_actions(self):
        if arcade.MOUSE_BUTTON_LEFT in self.pressed_keys:
            self.want_to_shoot = True
        else:
            self.want_to_shoot = False

    def update_movement(self, delta_time):

        if arcade.key.W in self.pressed_keys or arcade.key.SPACE in self.pressed_keys:
            self.want_to_jump = True
        else:
            self.want_to_jump = False

        if arcade.key.A in self.pressed_keys:
            self.change_x = -self.speed
        if arcade.key.D in self.pressed_keys:
            self.change_x = self.speed

        weapon_angle = self.current_weapon.angle if self.current_weapon else 0
        weapon_name = self.current_weapon.name if self.current_weapon else 'hands'
        weapon_scale = self.current_weapon.scale if self.current_weapon else 1

        self.window.send_message(GivePosition(self.center_x, self.center_y, weapon_angle, weapon_name, weapon_scale, self.health))

    def can_jump(self):
        return self.window.physics_engine.can_jump(self.ground_distance_threshold_for_jump)

    def on_key_press(self, symbol, modifiers):
        self.pressed_keys.add(symbol)

    def on_mouse_press(self, symbol, modifiers):
        self.pressed_keys.add(symbol)

    def on_mouse_release(self, symbol, modifiers):
        if symbol in self.pressed_keys:
            self.pressed_keys.remove(symbol)

    def on_key_release(self, symbol, modifiers):
        if symbol in self.pressed_keys:
            self.pressed_keys.remove(symbol)

    def spawn(self):
        e = explosion.ClientExplosion(
            self.nickname,
            self.center_x,
            self.center_y,
            max(self.width, self.height)*3
        )

        while not e.is_fully_exploded:
            e.explode()
        e.kill()
        self.health = self.max_health

    def respawn(self):
        self.center_x = random.randint(50, self.window.SCREEN_WIDTH - 50)
        self.center_y = random.randint(50, self.window.SCREEN_HEIGHT - 50)
        self.spawn()


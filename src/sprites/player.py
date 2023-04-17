import arcade
from src.sprites import explosion
from src.sprites import weapon

class Player(arcade.Sprite):
    def __init__(self, center_x, center_y):
        self.weapon_list = arcade.SpriteList()
        self.current_weapon = None

        self.pressed_keys = set()

        self.window = arcade.get_window()
        self.speed = self.window.settings.get('PLAYER_MOVE_SPEED', 50)
        self.jump_speed = self.window.settings.get('PLAYER_JUMP_SPEED', 100)
        self.ground_distance_threshold_for_jump = self.window.settings.get('PLAYER_JUMP_THRESHOLD', 5)
        self.want_to_jump = False
        self.want_to_shoot = False

        super().__init__('assets/images/player/player.png', center_x=center_x, center_y=center_y, scale=0.5, hit_box_algorithm='Detailed')
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
        e = explosion.Explosion(
            self.center_x,
            self.center_y,
            max(self.width, self.height)*3
        )

        while not e.is_fully_exploded:
            e.explode()
        e.kill()



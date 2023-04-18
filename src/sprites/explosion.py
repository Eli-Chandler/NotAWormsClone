import arcade
from src.multiplayer.message import CreateExplosion

sound = arcade.load_sound('assets/sounds/explosion/explosion.wav')





class Explosion(arcade.Sprite):
    def __init__(self, source, center_x, center_y, diameter):
        scale = diameter/32
        self.window = arcade.get_window()
        self.source=source

        self.diameter = diameter

        self.is_fully_exploded = False

        super().__init__('assets/images/explosion/explosion.png', center_x=center_x, center_y=center_y, scale=scale)

        arcade.play_sound(sound)
        #self.window.client.send_explosion(self)

    def check_sprite_fully_outside(self, sprite):
        # Calculate the closest point on the sprite's bounding box to the circle's center
        closest_x = max(sprite.left, min(self.center_x, sprite.right))
        closest_y = max(sprite.bottom, min(self.center_y, sprite.top))

        # Calculate the distance between the closest point and the circle's center
        distance_squared = (closest_x - self.center_x) ** 2 + (closest_y - self.center_y) ** 2

        # Check if the distance is greater than the circle's radius squared
        return distance_squared > (self.diameter / 2) ** 2

    def check_sprite_fully_encompassed(self, sprite):
        bottom_left = (sprite.left, sprite.bottom)
        bottom_right = (sprite.right, sprite.bottom)
        top_left = (sprite.left, sprite.top)
        top_right = (sprite.right, sprite.top)

        points = [bottom_left, bottom_right, top_left, top_right]

        for point in points:
            distance_from_center = ((point[0] - self.center_x)**2 + (point[1] - self.center_y)**2) ** 0.5
            if distance_from_center > self.diameter/2:
                return False
        return True

    def update(self, delta_time):
        if self.is_fully_exploded:
            self.destroy(delta_time)
        else:
            self.explode()

    def explode(self):
        hits = arcade.check_for_collision_with_list(self, self.window.block_list)

        num_subdivided = 0

        for hit in hits:
            if self.check_sprite_fully_encompassed(hit):
                self.window.block_list.remove(hit)
            elif self.check_sprite_fully_outside(hit):
                continue
            else:
                hit.subdivide()
                num_subdivided += 1

        if num_subdivided == 0:
            self.is_fully_exploded = True

    def destroy(self, delta_time):
        new_alpha = self.alpha / (1 + 10 * delta_time)
        if new_alpha > 10:
            self.alpha = new_alpha
        else:
            self.kill()

class ClientExplosion(Explosion):
    def __init__(self, source, center_x, center_y, diameter):
        self.window = arcade.get_window()
        self.source=source
        super().__init__(source, center_x, center_y, diameter)
        self.window.send_message(CreateExplosion(self))
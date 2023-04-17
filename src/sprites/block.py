import arcade
from PIL import Image
import random

textures = None

class Block(arcade.Sprite):
    def __init__(self, center_x, center_y, scale=1, depth=0):
        self.window = arcade.get_window()
        self.block_list = self.window.block_list

        self.max_depth = self.window.settings.get('MAX_DEPTH', 10)

        if textures is None: # If we haven't created textures for this size, let's do it!
            self.create_textures()

        texture = random.choice(textures)

        self.depth = depth

        super().__init__(
            center_x=center_x,
            center_y=center_y,
            texture=texture,
            scale=scale,
        )

        self.block_list.append(self)

    def subdivide(self):
        self.block_list.remove(self)

        if self.depth+1 >= self.max_depth:
            return
        offset_x = self.width/4
        offset_y = self.height/4

        for i in [-1, 1]:
            for j in [-1, 1]:
                new_block = Block(
                    self.center_x + (offset_x * i),
                    self.center_y + (offset_y * j),
                    self.scale/2,
                    depth=self.depth + 1
                )

        self.kill()

    def create_textures(self):
        global textures
        width = self.window.settings.get('SCREEN_WIDTH', 16)
        height = self.window.settings.get('SCREEN_HEIGHT', 9)

        textures = []

        for i in range(self.window.settings.get('NUM_BLOCK_COLORS', 30)):
            img = Image.new("RGBA", (width, height),
                            color=(random.randint(100, 110),
                                   random.randint(60, 70),
                                   random.randint(30, 40),
                                   255))
            texture = arcade.Texture(f"block_{width}_{height}_{i}", image=img)  # Cache texture
            textures.append(texture)
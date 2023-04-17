from src.game.game import MyGame
import json
import arcade

with open('settings.json') as f:
    settings = json.load(f)

def main():
    window = MyGame(settings)
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()
from src.multiplayer.server import Server
from src.multiplayer.client import Client
import json
import arcade


with open('settings.json') as f:
    settings = json.load(f)

def main():
    nickname = input('Enter nickname or leave blank to host game?')
    if not nickname:
        window = Server(settings)
    else:
        window = Client(nickname, settings)

    arcade.run()


if __name__ == "__main__":
    main()
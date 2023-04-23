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
        hostname = input('Enter hostname or leave blank to connect to localhost?') or 'localhost'
        window = Client(nickname, settings, hostname)

    arcade.run()


if __name__ == "__main__":
    main()
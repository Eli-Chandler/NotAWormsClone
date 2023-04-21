import json
import arcade
import struct

class Message:
    def __init__(self, action, author=None, **kwargs, ):
        self.author = author
        if author is None:
            self.author = arcade.get_window().nickname
        self.action = action
        self.body = kwargs



    def to_dict(self):
        return {
            "action": self.action,
            'author': self.author,
            "body": self.body
        }

    def to_message(self):
        # Prefix the message with its length
        #print('Sent:', self.to_dict())
        message_bytes = (json.dumps(self.to_dict())).encode('utf-8')
        length = len(message_bytes)
        length_bytes = struct.pack('!I', length)
        return length_bytes + message_bytes


    @classmethod
    def from_message(cls, message):
        #print('Recieved:', message.decode('utf-8').strip())
        message_dict = json.loads(message.decode('utf-8').strip())
        return cls(
            message_dict["action"],
            author=message_dict['author'],
            **message_dict["body"],
        )

    @classmethod
    def from_str(cls, message_str):
        message_dict = json.loads(message_str)
        return cls(
            message_dict["author"],
            message_dict["action"],
            **message_dict["body"]
        )

class UpdateNickname(Message):
    def __init__(self, nickname):
        super().__init__('update_nickname', nickname=nickname)

class GetPosition(Message):
    def __init__(self, nickname):
        super().__init__('get_position', nickname=nickname)

class GivePosition(Message):
    def __init__(self, center_x, center_y, weapon_angle, weapon_name, weapon_scale, health):
        super().__init__('give_position', center_x=center_x, center_y=center_y, weapon_angle=weapon_angle, weapon_name=weapon_name, weapon_scale=weapon_scale, health=health)


class GivePositions(Message):
    def __init__(self, player_list):
        positions = {}
        for player in player_list:
            weapon_angle = player.current_weapon.angle if player.current_weapon else 0
            weapon_name = player.current_weapon.name if player.current_weapon else 'hands'
            weapon_scale = player.current_weapon.scale if player.current_weapon else 1
            positions[player.nickname] = {'center_x': player.center_x, 'center_y': player.center_y, 'weapon_angle': weapon_angle, 'weapon_name': weapon_name, 'weapon_scale': weapon_scale, 'health': player.health}

        super().__init__('give_positions', positions=positions)

class UpdatePlayer(Message):
    def __init__(self, client):
        window = client.window

        center_x = window.player.center_x
        center_y = window.player.center_y

        super().__init__('update_player', center_x=center_x, center_y=center_y)

class CreateExplosion(Message):
    def __init__(self, explosion):
        super().__init__('create_explosion', source=explosion.source, center_x=explosion.center_x, center_y=explosion.center_y, diameter=explosion.diameter)

class CreateBullet(Message):
    def __init__(self, bullet):
        super().__init__('create_bullet', center_x=bullet.center_x, center_y=bullet.center_y, change_x=bullet.change_x, change_y=bullet.change_y, weapon_name=bullet.weapon_name, angle=bullet.angle, scale=bullet.scale)


class Ping(Message):
    def __init__(self, nick='server'):
        super().__init__(nick, 'ping')


class Pong(Message):
    def __init__(self, client):
        super().__init__(client.window.nickname, 'pong')
import json

class Message:
    def __init__(self, author, action, **kwargs):
        self.author = author
        self.action = action
        self.body = kwargs

    def to_dict(self):
        return {
            "author": self.author,
            "action": self.action,
            "body": self.body
        }

    def to_message(self):
        return (json.dumps(self.to_dict()) + '\n').encode('utf-8')

    @classmethod
    def from_str(cls, message_str):
        message_dict = json.loads(message_str)
        return cls(
            message_dict["author"],
            message_dict["action"],
            **message_dict["body"]
        )

class SendNickname(Message):
    def __init__(self, client):
        super().__init__(client.window.nickname, 'send_nickname', nickname=client.window.nickname)

class UpdatePlayer(Message):
    def __init__(self, client):
        window = client.window

        center_x = window.player.center_x
        center_y = window.player.center_y

        super().__init__(client.window.nickname, 'update_player', center_x=center_x, center_y=center_y)

class Ping(Message):
    def __init__(self, nick='server'):
        super().__init__(nick, 'ping')


class Pong(Message):
    def __init__(self, client):
        super().__init__(client.window.nickname, 'pong')
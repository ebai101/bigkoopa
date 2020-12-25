import json
from base64 import b64encode
from os import urandom


class TurtleManager:

    def __init__(self):
        pass


class Turtle:

    def __init__(self, wss, id):
        self.wss = wss
        self.id = id

    async def forward(self):
        res = await self.wss.submit('turtle.forward()')

    async def back(self):
        res = await self.wss.submit('turtle.back()')

    async def up(self):
        res = await self.wss.submit('turtle.up()')

    async def down(self):
        res = await self.wss.submit('turtle.down()')

    async def turnLeft(self):
        res = await self.wss.submit('turtle.turnLeft()')

    async def turnRight(self):
        res = await self.wss.submit('turtle.turnRight()')


class TurtlePacket:

    def __init__(self, p):
        self.packet = p
        self.turtle_id, self.command, self.type, self.nonce = self.unpack()

    def __init__(self, tid, cmd, typ):
        self.turtle_id = tid
        self.command = 'return ' + cmd
        self.type = typ
        self.nonce = self.get_nonce()
        self.packet = self.to_json()

    def get_nonce(self):
        return b64encode(urandom(8), altchars=b'-_')

    def unpack(self):
        p = json.loads(self.packet)
        return (p['turtle_id'], p['command'], p['type'], p['nonce'])

    def to_json(self):
        return json.dumps({
            'turtle_id': self.turtle_id,
            'command': self.command,
            'type': self.type,
            'nonce': self.nonce
        })

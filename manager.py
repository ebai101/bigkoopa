#!/usr/bin/env python3

import asyncio
import binascii
import struct

from apis import TURTLE as api

class TurtleManager:

    _outgoing = asyncio.Queue()

    async def t(self):
        pass

    async def parse_turtle_response(self, packet):
        p = await TurtlePacket(packet)
        await print(p._decoded)

    async def send_turtle_instruction(self, packet):
        await self.outgoing.put(packet)

class TurtlePacket:

    # packet structure:
    # packet type: (bool) 0 for instruction packet, 1 for response packet
    # turtle id: (unsigned short) numeric turtle id 0-255
    # type0:
    #     command id: (unsigned short) numeric command id, 0-255
    #     message: arg string, delimited by '|', null terminated
    # type1:
    #     command id: (unsigned short) numeric command id, 0-255
    #     message: response string, null terminated

    _encoded = None
    _decoded = None

    def __init__(self, packet: tuple or bytes) -> None:
        if type(packet) == tuple:
            # packet is decoded, need to encode
            self._decoded = packet
            print('encoding packet:',packet)
            if self.encode():
                print('encoded packet:',binascii.hexlify(self._encoded))

        elif type(packet) == bytes:
            # packet is encoded, need to decode
            self._encoded = packet
            print('decoding packet',binascii.hexlify(self._encoded))
            if self.decode():
                print('decoded packet:',self._decoded)

    # encode packet tuple into bytes
    def encode(self) -> bool:
        # validate packet type
        try:
            assert self._decoded[0] == 0 or self._decoded[0] == 1
        except AssertionError:
            print('invalid packet type:',self._decoded[0])
            return False
        # validate turtle id
        try:
            assert self._decoded[1] < 256 and self._decoded[1] >= 0
        except AssertionError:
            print('invalid turtle id:',self._decoded[1])
            return False
        # validate command id
        try:
            assert self._decoded[2] < 256 and self._decoded[2] >= 0
        except AssertionError:
            print('invalid command id:',self._decoded[1])
            return False

        if self._decoded[3]:
            # validate message length
            try:
                assert len(self._decoded[3]) < 64
            except AssertionError:
                print('message is too long: %d > 64' % (self._decoded[3]))
                return False
            message = self._decoded[3]
            message += '\0'
            message = bytes(message, encoding='utf-8')
        else:
            message = bytes('\0', encoding='utf-8')

        sanitized = (self._decoded[0], self._decoded[1], self._decoded[2], message)
        packer = struct.Struct('? B B %ds' % len(message))
        self._encoded = packer.pack(*sanitized)

        return True

    # decode packet bytes into tuple
    def decode(self) -> bool:
        unpacker = struct.Struct('? B B %ds' % (len(self._encoded) - 3))
        try:
            data = unpacker.unpack(self._encoded)
        except:
            return False
        self._decoded = data
        return True

class APIMap(dict):
    def __init__(self, *args, **kwargs):
        super(APIMap, self).__init__(*args, **kwargs)
        for arg in args:
            if isinstance(arg, dict):
                for k, v in arg.iteritems():
                    self[k] = v

        if kwargs:
            for k, v in kwargs.iteritems():
                self[k] = v

    def __getattr__(self, attr):
        return self.get(attr)

    def __setattr__(self, key, value):
        self.__setitem__(key, value)

    def __setitem__(self, key, value):
        super(APIMap, self).__setitem__(key, value)
        self.__dict__.update({key: value})

    def __delattr__(self, item):
        self.__delitem__(item)

    def __delitem__(self, key):
        super(APIMap, self).__delitem__(key)
        del self.__dict__[key]

import struct
import typing

import serial


class Communicator:
    def __init__(self, send_fmt: str, recv_fmt: str) -> None:
        self.send_struct = struct.Struct(send_fmt)
        self.recv_struct = struct.Struct(recv_fmt)

    def __enter__(self):
        return self

    def __exit__(self, typ, val, trace) -> None:
        self.close()

    def close(self) -> None:
        pass

    def read(self) -> tuple:
        raise NotImplemented()

    def write(self, *data) -> None:
        raise NotImplemented()

    def decode_dle(self, data: bytes) -> bytes:
        """
        >>> Communicator('', '').decode_dle(b'\\x10\\x02hello\\x10\\x03')
        b'hello'
        >>> Communicator('', '').decode_dle(
        ...     b'\\x10\\x02\\x01\\x10\\x10\\x11\\x10\\x03')
        b'\\x01\\x10\\x11'
        >>> Communicator('', '').decode_dle(b'hello')
        Traceback (most recent call last):
            ...
        ValueError: ('invalid format data', b'hello')
        """

        if data[:2] != b'\x10\x02' or data[-2:] != b'\x10\x03':
            raise ValueError('invalid format data', data)

        return data[2:-2].replace(b'\x10\x10', b'\x10')

    def decode_struct(self, data: bytes) -> tuple:
        """
        >>> Communicator('', '<i').decode_struct(b'\\x01\\x00\\x00\\x00')
        (1,)
        """

        return self.recv_struct.unpack(data)

    def decode(self, data: bytes) -> tuple:
        """
        >>> Communicator('', '<bb').decode(b'\\x10\\x02\\x01\\x02\\x10\\x03')
        (1, 2)
        """

        return self.decode_struct(self.decode_dle(data))

    def encode_dle(self, data: bytes) -> bytes:
        """
        >>> Communicator('', '').encode_dle(b'hello')
        b'\\x10\\x02hello\\x10\\x03'
        >>> Communicator('', '').encode_dle(b'\\x01\\x10\\x11')
        b'\\x10\\x02\\x01\\x10\\x10\\x11\\x10\\x03'
        """

        return b'\x10\x02' + data.replace(b'\x10', b'\x10\x10') + b'\x10\x03'

    def encode_struct(self, *data) -> bytes:
        """
        >>> Communicator('<i', '').encode_struct(1)
        b'\\x01\\x00\\x00\\x00'
        """

        return self.send_struct.pack(*data)

    def encode(self, *data) -> bytes:
        """
        >>> Communicator('<ib', '').encode(1, 1)
        b'\\x10\\x02\\x01\\x00\\x00\\x00\\x01\\x10\\x03'
        """

        return self.encode_dle(self.encode_struct(*data))


class DummyCommunicator(Communicator):
    def read(self) -> tuple:
        print('DummyCommunicator: reading... (will blocking)')
        import time
        while True:
            time.sleep(60 * 60)

    def write(self, *data) -> None:
        """
        >>> DummyCommunicator('<ii', '').write(1, 2)
        DummyCommunicator: writing: 01 00 00 00 | 02 00 00 00
        """

        msg = 'DummyCommunicator: writing: '

        for i, x in enumerate(self.encode_struct(*data)):
            if i != 0 and (i + 0) % 4 == 0:
                msg += '| '
            msg += '{0:02x} '.format(x)

        print(msg.strip())

        import time
        time.sleep(0.1)


class SerialCommunicator(Communicator):
    def __init__(self,
                 serial: serial.Serial,
                 send_fmt: str,
                 recv_fmt: str) -> None:

        super().__init__(send_fmt, recv_fmt)
        self.serial = serial

    @classmethod
    def get_instantiator(cls,
                         serial: serial.Serial
                         ) -> typing.Callable[[str, str], Communicator]:

        def instantiator(send_fmt: str, recv_fmt: str) -> Communicator:
            return cls(serial, send_fmt, recv_fmt)

        return instantiator

    def close(self) -> None:
        self.serial.close()

    def read(self) -> tuple:
        buf = b''

        while True:
            buf += self.serial.read(1)

            if buf.endswith(b'\x10\x02'):
                buf = b'\x10\x02'
            elif buf.endswith(b'\x10\x03'):
                return self.decode(buf)

    def write(self, *data)-> None:
        self.serial.write(self.encode(*data))

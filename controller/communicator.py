import struct

import serial


class Communicator:
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
		>>> Communicator().decode_dle(b'\\x10\\x02hello\\x10\\x03')
		b'hello'
		>>> Communicator().decode_dle(b'\\x10\\x02\\x01\\x10\\x10\\x11\\x10\\x03')
		b'\\x01\\x10\\x11'
		>>> Communicator().decode_dle(b'hello')
		Traceback (most recent call last):
			...
		ValueError: ('invalid format data', b'hello')
		"""

		if data[:2] != b'\x10\x02' or data[-2:] != b'\x10\x03':
			raise ValueError('invalid format data', data)

		return data[2:-2].replace(b'\x10\x10', b'\x10')

	def encode_dle(self, data: bytes) -> bytes:
		"""
		>>> Communicator().encode_dle(b'hello')
		b'\\x10\\x02hello\\x10\\x03'
		>>> Communicator().encode_dle(b'\\x01\\x10\\x11')
		b'\\x10\\x02\\x01\\x10\\x10\\x11\\x10\\x03'
		"""

		return b'\x10\x02' + data.replace(b'\x10', b'\x10\x10') + b'\x10\x03'


class DummyCommunicator(Communicator):
	def read(self) -> tuple:
		print('DummyCommunicator: reading')
		return ()

	def write(self, *data) -> None:
		print('DummyCommunicator: writing: {}'.format(data))


class StructSerial(Communicator):
	def __init__(self, serial: serial.Serial, fmt: str) -> None:
		self.serial = serial
		self.struct = struct.Struct(fmt)

	def close(self) -> None:
		self.serial.close()

	def decode(self, data: bytes) -> tuple:
		"""
		>>> StructSerial(None, '<i').decode(b'\\x10\\x02\\x01\\x00\\x00\\x00\\x10\\x03')
		(1,)
		>>> StructSerial(None, '<bb').decode(b'\\x10\\x02\\x01\\x02\\x10\\x03')
		(1, 2)
		"""

		return self.struct.unpack(self.decode_dle(data))

	def read(self) -> tuple:
		buf = b''

		for x in self.serial.read(1):
			buf += x

			if buf.endswith(b'\x10\x02'):
				buf = b'\x10\x02'
			elif buf.endswith(b'\x10\x03'):
				return self.decode(buf)

	def encode(self, *data) -> bytes:
		"""
		>>> StructSerial(None, '<i').encode(1)
		b'\\x10\\x02\\x01\\x00\\x00\\x00\\x10\\x03'
		>>> StructSerial(None, '<bb').encode(1, 16)
		b'\\x10\\x02\\x01\\x10\\x10\\x10\\x03'
		"""

		return self.encode_dle(self.struct.pack(*data))

	def write(self, *data) -> None:
		self.serial.write(self.encode(*data))


class AsymmetryStructSerial(Communicator):
	def __init__(self, serial: serial.Serial, in_: str, out: str) -> None:
		self._in = StructSerial(serial, in_)
		self._out = StructSerial(serial, out)

	def close(self) -> None:
		self._in.close()
		self._out.close()

	def read(self) -> tuple:
		return self._in.read()

	def write(self, *data)-> None:
		self._out.write(*data)

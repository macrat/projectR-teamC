import logging
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


class DummyCommunicator(Communicator):
	def read(self) -> tuple:
		logging.getLogger('DummyCommunicator').debug('reading')
		return ()

	def write(self, *data) -> None:
		logging.getLogger('DummyCommunicator').debug('writing {}'.format(data))
		pass

class StructSerial(Communicator):
	def __init__(self, serial: serial.Serial, fmt: str) -> None:
		self.serial = serial
		self.struct = struct.Struct(fmt)

	def close(self) -> None:
		self.serial.close()

	def read(self) -> tuple:
		return self.struct.unpack(self.serial.read(self.struct.size))

	def write(self, *data) -> None:
		self.serial.write(self.struct.pack(*data))


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

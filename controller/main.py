import contextlib
import struct
import time
import sys
import colorsys  # debug

import serial
import pygame


class StructSerial:
	def __init__(self, serial: serial.Serial, fmt: str) -> None:
		self.serial = serial
		self.struct = struct.Struct(fmt)

	def __enter__(self):
		return self

	def __exit__(self, typ, val, trace) -> None:
		self.close()

	def close(self) -> None:
		self.serial.close()

	def read(self) -> tuple:
		return self.struct.unpack(self.serial.read(self.struct.size))

	def write(self, *data) -> None:
		self.serial.write(self.struct.pack(*data))


class AsymmetryStructSerial:
	def __init__(self, serial: serial.Serial, in_: str, out: str) -> None:
		self._in = StructSerial(serial, in_)
		self._out = StructSerial(serial, out)

	def __enter__(self):
		return self

	def __exit__(self, typ, val, trace) -> None:
		self.close()

	def close(self) -> None:
		self._in.close()
		self._out.close()

	def read(self) -> tuple:
		return self._in.read()

	def write(self, *data)-> None:
		self._out.write(*data)


class JoystickController:
	def __init__(self):
		pygame.joystick.init()
		assert pygame.joystick.get_count() >= 1

		self.joystick = pygame.joystick.Joystick(0)
		self.joystick.init()


class Screen:
	def __init__(self):
		pygame.init()
		self.screen = pygame.display.set_mode([640, 480])
		self.clock = pygame.time.Clock()

	def mainloop(self):
		while True:
			for e in pygame.event.get():
				if e.type == pygame.QUIT:
					pygame.quit()
					sys.exit(0)

			self.update()
			pygame.display.flip()

			self.clock.tick(60)


class ColorScreen(Screen):
	def __init__(self):
		super().__init__()

		self.controller = JoystickController()
		self.serial = AsymmetryStructSerial(serial.Serial('/dev/tty.RNBT-92F0-RNI-SPP', 115200), '<i', '<fff')

	def update(self):
		color = (
			round(abs(self.controller.joystick.get_axis(0)), 2),
			round(abs(self.controller.joystick.get_axis(1)), 2),
			round(abs(self.controller.joystick.get_axis(2)), 2),
		)

		self.screen.fill(list(255*x for x in color))
		self.serial.write(*color)


if __name__ == '__main__':
	ColorScreen().mainloop()

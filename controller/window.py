import sys

import pygame

from controller import Controller
from communicator import Communicator


class Window:
	width = 640
	height = 480

	def __init__(self, controller: Controller, communicator: Communicator) -> None:
		pygame.init()
		self.screen = pygame.display.set_mode([self.width, self.height])
		self.clock = pygame.time.Clock()
		self.controller = controller
		self.communicator = communicator

	def mainloop(self) -> None:
		while True:
			for e in pygame.event.get():
				if e.type == pygame.QUIT:
					pygame.quit()
					sys.exit(0)

			self.communicator.write(*self.controller)

			self.screen.fill((0, 0, 0))
			self.update()
			pygame.display.flip()

			self.clock.tick(60)

	def update(self) -> None:
		raise NotImplemented()

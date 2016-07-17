import math

import pygame

from window import Window


class DummyWindow(Window):
	x = Window.width/2
	y = Window.height/2
	heading = 0.0
	arm_h = 0.0
	arm_v = 0.5

	def update(self) -> None:
		inp = self.controller.get_input()

		self.x += math.cos(self.heading) * (inp['body']['left'] + inp['body']['right'])
		self.y += math.sin(self.heading) * (inp['body']['left'] + inp['body']['right'])
		self.heading += (inp['body']['left'] - inp['body']['right']) / 40

		self.arm_h -= inp['arm']['horizontal'] / 2
		self.arm_v = max(0.1, min(0.7, self.arm_v + inp['arm']['vertical'] / 100))

		self.draw_bar(0.05, 0.1, 0.10, 0.9, inp['body']['left'], False)
		self.draw_bar(0.10, 0.1, 0.15, 0.9, inp['body']['right'], False)

		pygame.draw.circle(
			self.screen,
			(255, 255, 255),
			(int(self.x + self.arm_h*math.cos(self.heading+math.pi/2)), int(self.y + self.arm_h*math.sin(self.heading+math.pi/2))),
			int(40 * self.arm_v),
			0 if inp['arm']['grab'] else 1
		)
		pygame.draw.circle(self.screen, (255, 255, 255), (int(self.x), int(self.y)), 40, 2)
		pygame.draw.line(
			self.screen,
			(255, 255, 255),
			(int(self.x + self.arm_h*math.cos(self.heading+math.pi/2)), int(self.y + self.arm_h*math.sin(self.heading+math.pi/2))),
			(
				int(self.x + self.arm_h*math.cos(self.heading+math.pi/2) - math.cos(self.heading)*40),
				int(self.y + self.arm_h*math.sin(self.heading+math.pi/2) - math.sin(self.heading)*40)
			),
		)

import sys
import typing

import pygame

from controller import Controller


class Window:
    width = 640
    height = 480

    def __init__(self, controller: Controller) -> None:
        pygame.init()

        self.screen = pygame.display.set_mode([self.width, self.height],
                                              pygame.RESIZABLE)
        self.clock = pygame.time.Clock()
        self.controller = controller
        self.controller.start_send_loop()

        pygame.font.init()
        self.font = pygame.font.SysFont(None, 40)

    def mainloop(self) -> None:
        while True:
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit(0)
                elif e.type == pygame.VIDEORESIZE:
                    self.width = e.w
                    self.height = e.h
                    self.screen = pygame.display.set_mode((e.w, e.h),
                                                          pygame.RESIZABLE)

            self.screen.fill((0, 0, 0))
            self.update()
            pygame.display.flip()

            self.clock.tick(60)

    def draw_bar(self,
                 left: float, top: float,
                 right: float, bottom: float,
                 percent: float,
                 horizontal: bool) -> None:
        assert 0 <= left <= 1 and 0 <= top <= 1
        assert 0 <= right <= 1 and 0 <= bottom <= 1
        assert -1 <= percent <= 1

        pygame.draw.rect(self.screen, (255, 255, 255), (
            left * self.width,
            top * self.height,
            (right - left) * self.width,
            (bottom - top) * self.height,
        ), 1)

        if horizontal:
            pygame.draw.rect(self.screen, (255, 255, 255), (
                (left + right)/2 * self.width,
                top * self.height,
                (right - left)/2 * percent * self.width,
                (bottom - top) * self.height,
            ))
        else:
            pygame.draw.rect(self.screen, (255, 255, 255), (
                left * self.width,
                (top + bottom)/2 * self.height,
                (right - left) * self.width,
                (bottom - top)/2 * -percent * self.height,
            ))

    def draw_text(self,
                  x: float, y: float,
                  text: str,
                  color: typing.Tuple[int] = (255, 255, 255)) -> None:
        assert 0 <= x <= 1 and 0 <= y <= 1

        img = self.font.render(text, 1, color)
        self.screen.blit(img, (x * self.width - img.get_width()/2,
                               y * self.height - img.get_height()/2))

    def update(self) -> None:
        inp = self.controller.get_input()

        for x, name in ((0.05, 'left'), (0.1, 'right')):
            self.draw_bar(x, 0.1, x+0.05, 0.9, inp['body'][name], False)
        self.draw_text(0.1, 0.05,
                       '{left: 5.0%} {right: 5.0%}'.format(**inp['body']))

        self.draw_text(0.5, 0.85, '{0: 5.0%}'.format(inp['arm']['horizontal']))
        self.draw_bar(0.15, 0.9, 0.9, 0.95, inp['arm']['horizontal'], True)

        self.draw_text(0.9, 0.05, '{0: 5.0%}'.format(inp['arm']['vertical']))
        self.draw_bar(0.9, 0.1, 0.95, 0.9, inp['arm']['vertical'], False)

        pygame.draw.rect(self.screen, (255, 255, 255), (
            0.4 * self.width,
            0.4 * self.height,
            0.2 * self.width,
            0.2 * self.height,
        ), not inp['arm']['grab'])

        if inp['arm']['grab']:
            self.draw_text(0.5, 0.5, 'grab', color=(0, 0, 0))
        else:
            self.draw_text(0.5, 0.5, 'release')

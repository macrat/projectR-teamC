import threading
import time
import typing

import pygame
from pygame.locals import *

from communicator import Communicator


class Controller:
    def __init__(
            self,
            communicator: typing.Callable[[str, str], Communicator]
            ) -> None:

        self.communicator = communicator('<bbbbB', '')

    def get_input(self) -> dict:
        raise NotImplemented()

    def __dict__(self) -> dict:
        return self.get_input()

    def float2fixed(self, x: float) -> int:
        """
        >>> from communicator import DummyCommunicator
        >>> Controller(DummyCommunicator).float2fixed(1.0)
        127
        >>> Controller(DummyCommunicator).float2fixed(-1.0)
        -127
        """

        return int(round(x * 127, 1))

    def send_packet(self, packet: tuple) -> None:
        self.communicator.write(*packet)

    def make_packet(self) -> tuple:
        inp = self.get_input()

        return (
            self.float2fixed(inp['body']['left']),
            self.float2fixed(inp['body']['right']),
            self.float2fixed(inp['arm']['horizontal']),
            self.float2fixed(inp['arm']['vertical']),
            inp['arm']['grab'],
        )

    def send_loop(self) -> None:
        before = ()
        last_sent = 0

        while True:
            try:
                inp = self.make_packet()
            except pygame.error as e:
                if e.args[0] != 'video system not initialized':
                    raise
                break

            if last_sent + 1 < time.time() or before != inp:
                self.send_packet(inp)

                before = inp
                last_sent = time.time()

                time.sleep(0.2)

    def start_send_loop(self) -> None:
        threading.Thread(target=self.send_loop).start()


class JoystickController(Controller):
    def __init__(
            self,
            communicator: typing.Callable[[str, str], Communicator]
            ) -> None:

        super().__init__(communicator)

        pygame.joystick.init()
        assert pygame.joystick.get_count() >= 1

        self.joystick = pygame.joystick.Joystick(0)
        self.joystick.init()

        self.grabbed = False

    def get_input(self) -> dict:
        if self.joystick.get_button(5) != 0:
            self.grabbed = True

        elif (self.joystick.get_button(7) != 0
              and abs(self.joystick.get_axis(0)) < 0.1
              and abs(self.joystick.get_axis(1)) < 0.1):

            self.grabbed = False

        arm = {
            'horizontal': round(self.joystick.get_axis(3), 2),
            'vertical': (round(self.joystick.get_button(6), 2)
                         - round(self.joystick.get_button(4), 2)),
            'grab': int(self.grabbed),
        }
        arm_y = -(round(self.joystick.get_axis(2), 2) ** 3) / 2

        if (abs(arm['horizontal']) < 0.1 and abs(arm['vertical']) < 0.1
                and abs(arm_y) < 0.1):

            if self.joystick.get_button(1):
                x = -round(self.joystick.get_axis(0), 2)
                y = -round(self.joystick.get_axis(1), 2)

                right = max(-1.0, min(1.0, y + x))
                left = max(-1.0, min(1.0, y - x))

                right = right ** 3
                left = left ** 3
            else:
                right = left = -round(self.joystick.get_axis(1), 2)
        else:
            right = left = arm_y

        return {
            'body': {
                'right': right,
                'left': left,
                'free_run': self.joystick.get_button(1) != 0,
            },
            'arm': arm,
        }


class KeyboardController(Controller):
    def __init__(
            self,
            communicator: typing.Callable[[str, str], Communicator]
            ) -> None:

        super().__init__(communicator)

        self.grabbed = False

    def get_input(self) -> dict:
        key = pygame.key.get_pressed()

        if key[K_f]:
            self.grabbed = True
        elif (key[K_r]
              and not key[K_UP] and not key[K_DOWN]
              and not key[K_LEFT] and not key[K_RIGHT]):

            self.grabbed = False

        arm = {
            'horizontal': key[K_d] - key[K_a],
            'vertical': key[K_e] - key[K_q],
            'grab': int(self.grabbed),
        }
        arm_y = (key[K_w] - key[K_s]) / 2

        if arm['horizontal'] == 0 and arm['vertical'] == 0 and arm_y == 0:
            x = key[K_LEFT] - key[K_RIGHT]
            y = key[K_UP] - key[K_DOWN]

            right = max(-1.0, min(1.0, y + x))
            left = max(-1.0, min(1.0, y - x))
        else:
            right = left = arm_y

        return {
            'body': {
                'right': right,
                'left': left,
            },
            'arm': arm,
        }

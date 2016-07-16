import logging

from communicator import DummyCommunicator
from controller import JoystickController
from window_dummy import DummyWindow


if __name__ == '__main__':
	logging.basicConfig(level=logging.DEBUG)

	DummyWindow(
		JoystickController(),
		DummyCommunicator()
	).mainloop()

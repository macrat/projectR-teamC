import serial

from communicator import StructDummyCommunicator
from controller import JoystickController
from window_dummy import DummyWindow


if __name__ == '__main__':
	DummyWindow(JoystickController(StructDummyCommunicator)).mainloop()

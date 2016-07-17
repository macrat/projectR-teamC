from communicator import DummyCommunicator
from controller import KeyboardController
from window_dummy import DummyWindow


if __name__ == '__main__':
	DummyWindow(
		KeyboardController(),
		DummyCommunicator()
	).mainloop()

import serial

from communicator import SerialCommunicator
from controller import KeyboardController
from window import Window


if __name__ == '__main__':
    Window(
        KeyboardController(
            SerialCommunicator.get_instantiator(
                serial.Serial('/dev/tty.RNBT-92F0-RNI-SPP', 115200)
            )
        )
    ).mainloop()

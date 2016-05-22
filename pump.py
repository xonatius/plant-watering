import time
import RPi.GPIO as io

class Pump(object):
    forward_pin = 5
    backward_pin = 6
    ml_per_second = 0.5

    def __init__(self):
        io.setup(self.forward_pin, io.OUT)
        io.setup(self.backward_pin, io.OUT)

    def pump(self, amount_ml):
        wait_time = abs(amount_ml / self.ml_per_second)
        if amount_ml > 0:
            self.pump_forward()
        else:
            self.pump_backward()
        time.sleep(wait_time)
        self.stop()

    def pump_forward(self):
        self.__set_pin_state(True, False)

    def pump_backward(self):
        self.__set_pin_state(False, True)

    def stop(self):
        self.__set_pin_state(False, False)

    def __set_pin_state(self, fwd_pin_state, bwd_pin_state):
        io.output(self.forward_pin, fwd_pin_state)
        io.output(self.backward_pin, bwd_pin_state)


# Some code to play with a pump

def loop(pump):
    while True:
        cmd = raw_input("Command, f/b/s/p <amount>/q:")
        action = cmd.split(" ")[0]
        if action == "f":
            pump.pump_forward()
        elif action == "b":
            pump.pump_backward()
        elif action == "s":
            pump.stop()
        elif action == "p":
            amount = int(cmd.split(" ")[1])
            pump.pump(amount)
        elif cmd == "q":
            break


if __name__ == '__main__':
    io.setmode(io.BCM)
    pump = Pump()
    try:
        io.setmode(io.BCM)
        pump.stop()
        loop(pump)
    finally:
        pump.stop()
        io.cleanup()

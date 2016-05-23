import time, json
import asyncio
import traceback
import RPi.GPIO as io
from messages import *

class Pump(object):
    loop = None
    forward_pin = None
    backward_pin = None
    ml_per_second = None

    def __init__(self, loop=None, forward_pin=None, backward_pin=None, ml_per_second=0.5, inverse=False):
        self.loop = loop
        self.forward_pin = forward_pin
        self.backward_pin = backward_pin
        self.ml_per_second = ml_per_second
        self.inverse = inverse
        if self.forward_pin is not None:
            io.setup(self.forward_pin, io.OUT)
        if self.backward_pin is not None:
            io.setup(self.backward_pin, io.OUT)
        self.stop()

    def pump(self, amount_ml):
        if amount_ml > 0:
            self.pump_forward()
        else:
            self.pump_backward()

        wait_time = abs(amount_ml / self.ml_per_second)

        if self.loop:
            self.loop.call_later(wait_time, self.stop)
        else:
            time.sleep(wait_time)
            self.stop()

    def pump_forward(self):
        self.__set_pin_state(True, False)

    def pump_backward(self):
        self.__set_pin_state(False, True)

    def stop(self):
        self.__set_pin_state(False, False)

    def __set_pin_state(self, fwd_pin_state, bwd_pin_state):
        if self.forward_pin is None:
            if bwd_pin_state:
                raise Exception("No forward pin, can't pump forward.")
        else:
            io.output(self.forward_pin, fwd_pin_state != self.inverse)
        if self.backward_pin is None:
            if bwd_pin_state:
                raise Exception("No backward pin, can't pump backward.")
        else:
            io.output(self.backward_pin, bwd_pin_state != self.inverse)


class WateringController(object):
    pumps = None
    loop = None
    plants_pump_config = None

    def __init__(self, loop, plants_pump_config):
        self.loop = loop
        self.plants_pump_config = plants_pump_config

    def prepare_pumps(self):
        self.pumps = {}
        for plant, config in self.plants_pump_config.items():
            self.pumps[plant] = Pump(self.loop, **config)

    def water(self, plant, volume):
        if self.pumps is None:
            raise Exception("Controller is not initialized. Use with statement to initialize controller.")
        if plant not in self.pumps:
            raise KeyError("Plant '%s' is not found. Availabile plants are: %s" % (plant, ", ".join(self.pumps.keys())))
        self.pumps[plant].pump(volume)

    def __enter__(self):
        io.setmode(io.BCM)
        self.prepare_pumps()
        return self

    def __exit__(self, type, value, traceback):
        try:
            if self.pumps:
                for pump in self.pumps.values():
                    pump.stop()
        except:
            pass
        finally:
            io.cleanup()


class TcpWateringServer(object):
    loop = None
    watering_controller = None
    server = None

    def __init__(self, loop, watering_controller):
        self.loop = loop
        self.watering_controller = watering_controller
        coro = asyncio.start_server(self.handle_request, '127.0.0.1', 8888, loop=self.loop)
        self.server = self.loop.run_until_complete(coro)
        print('Serving on {}'.format(self.server.sockets[0].getsockname()))

    @asyncio.coroutine
    def handle_request(self, reader, writer):
        response = ResponseMessage(True, "Internal error")
        try:
            data = yield from reader.readline()
            message = BaseMessage.decode(data)
            if not isinstance(message, WaterMessage):
                raise Exception("Unknown message type.")
            self.watering_controller.water(message.plant, message.volume)
            response = ResponseMessage(False, "Pouring %.2f ml of water for %s" % (message.volume, message.plant))
        except Exception as e:
            traceback.print_exc()
            response = ResponseMessage(True, "Error: %s" % e)
        finally:
            writer.write(response.encode())
            yield from writer.drain()
            writer.close()

    def close(self):
        self.server.close()
        self.loop.run_until_complete(self.server.wait_closed())


if __name__ == '__main__':
    from plants import plants_pumps_config
    loop = asyncio.get_event_loop()
    with WateringController(loop, plants_pumps_config) as watering_controller:
        server = TcpWateringServer(loop, watering_controller)
        try:
            loop.run_forever()
        except KeyboardInterrupt:
            pass
        server.close()
    loop.close()

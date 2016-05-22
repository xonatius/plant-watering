import time, json
import asyncio
import RPi.GPIO as io

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


def create_pumps(loop):
    return {
            "Succulent" : Pump(loop, forward_pin=17, ml_per_second=1.0, inverse=True),
            "Pineapple Right" : Pump(loop, forward_pin=27, ml_per_second=1.0, inverse=True),
            "Pineapple Left" : Pump(loop, forward_pin=22, ml_per_second=1.0, inverse=True),
            "Basil" : Pump(loop, forward_pin=23, ml_per_second=1.0, inverse=True),
            "Empty" : Pump(loop, forward_pin=24, ml_per_second=1.0, inverse=True),
            "Orchid" : Pump(loop, forward_pin=5, backward_pin=6, ml_per_second=0.5, inverse=False),
            }

loop = None
pumps = None

def parse_message(message):
    try:
        message = json.loads(message)
        if 'plant' not in message:
            raise Exception("No 'plant' or 'volume' in message.")
        if 'volume' not in message:
            raise Exception("No 'plant' or 'volume' in message.")
        plant = message['plant']
        if plant not in pumps:
            raise Exception("Can't find plant '%s', availible plants are: %s" % (plant, ", ".join(pumps.keys())))
        volume = float(message['volume'])
        return plant, volume
    except ValueError:
        raise Exception("Not valid messge. Should be a json object.")


@asyncio.coroutine
def handle_watering(reader, writer):
    try:
        data = yield from reader.read(200)
        message = data.decode()
        addr = writer.get_extra_info('peername')
        print("Received %r from %r" % (message, addr))
        plant, volume = parse_message(message)
        pumps[plant].pump(volume)
        writer.write(("Pouring %.2f ml of water for '%s'" % (volume, plant)).encode())
    except Exception as e:
        writer.write(("Error while parsing: %s" % e).encode())
    finally:
        yield from writer.drain()
        writer.close()


if __name__ == '__main__':
    try:
        io.setmode(io.BCM)
        loop = asyncio.get_event_loop()
        pumps = create_pumps(loop)
        coro = asyncio.start_server(handle_watering, '127.0.0.1', 8888, loop=loop)
        server = loop.run_until_complete(coro)
        print('Serving on {}'.format(server.sockets[0].getsockname()))
        try:
            loop.run_forever()
        except KeyboardInterrupt:
            pass
        server.close()
        loop.run_until_complete(server.wait_closed())
        loop.close()
    finally:
        try:
            for pump in pumps.values():
                pump.stop()
        finally:
            io.cleanup()

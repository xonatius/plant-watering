from messages import *
from plants import plants
import asyncio

@asyncio.coroutine
def water_plant(loop, plant, volume, wait_time=None):
    message = None
    if wait_time is None:
        message = WaterMessage(plant, volume)
    else:
        message = FillDrainMessage(plant, volume, wait_time)
    reader, writer = yield from asyncio.open_connection('127.0.0.1', 8888, loop=loop)
    writer.write(message.encode())
    yield from writer.drain()

    data = yield from reader.read()
    reply = BaseMessage.decode(data)
    if reply.is_error():
        print('Received an error: %s' % reply.message)
    else:
        print('Succeeded: %s' % reply.message)
    writer.close()

def water_plant_sync(plant, volume, wait_time=None):
    loop = asyncio.get_event_loop()
    loop.run_until_complete(water_plant(loop, plant, volume, wait_time))
    loop.close()

def input_choice(prompt, choices):
    choice_id = -1
    while choice_id < 0 or choice_id >= len(choices):
        print(prompt)
        for i, item in enumerate(choices):
            print("%d) %s" % (i + 1, item))
        try:
            choice_id = int(input("Choose 1-%d: " % len(choices))) - 1
        except ValueError:
            pass
    return choices[choice_id]

def input_number(prompt, num_type=int):
    num = None
    while num is None:
        try:
            num = num_type(input(prompt))
        except ValueError:
            pass
    return num

if __name__ == '__main__':
    plant = input_choice("Select plant: ", plants)
    volume = input_number("Volume (ml): ", float)
    if plant == "Orchid":
        # Orchids are special
        wait_time = input_number("Wait time: ", float)
        water_plant_sync(plant, volume, wait_time)
    else:
        water_plant_sync(plant, volume)


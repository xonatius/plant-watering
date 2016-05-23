from messages import *
from plants import plants
import asyncio

@asyncio.coroutine
def water_plant(loop, plant, volume):
    message = WaterMessage(plant, volume)
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

def water_plant_sync(plant, volume):
    loop = asyncio.get_event_loop()
    loop.run_until_complete(water_plant(loop, plant, volume))
    loop.close()

if __name__ == '__main__':
    plant_id = -1
    while plant_id < 0 or plant_id >= len(plants):
        print("Select plant:")
        for i, plant in enumerate(plants):
            print("%d) %s" % (i + 1, plant))
        try:
            plant_id = int(input("Coose 1-%d: " % len(plants))) - 1
        except:
            pass

    volume = None
    while volume is None:
        try:
            volume = float(input("Volume: "))
        except:
            pass

    water_plant_sync(plants[plant_id], volume)


import base64
import pickle

class BaseMessage(object):
    def encode(self):
        return base64.b64encode(pickle.dumps(self)) + b'\n'

    @staticmethod
    def decode(message):
        return pickle.loads(base64.b64decode(message))


class WaterMessage(BaseMessage):
    def __init__(self, plant, volume):
        self.plant = plant
        self.volume = volume

class FillDrainMessage(WaterMessage):
    def __init__(self, plant, volume, wait_time):
        super(FillDrainMessage, self).__init__(plant, volume)
        self.wait_time = wait_time

class ResponseMessage(BaseMessage):

    def __init__(self, is_error, message):
        self.error = is_error
        self.message = message

    def is_error(self):
        return self.error

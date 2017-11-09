# TODO: create dictionary searching functions
import src.Device as Device
import src.Utilities as util


class Dictionary:
    __we_are_one = {}

    def __init__(self, d):
        self.__dict__ = self.__we_are_one
        self.dictionary = d

    # input: device_type (e.g. washer), device_name (e.g. GE_WSM2420D3WW), mode_name (e.g. regular), deviceID to assign
    # output: device object --- can be used to set constraints, find variables used in constraints, etc
    def get_device(self, dtype='random', device_name='random', mode_name='random', dID=0):
        if dtype == 'random':
            dtype = util.get_rand(self.dictionary)
        if device_name == 'random':
            device_name = util.get_rand(self.dictionary[dtype])
        if mode_name == 'random':
            mode_name = util.get_rand(self.dictionary[dtype][device_name]['modes'])
        return Device.Device(device=self.dictionary[dtype][device_name],dtype=dtype, device_name=device_name, mode_name=mode_name, dID=dID)
    '''
    def get_device(self, rule):
        location = rule.location
        if location[0] == 'd':
            print('testing')
        return None
    '''
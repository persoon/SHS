# TODO: create dictionary searching functions
import src.Device as Device


class Dictionary:
    __we_are_one = {}

    def __init__(self, d):
        self.__dict__ = self.__we_are_one
        self.dictionary = d

    # for now: takes in type_of_device (e.g. washer) and name_of_device (e.g. GE_WSM2420D3WW)
    def get_device(self, type, name):
        return Device.Device(self.dictionary[type][name])

import json
import src.Device
import src.Dictionary


class Reader:
    def __init__(self):
        with open('resources\\input\\devices.json') as device_file:
            devices = json.load(device_file)

        with open('resources\\input\\dictionary.json') as dictionary_file:
            json_dict = json.load(dictionary_file)

        # TODO: dictionary should do: inputs - json_dict and devices, output dictionary of devices in devices.json
        self.dictionary = src.Dictionary.Dictionary(json_dict)

    def get_dictionary(self):
        return self.dictionary

reader = Reader()

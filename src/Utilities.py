import random

def get_rand(json):
    mode_names = []
    for k in json.keys():
        mode_names.append(k)
    print(mode_names)
    return random.choice(mode_names)
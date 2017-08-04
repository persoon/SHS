import src.Window


class Device:

    def __init__(self, device):
        self.device = device
        mode = device['modes']['regular']
        self.phases = [None] * len(mode)
        for i in range(len(mode)):
            self.phases[i] = int(mode[i]['duration']), float(mode[i]['kWh']), mode[i]['name']

        # --- what needs to happen: --------------------------------------------------------
        # move files into separate folders based on what part of the program they are
        # set up other devices in dictionary
        # clean stuff up, comment, go through some TODO's

        # --- completed: -------------------------------------------------------------------
        # move add_rule_constraints(rule) from Solver.py to here without making things weird
        # use phases for adding rule constraints
        # make sure model in here is real model from parameters and not a copy

        self.window = src.Window.Window(phases=self.phases)

        print(self.phases)

    def add_constraints(self, rule):
        return self.window.add_rule_constraints(rule)
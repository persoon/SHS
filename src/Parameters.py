# 6_21_2017
#
# parameters used across multiple files in the program
import src.RuleParser as rp


class Parameters:
    verbose = 0        # set this to 1 if you want to see some extra information from solver and other places
    horizon = 192
    htype = 1          # house type
    city = 'houston'   # city name
    season = 'summer'  # season
    devices = []
    device_dependencies = []
    # TODO: make these location / season dependant --- they can be loaded in from elsewhere into parameters
    # outdoor temperature:
    out_temp = [77.0, 77.0, 77.0, 77.0, 75.2, 74.8, 75.6, 77.0, 82.4, 84.2, 86.0, 86.0, 89.6, 91.4, 93.2, 91.4, 89.6,
                89.6, 86.0, 86.0, 82.4, 82.4, 80.6, 78.8]
    # dew point:
    dp = [73.4, 71.6, 71.6, 71.6, 71.6, 71.6, 73.4, 71.6, 71.6, 71.6, 71.6, 69.8, 68.0, 66.2, 68.0, 68.0, 68.0, 66.2,
          69.8, 71.6, 73.4, 73.4, 73.4, 73.4]
    # solar:
    dni = [0, 0, 0, 0, 0, 0, 7, 218, 260, 467, 448, 103, 83, 53, 1, 380, 501, 277, 113, 0, 0, 0, 0, 0]

    # real time-of-use price schema from California
    '''
    price_schema = [
        0.198, 0.198, 0.198, 0.198, 0.198, 0.198, 0.198, 0.198,
        0.225, 0.225, 0.225, 0.225,
        0.249, 0.249,
        0.849, 0.849, 0.849, 0.849,
        0.225, 0.225, 0.225, 0.225,
        0.198, 0.198
    ]
    '''

    # goofy price schema which monotonically decreases so I can see that things are working
    price_schema = [
        40, 35, 30, 30, 28, 25,
        25, 25, 22, 22, 20, 20,
        16, 16, 12, 12, 10,  8,
         8,  8,  6,  6,  4,  2
    ]

    '''
    price_schema = [
         4,  4,  6,  6,  8,  8,
        10, 10, 12, 12, 14, 14,
        14, 14, 20, 12, 10, 16,
         8, 10,  6, 10,  4, 18
    ]
    '''
    # have to figure out the price if hard constraints are kept and set this value to it
    reg_price = 0

    '''
    old_ps = [
        0.198, 0.849, 0.849, 0.198, 0.849, 0.198, 0.849, 0.198,
        0.225, 0.225, 0.225, 0.225,
        0.249, 0.249,
        0.849, 0.849, 0.849, 0.849,
        0.225, 0.225, 0.849, 0.225,
        0.198, 0.198
    ]
    '''

    # The initial points selected by the bayesian optimization. If this is None, it goes with it's regular input
    initial_points = None
    # Restricted regions for bayesian optimization
    restricted = []
    user_score = None
    # the list of all possible points (black box values)
    x = None
    y = None
    # maximum and minimum y values found from black box (or oracle) by testing all possible points
    max_y = None
    min_y = None
    y_ind = -1
    scale = False  # temporary solution for target function to only scale when I want it to

    poly = None

    # if true, plots solution so you can see a visual representation of what's happening
    plot_solution = False

    hasSetup = False

    """
    Borg pattern --- https://stackoverflow.com/questions/747793/python-borg-pattern-problem/747888#747888
    """
    __we_are_one = {}

    def __init__(self, fname='../resources/input/rules.txt'):
        self.__dict__ = self.__we_are_one
        if not self.hasSetup:
            self.setup(fname)
            self.hasSetup = True

    def setup(self, fname):
        rule_parser = rp.RuleParser()
        #import os
        #cwd = os.getcwd()
        #print(cwd)
        self.rules, file_horizon = rule_parser.parse_rules(fname)
        self.rules[0].to_string()
        # Converts the rules and price schema to the horizon set in parameters
        self.scale_factor = int(self.horizon / file_horizon)
        self.convert_arrays()
        self.convert_rules()

    # converts rules to the appropriate times based on scale_factor
    def convert_rules(self):
        for r in range(len(self.rules)):
            self.rules[r].time1 *= self.scale_factor
            self.rules[r].time2 *= self.scale_factor

    # converts the temperature, dewpoint, solar radiation, and price_schema to horizon time steps (expands from 24).
    def convert_arrays(self):
        old_temp = self.out_temp
        old_dp = self.dp
        old_dni = self.dni
        old_ps = self.price_schema

        self.out_temp = []
        self.dp = []
        self.dni = []
        self.price_schema = []

        for k in range(0, len(old_ps)):
            for p in range(0, self.scale_factor):
                self.out_temp.append(old_temp[k])
                self.dp.append(old_dp[k])
                self.dni.append(old_dni[k])
                self.price_schema.append(old_ps[k])

    # A complete list of all values of x and y
    def set_blackbox(self, x, y):
        self.x = x
        self.y = y

    def get_blackbox(self):
        if self.x is None:
            return 0, 0
        else:
            return self.x, self.y

# 6_21_2017
#
# parameters used across multiple files in the program
import cplex
from cplex.exceptions import CplexError
import src.RuleParser as rp


class Parameters:
    horizon = 24

    old_ps = [
        0.198, 0.198, 0.198, 0.198, 0.198, 0.198, 0.198, 0.198,
        0.225, 0.225, 0.225, 0.225,
        0.249, 0.249,
        0.849, 0.849, 0.849, 0.849,
        0.225, 0.225, 0.225, 0.225,
        0.198, 0.198
    ]

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

    price_schema = []

    model = cplex.Cplex()

    """
    Borg pattern --- https://stackoverflow.com/questions/747793/python-borg-pattern-problem/747888#747888
    """
    __we_are_one = {}

    # todo: separate init function because 'Borg' pattern causes all these things to initialize over and over
    def __init__(self):
        self.__dict__ = self.__we_are_one
        rule_parser = rp.RuleParser()
        self.rules, file_horizon = rule_parser.parse_rules('resources/input/rules.txt')
        self.rules[0].to_string()
        # Converts the rules and price schema to the horizon set in parameters
        self.scale_factor = int(self.horizon / file_horizon)
        self.convert_price_schema()
        self.convert_rules()

    def convert_rules(self):
        for r in range(len(self.rules)):
            self.rules[r].time1 *= self.scale_factor
            self.rules[r].time2 *= self.scale_factor

    def convert_price_schema(self):
        price_schema = []
        for k in range(0, len(self.old_ps)):
            for p in range(0, self.scale_factor):
                price_schema.append(self.old_ps[k])
        self.price_schema = price_schema

    def reset_solver(self):
        self.model = cplex.Cplex()
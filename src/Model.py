# 12/7/2017
#
# Holds the cplex model
# code from here originally in Parameters.py
# uses "Borg" pattern

import cplex
import src.Utilities as util


class Model:
    model = cplex.Cplex()
    util.suppress_sol_out(model)
    """
    --- Borg pattern ---
    https://stackoverflow.com/questions/747793/python-borg-pattern-problem/747888#747888
    """
    __we_are_one = {}

    def __init__(self):
        self.__dict__ = self.__we_are_one

    def reset_solver(self):
        self.model = cplex.Cplex()
        util.suppress_sol_out(self.model)
        return self.model
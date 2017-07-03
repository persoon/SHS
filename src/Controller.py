import src.Parameters
import src.RuleParser as rp
import src.Solver as solver


def execute():
    parameters = src.Parameters.Parameters()
    rules, file_horizon = rp.parse_rules('../resources/input/rules.txt')

    solver.solve(parameters, rules)


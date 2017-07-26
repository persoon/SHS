# 6_22_2017 edited 7_7_2017

import src.Rule
import src.RuleParser
import cplex
from cplex.exceptions import CplexError

# TODO: idea: make heater take in an array of predicted heats --- can take into account outside weather forecast / oven

model = cplex.Cplex()

def setup(parameters):
    # TODO: make a function for converting rules to a different granularity

    global price_schema
    global horizon
    global scale_factor
    global max_val

    price_schema = parameters.price_schema
    horizon = parameters.horizon

    # action deltas and power consumptions will be mapped to this in the future:
    # ac_washer = {}

    # for now, the deltas for the washing actions are 0 or 1
    ac_washer = [0, 1]  # TODO: switch this over and map deltas to actions
    de_washer = [0, 1]

    SP_MAX = [None] * horizon  # maximum possible value of this sensor property state at each timestep
    SP_MIN = [None] * horizon  # minimum      "       "       "       "       "       "       "

    max_val = max(de_washer)
    min_val = min(de_washer)

    # upper and lower bounds
    for i in range(0, horizon):
        SP_MAX[i] = max_val * (i + 1)
        SP_MIN[i] = min_val * (i + 1)

    # setting objective to minimize
    model.objective.set_sense(model.objective.sense.minimize)

    # objective cost should be calculated based on objectives

def convert_rules(rules, scale_factor):
    for r in range(len(rules)):
        rules[r].time1 *= scale_factor
        rules[r].time2 *= scale_factor
    return rules

def add_rules(rules):
    for r in range(len(rules)):
        print(rules[r].to_string())
        add_rule_constraints(rule=rules[r])


# todo: add input for kWh usage for price objective
def create_phase(st_var, s_time, f_time, duration):

    price = 0
    for i in range(s_time, s_time + duration):
        price += price_schema[i]

    p_array = [None] * (f_time - duration - s_time)
    p_array[0] = price
    for i in range(s_time, f_time - duration):
        price += price_schema[i]
        price -= price_schema[i - duration - 1]
        p_array[i - s_time - duration] = price

    # add start time 1 variable
    model.variables.add(
        names=[st_var],
        types=[model.variables.type.integer]
    )

    # add variables for first phase
    model.variables.add(
        names=[st_var + '_' + str(k) for k in range(s_time, f_time - duration)],
        types=[model.variables.type.integer] * (f_time - duration - s_time),
        obj=p_array
    )

    model.linear_constraints.add(
        lin_expr=[
            cplex.SparsePair(
                ind=[st_var + '_' + str(k) for k in range(s_time, f_time - duration)],
                val=[1.0] * (f_time - s_time - duration)
            )],
        rhs=[1.0],
        senses=['E']
    )

    # add constraint to set start time 1
    for k in range(s_time, f_time - duration):
        model.indicator_constraints.add(
            indvar=st_var + '_' + str(k),
            complemented=0,
            rhs=k,
            sense='E',
            lin_expr=cplex.SparsePair(ind=[st_var], val=[1.0])
        )


def connect_phases(st_var1, st_var2, duration1):
    # add constraint making start time 2 > start time 1 + duration1
    model.linear_constraints.add(
        lin_expr=[cplex.SparsePair(ind=[st_var2, st_var1], val=[1.0, -1.0])],
        senses=['G'],
        rhs=[duration1]
    )


def add_rule_constraints(rule):
    goal = rule.goal
    time1 = rule.time1
    time2 = rule.time2 + 1

    duration = 0
    t_goal = 0

    while t_goal < goal:
        t_goal += max_val
        duration += 1

    print('duration:', duration)
    duration1 = 3
    duration2 = duration - duration1

    if duration > time2 - time1:
        raise Exception('S1: No solution. Goal cannot be met within time specified.')

    create_phase('st1', time1, time2 - duration2, duration1)
    create_phase('st2', time1 + duration1, time2, duration2)
    connect_phases('st1', 'st2', duration1)



def solve(parameters, rules, file_horizon):
    # TODO: fix '-0.0' return value bug
    try:
        scale = parameters.scale_factor(file_horizon=file_horizon)
        setup(parameters)
        convert_rules(rules, scale)
        add_rules(rules)
        # rule = rules[0]

        model.solve()

        solution = model.solution
        time1 = rules[0].time1
        time2 = rules[0].time2
        duration1 = rules[0]

        print()
        print("Solution status: ", solution.get_status())
        print("Objective value: ", solution.get_objective_value())

        '''
        print('schedule:', end='\t')
        for k in range(horizon):
            print(solution.get_values("x_" + str(k)), end='\t')
        print()
        '''

        print('st:       ', end='\n\n')
        for k in range(time1, time2 - duration):
            print(abs(solution.get_values("st1_" + str(k))), end=' ')
        print()
        print()

        for k in range(time1 + duration1, time2 - duration2):
            print(abs(solution.get_values("st2_" + str(k))), end=' ')
        print()
        print()

        print('st1:', end='\n\n')
        print(abs(solution.get_values("st1")))

        print('st2:', end='\n\n')
        print(abs(solution.get_values("st2")))

        '''
        print('s prop:   ', end='\t')
        for k in range(horizon):
            print(solution.get_values("sp_" + str(k)), end='\t')
        print()
        '''

    except CplexError as exc:
        print(exc)


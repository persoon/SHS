# 6_22_2017 edited 7_7_2017

import src.Rule
import src.RuleParser
import cplex
from cplex.exceptions import CplexError

model = cplex.Cplex()

def setup(parameters):
    # TODO: make a function for converting rules to a different granularity

    global price_schema
    global horizon
    global scale_factor
    global rule
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
        add_rule_constraints(rule=rules[r], r_index=r)


def add_rule_constraints(rule, r_index):
    # TODO: create at, within constraints
    # TODO: make constraint for {<= , =} (duration stuff...)
    # TODO: make time1, time2 non-global

    global duration
    global time1
    global time2
    global duration1
    global duration2

    active = rule.active
    sp = rule.sp
    predicate = rule.predicate
    goal = rule.goal
    prefix = rule.prefix
    time1 = rule.time1
    time2 = rule.time2 + 1

    duration = 0
    t_goal = 0
    phases = 1
    duration1 = 4
    duration2 = duration - duration1

    while t_goal < goal:
        t_goal += max_val
        duration += 1

    if duration > time2 - time1:
        raise Exception('S1: No solution. Goal cannot be met within time specified.')

    price = 0
    for i in range(time1, time1+duration):
        price += price_schema[i]

    #################all code for multiple phases in here #####################
    if phases == 1:

        ##add price goal for first phase##
        p_array1 = [None] * (time2 - duration1 - time1 - duration2)
        p_array1[0] = price
        for i in range(time1, time2 - duration2 - duration1):
            price += price_schema[i]
            price -= price_schema[i - duration1 - duration2 - 1]
            p_array1[i - (time1 + duration1 + duration2)] = price

        print('DURATIONS:')
        print(duration)
        print(duration1)
        print(duration2)

        ##price objective for 2nd phase##
        p_array2 = [None] * (time2 - (time1 + duration1) - duration2)
        p_array2[0] = price
        for i in range(time1 + duration1, time2 - duration2):
            price += price_schema[i]
            price -= price_schema[i - duration2 - 1]
            p_array2[i - (time1 + duration1)] = price

        ##add variables for first phase##
        model.variables.add(
            names=['st_' + str(r_index) + '_' + str(k) for k in range(time1, time2 - duration1 - duration2)],
            types=[model.variables.type.integer] * (time2 - duration1 - time1 - duration2),
            obj=p_array1
        )

        ##add variables for second phase##
        model.variables.add(
            names=['st_' + str(r_index) + '_2_' + str(k) for k in range(time1 + duration1, time2 - duration2)],
            types=[model.variables.type.integer] * (time2 - duration2 - (time1 + duration1)),
            obj=p_array2
        )

        ##constraint to get first start time##
        model.linear_constraints.add(
            lin_expr=[
                cplex.SparsePair(
                    ind=['st_' + str(r_index) + '_' + str(k) for k in range(time1, time2 - duration1 - duration2)],
                    val=[1.0] * (time2 - duration1 - time1 - duration2))],
            rhs=[1.0],
            senses=['E']
        )

        ##constraint to get 2nd start time##
        model.linear_constraints.add(
            lin_expr=[
                cplex.SparsePair(
                    ind=['st_' + str(r_index) + '_2_' + str(k) for k in range(time1 + duration1, time2 - duration2)],
                    val=[1.0] * (time2 - (time1 + duration1) - duration2))],
            rhs=[1.0],
            senses=['E']
        )

        #add start time 1 variable
        model.variables.add(
            names=['st1'],
            types=[model.variables.type.integer]
        )

        #add constraint to set start time 1
        for k in range (time1, time2-duration1-duration2):
            model.indicator_constraints.add(
                indvar='st_' + str(r_index) + '_' + str(k),
                complemented=1,
                rhs=k,
                sense='E',
                lin_expr=cplex.SparsePair(ind=['st1'], val=[k])

            )

        #add start time 2 variable
        model.variables.add(
            names=['st2'],
            types=[model.variables.type.integer]
        )

    #add constraint to set start time 2
        for k in range(time1 + duration1, time2 - duration2):
            model.indicator_constraints.add(
                indvar='st_' + str(r_index) + '_2_' + str(k),
                complemented=1,
                rhs=k,
                sense='E',
                lin_expr=cplex.SparsePair(ind=['st2'], val=[k])

        )

        '''''
        #add constraint making start time 2 > start time 1 + duration1
        model.linear_constraints.add(
            lin_expr= [cplex.SparsePair(ind=['st2', 'st1'], val=[1.0, -1.0])],
            senses=['G'],
            rhs=[1.0]
        )
        '''

#################END PHASES CODE##############################

    p_array = [None] * (time2 - time1 - duration)
    p_array[0] = price
    for i in range(time1+duration, time2):
        price += price_schema[i]
        price -= price_schema[i - duration - 1]
        p_array[i - (time1+duration)] = price



    # start time variable
    model.variables.add(
        names=['st_' + str(r_index) + '_' + str(k) for k in range(time1, time2 - duration)],
        types=[model.variables.type.integer] * (time2 - duration - time1),
        obj=p_array
    )

    model.linear_constraints.add(
        lin_expr=[cplex.SparsePair(ind=['st_' + str(r_index) + '_' + str(k) for k in range(time1, time2 - duration)],
                                   val=[1.0] * (time2 - duration - time1))],
        rhs=[1.0],
        senses=['E']
    )


def solve(parameters, rules, file_horizon):
    # TODO: fix '-0.0' return value bug
    try:
        scale = parameters.scale_factor(file_horizon=file_horizon)
        setup(parameters)
        convert_rules(rules, scale)
        add_rules(rules)
        model.solve()

        solution = model.solution

        print()
        print("Solution status: ", solution.get_status())
        print("Objective value: ", solution.get_objective_value())

        '''
        print('schedule:', end='\t')
        for k in range(horizon):
            print(solution.get_values("x_" + str(k)), end='\t')
        print()
        '''

        print('st:       ', end='\t')
        for k in range(time1, time2 - duration):
            print(solution.get_values("st_0_" + str(k)), end='\t')
        print()
        print()

        for k in range(time1 + duration1, time2 - duration2):
            print(solution.get_values("st_0_2_" + str(k)), end='\t')
        print()
        print()

        '''
        print('s prop:   ', end='\t')
        for k in range(horizon):
            print(solution.get_values("sp_" + str(k)), end='\t')
        print()
        '''

    except CplexError as exc:
        print(exc)


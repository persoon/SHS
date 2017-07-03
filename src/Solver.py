# 6_22_2017

import src.Rule
import src.RuleParser
import cplex
from cplex.exceptions import CplexError

model = cplex.Cplex()


def setup(parameters):
    # TODO: make a function for converting rules to a different granularity

    global horizon
    global mult
    global rule
    global max_val

    price_schema = parameters.price_schema
    horizon = parameters.horizon
    mult = parameters.mult

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
    model.variables.add(
        obj=price_schema,
        names=["x_" + str(i) for i in range(horizon)],
        types=[model.variables.type.integer] * horizon,
        ub=[1] * horizon,
        lb=[0] * horizon
    )

    # sensor property state --- used to apply constraints such as goal state constraint
    model.variables.add(
        names=["sp_" + str(i) for i in range(horizon)],
        types=[model.variables.type.integer] * horizon,  # TODO: mess around with continuous, figure out if it can be used for floats
        lb=SP_MIN,
        ub=SP_MAX
    )

    # forces sensor property value to be summation of previous 'x_' values + new 'x_' value
    temp_expr = [cplex.SparsePair(ind=["sp_0", "x_0"], val=[1.0, -1.0])]
    for i in range(1, horizon):
        temp_expr.append(
            cplex.SparsePair(ind=["sp_" + str(i), "sp_" + str(i - 1), "x_" + str(i)], val=[1.0, -1.0, -1.0])
        )

    model.linear_constraints.add(
        lin_expr=temp_expr,
        senses=['E'] * horizon,
        rhs=[0.0] * horizon
    )

def add_rules(rules):
    for r in range(len(rules)):
        print(rules[r].to_string())
        add_rule_constraints(rule=rules[r], w_index=r)


def add_rule_constraints(rule, w_index):
    # TODO: create at, within constraints
    # TODO: make constraint for {<= , =} (duration stuff...)
    # TODO: make time1, time2 non-global

    global duration
    global time1
    global time2

    active = rule.active
    sp = rule.sp
    predicate = rule.predicate
    goal = rule.goal
    prefix = rule.prefix
    time1 = rule.time1
    time2 = rule.time2 + 1

    duration = 0
    t_goal = 0

    window = []
    while t_goal < goal:
        t_goal += max_val
        window.append('x_' + str(time1 + duration))
        duration += 1

    if duration > time2 - time1:
        raise Exception('S1: No solution. Goal cannot be met within time specified.')

    # start time variable
    model.variables.add(
        names=['st_' + str(w_index) + '_' + str(k) for k in range(time1, time2 - duration)],
        types=[model.variables.type.integer] * (time2 - duration - time1)
    )

    # min(time2, horizon) used because 'after' and passive rules go until horizon and we add 1 to time2 to fix problems with range
    model.linear_constraints.add(
        lin_expr=[
            cplex.SparsePair(ind=["x_" + str(k) for k in range(time1, min(time2, horizon))], val=[1.0] * (min(time2, horizon) - time1))
        ],
        senses=[predicate],
        rhs=[goal]
    )
    print('blah1')
    model.linear_constraints.add(
        lin_expr=[cplex.SparsePair(ind=['st_' + str(w_index) + '_' + str(k) for k in range(time1, time2 - duration)],
                                   val=[1.0] * (time2 - duration - time1))],
        rhs=[1.0],
        senses=['E']
    )
    print('blah2')
    print(range(time1, time2 - duration))
    print(duration)
    for j in range(time1, time2 - duration):
        model.indicator_constraints.add(
            lin_expr=cplex.SparsePair(ind=window, val=[1.0] * duration),
            rhs=goal,
            sense='G',
            indvar='st_' + str(w_index) + '_' + str(j),
            complemented=0
        )
        print(window)
        window.reverse()
        window.pop()
        window.reverse()
        window.append('x_' + str(duration + j))


def solve(parameters, rules):
    # TODO: fix '-0.0' return value bug

    try:

        setup(parameters)
        add_rules(rules)
        model.solve()

        solution = model.solution

        print()
        print("Solution status: ", solution.get_status())
        print("Objective value: ", solution.get_objective_value())

        print('schedule:', end='\t')
        for k in range(horizon):
            print(solution.get_values("x_" + str(k)), end='\t')
        print()

        print('st:       ', end='\t')
        for k in range(time1, time2 - duration):
            print(solution.get_values("st_0_" + str(k)), end='\t')
        print()
        for k in range(time1, time2 - duration): print(k, end='\t')
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


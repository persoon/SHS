import src.Parameters
import src.Reader
import src.Solver as Solver
from src.bayes_opt.bayesian_optimization import BayesianOptimization as bayesian
import numpy as np
import src.PolynomGen
import random
import src.Oracle
import copy
import src.Rule

params = src.Parameters.Parameters()


horizon = params.horizon
solver = Solver.Solver(params)


def target_function(t):
    t = t.astype(int)
    for i in range(len(t)):
        if params.rules[i].prefix == 'after':  # TODO: have to change this if want we to handle at and within
            params.rules[i].time1 = t[i]
        else:
            params.rules[i].time2 = t[i]

    check = solver.reset(params=params, rules=params.rules)

    if check == -1:
        return -32768  # return a large negative number if rules inconsistent

    # solver.dependancy(params.devices[0], params.devices[1])
    solution = solver.solve()

    if params.verbose:
        print('=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+')
        print('SOLUTION STATUS:', solution.get_status())
        print('objPrice Value:', solution.get_values('objPrice'))
        print('=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+')

    polyval = params.poly.calculate(xval=t[0])

    if solution.get_status() != 103:  # if solution status is 101, optimal solution found --- 103 means infeasible
        if params.scale is True:
            ans = polyval - solution.get_values('objPrice') + params.reg_price
            # print(ans)
            if ans < 0:
                # print(params.min_y)
                ans = 5 - (ans / params.min_y[params.y_ind] * 5)
            else:
                ans = 5 + (ans / params.max_y[params.y_ind] * 5)  # get an answer out of 10.0
            # print(ans)
            # print('t:', t[0], 'val:', polyval, round(solution.get_values('objPrice'), 2), round(params.reg_price, 2), ans)
            return round(ans, 2)
        else:
            return round(polyval - solution.get_values('objPrice') + params.reg_price, 2)
    else:
        print('ERROR: INFEASIBLE SOLUTION')
        return -32768  # return a large negative number if solution is infeasible


def execute(type='normal', devices=None, fname=None):

    if devices is None:
        dictionary = src.Reader.Reader().get_dictionary()
        devices = [
            dictionary.get_device(device_type=    'washer', device_name='GE_WSM2420D3WW', mode_name="regular_w", dID=0),
            dictionary.get_device(device_type=     'dryer', device_name='GE_WSM2420D3WW', mode_name="regular_d", dID=1),
            dictionary.get_device(device_type=      'oven', device_name=   'Kenmore_790', mode_name=     "bake", dID=2),
            dictionary.get_device(device_type='dishwasher', device_name=   'Kenmore_665', mode_name=     "wash", dID=3)
        ]

    t_vals = []

    rules = []
    for d in devices:
        rules.append(generate_rule(d))
    params.rules = rules
    # rules = params.rules

    for _rule in params.rules:
        print(_rule.to_string())

    err = 0  # number of erroneous rules
    for r in range(len(rules)):
        print(rules[r].time1, rules[r].time2)
        if rules[r].time1 == 0:  # before
            t_vals.append((rules[r].time2, horizon - 1))
        elif rules[r].time2 == horizon:  # after
            t_vals.append((0, rules[r].time1))
        else:
            print('ERROR: unhandled rule:')
            print(rules[r].to_string())
            err += 1
            continue

    pbounds = {'t': t_vals}
    solver = Solver.Solver(params=params)

    # NOTE:
    # dryer values: time# 88 = 2430
    #               time#191 =  243
    params.devices = devices

    # restricted regions have to be times where the device cannot be run ever
    # What good does saying before 14 is out of bounds if before 15 isn't and generates the same schedule?
    restricted = []
    for i in range(len(devices)):  # restricted regions --- one list for each device
        restricted.append([])
    # restricted[0] = [[4, 8], [90, 102]]
    params.restricted = restricted

    # print('Price w/o changes:', reg_price)
    # print_info(solution, devices)

    # rule, horizon
    # bay = bayesian(f=target_function, pbounds=pbounds, verbose=0)
    # bay.maximize(init_points=2, n_iter=0, acq='ucb', kappa=5)

    x = []
    y = []
    user_score = []
    params.min_y = []
    params.max_y = []
    params.y_ind = -1
    params.user_score = []
    oracle = src.Oracle.Oracle()

    # print(t_vals)
    for i in range(len(t_vals)):
        rules[i].horizon = params.horizon
        params.rules = [copy.deepcopy(rules[i])]  # set up a single rule at a time

        solver.reset(params=params)
        solution = solver.solve()
        reg_price = round(solution.get_values('objPrice'), 2)
        params.reg_price = reg_price
        # print('reg_price for rule:', reg_price)
        x.append(np.linspace(t_vals[i][0], t_vals[i][1], t_vals[i][1] - t_vals[i][0] + 1))
        y.append([])
        user_score.append([])
        params.poly = src.PolynomGen.PolynomGen(bounds=t_vals[i], ymax=1000, num=random.randint(3, 5))

        for j in range(len(x[i])):
            y[i].append(target_function(np.asarray([x[i][j]])))
            # user_score[i].append(poly.calculate(x[i][j]))
        y[i] = np.asarray(y[i])
        # print(y)
        params.max_y.append(max(y[i]))
        params.min_y.append(min(y[i]))
        params.y_ind += 1
        params.scale = True
        for j in range(len(y[i])):  # set all y values in black box to be between 1 and 10
            ans = y[i][j]
            # print('---------------------')
            # print('before', ans)
            if ans < 0:
                if params.min_y[i] == 0:
                    ans = 5
                else:
                    ans = 5 - (ans / params.min_y[i] * 4)
            else:
                if params.max_y[i] == 0:
                    ans = 5
                else:
                    ans = 5 + (ans / params.max_y[i] * 5)  # get an answer out of 10.0
            # print('after', ans)
            # print('---------------------')
            y[i][j] = ans
            '''
            ans = user_score[i][j]
            if ans < 0:
                if params.min_y == 0:
                    ans = 5
                else:
                    ans = 5 - (ans / params.min_y[i] * 5)
            else:
                if params.max_y == 0:
                    ans = 5
                else:
                    ans = 5 + (ans / params.max_y[i] * 5)  # get an answer out of 10.0
            user_score[i][j] = ans
            '''
        params.scale = False
        print('adding', rules[i].to_string())
        oracle.add(rules[i], x[i], y[i])

        if type == 'rank2':
            for i in range(1, len(t_vals)):
                oracle.add(rules[0], x[0], y[0])
            break

    if fname is None:
        if type == 'normal':
            oracle.writeCSV()
        elif type == 'random':
            oracle.write_random()
        elif type == 'rank1':
            oracle.write_rank1()
        elif type == 'rand_rank1':
            oracle.write_random_rank1()
    else:
        if type == 'normal':
            oracle.writeCSV(fname)
        elif type == 'random':
            oracle.write_random(fname)
        elif type == 'rank1':
            oracle.write_rank1(fname)
        elif type == 'rand_rank1':
            oracle.write_random_rank1(fname)


# NOTE: rule_pref can be obtained from solver.rule_pref
def print_info(solution, devices=None, rule_pref=None):
    # solution if normal rule is used
    if devices is None:
        devices = []
    if rule_pref is None:
        rule_pref = []

    print('-------------------------------------')
    for d in range(len(devices)):
        print(devices[d].name)
        for p in range(len(devices[d].phases)):
            print(devices[d].mode[p]['name'] + ':', end='\t')
            for t in range(params.horizon):
                print(int(solution.get_values('d' + str(d) + '_p' + str(p) + '_' + str(t))), end='\t')
            print()
        print('-------------------------------------')

    for s in range(len(rule_pref)):
        print('T =', rule_pref[s][2])
        for p in range(rule_pref[s][1]):
            dname = rule_pref[s][0]
            print(devices[int(rule_pref[s][0].replace('d', ''))].mode[p]['name'] + ':', end='\t')
            for t in range(params.horizon):
                print(int(solution.get_values(dname + '_t' + str(rule_pref[s][2]) + '_p' + str(p) + '_' + str(t))),
                      end='\t')
            print()
        print('-------------------------------------')

    # prints out all of the best solutions (with increasing discomfort level)
    for s in range(len(rule_pref)):
        print('Solution ' + str(rule_pref[s][0]) + '_t' + str(rule_pref[s][2]) + ':',
              round(solution.get_values('d0_t' + str(rule_pref[s][2])), 2))


def generate_rule(device):
    sp = {
        'washer'    : 'wash',
        'dryer'     : 'dry',
        'oven'      : 'bake',
        'dishwasher': 'dish_wash'  # might change this one later
    }[device.mode_type]

    predicate = 'E'  # random.choice(['L', 'E', 'G']) # <=, ==, >=
    prefix = random.choice(['before', 'after'])
    #time1 = -1

    # before 5; before 17; after 5; after 17;
    time1 = random.randint(5, 17)
    time1 *= int(params.horizon / 24)

    '''
    if prefix == 'after':
        time1 = random.randint(0, params.horizon-device.duration-1)
    elif prefix == 'before':
        time1 = random.randint(device.duration+1, params.horizon-1)
    else:
        print('Need to setup \'within\'/\'at\' inside generate_rule in Controller.py before using')
        exit(-1)
    '''

    return src.Rule.Rule(
        r_type="1",
        loc='d:'+device.device_name,
        sp=sp,
        predicate=predicate,
        prefix=prefix,
        time1=time1,
        horizon=params.horizon
    )

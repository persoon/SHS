import src.Parameters
import src.Reader
import src.Solver as Solver
import src.Expectation as expectation
from src.bayes_opt.bayesian_optimization import BayesianOptimization as bayesian
import src.LineGraph as graph
import matplotlib.pyplot as plt
import numpy as np
import src.PolynomGen
from matplotlib import gridspec
params = src.Parameters.Parameters()

horizon = params.horizon
# todo: handle 'within', 'at' rules
t_vals = []
for r in params.rules:
    print(r.time1, r.time2)

    if r.time1 == 0:  # before
        t_vals.append((r.time2, horizon-1))
    elif r.time2 == horizon:  # after
        t_vals.append((0, r.time1))
    else:
        print('ERROR: unhandled rule:')
        print(r.to_string())
pbounds = {'t': t_vals}  # , 't2': (rt2_2, horizon-1)}
# print(pbounds)
solver = Solver.Solver(params=params)

'''
rt1_1 = 0
rt1_2 = 0
rt2_1 = 0
rt2_2 = 0
if params.rules[0].time1 == 0:  # before
    rt1_1 = params.rules[0].time2
    rt1_2 = horizon - 1
elif params.rules[0].time2 == horizon:  # after
    rt1_1 = 0
    rt1_2 = params.rules[0].time1

if params.rules[1].time1 == 0:  # before
    rt2_1 = params.rules[1].time2
    rt2_2 = horizon - 1
elif params.rules[1].time2 == horizon:  # after
    rt2_1 = 0
    rt2_2 = params.rules[1].time1
usr = user(rt1_1, rt1_2, rt2_1, rt2_2)
'''
expect_vals = [[0, 600]]#, [0, 1600]] # <--- these change based on devices in system
expect = expectation.Expectation(bounds=t_vals, expect=expect_vals)
# expect.show_graphs()
poly = src.PolynomGen.PolynomGen(bounds=[88, 191], ymax=2000, num=5)


def target_function(t):
    t = t.astype(int)
    for i in range(len(t)):
        if t[i] < params.rules[i].time1:
            params.rules[i].time1 = t[i]
        else:
            params.rules[i].time2 = t[i]
        # print(params.rules[i].to_string())
    check = solver.reset(params=params)
    if check == -1:
        return -32768  # return a large negative number if rules inconsistent

    # solver.dependancy(params.devices[0], params.devices[1])
    solution = solver.solve()

    if params.verbose:
        print('=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+')
        print('SOLUTION STATUS:', solution.get_status())
        print('objPrice Value:', solution.get_values('objPrice'))
        print('=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+')

    if solution.get_status() != 103:  # if solution status is 101, optimal solution found --- 103 means infeasible (hoping this works -- will require more experimentation)
        # expect.show_ucb()
        # if expect.get_value(t) == 0:
        # print('THE VALUE WHEN EXPECTATION WAS 0:', round(expect.get_value(t) - solution.get_values('objPrice') + params.reg_price, 2))
        return round(expect.get_value(t) - solution.get_values('objPrice') + params.reg_price, 2)
    else:
        return -32768  # return a large negative number if solution is infeasible


def target_function2(t):
    t = t.astype(int)
    for i in range(len(t)):
        if t[i] < params.rules[i].time1:
            params.rules[i].time1 = t[i]
        else:
            params.rules[i].time2 = t[i]
        # print(params.rules[i].to_string())
    check = solver.reset(params=params)
    if check == -1:
        return -32768  # return a large negative number if rules inconsistent

    #solver.dependancy(params.devices[0], params.devices[1])
    solution = solver.solve()

    if params.verbose:
        print('=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+')
        print('SOLUTION STATUS:', solution.get_status())
        print('objPrice Value:', solution.get_values('objPrice'))
        print('=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+')

    polyval = poly.calculate(xval=t[0])

    if solution.get_status() != 103:  # if solution status is 101, optimal solution found --- 103 means infeasible
        if params.max_y is not None and params.min_y is not None and params.min_y < params.max_y:
            ans = polyval - solution.get_values('objPrice') + params.reg_price

            if ans < 0:
                ans = 5 - (ans / params.min_y * 5)
            else:
                ans = 5 + (ans / params.max_y * 5)  # get an answer out of 10.0
            #  print('t:', t[0], 'val:', polyval, round(solution.get_values('objPrice'), 2), round(params.reg_price, 2), ans)
            return round(ans, 2)
        else:
            return round(polyval - solution.get_values('objPrice') + params.reg_price, 2)
    else:
        return -32768  # return a large negative number if solution is infeasible


def execute():
    dictionary = src.Reader.Reader().get_dictionary()
    devices = [
        dictionary.get_device(device_type='washer', device_name='GE_WSM2420D3WW', mode_name="regular_w", dID=0),
        #dictionary.get_device(device_type= 'dryer', device_name='GE_WSM2420D3WW', mode_name="regular_d", dID=1)
    ]

    # NOTE:
    # dryer values: time# 88 = 2430
    #               time#191 =  243
    params.devices = devices
    solver.reset(params=params)
    #solver.dependancy(devices[0], devices[1])
    solution = solver.solve()

    reg_price = round(solution.get_values('objPrice'), 2)
    params.reg_price = reg_price

    # restricted regions have to be times where the device cannot be run ever
    # What good does saying before 14 is out of bounds if before 15 isn't and generates the same schedule?
    restricted = []
    for i in range(len(devices)): # restricted regions --- one list for each device
        restricted.append([])
    print(restricted)
    #restricted[0] = [[4, 8], [90, 102]]
    params.restricted = restricted

    pref_price = [reg_price]
    rule = params.rules[0]

    poly = src.PolynomGen.PolynomGen(bounds=[88, 191], ymax=2000, num=5)

    #print('Price w/o changes:', reg_price)
    # print_info(solution, devices)

    # rule, horizon
    bay = bayesian(f=target_function2, pbounds=pbounds, verbose=0)
    #bay.maximize(init_points=2, n_iter=0, acq='ucb', kappa=5)

    x = np.linspace(t_vals[0][0], t_vals[0][1], t_vals[0][1] - t_vals[0][0] + 1)
    y = []
    user_score = []
    for i in range(len(x)):
        y.append(target_function2(np.asarray([x[i]])))
        user_score.append(poly.calculate(x[i]))

    y = np.asarray(y)

    params.max_y = max(y)
    params.min_y = min(y)
    for i in range(len(x)):  # set all y values in black box to be between 0 and 10
        ans = y[i]
        if ans < 0:
            ans = 5 - (ans / params.min_y * 5)
        else:
            ans = 5 + (ans / params.max_y * 5)  # get an answer out of 10.0
        y[i] = ans

        ans = user_score[i]
        if ans < 0:
            ans = 5 - (ans / params.min_y * 5)
        else:
            ans = 5 + (ans / params.max_y * 5)  # get an answer out of 10.0
        user_score[i] = ans

    params.user_score = user_score
    params.set_blackbox(x, y)

    # for i in range(5):
    bay.maximize(init_points=3, n_iter=20, acq='ucb', kappa=5)

    # plot_gp(bay, x.reshape(-1, 1), y, t_vals[0][0], t_vals[0][1])

    # plt.show()



    #p_x, p_mean, p_std = bay.maximize()
    #return expect, p_x, p_mean, p_std
    #line_graph = graph.LineGraph(expect.bounds[0])
    #line_graph.add_expectation(expect.kline[0])
    #line_graph.add_confidence_interval(2.53*100, p_mean, p_std, p_x)
    #expect.show_ucb()
    #line_graph.show_graph()





    #span = params.horizon - (rt2_1+1)
    #freq = 25  # distance between samples

    #num_tries = int(span/freq)
    #Ydata = []
    #Xdata = []
    '''
    for t in range(num_tries):
        _time = rt2 + ((t+1) * freq)
        _time = min(params.horizon-1, _time)
        rule.time2 = _time
        params.rules[0] = rule
        solver.reset(params=params)

        solution = solver.solve()
        p = round(solution.get_values('objPrice'), 2)
        print(params.rules[0].time2, ':', p)
        pref_price.append(p)

        Ydata.append(pref_price[0] - pref_price[len(pref_price)-1])
        Xdata.append(_time)
        # print_info(solution=solution, devices=devices)

    usr = user(rtime2, params.horizon-1)
    print(rtime2, params.horizon-1)
    usr.showBlackbox()
    usr.gauss(Xdata=Xdata, Ydata=Ydata)
    '''

    '''
    for i in range(len(pref_price)):
        print(rtime2+i, ':', pref_price[i])
    '''


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

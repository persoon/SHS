import src.Parameters
import src.Reader
from src.bayes_opt.bayesian_optimization import BayesianOptimization as bayesian
import numpy as np
import src.PolynomGen
import random
import src.Oracle

params = src.Parameters.Parameters()


def target_function(t):
    t = t.astype(int)
    print(t)
    return params.y[t[0]]


def execute(devices=None, fname=None):

    dictionary = src.Reader.Reader().get_dictionary()
    if devices is None:
        devices = [
            dictionary.get_device(device_type=    'washer', device_name='GE_WSM2420D3WW', mode_name="regular_w", dID=0),
            dictionary.get_device(device_type=     'dryer', device_name='GE_WSM2420D3WW', mode_name="regular_d", dID=1),
            dictionary.get_device(device_type=      'oven', device_name=   'Kenmore_790', mode_name=     "bake", dID=2),
            dictionary.get_device(device_type='dishwasher', device_name=   'Kenmore_665', mode_name=     "wash", dID=3)
        ]

    params.devices = devices

    params.min_y = []
    params.max_y = []
    params.y_ind = -1

    oracle = src.Oracle.Oracle()

    if fname is None:
        horizon, span, values, initial_points = oracle.readCSV()
    else:
        horizon, span, values, initial_points = oracle.readCSV(name=fname)

    print('horizon:', horizon)
    for s in range(len(span)):
        print('--------------------------------------')
        print('span:', span[s])
        print('values:', values[s])
        print('--------------------------------------')

    restricted = []
    for i in range(len(devices)):  # restricted regions --- one list for each device
        restricted.append([])
    params.restricted = restricted

    errors = []

    for i in range(len(values)):
        t_vals = []
        err = 0
        t_vals.append(span[i])
        '''
        if span[i][0] == 0:  # before
            t_vals.append((span[i][1], horizon - 1))
        elif span[i][1] == horizon:  # after
            t_vals.append((0, span[i][0]))
        else:
            print('ERROR: unhandled rule:')
            print(span[i])
            err += 1
            continue
        '''
        pbounds = {'t': t_vals}
        print(pbounds)
        target_values = values[i]
        params.initial_points = initial_points[i]
        x = np.linspace(t_vals[0][0], t_vals[0][1], t_vals[0][1] - t_vals[0][0] + 1)
        y = target_values
        y = np.asarray(y)
        print(x.shape)
        print(y.shape)
        params.set_blackbox(x, y)
        bay = bayesian(f=target_function, pbounds=pbounds)
        p_x, p_mean, p_std = bay.maximize(init_points=3, n_iter=8, acq='ucb', kappa=2)

        '''
        bay.gp.fit(bay.space.X, bay.space.Y)
        print('t_val range:', range(t_vals[0][0], t_vals[0][1]))
        p_x = []
        p_y = []
        for x in range(t_vals[0][0], t_vals[0][1]):
            mu, sigma = bay.gp.predict(x, return_std=True)
            p_x.append(x)
            p_y.append(mu)
        '''

        p_y = p_mean
        averages = []
        for j in range(len(p_x)):
            tot = 0
            for k in range(len(p_x[j])):
                # print('(', round(p_x[j][k]), values[i][int(round(p_x[j][k]))], ') ?:', p_y[j][k])
                tot += abs(values[i][int(round(p_x[j][k][0]))] - p_y[j][k][0])

            avg = tot / len(p_x[j])
            averages.append(avg)

        print(bay.point_bounds)

        '''
        avg_err = []
        for j in range(len(p_x)):
            uniq = -1
            step = p_x[j]
            total = 0
            num_timesteps = 0
            timesteps = []
            averages = []
            k = 0
            while k in range(len(step)):
                uniq = int(round(step[k]))
                count = 0
                tot = 0
                while k in range(len(step)) and uniq == int(round(step[k])):
                    #print(count, int(round(step[k])))
                    tot += p_mean[j][k][0]
                    count += 1
                    k += 1
    
                if count != 0:
                    timesteps.append(uniq)
                    averages.append(tot / count)
                    num_timesteps += 1
                else:
                    print('ERROR: count is 0')
    
            error = 0
            for t in range(len(timesteps)):
                print(timesteps[t], ':', values[i][timesteps[t]], averages[t], values[i][timesteps[t]] - averages[t])
                error += abs(values[i][timesteps[t]] - averages[t])
                #print(timesteps[t], ':', averages[t])
    
    
    
            error /= len(timesteps) + j
            avg_err.append(error)
            # print('error:', error)
    
    
            ##################
            
            
            tot = 0
            for k in range(len(step)):
                print('(', round(step[k]), values[i][int(round(step[k]))], ') ?:', p_mean[j][k][0])
    
                tot += abs(values[i][int(round(step[k]))] - p_mean[j][k][0])
    
            avg = tot / len(step)
            averages.append(avg)
            '''

        print('p_x:\n', p_x)
        print('p_y:\n', p_y)
        #print('values:\n', values[i])
        print('ERRORS PER TIMESTEP:')
        for j in range(len(averages)):
            print(str(j)+':', averages[j])
        print('~~~~~~~~~~~~~~ DONE', i, '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
        errors.append(averages)
    totals = None
    for i in range(len(errors)):
        for j in range(len(errors[i])):
            if totals is None:
                totals = errors[i][:]
                break
            else:
                totals[j] = totals[j] + errors[i][j]
                if i == len(errors[i])-1:
                    totals[j] = totals[j] / len(errors[i])

    #print(errors)
    #print(totals)
    return totals


def execute_rank1(devices=None, fname=None):
    dictionary = src.Reader.Reader().get_dictionary()
    if devices is None:
        devices = [
            dictionary.get_device(device_type='washer', device_name='GE_WSM2420D3WW', mode_name="regular_w", dID=0),
            dictionary.get_device(device_type='dryer', device_name='GE_WSM2420D3WW', mode_name="regular_d", dID=1),
            dictionary.get_device(device_type='oven', device_name='Kenmore_790', mode_name="bake", dID=2),
            dictionary.get_device(device_type='dishwasher', device_name='Kenmore_665', mode_name="wash", dID=3)
        ]

    params.devices = devices

    params.min_y = []
    params.max_y = []
    params.y_ind = -1

    oracle = src.Oracle.Oracle()

    if fname is None:
        horizon, span, values, initial_points = oracle.get_rank1()
    else:
        horizon, span, values, initial_points = oracle.get_rank1(name=fname)

    print('horizon:', horizon)
    for s in range(len(span)):
        print('--------------------------------------')
        print('span:', span[s])
        print('values:', values[s])
        print('--------------------------------------')

    restricted = []
    for i in range(len(devices)):  # restricted regions --- one list for each device
        restricted.append([])
    params.restricted = restricted

    errors = []

    for i in range(len(values)):
        t_vals = []
        err = 0
        t_vals.append(span[i])

        pbounds = {'t': t_vals}
        print(pbounds)
        target_values = values[i]
        params.initial_points = initial_points[i]
        x = np.linspace(t_vals[0][0], t_vals[0][1], t_vals[0][1] - t_vals[0][0] + 1)
        y = target_values
        y = np.asarray(y)
        print(x.shape)
        print(y.shape)
        params.set_blackbox(x, y)
        bay = bayesian(f=target_function, pbounds=pbounds)
        p_x, p_mean, p_std = bay.maximize(init_points=3, n_iter=8, acq='ucb', kappa=2)

        p_y = p_mean
        averages = []
        for j in range(len(p_x)):
            tot = 0
            for k in range(len(p_x[j])):
                # print('(', round(p_x[j][k]), values[i][int(round(p_x[j][k]))], ') ?:', p_y[j][k])
                tot += abs(values[i][int(round(p_x[j][k]))] - p_y[j][k])

            avg = tot / len(p_x[j])
            averages.append(avg)

        print(bay.point_bounds)

        print('p_x:\n', p_x)
        print('p_y:\n', p_y)
        # print('values:\n', values[i])
        print('ERRORS PER TIMESTEP:')
        for j in range(len(averages)):
            print(str(j) + ':', averages[j])
        print('~~~~~~~~~~~~~~ DONE', i, '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
        errors.append(averages)

    return errors


# todo: make this version of bayesian optimization do all devices at once, keep other one working
# use all of them to find the solution
# 1) point bounds lists that contain a value for each point
# 2) rework points lists to be a list of lists (one for each device)
#   2a) x and y
#   2b) initial points
#   2c) p_x, p_mean, p_std
# 3) pbounds list for target function updated to include multiple devices again
def target_function2(t):

    # this prevents the list from continually trying the same point:
    # initialize list
    # if params.tested_points is None:
    #    params.tested_points = []

    t = t.astype(int)

    # add to list
    # params.tested_points.append(t)
    val = 0
    for i in range(len(t)):
        val = val + params.y[i][t[i]]
    #print(params.y)
    #print('testing:', t)
    #print('result:', val)
    print(val)
    return val


def execute2(devices=None, fname=None):
    dictionary = src.Reader.Reader().get_dictionary()
    if devices is None:
        devices = [
            dictionary.get_device(device_type='washer', device_name='GE_WSM2420D3WW', mode_name="regular_w", dID=0),
            dictionary.get_device(device_type='dryer', device_name='GE_WSM2420D3WW', mode_name="regular_d", dID=1),
            dictionary.get_device(device_type='oven', device_name='Kenmore_790', mode_name="bake", dID=2),
            dictionary.get_device(device_type='dishwasher', device_name='Kenmore_665', mode_name="wash", dID=3)
        ]

    params.devices = devices

    params.min_y = []
    params.max_y = []
    params.y_ind = -1

    oracle = src.Oracle.Oracle()

    if fname is None:
        horizon, span, values, initial_points = oracle.readCSV()
    else:
        horizon, span, values, initial_points = oracle.readCSV(name=fname)

    print('horizon:', horizon)
    for s in range(len(span)):
        print('--------------------------------------')
        print('span:', span[s])
        print('values:', values[s])
        print('--------------------------------------')

    restricted = []
    for i in range(len(devices)):  # restricted regions --- one list for each device
        restricted.append([])
    params.restricted = restricted

    errors = []

    t_vals = list(span)  # make a copy of the span list for use as the boundaries for target function
    pbounds = {'t': t_vals}
    init_points = []
    for i in range(len(initial_points[0])):
        init_points.append([])

    for i in range(len(initial_points)):
        for j in range(len(initial_points[i])):
            init_points[j].append(initial_points[i][j][0])

    print(init_points)
    params.initial_points = init_points

    x = []
    for i in range(len(values)):
        x.append(np.linspace(t_vals[i][0], t_vals[i][1], t_vals[i][1] - t_vals[i][0] + 1))
    y = values
    y = np.asarray(y)
    params.set_blackbox(x, y)
    bay = bayesian(f=target_function2, pbounds=pbounds)
    p_x, p_mean, p_std = bay.maximize(init_points=3, n_iter=8, acq='ucb', kappa=2)
    print('p_x:')
    print(p_x)
    print('p_mean:')
    print(p_mean)
    #print('p_std')
    #print(p_std)
    #print('DONE')

    averages = []
    for i in range(len(p_x)):  # each iteration
        tot = 0
        for j in range(len(p_x[i])):  # each test value
            val = abs(target_function2(p_x[i][j]) - p_mean[i][j][0])
            print(val, end='\t')
            tot += val
        print()
        avg = tot / len(p_x[i])
        averages.append(avg / 4)

    print(averages)

    return averages



    '''
    bay.gp.fit(bay.space.X, bay.space.Y)
    print('t_val range:', range(t_vals[0][0], t_vals[0][1]))
    p_x = []
    p_y = []
    for x in range(t_vals[0][0], t_vals[0][1]):
        mu, sigma = bay.gp.predict(x, return_std=True)
        p_x.append(x)
        p_y.append(mu)
    '''

    '''
    p_y = p_mean
    averages = []
    for j in range(len(p_x)):
        tot = 0
        for k in range(len(p_x[j])):
            # print('(', round(p_x[j][k]), values[i][int(round(p_x[j][k]))], ') ?:', p_y[j][k])
            tot += abs(values[i][int(round(p_x[j][k]))] - p_y[j][k])

        avg = tot / len(p_x[j])
        averages.append(avg)

    print(bay.point_bounds)


    print('p_x:\n', p_x)
    print('p_y:\n', p_y)
    # print('values:\n', values[i])
    print('ERRORS PER TIMESTEP:')
    for j in range(len(averages)):
        print(str(j) + ':', averages[j])
    print('~~~~~~~~~~~~~~ DONE', i, '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
    errors.append(averages)
    
    return errors
    '''

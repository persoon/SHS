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
    return target_values[t[0]]

dictionary = src.Reader.Reader().get_dictionary()
devices = [
    dictionary.get_device(device_type=    'washer', device_name='GE_WSM2420D3WW', mode_name="regular_w", dID=0),
    dictionary.get_device(device_type=     'dryer', device_name='GE_WSM2420D3WW', mode_name="regular_d", dID=1),
    dictionary.get_device(device_type=      'oven', device_name=   'Kenmore_790', mode_name=     "bake", dID=2),
    dictionary.get_device(device_type='dishwasher', device_name=   'Kenmore_665', mode_name=     "wash", dID=3)
]

params.devices = devices

x = []
y = []
user_score = []
params.min_y = []
params.max_y = []
params.y_ind = -1
params.user_score = []

oracle = src.Oracle.Oracle()

horizon, span, values, initial_points = oracle.readCSV()

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
    bay = bayesian(f=target_function, pbounds=pbounds)
    p_x, p_mean, p_std = bay.maximize(init_points=3, n_iter=8, acq='ucb', kappa=5)

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
            #print('(', round(p_x[j][k]), values[i][int(round(p_x[j][k]))], ') ?:', p_y[j][k])
            tot += abs(values[i][int(round(p_x[j][k]))] - p_y[j][k])

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


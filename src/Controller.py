import src.Parameters
import src.RuleParser as RP
import src.Rule as R
import src.Reader
import cplex
from cplex.exceptions import CplexError
import numpy
import time
import random
import src.Solver as Solver

params = src.Parameters.Parameters()


def execute():
    dictionary = src.Reader.Reader().get_dictionary()
    devices = [
        dictionary.get_device(device_type='HVAC', mode_name='cool', dID=0),
        dictionary.get_device(device_type='washer', device_name='GE_WSM2420D3WW', mode_name="regular_w", dID=1),
        dictionary.get_device(device_type='dryer', device_name='GE_WSM2420D3WW', mode_name="regular_d", dID=2),
        dictionary.get_device(device_type='oven', device_name='Kenmore_790', mode_name="bake", dID=3),
        dictionary.get_device(device_type='dishwasher', device_name='Kenmore_665', mode_name="wash", dID=4)
    ]
    params = src.Parameters.Parameters()
    params.devices = devices
    solver = Solver.Solver(params=params)
    solution = solver.solve()

    '''
    rules = []
    for i in range(len(devices)):
        print(devices[i].to_string())
        rules.append(generate_rule(devices[i]))
        print(rules[i].to_string())
        print()
    '''
    print('-------------------------------------')
    for d in range(len(devices)):
        print(devices[d].name)
        for p in range(len(devices[d].phases)):
            print(devices[d].mode[p]['name'] + ':', end='\t')
            for t in range(params.horizon):
                print(int(solution.get_values('d'+str(d)+'_p'+str(p)+'_'+str(t))) ,end='\t')
            print()
        print('-------------------------------------')


    ''' TODO: Fix schedule printing with new Solver '''
    #f = open('resources/output/schedule.txt', 'w')
    #f.write(run_experiment(timeout=10, devices=devices, rules=rules))
    #f.close()


# generates devices
# does not add device variables, make sure to add those
# inputs:
#   type -- determines which devices to generate
#       'mix' : makes a perfect mix, one of each device type created so far -- then repeats
#       'random' : generates random devices
#       dtype (e.g. 'washer'): to generate a number of that type of device
#       default: 'random'
#   num_devs -- determines number of devices to generate
#       default: 4
#   OPTIONAL::model -- this is here for when I add more than one model of any type of device
def generate_devices(type='random', num_devs=4, model='random'):
    dictionary = src.Reader.Reader().get_dictionary()
    devices = []

    if type == 'random':
        for i in range(num_devs):
            devices.append(dictionary.get_device(dID=i))
    elif type == 'mix':
        for i in range(num_devs):
            if i % 4 == 0:
                devices.append(dictionary.get_device(dtype='washer', dID=i))
            elif i % 4 == 1:
                devices.append(dictionary.get_device(dtype='dryer', dID=i))
            elif i % 4 == 2:
                devices.append(dictionary.get_device(dtype='oven', dID=i))
            elif i % 4 == 3:
                devices.append(dictionary.get_device(dtype='dishwasher', dID=i))
    else:
        for i in range(num_devs):
            devices.append(dictionary.get_device(dtype=type, device_name=model, dID=i))
    return devices


def generate_rule(device):
    sp = {
        'washer'     : 'wash',
        'dryer'      : 'dry',
        'oven'       : 'bake',
        'dishwasher': 'dish_wash'  # might change this one later
    }[device.dtype]

    predicate = 'E'# random.choice(['L', 'E', 'G']) # <=, ==, >=
    prefix = random.choice(['before'])#, 'after'])  # todo: confirm at and within work properly 9_18_2017
    time1 = -1
    # todo: refine these to fit full possible range && add 'at' and 'within' 9_18_2017
    if prefix == 'after':
        time1 = random.randint(0, params.horizon-device.duration-1)
    elif prefix == 'before':
        time1 = random.randint(device.duration+1, params.horizon-1)
    else:
        print('Need to setup \'within\'/\'at\' inside generate_rule in Controller.py before using')
        exit(-1)
    # todo: figure out this location mess, right now all devices coincidentally are their loc 9_18_2017
    return R.Rule(
        loc=device.device_name,
        sp=sp,
        predicate=predicate,
        prefix=prefix,
        time1=time1,
        horizon=params.horizon
    )

def run_experiment(timeout, devices, rules):
    model = params.model
    model.parameters.timelimit.set(timeout)
    horizon = params.horizon

    vars = []
    for i in range(len(devices)):
        devices[i].add_variables()
        vars.append(devices[i].add_constraints(rules[i])[0])

    model.variables.add(
        names=['s_' + str(t) for t in range(horizon)],
        types=[model.variables.type.continuous] * horizon,
        lb=[0.0] * horizon
        # obj=params.price_schema
    )

    for t in range(len(vars[0])):
        indices = ['s_' + str(t)]
        values = [-1.0]
        for k in range(len(vars)):
            indices.append(vars[k][t])
            values.append(1000.0)

        model.linear_constraints.add(
            lin_expr=[
                cplex.SparsePair(
                    ind=indices,
                    val=values
                )],
            senses=['E'],
            rhs=[0.0]
        )

    model.parameters.solutiontarget = 2
    # model.objective.set_quadratic_coefficients(quad_cons)
    model.objective.set_sense(model.objective.sense.minimize)
    print('num variables: ', model.variables.get_num())
    quad = []
    for k in range(model.variables.get_num() - horizon):
        quad.append([[k], [0.0]])
    # adding quadratic objective
    price = params.price_schema
    for t in range(horizon):
        quad.append([[len(quad)], [price[t]]])  # [1.0]])
    print(quad)
    model.objective.set_quadratic(quad)
    model.write('problem.lp')
    print('lin ', model.objective.get_linear())
    print('quad', model.objective.get_quadratic())

    model.solve()

    solution = model.solution

    print("Solution status: ", solution.get_status())
    print("Objective value: ", solution.get_objective_value())

    '''
    scheduled = numpy.asarray([0] * horizon)  # this is a list of number of on devices for each timestep
    for i in range(num_devs):
        d_sched = numpy.asarray(devs[i].get_schedule(solution))
        for j in range(horizon):
            if d_sched[j] > 0.0001:
                d_sched[j] = 1
            else:
                d_sched[j] = 0
            scheduled[j] += d_sched[j]
            if d_sched[j] == -1:
                print('ERROR: negative number detected in device schedule.')
    '''
    schedule = ''
    for i in range(len(devices)):
        schedule += devices[i].get_info()
        schedule += devices[i].get_phase_sched(solution)

    power_sched = []
    print('power usage:')
    for t in range(len(vars[0])):
        print(round(solution.get_values('s_' + str(t)), 2), end='\t')
        power_sched.append(round(solution.get_values('s_' + str(t)), 2))
    print()
    print()
    # print('sum:', sum(power_sched))

    # TODO: find out if there is a way to return the current solution and different intervals 8_31_17
    '''
    s = ''
    for i in range(horizon):
        s += str(power_sched[i]) + '\t'
        s += str(round(power_sched[i] * price[i], 2))

        if i < horizon - 1:
            s += '\t'
        else:
            s += '\n'
    '''

    return schedule

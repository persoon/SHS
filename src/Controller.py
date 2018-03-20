import src.Parameters
import src.Reader
import src.Solver as Solver
import src.Utilities as util
from src.gauss import UserExpectation as user
from src.bayes_opt.bayesian_optimization import BayesianOptimization as bayesian


params = src.Parameters.Parameters()

horizon = params.horizon
rt2 = params.rules[0].time2

pbounds = {'t': (rt2, horizon-1)}
print(pbounds)
solver = Solver.Solver(params=params)
usr = user(rt2, horizon-1)

def target_function(t):
    params.rules[0].time2 = int(t)  # Todo: figure out how to make t always try integers
    solver.reset(params=params)
    solution = solver.solve()
    return round(usr.getValue(x=int(t)) - solution.get_values('objPrice'), 2) + 690


def execute():
    dictionary = src.Reader.Reader().get_dictionary()
    devices = [
        dictionary.get_device(device_type='washer', device_name='GE_WSM2420D3WW', mode_name="regular_w", dID=0),
    ]

    params.devices = devices

    solution = solver.solve()

    reg_price = round(solution.get_values('objPrice'), 2)

    pref_price = [reg_price]
    rule = params.rules[0]
    print(params.rules[0].time2, ':', reg_price)

    span = params.horizon - (rt2+1)
    freq = 25  # distance between samples

    num_tries = int(span/freq)
    Ydata = []
    Xdata = []

    # rule, horizon
    bay = bayesian(f=target_function, pbounds=pbounds)
    bay.maximize()

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


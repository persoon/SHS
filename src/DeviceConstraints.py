# 12/8/2017
#
# Picks what type of constraints specified device uses and adds variables to the model
# TODO: add device to appropriate state property lists

# problem with model in pycharm making it so I can't see correct options when I type 'self.model.'
# TODO: fix self.model so I don't have to do this:
import src.Model
import src.ActionDuration
import src.Action

class DeviceConstraints:

    def __init__(self, model, params, devices):
        self.model = model
        self.mode_cons = []
        self.params = params
        self.horizon = params.horizon
        self.vars = []
        for t in range(self.horizon):
            self.vars.append([])

        for d in devices:
            dvars = self.add_device_vars(device=d)
            for h in range(self.horizon):
                self.vars[h].append(dvars[h])
        print('vars:', self.vars)
        for h in range(self.horizon):
            print(str(h), end=": ")
            for i in range(len(self.vars[h])):
                print(self.vars[h][i], end=", ")
            print()

    '''
    generates the variables for each device
    '''
    def add_device_vars(self, device):
        name = device.name

        max_kWh = 0.0
        phases = device.phases
        mode = device.mode

        for i in range(len(mode)):
            phases[i] = int(mode[i]['duration']), float(mode[i]['kWh']), name + '_p' + str(i)
            max_kWh = max(max_kWh, float(mode[i]['kWh']))

        # creating a variable for each timestep from 0 to horizon-1
        # this is our device schedule -- used later to aggregate power consumption per timestep
        self.model.variables.add(
            names=[name + '_' + str(k) for k in range(self.horizon)],
            types=[self.model.variables.type.continuous] * self.horizon,
            lb=[0.0] * self.horizon,
            ub=[max_kWh * 1.05] * self.horizon
            # obj=params.price_schema
        )

        dvars = []
        for k in range(self.horizon):
            dvars.append(name + '_' + str(k))

        # need to find out what type of constraints to generate (e.g. action w/ duration)
        mode_type = device.mode_type
        device.phases = phases
        if mode_type == 'HVAC':  # TODO: extend this to all Action modeled devices such as electric car
            action_model = src.Action.Action(model=self.model, params=self.params, name=name, actions=phases)
            action_model.setup_actions()
            self.mode_cons.append((device, action_model))
        else:
            self.mode_cons.append((device, src.ActionDuration.ActionDuration(model=self.model, params=self.params, name=name, phases=phases)))
        print(phases)
        return dvars



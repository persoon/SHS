# 12/5/2017
#
# Generates Cplex model and adds all of the constraints
# Generate schedule kWh usage variables --- this one might be moved later
# returns solution

import src.Model
import src.HVAC
# import src.RuleConstraints
import src.DeviceConstraints as DCons
import src.RuleConstraints as RCons
import cplex


import src.Parameters
import src.Reader

class Solver:

    def __init__(self, params):
        self.params = params
        horizon = params.horizon
        self.rules = params.rules
        self.devices = params.devices  # todo: place devices in params for use here

        self.model = src.Model.Model().model
        dcons = DCons.DeviceConstraints(model=self.model, params=self.params, devices=self.devices)
        RCons.RuleConstraints(model=self.model, mode_cons=dcons.mode_cons, rules=self.rules)

        self.model.variables.add(
            names=['s_' + str(t) for t in range(horizon)],
            types=[self.model.variables.type.continuous] * horizon,
            lb=[0.0] * horizon
            # obj=params.price_schema
        )

        vars = dcons.vars
        val = []
        for v in range(len(vars[0])):
            val.append(1000.0)

        values = [-1.0]
        values.extend(val)
        for t in range(horizon):
            indices = ['s_' + str(t)]

            indices.extend(vars[t])
            self.model.linear_constraints.add(
                lin_expr=[
                    cplex.SparsePair(
                        ind=indices,
                        val=values
                    )
                ],
                senses=['E'],
                rhs=[0.0]
            )

        self.model.parameters.solutiontarget = 2
        # model.objective.set_quadratic_coefficients(quad_cons)
        self.model.objective.set_sense(self.model.objective.sense.minimize)
        print('num variables: ', self.model.variables.get_num())
        quad = []
        for k in range(self.model.variables.get_num() - horizon):
            quad.append([[k], [0.0]])
        # adding quadratic objective
        price = params.price_schema
        for t in range(horizon):
            quad.append([[len(quad)], [price[t]]])  # [1.0]])
        print(quad)
        self.model.objective.set_quadratic(quad)
        self.model.write('problem.lp')
        self.model.solve()

        solution = self.model.solution

        print("Solution status: ", solution.get_status())
        print("Objective value: ", solution.get_objective_value())

        for t in range(horizon):
            print(solution.get_values('s_' + str(t)), end="\t")
        print()

        for d in range(len(vars[0])):
            print(vars[0][d].split("_")[0])
            for t in range(horizon):
                print(solution.get_values(vars[t][d]), end="\t")
            print()

        for i in range(24):
            print(solution.get_values('T_z' + str(i)), end="\t")

dictionary = src.Reader.Reader().get_dictionary()
devices = []
devices.append(dictionary.get_device(device_type='HVAC', mode_name='cool', dID=0))
print(devices[0].mode)
# devices.append(dictionary.get_device(device_type='washer', device_name='GE_WSM2420D3WW', mode_name="regular", dID=1))
# devices.append(dictionary.get_device(device_type='oven', device_name='Kenmore_790', mode_name="bake", dID=2))
params = src.Parameters.Parameters()
params.devices = devices
Solver(params=params)

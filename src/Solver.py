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
        self.horizon = params.horizon
        self.rules = params.rules
        self.devices = params.devices  # todo: place devices in params for use here

        self.model = src.Model.Model().model
        dcons = DCons.DeviceConstraints(model=self.model, params=self.params, devices=self.devices)
        RCons.RuleConstraints(model=self.model, mode_cons=dcons.mode_cons, rules=self.rules)

        self.model.variables.add(
            names=['objPrice'],
            types=[self.model.variables.type.continuous],
            lb=[0.0]
        )

        self.model.variables.add(
            names=['s_' + str(t) for t in range(self.horizon)],
            types=[self.model.variables.type.continuous] * self.horizon,
            lb=[0.0] * self.horizon,
            obj=params.price_schema
        )

        self.vars = dcons.vars
        val = []
        for v in range(len(self.vars[0])):
            val.append(1.0)

        values = [-1.0]
        values.extend(val)
        for t in range(self.horizon):
            indices = ['s_' + str(t)]

            indices.extend(self.vars[t])
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

        # obj price for testing
        _ind = ['objPrice']
        _val = [-1.0]
        for t in range(self.horizon):
            _ind.append('s_' + str(t))
            _val.append(params.price_schema[t])
        self.model.linear_constraints.add(
            lin_expr=[
                cplex.SparsePair(
                    ind=_ind,
                    val=_val
                )
            ],
            senses=['E'],
            rhs=[0.0]
        )

        self.model.parameters.solutiontarget = 2
        # model.objective.set_quadratic_coefficients(quad_cons)
        self.model.objective.set_sense(self.model.objective.sense.minimize)
        print('Number of Variables: ', self.model.variables.get_num())
        quad = []
        for k in range(self.model.variables.get_num() - self.horizon):
            quad.append([[k], [0.0]])
        # adding quadratic objective
        price = params.price_schema
        for t in range(self.horizon):
            quad.append([[len(quad)], [1.0]]) # [price[t]]])

        # self.model.objective.set_quadratic(quad)
        self.model.write('problem.lp')

    def solve(self):
        self.model.solve()

        solution = self.model.solution

        print("Solution status: ", solution.get_status())
        print("Objective value: ", solution.get_objective_value())

        for d in range(len(self.vars[0])):
            print(self.vars[0][d].split("_")[0])
            for t in range(self.horizon):
                print(round(solution.get_values(self.vars[t][d]), 2), end="\t")
            print()

        '''
        print('================= Indoor Temperature ==================')
        for i in range(self.horizon):
            print(round(solution.get_values('T_z' + str(i)), 1), end="  ")
        print()
        '''
        print('++++++++++++++++++++++ Schedule ++++++++++++++++++++++')
        for t in range(self.horizon):
            print(" "+str(round(solution.get_values('s_' + str(t)), 1)),end="  ")
        print()
        print('++++++++++++++++++++++++++++++++++++++++++++++++++++++')
        print()
        print('objPrice: ', round(solution.get_values('objPrice')))
        print('objPower: ', round(solution.get_objective_value()) - round(solution.get_values('objPrice')))



        for T in range(16, 23):
            print('Solution d0_t'+str(T)+':', round(solution.get_values('d0_t'+str(T)), 2))


        return solution
'''
dictionary = src.Reader.Reader().get_dictionary()
devices = []
devices.append(dictionary.get_device(device_type='HVAC', mode_name='cool', dID=0))
#print(devices[0].mode)
devices.append(dictionary.get_device(device_type='washer', device_name='GE_WSM2420D3WW', mode_name="regular", dID=1))
devices.append(dictionary.get_device(device_type='oven', device_name='Kenmore_790', mode_name="bake", dID=2))
params = src.Parameters.Parameters()
params.devices = devices
Solver(params=params)
'''

# 12/5/2017
#
# Generates Cplex model and adds all of the constraints
# Generate schedule kWh usage variables --- this one might be moved later
# returns solution

import src.Model
import src.HVAC
import src.DeviceConstraints as DCons
import src.RuleConstraints as RCons
import cplex
import src.Parameters
import src.Reader
import src.Utilities as util

class Solver:

    def __init__(self, params):
        self.params = params
        self.horizon = params.horizon
        self.rules = params.rules
        self.devices = params.devices

        self.model = src.Model.Model().model
        dcons = DCons.DeviceConstraints(model=self.model, params=self.params, devices=self.devices)
        rcons = RCons.RuleConstraints(model=self.model, mode_cons=dcons.mode_cons, rules=self.rules)
        self.rule_pref = rcons.rule_pref

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
        # print('Number of Variables: ', self.model.variables.get_num())
        quad = []
        for k in range(self.model.variables.get_num() - self.horizon):
            quad.append([[k], [0.0]])
        # adding quadratic objective
        price = params.price_schema
        for t in range(self.horizon):
            quad.append([[len(quad)], [1.0]]) # [price[t]]])

        # self.model.objective.set_quadratic(quad)  # <---- add power objective
        # self.model.write('problem.lp')

    # resets the solver, preparing it for a new solution
    def reset(self, params):
        self.model = src.Model.Model().reset_solver()
        self.params = params
        self.horizon = params.horizon
        self.rules = params.rules
        self.devices = params.devices

        dcons = DCons.DeviceConstraints(model=self.model, params=self.params, devices=self.devices)
        rcons = RCons.RuleConstraints(model=self.model, mode_cons=dcons.mode_cons, rules=self.rules)
        self.rule_pref = rcons.rule_pref

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
        # print('Number of Variables: ', self.model.variables.get_num())
        quad = []
        for k in range(self.model.variables.get_num() - self.horizon):
            quad.append([[k], [0.0]])
        # adding quadratic objective
        price = params.price_schema
        for t in range(self.horizon):
            quad.append([[len(quad)], [1.0]])  # [price[t]]])

        # self.model.objective.set_quadratic(quad)  # <---- add power objective
        # self.model.write('problem.lp')

    def solve(self):
        self.model.solve()

        solution = self.model.solution

        # print("Solution status: ", solution.get_status())
        # print("Objective value: ", solution.get_objective_value())
        ''' print device kWh:
        for d in range(len(self.vars[0])):
            print(self.vars[0][d].split("_")[0])
            for t in range(self.horizon):
                print(round(solution.get_values(self.vars[t][d]), 2), end="\t")
            print()
        '''
        '''
        print('================= Indoor Temperature ==================')
        for i in range(self.horizon):
            print(round(solution.get_values('T_z' + str(i)), 1), end="  ")
        print()
        '''
        '''
        print('++++++++++++++++++++++ Schedule ++++++++++++++++++++++')
        for t in range(self.horizon):
            print(" "+str(round(solution.get_values('s_' + str(t)), 1)),end="  ")
        print()
        print('++++++++++++++++++++++++++++++++++++++++++++++++++++++')
        print()
        print('objPrice: ', round(solution.get_values('objPrice')))
        print('objPower: ', round(solution.get_objective_value()) - round(solution.get_values('objPrice')))
        '''
        return solution


    # TODO: put this code inside rule constraints and make them loadable with rules.txt
    # Constraint: device1 must finish before device2 starts
    # device1.phase_n + d1.p_n.duration < device2.phase_1
    def dependancy(self, device1, device2):
        d1pn = device1.phases[len(device1.phases)-1]
        d2p1 = device2.phases[0]
        print(d1pn)
        print(d2p1)
        self.model.linear_constraints.add(
            lin_expr=[cplex.SparsePair(ind=[d2p1[2], d1pn[2]], val=[1.0, -1.0])],
            senses=['G'],
            rhs=[d1pn[0]]
        )

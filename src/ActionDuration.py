import cplex
from cplex.exceptions import CplexError


class ActionDuration:

    def __init__(self, model, params, name, phases):
        self.params = params
        self.model = model
        self.phases = phases
        self.name = name
        self.var_names = [[]]

    def add_rule_pref(self, rule):
        horizon = self.params.horizon
        duration = 0
        DURATION = 0
        prev_duration = 0

        max_kWh = 0
        for i in range(len(self.phases)):
            max_kWh = max(max_kWh, float(self.phases[i][1]))


        for i in range(len(self.phases)):
            duration += self.phases[i][0]

        DURATION = duration

        for T in range(rule.time2, horizon-1):
            duration = DURATION
            prev_duration = 0
            print(self.phases)
            print(T)
            temp = []
            print(self.phases[0][2], rule.time1, T - duration, self.phases[0][0], self.phases[0][1])
            self.create_phase(self.phases[0][2], rule.time1, T - duration, self.phases[0][0], self.phases[0][1])
            temp2 = (self.phases[0][0], self.phases[0][1], self.name+'_t'+str(T+1)+'_p0')
            temp.append(temp2)
            for j in range(1, len(self.phases)):
                duration -= self.phases[j-1][0]
                prev_duration += self.phases[j-1][0]
                print(self.phases[j][2], rule.time1 + prev_duration, T - duration, self.phases[j][0], self.phases[j][1])
                self.create_phase(self.phases[j][2], rule.time1 + prev_duration, T - duration, self.phases[j][0], self.phases[j][1])
                self.connect_phases(self.phases[j-1][2], self.phases[j][2], self.phases[j][0])
                temp2 = (self.phases[j][0], self.phases[j][1], self.name+'_t'+str(T+1)+'_p'+str(j))
                temp.append(temp2)
            self.phases = temp
            self.name = self.name.split('_')[0] + '_t' + str(T)

            self.model.variables.add(
                names=[self.name + '_' + str(k) for k in range(horizon)],
                types=[self.model.variables.type.continuous] * horizon,
                lb=[0.0] * horizon,
                ub=[max_kWh * 1.05] * horizon
                # obj=params.price_schema
            )

            # the cost of schedule T = X
            self.model.variables.add(
                names=[self.name],
                types=[self.model.variables.type.continuous],
                lb=[0.0],
                obj=[1.0]
            )

            _ind = [self.name]
            _val = [-1.0]

            _ind.extend([self.name + '_' + str(k) for k in range(horizon)])
            _val.extend(self.params.price_schema)

            self.model.linear_constraints.add(
                lin_expr=[
                    cplex.SparsePair(
                        ind=_ind,
                        val=_val
                    )
                ],
                senses=['E'],
                rhs=[1.0]
            )

    # TODO: create 'setup_actions()' which creates all of the phases and rules for when each phase can be run 1/26/2018
    # TODO: (cont'd) 'add_rule_constraints()' sets the req. that p_1 doesnt start before time1 & p_n ends before time2
    def add_rule_constraints(self, rule):
        time1 = rule.time1
        time2 = rule.time2

        duration = 0
        prev_duration = 0

        for i in range(len(self.phases)):
            duration += self.phases[i][0]
        print('duration', duration)
        self.create_phase(self.phases[0][2], time1, time2 - duration, self.phases[0][0], self.phases[0][1])
        self.var_names[0].append(self.phases[0][2])

        for i in range(1, len(self.phases)):
            duration -= self.phases[i-1][0]
            prev_duration += self.phases[i-1][0]
            self.create_phase(self.phases[i][2], time1 + prev_duration, time2 - duration, self.phases[i][0], self.phases[i][1])
            self.var_names[0].append(self.phases[i][2])
            self.connect_phases(self.phases[i-1][2], self.phases[i][2], self.phases[i][0])

        return self.var_names

    def create_phase(self, pname, s_time, f_time, duration, kWh):
        price_schema = self.params.price_schema

        price = 0
        for i in range(s_time, s_time + duration):
            price += price_schema[i]

        p_array = [None] * (f_time - s_time)
        p_array[0] = price
        # print('\tst_var:', pname, '\ts_time:', s_time, '\tf_time:', f_time)
        for i in range(s_time, f_time):
            price += price_schema[i]
            price -= price_schema[i-1 - duration]  # should this have -1?
            p_array[i - s_time] = price * kWh * 100

        # add start time variable
        self.model.variables.add(
            names=[pname],
            types=[self.model.variables.type.integer]
        )

        # add variables for first phase
        self.model.variables.add(
            names=[pname + '_' + str(k) for k in range(0, self.params.horizon)],
            types=[self.model.variables.type.binary] * self.params.horizon,
            # obj=p_array
        )
        # print('s_time', s_time)
        # print('f_time', f_time)
        # print('p_array', p_array)
        self.var_names.append([])
        for k in range(s_time, f_time):
            self.var_names[len(self.var_names)-1].append((pname + '_' + str(k), k, kWh))

        self.model.linear_constraints.add(
            lin_expr=[
                cplex.SparsePair(
                    ind=[pname + '_' + str(k) for k in range(s_time, f_time)],
                    val=[1.0] * (f_time - s_time)
                )
            ],
            senses=['E'],
            rhs=[1.0]
        )

        # add constraint to set start time 1
        for k in range(s_time, f_time):
            self.model.indicator_constraints.add(
                indvar=pname + '_' + str(k),
                complemented=0,
                lin_expr=cplex.SparsePair(ind=[pname], val=[1.0]),
                sense='E',
                rhs=k
            )

        for k in range(s_time, f_time):
            for j in range(k, k+duration):
                self.model.indicator_constraints.add(
                    indvar=pname + '_' + str(k),
                    complemented=0,
                    lin_expr=cplex.SparsePair(
                        ind=[self.name + '_' + str(j)],
                        val=[1.0]
                    ),
                    sense='E',
                    rhs=kWh
                )

    def connect_phases(self, pname1, pname2, duration):
        # add constraint making start time 2 > start time 1 + duration1
        self.model.linear_constraints.add(
            lin_expr=[cplex.SparsePair(ind=[pname2, pname1], val=[1.0, -1.0])],
            senses=['G'],
            rhs=[duration]
        )
import src.Parameters as Parameters
import cplex
from cplex.exceptions import CplexError


class Window:

    def __init__(self, phases):
        self.parameters = Parameters.Parameters()
        self.model = self.parameters.model
        self.phases = phases

    def add_rule_constraints(self, rule):
        goal = rule.goal
        time1 = rule.time1
        time2 = rule.time2 + 1
        self.var_names = [[]]

        print('time1', time1, 'time2', time2)

        duration = 0
        prev_duration = 0

        for i in range(len(self.phases)):
            duration += self.phases[i][0]

        self.create_phase(self.phases[0][2]+str(1), time1, time2 - duration, self.phases[0][0], self.phases[0][1])
        self.var_names[0].append(self.phases[0][2]+str(1))

        for i in range(1, len(self.phases)):
            duration -= self.phases[i-1][0]
            prev_duration += self.phases[i-1][0]
            self.create_phase(self.phases[i][2]+str(1), time1 + prev_duration, time2 - duration, self.phases[i][0], self.phases[i][1])
            self.var_names[0].append(self.phases[i][2] + str(1))
            self.connect_phases(self.phases[i-1][2]+ str(1), self.phases[i][2]+ str(1), self.phases[i][0])

        return self.var_names

    def create_phase(self, st_var, s_time, f_time, duration, kWh):
        price_schema = self.parameters.price_schema

        price = 0
        for i in range(s_time, s_time + duration):
            price += price_schema[i]

        p_array = [None] * (f_time - s_time)
        p_array[0] = price
        for i in range(s_time, f_time):
            price += price_schema[i]
            price -= price_schema[i-1 - duration]  # should this have -1?
            p_array[i - s_time] = price * kWh

        # add start time variable
        self.model.variables.add(
            names=[st_var],
            types=[self.model.variables.type.integer]
        )

        # add variables for first phase
        self.model.variables.add(
            names=[st_var + '_' + str(k) for k in range(s_time, f_time)],
            types=[self.model.variables.type.integer] * (f_time - s_time),
            obj=p_array
        )
        self.var_names.append([])
        for k in range(s_time, f_time):
            self.var_names[len(self.var_names)-1].append((st_var + '_' + str(k), kWh))

        self.model.linear_constraints.add(
            lin_expr=[
                cplex.SparsePair(
                    ind=[st_var + '_' + str(k) for k in range(s_time, f_time)],
                    val=[1.0] * (f_time - s_time)
                )],
            rhs=[1.0],
            senses=['E']
        )

        # add constraint to set start time 1
        for k in range(s_time, f_time):
            self.model.indicator_constraints.add(
                indvar=st_var + '_' + str(k),
                complemented=0,
                rhs=k,
                sense='E',
                lin_expr=cplex.SparsePair(ind=[st_var], val=[1.0])
            )

    def connect_phases(self, st_var1, st_var2, duration):
        # add constraint making start time 2 > start time 1 + duration1
        self.model.linear_constraints.add(
            lin_expr=[cplex.SparsePair(ind=[st_var2, st_var1], val=[1.0, -1.0])],
            senses=['G'],
            rhs=[duration]
        )
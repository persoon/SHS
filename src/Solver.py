# 6_22_2017 edited 7_7_2017

import src.Rule
import src.RuleParser
import src.Parameters as parameters
import cplex
from cplex.exceptions import CplexError

# TODO: idea: make heater take in an array of predicted heats --- can take into account outside weather forecast / oven

model = src.Parameters.Parameters().model  # cplex.Cplex()


# input: the variables, and power consumption created from applying the price constraint for use in the power objective
# variables structure:
#   integer vars    [ ...................... ]
#   phase vars      [ [wash1_245, 245, 0.007], [wash1_246, 246, 0.007], [wash1_247, 247, 0.007], ... [wash1_1045, 1045, 0.007] ... ]
#                   .
#                   .
#                   .
#                   [ [rinse1_247, 247, 0.007], ................................................................ ]
# each phase variable has 'name', timestep, kWh
def add_peak_constraint(variables):
    arr_index = [0] * (len(variables) - 1)
    time_index = src.Parameters.Parameters().horizon+1

    # 1 -- look for the first timestep among the variables
    for i in range(1, len(variables)):
        if time_index > variables[i][0][1]:
            time_index = variables[i][0][1]

    print('first time: ', time_index)

    curr_vars = []

    for i in range(len(variables)):
        if variables[i][arr_index[i]][1] == time_index:
            curr_vars.append(variables[i][arr_index])
            arr_index[i] += 1  # increment index

    print('time: ', time_index, 'vars: ', curr_vars)

    model.variables.add(
        names=[st_var + '_' + str(k) for k in range(s_time, f_time)],
        types=[self.model.variables.type.integer] * (f_time - s_time),
        obj=p_array
    )
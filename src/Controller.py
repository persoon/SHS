import src.Parameters
import src.RuleParser as rp
import src.Reader
import cplex
from cplex.exceptions import CplexError

def execute():

    dictionary = src.Reader.Reader().get_dictionary()
    device = dictionary.get_device(type='washer', name='GE_WSM2420D3WW')

    # adding the device constraints and price objective:
    variables = device.add_constraints(src.Parameters.Parameters().rules[0])
    # sending the variables through the power objective:


    model = src.Parameters.Parameters().model
    model.objective.set_sense(model.objective.sense.minimize)
    model.solve()
    try:
        solution = model.solution
        print("Solution status: ", solution.get_status())
        print("Objective value: ", solution.get_objective_value())

        for j in range(len(variables[0])):
            print(variables[0][j], end='\t')
        print()
        for j in range(len(variables[0])):
            print(abs(solution.get_values(variables[0][j])), end='\t\t\t')
        print()
        print()

        for i in range(1, len(variables)):
            for j in range(len(variables[i])):
                print(variables[i][j][0], end='\t\t\t')
            print()
            for j in range(len(variables[i])):
                print('[', abs(solution.get_values(variables[i][j][0])), ',', variables[i][j][1], ']', end='\t\t')
            print()
            print()
    except CplexError as exc:
        print(exc)


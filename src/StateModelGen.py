import src.Parameters as Parameters
import src.HVAC as HVAC
import cplex

# State Property Model Generator
# input: rules affecting state properties IN ROOM
# TODO: add support for multiple rooms
class StateModelGen:
    def __init__(self):
        self.HVAC = HVAC.HVAC

        # setting up air temperature model --- this must happen after rules are loaded in
        self.HVAC.setup()
        # Heat loss variables
        #  scheduled devices
model = Parameters.Parameters.model

model.variables.add(
    names=['dev1_' + str(i) for i in range(0, Parameters.Parameters.horizon)],
    types=[model.variables.type.binary] * Parameters.Parameters.horizon
)

model.variables.add(
    names=['btu' + str(i) for i in range(0, Parameters.Parameters.horizon)],
    types=[model.variables.type.continuous] * Parameters.Parameters.horizon,
    ub=[0] * Parameters.Parameters.horizon,
    lb=[-21500] * Parameters.Parameters.horizon
)

HVAC = HVAC.HVAC('temp', ['btu'])


for i in range(0, Parameters.Parameters.horizon):
    model.indicator_constraints.add(
        indvar='dev1_' + str(i),
        complemented=0,
        lin_expr=cplex.SparsePair(ind=['btu' + str(i)], val=[1.0]),
        sense='E',
        rhs=-21500
    )

model.parameters.solutiontarget = 2
model.objective.set_sense(model.objective.sense.minimize)
model.write('HVAC.lp')
model.solve()
solution = model.solution

for i in range(0, Parameters.Parameters.horizon):
    print(round(solution.get_values('T_z'+str(i)), 2), end='\t')
print()
print()
for i in range(0, Parameters.Parameters.horizon):
    print(round(solution.get_values('dev1_'+str(i)), 2), end='\t')
print()
for i in range(0, Parameters.Parameters.horizon):
    print(round(solution.get_values('Q_s'+str(i)), 2), end='\t')
print()
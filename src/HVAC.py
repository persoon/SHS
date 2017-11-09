import src.Parameters as Parameters
import cplex
from cplex.exceptions import CplexError

horizon = 24
model = cplex.Cplex()

model.variables.add(
    names=['e' + str(i) for i in range(horizon)],
    types=[model.variables.type.continuous] * horizon,
    lb=[-cplex.infinity] * horizon,
    ub=[cplex.infinity] * horizon
)

# Boston (Winter..?)
# time vs. energy loss: y = - 65.801*x - 9795.1
c1 = -9795.1
# time vs. temperature: y = -  0.119*x +   43.986

lhs_energy = []

# 65.801*x = -9795.1 - t
mult = 65.801
const = -9795.1
for i in range(horizon):
    lhs_energy.append(
        cplex.SparsePair(
            ind=['e'+str(i)],
            val=[mult]
        )
    )

model.linear_constraints.add(
    lin_expr=lhs_energy,
    senses=['E']*horizon,
    rhs=[const - (t*1440/horizon) for t in range(horizon)],
)

# model.set_problem_type(cplex.Cplex.problem_type.LP)
model.write('HVAC.lp')
model.solve()
solution = model.solution
for i in range(horizon):
    print(round(solution.get_values('e'+str(i)), 0), end='\t')
    print(end='')
print()

for i in range(horizon):
    print(round((const - (i*1440/horizon)) / mult, 0), end='\t')



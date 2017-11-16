import src.Parameters as Parameters
import cplex
from cplex.exceptions import CplexError

horizon = 24


htype = 1
Aw = 0
Ar = 0
Af = 0
Ad = 0
Ao = 0

if htype == 0:
    Aw = 646
    Ar = 546
    Af = 500
    Ad = 18
    Ao = 56
elif htype == 1:
    Aw = 920
    Ar = 1066
    Af = 1000
    Ad = 36
    Ao = 84
elif htype == 2:
    Aw = 1680
    Ar = 2106
    Af = 2000
    Ad = 66
    Ao = 180

# people in house
num_people = 3
# walls
Uw = 0.085
# roof
Ur = 0.069
# floor
Uf = 0.29
# windows & doors
Uo = 0.5
Gt = 75
Fref = 0.88
SC = 0.87

# ventilation stuff
rho = 0.075
vdot = 20 * num_people
mdot = 60 * vdot * 0.075
hz = 26.93  # inside enthalpy --- we keep this static, does technically change a bit based on above factors

# houston summer:
T_a = [77.0, 77.0, 77.0, 77.0, 75.2, 74.8, 75.6, 77.0, 82.4, 84.2, 86.0, 86.0, 89.6, 91.4, 93.2, 91.4, 89.6, 89.6, 86.0, 86.0, 82.4, 82.4, 80.6, 78.8]
dp = [73.4, 71.6, 71.6, 71.6, 71.6, 71.6, 73.4, 71.6, 71.6, 71.6, 71.6, 69.8, 68.0, 66.2, 68.0, 68.0, 68.0, 66.2, 69.8, 71.6, 73.4, 73.4, 73.4, 73.4]
dni = [0, 0, 0, 0, 0, 0, 7, 218, 260, 467, 448, 103, 83, 53, 1, 380, 501, 277, 113, 0, 0, 0, 0, 0]

m = 475.0
if htype == 0:  # small
    m *= 5
elif htype == 1:  # medium
    m *= 10
else:  # htype == 2: large
    m *= 15
cp = 0.25

def get_enthalpy(location, season, dp):
    if location == 'houston':
        if season == 'winter':  # 1/1/2010
            return 0.4216 * dp + 2.309
        else:  # season == 'summer': 6/1/2010
            return 0.5328 * dp + 0.7110
    elif location == 'chicago':
        if season == 'winter':
            return 0.2873 * dp + 3.481
        else:
            return 0.5658 * dp - 3.915
    else:  # location == 'Boston':
        if season == 'winter':
            return 0.2711 * dp + 4.584
        else:  # <-- this one lined up the least well
            return 0.2196 * dp + 16.16

V = []
for i in range(0, horizon):
    ha = get_enthalpy('houston', 'summer', dp[i])
    V.append(mdot * (ha - hz))

model = cplex.Cplex()

# Adding variables ------------------------------------------------
# Indoor temperature variables
model.variables.add(
    names=['T_z' + str(i) for i in range(0, horizon)],
    ub=[200.0]*horizon,
    lb=[-200.0]*horizon,
    obj=[1.0]*horizon
)
model.variables.add(
    names=['delta' + str(i) for i in range(1, horizon)],
    ub=[100.0]*(horizon-1),
    lb=[-100.0]*(horizon-1)
)
# Heat loss variables
#  scheduled devices
model.variables.add(
    names=['s' + str(i) for i in range(0, horizon)],
    types=[model.variables.type.binary] * horizon
)
model.variables.add(
    names=['Q_s' + str(i) for i in range(0, horizon)],
    ub=[0.0] * horizon,
    lb=[-21500.0] * horizon
)

#  total
model.variables.add(
    names=['Q_total' + str(i) for i in range(0,horizon)],
    ub=[1000000.0]*horizon,
    lb=[-1000000.0]*horizon
)
#  walls
model.variables.add(
    names=['Q_w' + str(i) for i in range(0, horizon)],
    ub=[500000.0]*horizon,
    lb=[-500000.0]*horizon
)
#  roof
model.variables.add(
    names=['Q_r' + str(i) for i in range(0, horizon)],
    ub=[500000.0]*horizon,
    lb=[-500000.0]*horizon
)
#  floor
model.variables.add(
    names=['Q_f' + str(i) for i in range(0, horizon)],
    ub=[500000.0]*horizon,
    lb=[-500000.0]*horizon
)
#  door
'''
model.variables.add(
    names=['Q_d' + str(i) for i in range(0, horizon)]
)
'''
#  windows
model.variables.add(
    names=['Q_o' + str(i) for i in range(0, horizon)],
    ub=[500000.0]*horizon,
    lb=[-500000.0]*horizon
)

# Adding constraints ------------------------------------------------
model.linear_constraints.add(
    lin_expr=[
        cplex.SparsePair(
            ind=['T_z0'],
            val=[1.0]
        )
    ],
    senses=['E'],
    rhs=[70.0],
)

for i in range(0, horizon):
    # walls
    #if i == 0:
    model.linear_constraints.add(
        lin_expr=[
            cplex.SparsePair(
                ind=['Q_w' + str(i), 'T_z' + str(i)],
                val=[1.0/(Aw * Uw), 1.0]
            )
        ],
        senses=['E'],
        rhs=[T_a[i]]
    )
    # roof
    model.linear_constraints.add(
        lin_expr=[
            cplex.SparsePair(
                ind=['Q_r' + str(i), 'T_z' + str(i)],
                val=[1.0 / (Ar * Ur), 1.0]
            )
        ],
        senses=['E'],
        rhs=[T_a[i]]
    )
    # floor
    model.linear_constraints.add(
        lin_expr=[
            cplex.SparsePair(
                ind=['Q_f' + str(i), 'T_z' + str(i)],
                val=[1.0 / (Af * Uf), 1.0]
            )
        ],
        senses=['E'],
        rhs=[T_a[i]]
    )
    # doors & windows --- for now they are calculated together
    model.linear_constraints.add(
        lin_expr=[
            cplex.SparsePair(
                ind=['Q_o' + str(i), 'T_z' + str(i)],
                val=[1.0 / ((Ad+Ao) * Uo), 1.0]
            )
        ],
        senses=['E'],
        rhs=[T_a[i] + ((Gt * Fref * SC)/Uo)]
    )
    # total heat gain
    model.linear_constraints.add(
        lin_expr=[
            cplex.SparsePair(
                ind=['Q_total' + str(i), 'Q_w' + str(i), 'Q_r' + str(i), 'Q_f' + str(i), 'Q_o' + str(i)],
                val=[-1.0, 1.0, 1.0, 1.0, 1.0]
            )
        ],
        senses=['E'],
        rhs=[-1.0 * V[i]]
    )

    if(i < horizon-1):
        # change indoor temperature for next time step
        model.linear_constraints.add(
            lin_expr=[
                cplex.SparsePair(
                    ind=['delta' + str(i + 1), 'Q_total' + str(i), 'Q_s' + str(i)],
                    val=[1.0, - 1.0 / (m * cp), -1.0 / (m * cp)]
                )
            ],
            senses=['E'],
            rhs=[0.0]
        )

        model.linear_constraints.add(
            lin_expr=[
                cplex.SparsePair(
                    ind=['T_z' + str(i + 1), 'T_z' + str(i), 'delta' + str(i + 1)],
                    val=[-1.0, 1.0, 1.0]
                )
            ],
            senses=['E'],
            rhs=[0.0]
        )

    # cooler schedule:
    model.linear_constraints.add(
        lin_expr=[
            cplex.SparsePair(
                ind=['Q_s' + str(i), 's' + str(i)],
                val=[-1.0, -21500]
            )
        ],
        senses=['E'],
        rhs=[0.0]
    )

# passive rules:
model.linear_constraints.add(
    lin_expr=[
        cplex.SparsePair(
            ind=['T_z' + str(i)],
            val=[1.0]
        ) for i in range(1, horizon)
    ],
    senses=['G']*(horizon-1),
    rhs=[50.0]*(horizon-1)
)
model.linear_constraints.add(
    lin_expr=[
        cplex.SparsePair(
            ind=['T_z' + str(i)],
            val=[1.0]
        ) for i in range(1, horizon)
    ],
    senses=['L']*(horizon-1),
    rhs=[85.0]*(horizon-1)
)
# active rules:
model.linear_constraints.add(
    lin_expr=[
        cplex.SparsePair(
            ind=['T_z' + str(i)],
            val=[1.0]
        ) for i in range(7, 14)
    ],
    senses=['G'] * 7,
    rhs=[65.0] * 7
)

model.parameters.solutiontarget = 2
model.objective.set_sense(model.objective.sense.minimize)
model.write('HVAC.lp')
model.solve()
solution = model.solution

for i in range(0, horizon):
    print(round(solution.get_values('T_z'+str(i)), 2), end='\t')
print()
print()
for i in range(0, horizon):
    print(round(solution.get_values('s'+str(i)), 2), end='\t')
print()
for i in range(0, horizon):
    print(round(solution.get_values('Q_s'+str(i)), 2), end='\t')
print()

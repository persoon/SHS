import src.Parameters as Parameters
import cplex
from cplex.exceptions import CplexError

# TODO: make horizon change dynamically --- right now, it is in 24 steps 1/22/2018
# TODO: add location to beginning of each variable name (so multiple rooms is possible) 1/22/2018
# model for the HVAC of a room --- (assuming 1 room house atm)
# input:
#   rname = room name
#   devices = array of device names for each device affecting temperature
#       example: [oven1, oven2, cooler1]
#           oven1 means there is a BTU schedule: oven1BTU + str(i) for all i in range(horizon)
class HVAC:
    def __init__(self, model, rname, devices):
        self.params = Parameters.Parameters()
        self.model = model
        self.rname = rname
        self.devices = devices
        self.horizon = self.params.horizon
        self.htype = self.params.htype
        self.T_a = self.params.out_temp
        self.dp = self.params.dp
        self.city = self.params.city
        self.season = self.params.season

        self.Aw = 0
        self.Ar = 0
        self.Af = 0
        self.Ad = 0
        self.Ao = 0
        if self.htype == 0:
            self.Aw = 646
            self.Ar = 546
            self.Af = 500
            self.Ad = 18
            self.Ao = 56
        elif self.htype == 1:
            self.Aw = 920
            self.Ar = 1066
            self.Af = 1000
            self.Ad = 36
            self.Ao = 84
        elif self.htype == 2:
            self.Aw = 1680
            self.Ar = 2106
            self.Af = 2000
            self.Ad = 66
            self.Ao = 180

        # people in house
        num_people = 3
        # walls
        self.Uw = 0.085
        # roof
        self.Ur = 0.069
        # floor
        self.Uf = 0.29
        # windows & doors
        self.Uo = 0.5
        self.Gt = 75
        self.Fref = 0.88
        self.SC = 0.87

        # ventilation stuff
        rho = 0.075
        vdot = 20 * num_people
        self.mdot = 60 * vdot * rho
        self.hz = 26.93  # inside enthalpy --- we keep this static, does technically change a bit based on above factors

        self.m = 475.0
        if self.htype == 0:  # small
            self.m *= 5
        elif self.htype == 1:  # medium
            self.m *= 10
        else:  # htype == 2: large
            self.m *= 15
        self.cp = 0.25

        upperBTU = 0.0
        lowerBTU = 0.0
        for d in self.devices:
            mode = d.mode
            max_BTU = 0.0
            min_BTU = 0.0
            for p in range(len(mode)):
                print('p', p)
                if 'air_temp' in mode[p]: # <--- this is to prevent bugs if air_temp left out of an action
                    mode[p]['air_temp'] *= (1440/24)
                    max_BTU = max(max_BTU, mode[p]['air_temp'])
                    min_BTU = min(min_BTU, mode[p]['air_temp'])
            upperBTU += max_BTU
            lowerBTU += min_BTU

        self.upperBTU = upperBTU
        self.lowerBTU = lowerBTU
        print('lower BTU:', self.lowerBTU)
        self.setup()

    # helper function that gets an estimate of the enthalpy using linear regression of data
    def get_enthalpy(self, location, season, dp):
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

    def setup(self):
        horizon = self.horizon
        V = []
        for i in range(0, self.horizon):
            ha = self.get_enthalpy(self.city, self.season, self.dp[i])
            V.append(self.mdot * (ha - self.hz))

        # Adding variables ------------------------------------------------
        # Indoor temperature
        self.model.variables.add(
            names=['T_z' + str(i) for i in range(0, horizon)],
            ub=[200.0]*horizon,
            lb=[-200.0]*horizon,
            # obj=[1.0]*horizon
        )

        #Change in BTU since last timestep
        self.model.variables.add(
            names=['Q_delta' + str(i) for i in range(1, horizon)],
            ub=[100.0]*(horizon-1),
            lb=[-100.0]*(horizon-1)
        )

        self.model.variables.add(
            names=['Q_s' + str(i) for i in range(0, horizon)],
            ub=[self.upperBTU] * horizon,
            lb=[self.lowerBTU] * horizon
        )

        #  total
        self.model.variables.add(
            names=['Q_total' + str(i) for i in range(0,horizon)],
            ub=[1000000.0]*horizon,
            lb=[-1000000.0]*horizon
        )

        #  walls
        self.model.variables.add(
            names=['Q_w' + str(i) for i in range(0, horizon)],
            ub=[500000.0]*horizon,
            lb=[-500000.0]*horizon
        )
        #  roof
        self.model.variables.add(
            names=['Q_r' + str(i) for i in range(0, horizon)],
            ub=[500000.0]*horizon,
            lb=[-500000.0]*horizon
        )
        #  floor
        self.model.variables.add(
            names=['Q_f' + str(i) for i in range(0, horizon)],
            ub=[500000.0]*horizon,
            lb=[-500000.0]*horizon
        )
        #  door --- combining with windows for now (assuming all doors are glass)
        '''
        model.variables.add(
            names=['Q_d' + str(i) for i in range(0, horizon)]
        )
        '''
        #  windows
        self.model.variables.add(
            names=['Q_o' + str(i) for i in range(0, horizon)],
            ub=[500000.0]*horizon,
            lb=[-500000.0]*horizon
        )

        # Adding constraints ------------------------------------------------
        self.model.linear_constraints.add(
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
            self.model.linear_constraints.add(
                lin_expr=[
                    cplex.SparsePair(
                        ind=['Q_w' + str(i), 'T_z' + str(i)],
                        val=[1.0/(self.Aw * self.Uw), 1.0]
                    )
                ],
                senses=['E'],
                rhs=[self.T_a[i]]
            )
            # roof
            self.model.linear_constraints.add(
                lin_expr=[
                    cplex.SparsePair(
                        ind=['Q_r' + str(i), 'T_z' + str(i)],
                        val=[1.0 / (self.Ar * self.Ur), 1.0]
                    )
                ],
                senses=['E'],
                rhs=[self.T_a[i]]
            )
            # floor
            self.model.linear_constraints.add(
                lin_expr=[
                    cplex.SparsePair(
                        ind=['Q_f' + str(i), 'T_z' + str(i)],
                        val=[1.0 / (self.Af * self.Uf), 1.0]
                    )
                ],
                senses=['E'],
                rhs=[self.T_a[i]]
            )
            # doors & windows --- for now they are calculated together
            self.model.linear_constraints.add(
                lin_expr=[
                    cplex.SparsePair(
                        ind=['Q_o' + str(i), 'T_z' + str(i)],
                        val=[1.0 / ((self.Ad+self.Ao) * self.Uo), 1.0]
                    )
                ],
                senses=['E'],
                rhs=[self.T_a[i] + ((self.Gt * self.Fref * self.SC)/self.Uo)]
            )
            # total non-actuator heat gain
            self.model.linear_constraints.add(
                lin_expr=[
                    cplex.SparsePair(
                        ind=['Q_total' + str(i), 'Q_w' + str(i), 'Q_r' + str(i), 'Q_f' + str(i), 'Q_o' + str(i)],
                        val=[-1.0, 1.0, 1.0, 1.0, 1.0]
                    )
                ],
                senses=['E'],
                rhs=[-1.0 * V[i]]
            )

            # adding devices' BTU
            _ind = ['Q_s' + str(i)]
            _val = [-1.0]
            for j in range(len(self.devices)):
                for p in range(len(self.devices[j].phases)):
                    _ind.append(self.devices[j].phases[p][2] + '_' + str(i))
                    _val.append(self.devices[j].mode[p]['air_temp'])

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

            if(i < horizon-1):
                # change indoor temperature for next time step
                self.model.linear_constraints.add(
                    lin_expr=[
                        cplex.SparsePair(
                            ind=['Q_delta' + str(i + 1), 'Q_total' + str(i), 'Q_s' + str(i)],
                            val=[1.0, - 1.0 / (self.m * self.cp), -1.0 / (self.m * self.cp)]
                        )
                    ],
                    senses=['E'],
                    rhs=[0.0]
                )

                self.model.linear_constraints.add(
                    lin_expr=[
                        cplex.SparsePair(
                            ind=['T_z' + str(i + 1), 'T_z' + str(i), 'Q_delta' + str(i + 1)],
                            val=[-1.0, 1.0, 1.0]
                        )
                    ],
                    senses=['E'],
                    rhs=[0.0]
                )



        # todo: move this to rule.txt and RuleConstraints.py 1/22/2018
        # passive rules:
        # indoor temperature >= 50.0
        self.model.linear_constraints.add(
            lin_expr=[
                cplex.SparsePair(
                    ind=['T_z' + str(i)],
                    val=[1.0]
                ) for i in range(1, horizon)
            ],
            senses=['G']*(horizon-1),
            rhs=[50.0]*(horizon-1)
        )

        # indoor temperature <= 85.0
        self.model.linear_constraints.add(
            lin_expr=[
                cplex.SparsePair(
                    ind=['T_z' + str(i)],
                    val=[1.0]
                ) for i in range(1, horizon)
            ],
            senses=['L']*(horizon-1),
            rhs=[85.0]*(horizon-1)
        )

    def add_active_rule(self, rule):

        self.model.linear_constraints.add(
            lin_expr=[
                cplex.SparsePair(
                    ind=['T_z' + str(i)],
                    val=[1.0]
                ) for i in range(rule.time1, rule.time2)
            ],
            senses=[rule.predicate] * (rule.time2 - rule.time1),
            rhs=[rule.goal] * (rule.time2 - rule.time1)
        )

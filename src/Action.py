# 1/16/2018
#
# Each time step, an action is chosen from a list of actions

# for now I am going to assume all durations are the same for all possible actions
# in the future I would like to add a separate model for devices with multiple actions of varying durations
# WIP: untested but pretty much complete 1/16/2018
import cplex


class Action:

    def __init__(self, model, params, name, actions):
        self.params = params
        self.model = model
        self.actions = actions
        self.name = name
        self.var_names = [[]]

    # Sets up actions --- doesn't add rules (some devices e.g. HVAC don't have rules -- used to affect a location)
    def setup_actions(self):
        for a in range(len(self.actions)):
            self.create_action(self.actions[a], 0, self.params.horizon)

        # Only 1 action per timestep
        for k in range(0, self.params.horizon):
            self.model.linear_constraints.add(
                lin_expr=[
                    cplex.SparsePair(
                        ind=[self.actions[a][2]+'_'+str(k) for a in range(len(self.actions))],
                        val=[1.0] * len(self.actions)
                    )
                ],
                senses=['E'],
                rhs=[1.0]
            )

            _ind = [self.name+'_'+str(k)]
            _val = [-1.0]
            for a in range(len(self.actions)):
                _ind.append(self.actions[a][2]+'_'+str(k))
                _val.append(self.actions[a][1])

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



    # Todo: add functionality for multiple rules
    def add_rule_constraints(self, rule):
        s_time = rule.time1
        f_time = rule.time2
        goal = rule.goal
        predicate = rule.predicate

        # Connect Goal to actions -------------------------------------------
        _ind = []
        _val = []
        for k in range(s_time, f_time):
            for a in range(len(self.actions)):
                _ind.append(self.actions[a]['name'] + '_' + k)
                _val.append(self.actions[a]['delta'])

        # Sets the goal
        self.model.linear_constraints.add(
            lin_expr=[
                cplex.SparsePair(
                    ind=_ind,
                    val=_val
                )
            ],
            senses=[predicate],
            rhs=[goal]
        )

        for i in range(0, len(self.actions)):
            self.var_names[0].append(self.actions[i][2])

        return self.var_names

    def create_action(self, action, s_time, f_time):
        aname = action[2]
        print('aname:', aname)
        akWh = action[1] * action[0]
        self.model.variables.add(
            names=[aname],
            types=[cplex.Cplex().variables.type.integer],
            # obj = akWh
        )

        self.model.variables.add(
            names=[aname+'_'+str(k) for k in range(s_time, f_time)],
            types=[cplex.Cplex().variables.type.binary] * (f_time - s_time)
        )

        _ind = [aname]
        _val = [-1.0]

        for k in range(s_time, f_time):
            _ind.append(aname+'_'+str(k))
            _val.append(1.0)

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



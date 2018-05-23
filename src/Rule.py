# 6_21_2017
#
# Simple rule object
# Groups rule information in an object for use in the solver
# Parameters:
#   active      - True if the rule is an active rule, False if passive (a rule that is always on)
#   loc         - Location of the rule
#   sp          - Sensor property the rule affects
#   predicate   - One of: {<, <=, =, >=, >} If the value needs to be larger, smaller, or the same as 'goal'
#   goal        - The goal state
#   prefix      - {'before', 'after', 'at', 'within'}
#   time1       - Time step the rule applies to
#   time2       - Secondary time step used for 'within' rules


class Rule:
    def __init__(self, loc, sp, predicate,
                 prefix, horizon, active=True, goal=None, time1=-1, time2=-1, r_type=None):
        self.active = active
        self.r_type = r_type
        self.location = loc
        self.sp = sp
        self.predicate = predicate  # <=, =, >=
        self.goal = goal
        self.horizon = horizon
        if not active:  # passive rules don't have a time prefix (if they did it would be 'always')
            self.prefix = None
            self.time1 = 0
            self.time2 = horizon
        elif prefix == 'before':
            self.prefix = prefix
            self.time1 = 0
            self.time2 = time1
        elif prefix == 'within':
            self.prefix = prefix
            self.time1 = time1
            self.time2 = time2
        elif prefix == 'after':
            self.prefix = prefix
            self.time1 = time1
            self.time2 = horizon  # NOTE: should be horizon-1 but this allows us to keep before rule exclusive of time2
        elif prefix == 'at':
            self.prefix = prefix
            self.time1 = time1
            self.time2 = time1
        else:
            raise Exception('R1: not a valid time prefix')

    def to_string(self):
        s  = str(self.active) + ' '
        s += (str(self.r_type) + '\t') if self.r_type is not None else ''
        s += self.location + '\t' + self.sp + '\t'
        s += (str(self.predicate) + '\t') if self.predicate is not None else ''
        s += str(self.goal) + '\t' + str(self.prefix) + '\t'
        s += str(self.time1) + '\t' + str(self.time2)
        return s

    def print_rule(self):
        time = -1
        if self.prefix == 'before':
            time = self.time2
        elif self.prefix == 'after':
            time = self.time1
        else:
            print('Have not set up this rule type for print_rule()!')

        print(self.location + '  ' + self.sp + '  ' + str(self.prefix) + '  ' + str(time))

# 6_21_2017
#
# Simple rule object
# Groups rule information in an object for use in the solver
# Parameters:
#   active      - True if the rule is an active rule, False if passive (a rule that is always on)
#   sp          - Sensor property the rule affects
#   predicate   - One of: {<, <=, =, >=, >} If the value needs to be larger, smaller, or the same as 'goal'
#   goal        - The goal state
#   prefix      - {'before', 'after', 'at', 'within'}
#   time1       - Time step the rule applies to
#   time2       - Secondary time step used for 'within' rules

# TODO: add function for switching granularities
# TODO: explain how rules work
# TODO: add location

class Rule:
    def __init__(self, active, sp, predicate,
                 goal, prefix, time1, time2, horizon):
        self.active = active
        self.sp = sp
        self.predicate = predicate
        self.goal = goal
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
            self.time2 = horizon # NOTE: this is one more than it should be but this allows us to keep before rule exclusive of time2
        elif prefix == 'at':
            self.prefix = prefix
            self.time1 = time1
            self.time2 = time1
        else:
            raise Exception('R1: not a valid time prefix')

    def to_string(self):
        print(
            self.active, '\t',
            self.sp, '\t',
            self.predicate, '\t',
            self.goal, '\t',
            self.prefix, '\t',
            self.time1, '\t',
            self.time2
        )
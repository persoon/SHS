import src.Rule
import math
import random
# Stores all of the x and y values for all given rules for easy exportation to CSV


class Oracle:

    def __init__(self):
        self.rules = []
        self.xvals = []
        self.yvals = []

    def add(self, rule, x, y):
        self.rules.append(rule)
        self.xvals.append(x)
        self.yvals.append(y)

    def writeCSV(self, name='test', delim=', ', init_points=3, write24=True):
        if write24 is True:
            f_oracle24 = open(name+'_oracle24.csv', 'w+')

        f_rule = open(name+'_rule.csv', 'w+')
        f_oracle = open(name+'_oracle.csv', 'w+')
        f_init = open(name+'_init.csv', 'w+')

        for r in range(len(self.rules)):  # for each rule
            rule = self.rules[r]
            init = [0]  # init always has the starting value
            num = random.randint(1, len(self.yvals[r]))
            for i in range(init_points-1):
                while num in init:
                    num = random.randint(1, len(self.yvals[r]))

                init.append(num)

            # write the rule, this will be ignored by Tiep's code but is important for my code

            f_rule.write(rule.r_type)
            f_rule.write(delim)
            f_rule.write(rule.location)
            f_rule.write(delim)
            f_rule.write(rule.sp)
            f_rule.write(delim)
            if rule.predicate is not None:
                f_rule.write(rule.predicate)
            else:
                f_rule.write('None')
            f_rule.write(delim)
            if rule.goal is not None:
                f_rule.write(rule.goal)
            else:
                f_rule.write('None')
            f_rule.write(delim)
            f_rule.write(rule.prefix)
            f_rule.write(delim)
            f_rule.write(str(rule.time1))
            f_rule.write(delim)
            f_rule.write(str(rule.time2))
            f_rule.write(delim)
            f_rule.write(str(rule.horizon))
            f_rule.write(delim)

            # write the values of y
            scale_factor = rule.horizon / 24  # for scaling to 24 time steps
            print('scale:', scale_factor)
            for i in range(len(self.yvals[r])):
                if math.isnan(self.yvals[r][i]) is not True:
                    if write24 and i % scale_factor == 0:
                        f_oracle24.write(str(int(self.yvals[r][i])))
                    f_oracle.write(str(int(self.yvals[r][i])))
                    if i in init:
                        f_init.write(str(int(self.yvals[r][i])))
                    else:
                        f_init.write('-1')
                else:
                    print('ERROR: NaN float value detected.')
                    f_oracle.write(str(-1))

                if write24 and i % scale_factor == 0:
                    f_oracle24.write(delim)
                f_oracle.write(delim)
                f_init.write(delim)

            if write24:
                f_oracle24.write('\n')
            f_rule.write('\n')
            f_oracle.write('\n')
            f_init.write('\n')

        if write24:
            f_oracle24.close()
        f_rule.close()
        f_oracle.close()
        f_init.close()

    def readCSV(self, name='test', delim=', '):
        f_rule = open(name + '_rule.csv', 'r')
        f_oracle = open(name + '_oracle.csv', 'r')
        f_init = open(name + '_init.csv', 'r')

        span = []
        values = []
        initial_points = []
        horizon = -1

        # setup rule
        rline = f_rule.readline()
        while rline != '':
            if rline == '\n':  # ignore blank lines
                continue
            sline = rline.split(sep=delim)

            '''
            rule = src.Rule.Rule(
                r_type=sline[0],
                loc=sline[1],
                sp=sline[2],
                predicate=sline[3] if sline[3] != 'None' else None,
                goal=sline[4] if sline[4] != 'None' else None,
                prefix=sline[5],
                time1=int(sline[6]),
                time2=int(sline[7]),
                horizon=int(sline[8])
            )
            '''

            horizon = int(sline[8])
            if sline[5] == 'after':
                span.append((0, int(sline[6])))
            elif sline[5] == 'before':
                span.append((0, int(sline[8]) - int(sline[7]) - 1))
            else:
                print('Error: Unhandled time prefix in Oracle.py')

            rline = f_rule.readline()

        # setup oracle values
        oline = f_oracle.readline()
        while oline != '':
            if oline == '\n':  # ignore blank lines
                continue
            sline = oline.split(sep=delim)

            val = []
            for i in range(len(sline)):
                if sline[i] != '\n':
                    val.append(int(sline[i]))

            values.append(val)

            oline = f_oracle.readline()

        # setup initial values
        iline = f_init.readline()
        while iline != '':
            if iline == '\n':  # ignore blank lines
                continue
            sline = iline.split(sep=delim)

            val = []
            for i in range(len(sline)):
                if sline[i] != '\n':
                    if int(sline[i]) != -1:
                        val.append([i])

            initial_points.append(val)

            iline = f_init.readline()

        return horizon, span, values, initial_points

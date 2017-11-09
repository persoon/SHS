# 6_21_2017
#
# Simple function for parsing CSV rule files. Turns the input into an array of Rule objects
# Parameters:
#   filename - File location containing all of the rules
# Returns:
#   rules - List of all of all rules contained in the file

import csv
import src.Rule as r
from collections import defaultdict

class RuleParser:
    def parse_rules(self, filename):
        rules = []
        with open(filename, 'r') as csvfile:
            reader = csv.reader(csvfile, delimiter='\t')
            file_horizon = int(next(reader)[0])
            for row in reader:
                for i in range(len(row)):
                    if row[i] == '-':
                        row[i] = None
                active = True if int(row[0]) == 1 else False
                r_type = row[1]
                location = row[2]
                sp = row[3]
                predicate = self.lookup_pred(row[4])
                if predicate is None:
                    predicate = row[4]
                goal = int(row[5]) if row[5] is not None else None
                prefix = row[6]
                time1 = int(row[7])
                time2 = 0 if len(row) != 9 else int(row[8])

                rule = r.Rule(
                    active=active,
                    r_type=r_type,
                    loc=location,
                    sp=sp,
                    predicate=predicate,
                    goal=goal,
                    prefix=prefix,
                    time1=time1,
                    time2=time2,
                    horizon=file_horizon
                )
                rules.append(rule)

        return rules, file_horizon

    # todo: We need to either figure out how to represent lt and gt or disallow them from rule creation
    def lookup_pred(self, x):
        dict = {
            'lt': 'L',
            'leq': 'L',
            'eq': 'E',
            'geq': 'G',
            'gt': 'G'
        }
        dict = defaultdict(lambda: None, dict)
        return dict[x]

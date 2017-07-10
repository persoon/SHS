# 6_21_2017
#
# Simple function for parsing CSV rule files. Turns the input into an array of Rule objects
# Parameters:
#   filename - File location containing all of the rules
# Returns:
#   rules - List of all of all rules contained in the file

import csv
import src.Rule as r


def parse_rules(filename):
    rules = []
    file_horizon = None
    with open(filename, 'r') as csvfile:
        reader = csv.reader(csvfile, delimiter='\t')
        file_horizon = int(next(reader)[0])
        for row in reader:
            active = True if int(row[0]) == 1 else False
            sp = row[1]
            predicate = lookup_pred(row[2])
            goal = int(row[3])
            prefix = row[4]
            time1 = int(row[5])
            time2 = row[6] if len(row) == 7 else 0

            rule = r.Rule(
                    active=active,
                    sp=sp,
                    predicate=predicate,
                    goal=goal,
                    prefix=prefix,
                    time1=time1,
                    time2=time2
                )
            rules.append(
                rule
            )

    return rules, file_horizon


# We need to either figure out how to represent lt and gt or disallow them from rule creation
def lookup_pred(x):
    return {
        'lt': 'L',
        'leq': 'L',
        'eq': 'E',
        'geq': 'G',
        'gt': 'G'
    }[x]
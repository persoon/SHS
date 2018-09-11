import src.testGenerator as generate
import src.testRunner as run
import src.writeReport as report

runs_sep = []
runs_mult = []

for i in range(1, 11):
    generate.execute(type='large_rank1', fname='../resources/output/tests/exp7_'+str(i))
    runs_sep.append([run.execute(fname='../resources/output/tests/exp6_'+str(i))])
report.write_file(filename='../resources/output/tests/results8_norm40_sep.txt', runs=runs_sep)

#for i in range(3, 4):
#    runs_mult.append([run.execute2(fname='../resources/output/tests/exp2_' + str(i))])
#report.write_file(filename='../resources/output/tests/results9_norm_mult.txt', runs=runs_mult)



# exp2 == normal  4 rules
# exp3 == random  4 rules
# exp4 ==  rank1  4 rules
# exp5 == randr1  4 rules
# exp6 ==   norm 40 rules
# exp7 ==  rank1 40 rules

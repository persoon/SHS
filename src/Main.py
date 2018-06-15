import src.testGenerator as generate
import src.testRunner as run
import src.writeReport as report

runs = []
for i in range(1, 11):
    #generate.execute(type='rand_rank1', fname='../resources/output/tests/exp5_'+str(i))
    errors = run.execute(fname='../resources/output/tests/exp5_'+str(i))
    runs.append(errors)

report.write_file(filename='../resources/output/tests/results5_rank1_rand.txt', runs=runs)

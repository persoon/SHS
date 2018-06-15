# writes the statistics to file


def write_file(runs, horizon=None, num_dev=None, num_iter=None, filename='test_results'):
    f = open(filename, 'w+')

    space = False

    if horizon is not None:
        f.write(str(horizon) + '\t')
        space = True
    if num_dev is not None:
        f.write(str(num_dev) + '\t')
        space = True
    else:
        num_dev = len(runs[0])
    if num_iter is not None:
        f.write(str(num_iter) + '\t')
        space = True
    else:
        num_iter = len(runs[0][0])

    if space:
        f.write('\n')

    # 1. runs
    #   2. run
    #      3. device
    #         4. iteration
    for i in range(len(runs)):
        f.write(str(i)+'\n')
        for device in runs[i]:
            for iteration in device:
                f.write(str(iteration) + '\t')
            f.write('\n')
        f.write('\n')

    aggregator = []
    for i in range(num_dev):
        aggregator.append([])
        for j in range(num_iter):
            aggregator[i].append(0)

    print(aggregator)

    for run in runs:
        for i in range(num_dev):
            for j in range(num_iter):
                aggregator[i][j] += run[i][j]

    num_runs = len(runs)
    f.write('TOTAL\n')
    for i in range(num_dev):
        for j in range(num_iter):
            aggregator[i][j] /= num_runs
            f.write(str(aggregator[i][j])+'\t')
        f.write('\n')
    f.write('\n')
    f.close()
    print(aggregator)


write_file(runs=[[[1, 2, 3, 4, 5], [6, 7, 8, 9, 10]], [[1, 2, 3, 4, 5], [0, 0, 0, 0, 0]]], horizon=24, num_dev=2, num_iter=5)


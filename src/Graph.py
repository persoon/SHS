import csv
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.lines as lines
import matplotlib.transforms as mtransforms
import matplotlib.text as mtext

def open_experiment(filename):
    power = [[]]
    price = [[]]
    with open(filename, 'r') as csvfile:
        reader = csv.reader(csvfile, delimiter='\t')
        for row in reader:
            i = 0
            while i < len(row):
                power[len(power)-1].append(row[i])
                price[len(power)-1].append(row[i+1])
                i += 2
            power.append([])
            price.append([])

    plt.figure(1)
    for i in range(len(power)-1):
        plt.plot(power[i], label=str(i))
        'L'+str(i)

    plt.legend()
    plt.xlabel('timestep')
    plt.ylabel('power')

    plt.figure(2)
    for i in range(len(price)-1):
        plt.plot(price[i], label=str(i))
        'L'+str(i)

    plt.legend()
    plt.xlabel('timestep')
    plt.ylabel('price')

    plt.figure(3)
    for i in range(len(price)-1):
        ratio = []
        for j in range(len(price[0])):
            ratio.append(float(price[i][j]) / float(power[i][j]))
        plt.plot(ratio, label=str(i))
        'L' + str(i)

    plt.legend()
    plt.xlabel('timestep')
    plt.ylabel('ratio')

    plt.show()

# def open_schedule(filename):


# 'main method':
open_experiment('../resources/output/experiment.txt')

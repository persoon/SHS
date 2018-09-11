# monotonic user expectation function
# generates and holds generated values for use

import random
import math
import matplotlib.pyplot as plt

class MonotonicFunc:
    poly = []

    def __init__(self, bounds=None):
        if bounds is None:
            self.bounds = [0, 1000]
        else:
            self.bounds = bounds
        assert self.bounds[0] <= self.bounds[1]
        self.length = self.bounds[1] - self.bounds[0]

        self.low = None
        self.high = None

        self.scale = 100
        self.ymax = 1000

        x, y = self.generate_random()
        x2, y2 = self.generate_consistent()
        plt.plot(x, y)
        plt.plot(x2, y2)
        plt.show()

    def generate_consistent(self):
        x = []
        y = []
        incr = []  # the amount to increase by

        for i in range(0, self.length):
            x.append(i)
            incr.append(1-math.cos(i/self.scale))

        yval = 0
        for i in range(0, self.length):
            y.append(yval)
            yval += incr[i]

        for i in range(0, self.length):
            y[i] = y[i] / yval * self.ymax

        return x, y

    def generate_random(self):
        x = []
        y = []
        yval = 0
        incr = 0
        for i in range(0, self.length):
            x.append(i)
            y.append(yval)
            incr += random.random() - 0.5
            yval += abs(incr)

        for i in range(0, self.length):
            y[i] = (y[i] / yval * self.ymax) + (1-math.cos(i/self.scale))

        return x, y

mono = MonotonicFunc()

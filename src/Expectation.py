# Simulates User expectations
import random
import numpy as np
import matplotlib.pyplot as plt


# TODO: fix length (list is slightly too long but this is a good enough approximation)
class Expectation:

    knowledge = []
    kline = []
    blength = None
    bounds = None

    def __init__(self, bounds, expect, num_points=5, rseed=None):
        assert(len(bounds) == len(expect))
        self.bounds = bounds
        self.blength = len(bounds)
        self.foundx = []
        self.foundy = []
        for i in range(self.blength):
            self.foundx.append([])
            self.foundy.append([])

        random.seed(rseed)
        dist = []
        for i in range(self.blength):
            self.knowledge.append([0])
            self.kline.append(None)
            # print('DIST', bounds[i][1] - bounds[i][0] + 1)
            dist.append((bounds[i][1] - bounds[i][0] + 1) / (num_points - 1))
            rnum = None
            for j in range(num_points):
                if rnum is None:
                    rnum = random.randint(expect[i][0], expect[i][1])
                else: # makes it so numbers don't change super fast
                    rnum = ((0.5*rnum) + random.randint(expect[i][0], expect[i][1])) / 1.5

                self.knowledge[i].append(rnum)
                if self.kline[i] is None:
                    self.kline[i] = np.linspace(float(self.knowledge[i][0]), float(self.knowledge[i][1]), num=int(dist[i]))
                else:
                    k_new = np.linspace(float(self.knowledge[i][j]), float(self.knowledge[i][j+1]), num=int(dist[i]+1))
                    # k_new = np.delete(k_new, 0)
                    while (len(k_new) + len(self.kline[i])) > (bounds[i][1] - bounds[i][0] + 1):
                        k_new = np.delete(k_new, 0)
                    self.kline[i] = np.concatenate((self.kline[i], k_new))

    def get_value(self, x):
        assert len(x) == self.blength
        val = 0
        for i in range(len(x)):
            v = self.kline[i][x[i] - self.bounds[i][0]]

            self.foundx[i].append(x[i])
            self.foundy[i].append(v)
            val += v
        return val

    def show_graphs(self):
        for i in range(len(self.kline)):
            plt.figure(1+i)
            n = self.bounds[i][1] - self.bounds[i][0] + 1
            x = np.linspace(self.bounds[i][0], self.bounds[i][1], num=n).reshape(-1, 1)
            plt.plot(x, self.kline[i])
        plt.show()

    def show_ucb(self):
        for i in range(len(self.kline)):
            plt.figure(1+i)
            n = self.bounds[i][1] - self.bounds[i][0] + 1
            x = np.linspace(self.bounds[i][0], self.bounds[i][1], num=n).reshape(-1, 1)
            plt.plot(x, self.kline[i])
            plt.plot(self.foundx[i], self.foundy[i], 'ro')
        plt.show()


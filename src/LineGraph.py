import matplotlib.pyplot as plt
import numpy as np


# For creating a graph of the gaussian process
class LineGraph:

    def __init__(self, bounds):
        self.bounds = bounds
        self.pointx = []
        self.pointy = []

    def add_expectation(self, kline):
        self.kline = kline
        n = self.bounds[1] - self.bounds[0] + 1
        x = np.linspace(self.bounds[0], self.bounds[1], num=n).reshape(-1, 1)
        plt.plot(x, self.kline)

    def add_point(self, x, y):
        plt.plot(x, y, 'ro')
        self.pointx.append(x)
        self.pointy.append(y)

    @staticmethod
    def show_graph():
        plt.show()

    def reset(self):
        plt.clf()
        self.add_expectation(self.kline)
        plt.plot(self.pointx, self.pointy, 'ro')

    # Inputs:
    #   kappa -
    #   mu    - mean
    #   stdv  - standard deviation
    #   Xtest - Tested points
    def add_confidence_interval(self, kappa, mu, stdv, Xtest):
        #print(len(Xtest))
        #print(len(mu))
        #print(len(stdv))
        fig1 = plt.figure(1)
        ax1 = fig1.add_subplot(111)
        y1 = []
        y2 = []
        print('----------------------------')
        for i in range(len(Xtest)):
            y1.append(mu[i]-(kappa*stdv[i]))
            y2.append(mu[i]+(kappa*stdv[i]))

        ay1 = np.asarray(y1)
        ay2 = np.asarray(y2)
        aXtest = np.asarray(Xtest)
        #print(aXtest.shape, ay1.shape, ay2.shape)
        fig1.gca().fill_between(aXtest.flatten(), ay1.flatten(), ay2.flatten(), color="#dddddd")
        ax1.plot(aXtest, mu)
        fig2 = plt.figure(2)
        ax2 = fig2.add_subplot(111)
        ax2.plot(aXtest, ay2)






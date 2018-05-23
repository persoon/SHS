import numpy as np
import matplotlib.pyplot as plt
from matplotlib import gridspec
import math
from src.bayes_opt.bayesian_optimization import BayesianOptimization
from src.LineGraph import LineGraph
import src.Parameters
params = src.Parameters.Parameters()


def posterior(bo, x):
    bo.gp.fit(bo.X, bo.Y)
    mu, sigma = bo.gp.predict(x, return_std=True)
    return mu, sigma


def plot_gp(bo, x, y, xmin, xmax):
    fig = plt.figure(figsize=(16, 10))
    fig.suptitle('Gaussian Process and Utility Function After {} Steps'.format(len(bo.X)), fontdict={'size': 30})

    gs = gridspec.GridSpec(2, 1, height_ratios=[3, 1])
    axis = plt.subplot(gs[0])
    acq = plt.subplot(gs[1])

    mu, sigma = posterior(bo, x)
    axis.plot(x, y, linewidth=3, label='Target')
    axis.plot(bo.X.flatten(), bo.Y, 'D', markersize=8, label=u'Observations', color='r')
    axis.plot(x, mu, '--', color='k', label='Prediction')

    axis.fill(np.concatenate([x, x[::-1]]),
              np.concatenate([mu - 1.9600 * sigma, (mu + 1.9600 * sigma)[::-1]]),
              alpha=.6, fc='c', ec='None', label='95% confidence interval')

    axis.set_xlim((xmin, xmax))
    axis.set_ylim((None, None))
    axis.set_ylabel('f(x)', fontdict={'size': 20})
    axis.set_xlabel('x', fontdict={'size': 20})

    utility = bo.util.utility(x, bo.gp, 0)[0]
    acq.plot(x, utility, label='Utility Function', color='purple')
    acq.plot(x[np.argmax(utility)], np.max(utility), '*', markersize=15,
             label=u'Next Best Guess', markerfacecolor='gold', markeredgecolor='k', markeredgewidth=1)
    acq.set_xlim((xmin, xmax))
    acq.set_ylim((0, np.max(utility) + 0.5))
    acq.set_ylabel('Utility', fontdict={'size': 20})
    acq.set_xlabel('x', fontdict={'size': 20})

    axis.legend(loc=2, bbox_to_anchor=(1.01, 1), borderaxespad=0.)
    acq.legend(loc=2, bbox_to_anchor=(1.01, 1), borderaxespad=0.)


# a test that will help us look at bayesian optimization code
class SmoothConvex:
    def __init__(self, bounds, smoothness=1, flatness=1):
        self.bounds = bounds
        self.n = bounds[1] - bounds[0]

        self.x = np.linspace(0 , self.bounds[1], (self.n*smoothness)+1)
        self.y = np.zeros(len(self.x))
        for i in range(round(len(self.x))):
            self.y[i] = pow(self.x[i] - self.bounds[0] - (math.ceil(self.bounds[1]/2)), 2) / flatness
            # print(self.x[i], ':', self.y[i])


    def graph(self, show=False):
        plt.plot(self.x, self.y)
        if show:
            plt.show()

    def show(self):
        plt.show()

    def getValue(self, x):
        return self.y[int(x[0])]

bounds = [0, 100]
criminal = SmoothConvex(bounds=bounds, flatness=4)


def target_function(x):
    y = criminal.getValue(x)
    #plt.plot(x, y, 'ro')
    return y

pbounds = {'x': [bounds]}

x = np.linspace(0, 100, 101)
y = []
for i in range(len(x)):
    y.append(target_function([x[i]]))

y = np.asarray(y)
params.set_blackbox(x, y)

bayesian = BayesianOptimization(f=target_function, pbounds=pbounds, verbose=0)
bayesian.maximize(init_points=2, n_iter=5, acq='ucb', kappa=25)


#plot_gp(bayesian, x.reshape(-1, 1), y, bounds[0], bounds[1])
#plt.show()


'''
for i in range(len(p_x)):
    line_graph.add_confidence_interval(2.53*100, Xtest=p_x[i], mu=p_mean[i], stdv=p_std[i])
    criminal.graph()
    line_graph.show_graph()
'''












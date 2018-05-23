from __future__ import print_function
from __future__ import division
import numpy as np
from datetime import datetime
from scipy.stats import norm
from scipy.optimize import minimize
from math import floor, ceil
from src.Selector import get_bounds


def acq_max(ac, gp, y_max, bounds, random_state, point_bounds=None, n_warmup=100000, n_iter=250):
    """
    A function to find the maximum of the acquisition function

    It uses a combination of random sampling (cheap) and the 'L-BFGS-B'
    optimization method. First by sampling `n_warmup` (1e5) points at random,
    and then running L-BFGS-B from `n_iter` (250) random starting points.

    Parameters
    ----------
    :param ac:
        The acquisition function object that return its point-wise value.

    :param gp:
        A gaussian process fitted to the relevant data.

    :param y_max:
        The current maximum known value of the target function.

    :param bounds:
        The variables bounds to limit the search of the acq max.

    :param point_bounds:
        ### Description by Bill --- Idea by Nando ###
        The boundaries for each point tried so far.
        If I tried points [ 3,  6,  100 ] and bounds are [0, 100]:
            point_bounds = [[2.5, 3.5], [5.5, 6.5], [99.5, 100]]

    :param random_state:
        instance of np.RandomState random number generator

    :param n_warmup:
        number of times to randomly sample the acquisition function

    :param n_iter:
        number of times to run scipy.minimize

    Returns
    -------
    :return: x_max, The arg max of the acquisition function.
    """

    if point_bounds is None:
        point_bounds = []
        for i in range(len(bounds)):
            point_bounds.append([])

    # todo: move these checks to Bound.py
    for i in range(len(point_bounds)):

        if len(point_bounds[i]) == 0:
            print('point_bounds', point_bounds)
            print('bounds', bounds)
            point_bounds[i].append((bounds[i][0], bounds[i][0]))
            point_bounds[i].append((bounds[i][1], bounds[i][1]))

        if point_bounds[i][0][0] != bounds[i][0]:
            point_bounds[i].insert(0, (bounds[i][0], bounds[i][0]))
        if point_bounds[i][len(point_bounds[i])-1][1] != bounds[i][1]:
            point_bounds[i].insert(len(point_bounds[i]), (bounds[i][1]-0.5, bounds[i][1]))

    solutions = []
    #print('POINTS:', point_bounds)
    # there's an issue with this...
    # If we have multiple different bounds lists for each variable ---
    #                               do we need to try this with every permutation of bounds?
    # If we find a dependency issue (unsolvable schedule) I suppose we can add big chunks to bounds list,
    #                                               but what about two devices that aren't dependant on each other?

    # ANSWER:
    # Only ask multiple questions when the devices have dependencies
    # Otherwise ask a series of questions one at a time
    # TODO: implement multiple bounds lists
    # TODO: figure out how to ask only one change at a time
    # TODO: write a pynb file
    point_bounds = get_bounds(point_bounds)

    p_x, p_mean, p_std = [], [], []

    for b in point_bounds:

        bounds = np.array(b, dtype=np.float)

        # Warm up with random points
        x_tries = random_state.uniform(bounds[:, 0], bounds[:, 1], size=(n_warmup, bounds.shape[0]))
        ys, mean, std = ac(x_tries, gp=gp, y_max=y_max)

        x_max = x_tries[ys.argmax()]
        max_acq = ys.max()

        # Explore the parameter space more thoroughly
        x_seeds = random_state.uniform(bounds[:, 0], bounds[:, 1], size=(n_iter, bounds.shape[0]))
        #print('number of x_seeds:', len(np.unique(x_seeds)))
        for x_try in np.unique(x_seeds):
            #print('x_try:', x_try)
            # Find the minimum of minus the acquisition function
            res = minimize(lambda x: -ac(x.reshape(1, -1), gp=gp, y_max=y_max)[0],
                           x_try.reshape(1, -1),
                           bounds=bounds,
                           method="L-BFGS-B")

            val, mean, std = ac(res.x.reshape(1, -1), gp=gp, y_max=y_max)  # need these to see confidence interval
            p_x.append(x_try), p_mean.append(mean), p_std.append(std)
            # Store it if better than previous minimum(maximum).
            #res.fun[0] = round(res.fun[0], 1)
            if max_acq is None or -res.fun > max_acq:
                #if max_acq is not None:
                    #print('y_max:', y_max)
                    #print('x_max:', x_max, '->', res.x)
                    #print('max_acq:', max_acq, '->', -res.fun)
                x_max = res.x
                max_acq = -res.fun


        for i in range(len(x_max)):
            if floor(x_max[i]) == floor(bounds[i][0]):
                x_max[i] = ceil(x_max[i])
            elif ceil(x_max[i]) == ceil(bounds[i][1]):
                x_max[i] = floor(x_max[i])

        solutions.append((max_acq, x_max, p_x, p_mean, p_std))

    sol_idx = np.argmax([x for x, y, z1, z2, z3 in solutions])

    return solutions[sol_idx]


class UtilityFunction(object):
    """
    An object to compute the acquisition functions.
    """

    def __init__(self, kind, kappa, xi):
        """
        If UCB is to be used, a constant kappa is needed.
        """
        self.kappa = kappa

        self.xi = xi

        if kind not in ['ucb', 'ei', 'poi']:
            err = "The utility function " \
                  "{} has not been implemented, " \
                  "please choose one of ucb, ei, or poi.".format(kind)
            raise NotImplementedError(err)
        else:
            self.kind = kind

    def utility(self, x, gp, y_max):
        if self.kind == 'ucb':
            val, mean, std = self._ucb(x, gp, self.kappa)
            #print('MEAN:', mean, 'STD:', std)
            return val, mean, std
        if self.kind == 'ei':
            return self._ei(x, gp, y_max, self.xi)
        if self.kind == 'poi':
            return self._poi(x, gp, y_max, self.xi)

    @staticmethod
    def _ucb(x, gp, kappa):
        mean, std = gp.predict(x, return_std=True)
        return mean + kappa * std, mean, std

    @staticmethod
    def _ei(x, gp, y_max, xi):
        mean, std = gp.predict(x, return_std=True)
        z = (mean - y_max - xi)/std
        return (mean - y_max - xi) * norm.cdf(z) + std * norm.pdf(z)

    @staticmethod
    def _poi(x, gp, y_max, xi):
        mean, std = gp.predict(x, return_std=True)
        z = (mean - y_max - xi)/std
        return norm.cdf(z)


def unique_rows(a):
    """
    A functions to trim repeated rows that may appear when optimizing.
    This is necessary to avoid the sklearn GP object from breaking

    :param a: array to trim repeated rows from

    :return: mask of unique rows
    """
    if a.size == 0:
        return np.empty((0,))

    # Sort array and kep track of where things should go back to
    order = np.lexsort(a.T)
    reorder = np.argsort(order)

    a = a[order]
    diff = np.diff(a, axis=0)
    ui = np.ones(len(a), 'bool')
    ui[1:] = (diff != 0).any(axis=1)

    return ui[reorder]


def ensure_rng(random_state=None):
    """
    Creates a random number generator based on an optional seed.  This can be
    an integer or another random state for a seeded rng, or None for an
    unseeded rng.
    """
    if random_state is None:
        random_state = np.random.RandomState()
    elif isinstance(random_state, int):
        random_state = np.random.RandomState(random_state)
    else:
        assert isinstance(random_state, np.random.RandomState)
    return random_state


class BColours(object):
    BLUE = '\033[94m'
    CYAN = '\033[36m'
    GREEN = '\033[32m'
    MAGENTA = '\033[35m'
    RED = '\033[31m'
    ENDC = '\033[0m'


class PrintLog(object):

    def __init__(self, params):

        self.ymax = None
        self.xmax = None
        self.params = params
        self.ite = 1

        self.start_time = datetime.now()
        self.last_round = datetime.now()

        # sizes of parameters name and all
        self.sizes = [max(len(ps), 7) for ps in params]

        # Sorted indexes to access parameters
        self.sorti = sorted(range(len(self.params)),
                            key=self.params.__getitem__)

    def reset_timer(self):
        self.start_time = datetime.now()
        self.last_round = datetime.now()

    def print_header(self, initialization=True):

        if initialization:
            print("{}Initialization{}".format(BColours.RED,
                                              BColours.ENDC))
        else:
            print("{}Bayesian Optimization{}".format(BColours.RED,
                                                     BColours.ENDC))

        print(BColours.BLUE + "-" * (29 + sum([s + 5 for s in self.sizes])) +
            BColours.ENDC)

        print("{0:>{1}}".format("Step", 5), end=" | ")
        print("{0:>{1}}".format("Time", 6), end=" | ")
        print("{0:>{1}}".format("Value", 10), end=" | ")

        for index in self.sorti:
            print("{0:>{1}}".format(self.params[index],
                                    self.sizes[index] + 2),
                  end=" | ")
        print('')

    def print_step(self, x, y, warning=False):

        print("{:>5d}".format(self.ite), end=" | ")

        m, s = divmod((datetime.now() - self.last_round).total_seconds(), 60)
        print("{:>02d}m{:>02d}s".format(int(m), int(s)), end=" | ")

        if self.ymax is None or self.ymax < y:
            self.ymax = y
            self.xmax = x
            print("{0}{2: >10.5f}{1}".format(BColours.MAGENTA,
                                             BColours.ENDC,
                                             y),
                  end=" | ")

            for index in self.sorti:
                print("{0}{2: >{3}.{4}f}{1}".format(
                            BColours.GREEN, BColours.ENDC,
                            x[index],
                            self.sizes[index] + 2,
                            min(self.sizes[index] - 3, 6 - 2)
                        ),
                      end=" | ")
        else:
            print("{: >10.5f}".format(y), end=" | ")
            for index in self.sorti:
                print("{0: >{1}.{2}f}".format(x[index],
                                              self.sizes[index] + 2,
                                              min(self.sizes[index] - 3, 6 - 2)),
                      end=" | ")

        if warning:
            print("{}Warning: Test point chose at "
                  "random due to repeated sample.{}".format(BColours.RED,
                                                            BColours.ENDC))

        print()

        self.last_round = datetime.now()
        self.ite += 1

    def print_summary(self):
        pass

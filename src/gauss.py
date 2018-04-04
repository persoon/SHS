# going to rename this later - Bill
import numpy as np
import matplotlib.pyplot as plt
from src.bayes_opt import BayesianOptimization


class UserExpectation:
    # todo: make this not static --- we are trying to model a washer and dry right now and this wasn't top priority
    def __init__(self, start, end, start2, end2):
        assert(start < end)
        self.support = [start, end]
        self.n = end - start + 1

        knowledge = [0, 156, 344, 450, 498, 400, 279, 142, 10, 14, 150, 214]
        dist = self.n / (len(knowledge)-1)
        #for i in range(len(knowledge)):
        #    knowledge[i][0] = int(knowledge[i][0] * dist)

        # print(start, end, end-start)
        # print(dist)
        # print(knowledge)

        k_nd = np.linspace(float(knowledge[0]), float(knowledge[1]), num=int(dist))
        for i in range(len(knowledge)-2):
            k_new = np.linspace(float(knowledge[i+1]), float(knowledge[i+2]), num=int(dist+1))
            k_new = np.delete(k_new, 0)
            k_nd = np.concatenate((k_nd, k_new))

        while len(k_nd) < self.n:
            k_nd = np.concatenate((k_nd, [214.0]))

        # This is the preferences of the user:
        self.blackbox = k_nd

        # this is what a prior is: https://en.wikipedia.org/wiki/Prior_probability
        # Basically: the 'probability distribution' that expresses our belief before evidence is taken into account
        # we will probably use a uniform prior
        # Cholesky Decomposition --- http://www.gaussianprocess.org/gpml/chapters/RWA.pdf  --- pg.4

        assert (start2 < end2)
        self.support2 = [start2, end2]
        self.n2 = end2 - start2 + 1

        knowledge2 = [0, 156, 344, 450, 498, 400, 279, 142, 10, 14, 150, 214]
        dist2 = self.n2 / (len(knowledge2) - 1)
        # for i in range(len(knowledge)):
        #    knowledge[i][0] = int(knowledge[i][0] * dist)

        # print(start2, end2, end2 - start2)
        # print(dist2)
        # print(knowledge2)

        k_nd2 = np.linspace(float(knowledge2[0]), float(knowledge2[1]), num=int(dist2))
        for i in range(len(knowledge2) - 2):
            k_new2 = np.linspace(float(knowledge2[i + 1]), float(knowledge2[i + 2]), num=int(dist2 + 1))
            k_new2 = np.delete(k_new2, 0)
            k_nd2 = np.concatenate((k_nd2, k_new2))

        while len(k_nd2) < self.n:
            k_nd2 = np.concatenate((k_nd2, [214.0]))

        # This is the preferences of the user:
        self.blackbox2 = k_nd2


    def getValue(self, x):
        # print(x, self.support[0])
        return self.blackbox[x-self.support[0]]

    def getValue2(self, x):
        # print(x, self.support[0])
        return self.blackbox2[x-self.support2[0]]

    # hehe.
    def showBlackbox(self):
        # Xtest is 'n' evenly spaced samples from start to end -- we can use it to print out our graph or something
        Xtest = np.linspace(self.support[0], self.support[1], num=self.n).reshape(-1, 1)
        plt.plot(Xtest, self.blackbox)
        plt.axis([self.support[0], self.support[1], 0, 591])
        plt.show()

    def showBlackbox2(self):
        # Xtest is 'n' evenly spaced samples from start to end -- we can use it to print out our graph or something
        Xtest = np.linspace(self.support2[0], self.support2[1], num=self.n2).reshape(-1, 1)
        plt.plot(Xtest, self.blackbox2)
        plt.axis([self.support2[0], self.support2[1], 0, 591])
        plt.show()

    '''
    def kernel(self, x, y, sigma):
        sqdist = np.sum(x ** 2, 1).reshape(-1, 1) + np.sum(y ** 2, 1) - 2 * np.dot(x, y.T)
        return np.exp(-0.5 * 1 / sigma * sqdist)


    def gauss(self, Xdata, Ydata):
        Xtest = np.linspace(self.support[0], self.support[1], num=self.n).reshape(-1, 1)
        # The parameter denotes the 'smoothness' of our prior
        param = 20
        K_ss = self.kernel(Xtest, Xtest, param)  # we estimate K**

        # Get cholesky decomposition (square root) of the covariance
        # matrix: I.e., we find L s.t.  L * L^t = K_ss
        L = np.linalg.cholesky(K_ss + 1e-10 * np.eye(self.n))

        # Now our functions can be expressed as multivariate normal
        # distributions in terms of standard normals: f ~ mu + L * Normal(0,1)

        # Sample a standard normal for our test points. We can sample more functions
        # here. Multiply them by the square root of the covariance matrix (L)
        f_prior = np.dot(L, np.random.normal(size=(self.n, 1)))

        YReward = []
        for i in range(len(Ydata)):
            YReward.append(Ydata[i]-self.getValue(Xdata[i]))

        Xtrain = np.array(Xdata).reshape(len(Xdata), 1)
        Ytrain = np.array(YReward).reshape(len(Xdata), 1)

        # Apply the kernel function to our training points
        # We estimate K
        K = self.kernel(Xtrain, Xtrain, param)
        # The co-variance matrix for the "training" distribution is:
        L = np.linalg.cholesky(K + 1e-10 * np.eye(len(Xtrain)))

        # Compute the mean at our test points.

        # We estimate K*:
        K_s = self.kernel(Xtrain, Xtest, param)
        # We solve tLkhe  Ax = b (where A is L (the co-variance matrix of the training distr.),
        #  and b is K*)

        Lk = np.linalg.solve(L, K_s)

        # The mean at the test points is:
        mu = np.dot(Lk.T, np.linalg.solve(L, Ytrain)).reshape((self.n,))

        # Compute the standard deviation so we can plot it
        s2 = np.diag(K_ss) - np.sum(Lk ** 2, axis=0)
        stdv = np.sqrt(s2)

        # Draw samples from the posterior at our test points
        L = np.linalg.cholesky(K_ss + 1e-10 * np.eye(self.n) - np.dot(Lk.T, Lk))
        f_post = mu.reshape(-1, 1) + np.dot(L, np.random.normal(size=(self.n, len(Xdata))))

        plt.plot(Xtrain, Ytrain, 'bs', ms=8)
        # the posterior curves
        plt.plot(Xtest, f_post, lw=0.5)
        #plt.plot(Xtest, f_prior)
        plt.gca().fill_between(Xtest.flat, mu - 2 * stdv, mu + 2 * stdv, color="#dddddd")
        # The posterior mean
        plt.plot(Xtest, mu, 'r--', lw=3)
        plt.axis([self.support[0], self.support[1], -500, 500])
        plt.show()
    '''

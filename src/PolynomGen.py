import random
import math


class PolynomGen:
    poly = []

    def __init__(self, bounds=None, ymax=1, num=5):
        if bounds is None:
            self.bounds = [0, 99]
        else:
            self.bounds = bounds
        assert self.bounds[0] <= self.bounds[1]
        self.n = self.bounds[1] - self.bounds[0]

        # max randomly generated value:
        self.ymax = ymax
        self.low = None
        self.high = None
        if self.n-3 > num:
            self.generate(num)
        else:
            if self.n > 3:
                self.generate(self.n-3)
            else:
                self.generate(1)

    def generate(self, num=5):
        self.poly = []
        # our x-roots should all be between 0 and 191 --- TODO: make them all between 0 and preference_horizon - 1
        self.poly.append(0)  # there should be a root at 0 (user should expect 0 there)
        for i in range(num-1):
            r = int(round(random.random() * (self.n*1.8)))
            while r in self.poly:
                r = int(round(random.random() * (self.n*1.8)))
            self.poly.append(r)

        # WE PROBABLY WANT IT TO SPIKE....
        # the last point needs to be after the graph (so there isn't an upward spike
        '''
        r = (random.random() * self.n)*0.25 + self.bounds[1]
        while r in self.poly:
            r = (random.random() * self.n) * 0.5 + self.bounds[1]
        self.poly.append(r)
        '''

        print('roots:', self.poly)

        high = self.high
        low = self.low
        for x in range(self.bounds[0], self.bounds[1]+1):
            _val = self.temp_calc(x)
            if high is None or high < _val:
                high = _val
            if low is None or low > _val:
                low = _val

        self.low = low
        self.high = high

    def temp_calc(self, xval):
        xval -= self.bounds[0]
        '''
        if xval != 0:
            xval = (xval-self.bounds[0]) / (self.bounds[1] - self.bounds[0])
        '''
        val = xval - self.poly[0]
        for i in range(1, len(self.poly)):
            val *= xval - self.poly[i]
        return val

    def calculate(self, xval):
        _x = xval - self.bounds[0]
        val = _x - self.poly[0]
        #print('poly:', self.poly)
        #print('-----------------------------------------')
        #print('0', 'calculate:', val, '=', _x, '-', self.poly[0])
        for i in range(1, len(self.poly)):
            val *= _x - self.poly[i]
            #print(str(i), 'calculate:', val, '=', _x, '-', self.poly[i])
        #print('-----------------------------------------')
        # scaling the problem:
        val = val
        if self.high == 0:
            print(val, self.high, self.ymax)
        if val > 0:
            val = val / self.high * self.ymax
        elif val < 0:
            val = val / -self.low * self.ymax
        return val

'''
p = PolynomGen(bounds=[0, 191], ymax=600, num=5)
old = None
range1 = [0, 192]
range2 = [1, 10]
high = None
low = None
for x in range(range1[0], range1[1]):
    new = p.calculate(x)
    if high is None or high < new:
        high = new
    if low is None or low > new:
        low = new

for x in range(range1[0], range1[1]):
    new = p.calculate(x)
    new = new - low
    new = new / (high-low) * 600
    #print(((new+low) / (high+low)))
    #new = ((new+low) / (high+low)) * 600

    if new == 0 or x == 0:
        new = 0
        print(x, ':', 0, end=' ')
    else:
        print('                                                                                                        ', high / new)
        print(x, ':', new, end=' ')
    if old is not None:
        if old < new:
            print('+', end='')
        elif old > new:
            print('-', end='')
        else:
            print('=', end='')
    old = new
    print()

print(p.poly)
print(low, ',', high)
'''
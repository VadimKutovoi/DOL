import math
import os
import sys
from os.path import dirname as up
root_dir = os.path.join(up(os.path.abspath(os.curdir)))
sys.path.insert(0, root_dir)
from src.interval import interval
from src.solution import solution

class opt(object):
    lb = None
    rb = None
    r = None
    max_iter = 100
    minimum = None
    spent_iter = 0
    eps = 0.01
    sol = solution()
    use_method = None
    methods = { 
               "Piyavsky": interval.GetPiyavskyCharacteristic,
               "Strongin": interval.GetStronginCharacteristic,
               "BruteForse": interval.GetBruteForceCharacteristic
              }

    next_point = {
                  "Piyavsky": lambda _x_l, _x_r, _y_l, _y_r, _lipsh: 0.5 * (_x_r + _x_l) - 0.5 * ((_y_r - _y_l) / _lipsh),
                  "Strongin": lambda _x_l, _x_r, _y_l, _y_r, _lipsh: 0.5 * (_x_r + _x_l) - 0.5 * ((_y_r - _y_l) / _lipsh),
                  "BruteForse": lambda _x_l, _x_r, _y_l, _y_r, _lipsh: _x_l + (_x_r - _x_l) / 2.0
                 }
    
    def __init__(self):
        pass

    def __SetLb(self, _lb):
        self.lb = _lb
    
    def __SetRb(self, _rb):
        self.rb = _rb

    def __SetR(self, _r):
        self.r = _r

    def __SetMethod(self, _method):
        self.use_method = _method

    def __SetSpentIter(self, _spent_iter):
        self.spent_iter = _spent_iter

    def __SetMaxIter(self, _max_iter):
        self.max_iter = _max_iter

    def __SetEps(self, _eps):
        self.eps = _eps

    def __SetMin(self, _min):
        self.minimum = _min
        
    #def

    def __CorrectnessParameters(self, lb, rb, r, max_iter, method):
        if type(lb) is not float or type(rb) is not float \
            or type(r) is not float or method not in self.methods or (type(max_iter) is not int \
                and max_iter is not None):
            return False
        return True

    def __InitializeData(self, lb, rb, r, max_iter, method, eps):
        self.__SetLb(lb)
        self.__SetRb(rb)
        self.__SetR(r)
        self.__SetMethod(method)
        if max_iter is not None:
            self.__SetMaxIter(max_iter)
        if eps is not None:
            self.__SetEps(eps)

    def TestFunc(self, x):
        return 2 * math.sin(3 * x) + 3 * math.cos(5 * x)

    def __UpdateMinValue(self, *args):
        if self.minimum is None:
            self.__SetMin(args[0])
        for arg in args:
            if self.minimum[1] > arg[1]:
                self.__SetMin(arg)

    def __IncreaseIterCount(self):
        self.__SetSpentIter(self.spent_iter + 1)


    def __GetLipsh(self, _intervals):
        M = None
        for i, i_interval in enumerate(_intervals):
            for j_interval in  _intervals[i:]:
                M_interval = abs((j_interval.GetIRb()[1] - i_interval.GetILb()[1]) / (j_interval.GetIRb()[0] - i_interval.GetILb()[0]))
                if M is None:
                    M = M_interval
                else:
                    M = M_interval if M < M_interval else M
        return 1 if M == 0 else self.r * M

    def __GetBestInterval(self, _intervals):
        max_charact = _intervals[0].GetIR()
        num_interval = 0
        for num, interval in enumerate(_intervals):
            if max_charact < interval.GetIR():
                max_charact = interval.GetIR()
                num_interval = num
        return num_interval

    def PrintIntervals(self, intervals):
        s = ""
        for interval in intervals:
            s += "( " + str(interval.GetILb()[0]) + "; " +   str(interval.GetIRb()[0]) + " )"
        s += '\n'
        print(s)

    def __GetNewIntervals(self, intervals, lipsh, method):
        num = self.__GetBestInterval(intervals)
        if self.__CheckStop(intervals[num]):
            return 0
        old_interval = intervals.pop(num)
        x = self.next_point[self.use_method](old_interval.GetILb()[0], old_interval.GetIRb()[0], old_interval.GetILb()[1], \
            old_interval.GetIRb()[1], lipsh)
        y = self.TestFunc(x)
        self.sol.points.append((x, y))
        self.__UpdateMinValue((x, y))
        new_interval_l = interval(old_interval.GetILb(), (x, y)) 
        new_interval_r = interval((x, y), old_interval.GetIRb())

        method(new_interval_l, lipsh)
        method(new_interval_r, lipsh)

        new_intervals_1 = intervals[:num]
        new_intervals_2 = []

        if num != len(intervals):
            new_intervals_2 = intervals[num:]
        intervals = new_intervals_1
        intervals.extend([new_interval_l, new_interval_r])
        intervals.extend(new_intervals_2)
        return intervals

    def __CheckStop(self, _interval):
        return True if _interval.GetIRb()[0] - _interval.GetILb()[0] < self.eps else False

    def Minimize(self, lb, rb, r, method, max_iter=None, eps=None):
        intervals = list()
        lipsh = None

        if self.__CorrectnessParameters(lb, rb, r, max_iter, method):
            self.__InitializeData(lb, rb, r, max_iter, method, eps)
        else:
            raise TypeError("Invalid type of parameters")

        method = self.methods[method]
        initial_intervals = interval((lb, self.TestFunc(lb)), (rb, self.TestFunc(rb)))
        self.sol.points.append((lb, self.TestFunc(lb)))
        self.sol.points.append((rb, self.TestFunc(rb)))
        self.__UpdateMinValue(initial_intervals.GetILb(), initial_intervals.GetIRb())
        intervals.append(initial_intervals)
        while True:
            if self.spent_iter == self.max_iter:
                self.sol.minimum = self.minimum
                return self.sol
            if type(intervals) is int:
                self.sol.minimum = self.minimum
                return self.sol
            self.__IncreaseIterCount()
            self.sol.spent_iter = self.spent_iter
            lipsh = self.__GetLipsh(intervals)
            for iterv in intervals:
                method(iterv, lipsh)
            intervals = self.__GetNewIntervals(intervals, lipsh, method)

            
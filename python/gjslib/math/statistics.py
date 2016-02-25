#a Imports
import math
#a Correlation
class c_correlation(object):
    def __init__(self):
        self.sum_x = 0
        self.sum_y = 0
        self.sum_xy = 0
        self.sum_x2 = 0
        self.sum_y2 = 0
        self.n = 0
        pass
    def add_entry(self,x,y):
        self.sum_x += x
        self.sum_y += y
        self.sum_x2 += x*x
        self.sum_y2 += y*y
        self.sum_xy += x*y
        self.n += 1
        pass
    def correlation_coefficient(self):
        if self.n==0: return 0
        rn = self.sum_xy*self.n - self.sum_x*self.sum_y
        rd = ( math.sqrt(self.n*self.sum_x2 - self.sum_x*self.sum_x) *
               math.sqrt(self.n*self.sum_y2 - self.sum_y*self.sum_y) )
        if (rd<0.000001): return 0
        return rn/rd


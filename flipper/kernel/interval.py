
''' A module for representing and manipulating intervals.

Provides one class: Interval. '''

from fractions import Fraction

import flipper

class FixedPointField(object):
    def __init__(self, precision):
        self.precision = precision
        

class FixedPointInterval(object):
    def __init__(self, field, lower, upper):
        pass

class Interval(object):
    ''' This represents a closed interval [lower / 10**precision, upper / 10**precision]. '''
    def __init__(self, lower, upper, precision):
        assert isinstance(lower, flipper.IntegerType)
        assert isinstance(upper, flipper.IntegerType)
        assert isinstance(precision, flipper.IntegerType)
        if lower > upper: raise ValueError('Interval is empty.')
        
        self.lower = lower
        self.upper = upper
        self.precision = precision
    
    @classmethod
    def from_string(cls, string, precision):
        ''' A short way of constructing Intervals from a string. '''
        
        assert '.' in string
        string = string.ljust(precision, '0')
        i, r = string.split('.')
        assert len(str(r)) >= precision
        x = int(i + r[:precision])
        return cls(x-1, x+1, precision)
    
    @classmethod
    def from_integer(cls, integer, precision):
        ''' A short way of constructing Intervals from a fraction. '''
        
        return cls(integer*10**precision, integer*10**precision, precision)
    
    @classmethod
    def from_fraction(cls, fraction, precision):
        ''' A short way of constructing Intervals from a fraction. '''
        
        return cls((fraction.numerator*10**precision - 1) // fraction.denominator, (fraction.numerator*10**precision + 1) // fraction.denominator, precision)
    
    def __repr__(self):
        return str(self)
    def __str__(self):
        p = self.precision
        l, u = str(self.lower).zfill(p+1), str(self.upper).zfill(p+1)
        return '[{}.{}, {}.{}]'.format(l[:-p], l[-p:], u[:-p], u[-p:])
    
    def __add__(self, other):
        if isinstance(other, Interval):
            assert self.precision == other.precision
            values = [
                self.lower + other.lower,
                self.upper + other.upper
                ]
            return Interval(min(values), max(values), self.precision)
        elif isinstance(other, flipper.IntegerType):
            return self + Interval.from_integer(other, self.precision)
        elif isinstance(other, Fraction):
            return self + Interval.from_fraction(other, self.precision)
        else:
            return NotImplemented
    def __radd__(self, other):
        return self + other
    def __sub__(self, other):
        return self + (-other)
    def __neg__(self):
        return Interval(-self.upper, -self.lower, self.precision)
    def __mul__(self, other):
        if isinstance(other, Interval):
            assert self.precision == other.precision
            values = [
                self.lower * other.lower // 10**self.precision,
                self.upper * other.lower // 10**self.precision,
                self.lower * other.upper // 10**self.precision,
                self.upper * other.upper // 10**self.precision
                ]
            return Interval(min(values), max(values), self.precision)
        elif isinstance(other, flipper.IntegerType):
            return self * Interval.from_integer(other, self.precision)
        elif isinstance(other, Fraction):
            return self * Interval.from_fraction(other, self.precision)
        else:
            return NotImplemented
    def __rmul__(self, other):
        return self * other
    
    def __int__(self):
        return self.upper // 10**self.precision
    
    def simplify(self, new_precision):
        assert new_precision <= self.precision
        d = self.precision - new_precision
        return Interval(self.lower // 10**d, self.upper // 10**d, new_precision)
    
    def sign(self):
        if self.upper < 0:
            return -1
        elif self.lower > 0:
            return 1
        else:
            return 0


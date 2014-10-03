#
#
def odd(x):
    return (x & 1) == 1

class IntervalSet:
    def __init__(self,*inflections,neg_inf=False):
        self.neg_inf = neg_inf
        self.inflections = inflections
    def contains(self,probe):
        return odd(self.index_after(probe))!=self.neg_inf
    def index_after(self,probe):
        i = 0
        while i < len(self.inflections) and probe >= self.inflections[i]:
            i = i + 1
        return i
    def commensurable_with(self,other):
        return type(self) == type(other)
    def inverse(self):
        return type(self)(*self.inflections,neg_inf=(not self.neg_inf))
    def intersection(*sets):
        return sets[0].meld(sets,len(sets),len(sets))
    def union(*sets):
        return sets[0].meld(sets,1,len(sets))
    def meld(self,sets,l,h):
        assert all(s.commensurable_with(sets[0]) for s in sets)
        depth = len([s for s in sets if s.neg_inf])
        neg_inf = l <= depth <= h
        #print(neg_inf,l,depth,h)
        inflections = []
        index = {s:0 for s in sets if len(s.inflections) > 0}
        state = neg_inf
        # cycle through sets, producing a result set for all points
        # at which l <= depth <= h
        while len(index) > 0:
            active = index.keys()
            v = min([s.inflections[index[s]] for s in active])
            hits = [s for s in active if s.inflections[index[s]] == v]
            delta_depth = sum([(+1 if odd(index[s]) == s.neg_inf else -1) for s in hits])
            new_state = l <= depth+delta_depth <= h
            if state != new_state: inflections.append(v)
            state = new_state
            depth += delta_depth
            for s in hits:
                index[s] += 1
                if index[s] >= len(s.inflections): del index[s]
        return type(sets[0])(*inflections,neg_inf=neg_inf)
    def ranges(self):
        xs = [float("-inf")]+list(self.inflections) if self.neg_inf else list(self.inflections)
        if odd(len(xs)): xs.append(float("inf"))
        return [(xs[i],xs[i+1]) for i in range(0, len(xs), 2)]
    def __str__(self):
        return "{"+", ".join("{}..{}".format(l,h).replace('-inf','').replace('inf','') for l,h in self.ranges())+"}"
    __repr__ = __str__
        
x = IntervalSet(5,15,neg_inf=True)

assert str(x) == "{..5, 15..}"
assert str(x.inverse()) == "{5..15}"
assert x.contains(-10)
assert x.contains(0)
assert not x.contains(10)
assert x.contains(20)
assert str(IntervalSet(5,15,neg_inf=True).union(IntervalSet(10)))        == "{..5, 10..}"
assert str(IntervalSet(5,15,neg_inf=True).intersection(IntervalSet(10))) == "{15..}"

class ModuloIntervalSet(IntervalSet):
    low  = 0.0
    high = 1.0
    def __init__(self,*inflections,neg_inf=False):
        assert not odd(len(inflections)),"Modulo intervals must have an even number of inflections."
        self.span = self.high - self.low
        if neg_inf or len(inflections) > 2:
            assert all(self.low <= i <= self.high for i in inflections),"For now wrapping can only be done on a single pair of inflections "
            IntervalSet.__init__(self,*inflections,neg_inf=neg_inf)
        elif len(inflections) == 0:
            IntervalSet.__init__(self)
        else:
            inflections = [self.wrap(i) for i in inflections]
            IntervalSet.__init__(self,*sorted(inflections),neg_inf = inflections[0] > inflections[1])
    def commensurable_with(self,other):
        return IntervalSet.commensurable_with(self,other) and self.low == other.low and self.high == other.high
    def contains(self,probe):
        return IntervalSet.contains(self,self.wrap(probe))
    def wrap(self,value):
        return ((value-self.low) % self.span) + self.low

from math import pi
class AngularIntervalSet(ModuloIntervalSet):
    low  = -pi
    high =  pi

x = AngularIntervalSet(1,5)
assert str(x) == "{.."+str(5-2*pi)+", 1.0..}"  # e.g. {..-1.2831853071795862, 1.0..}
assert str(x.inverse()) == "{"+str(5-2*pi)+"..1.0}"
assert x.contains(-pi)
assert x.contains(pi)
assert not x.contains(2*pi)
assert x.contains(3*pi)

assert str(x.intersection(AngularIntervalSet(0,2))) == "{1.0..2.0}"
assert str(x.intersection(AngularIntervalSet(-2,2))) == "{-2.0.."+str(5-2*pi)+", 1.0..2.0}"

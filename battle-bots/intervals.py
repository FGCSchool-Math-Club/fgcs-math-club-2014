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
    def inverse(self):
        return IntervalSet(*self.inflections,neg_inf=(not self.neg_inf))
    def intersection(*sets):
        return sets[0].meld(sets,len(sets),len(sets))
    def union(*sets):
        return sets[0].meld(sets,1,len(sets))
    def meld(self,sets,l,h):
        depth = len([s for s in sets if s.neg_inf])
        neg_inf = l <= depth <= h
        #print(neg_inf,l,depth,h)
        inflections = []
        index = {s:0 for s in sets}
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
        return IntervalSet(*inflections,neg_inf=neg_inf)
    def __str__(self):
        if self.neg_inf:
            s = '..'
            o = 1
        else:
            s = ''
            o = 0
        i = 0
        n = len(self.inflections)
        while i < n:
            s = s + ("%s" % self.inflections[i])
            s = s + ('..' if not odd(i+o) else ', ' if i+1 < n else '')
            i += 1
        return "{"+s+"}"
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

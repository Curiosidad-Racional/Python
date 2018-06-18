from collections import Iterable
from itertools import product


class iter_inf:
    def __init__(self, always):
        self.always = always

    def __iter__(self):
        while True:
            yield self.always


class iter_ell:
    def __init__(self, ellipsis):
        self.ellipsis = ellipsis

    def __iter__(self):
        ellipsis = False
        for item in self.ellipsis:
            if item is Ellipsis:
                ellipsis = True
                continue
            if ellipsis:
                ellipsis = False
                beg = cell.coord(last)
                end = cell.coord(item)
                inc = [ 1 if b <= e else -1 for b, e in zip(beg, end) ]
                points = []
                for b, e, i in zip(beg, end, inc):
                    points.append([])
                    for var in range(b, e + i, i):
                        points[-1].append(var)
                for comb in product(*points):
                    yield comb
            else:
                yield item
            last = item


class cell:
    def __init__(self, point, get=None, rel=False, func=lambda x: x, cond=None):
        if isinstance(point, (str, tuple)):
            self.point = self.coord(point)
            self.get = get
            self.rel = rel
            self.func = func
            self.unique = True
        elif isinstance(point, Iterable):
            self.points = iter_ell(point)
            if isinstance(get, Iterable):
                self.gets = get
            else:
                self.gets = iter_inf(get)
            if isinstance(rel, Iterable):
                self.rels = rel
            else:
                self.rels = iter_inf(rel)
            if isinstance(func, Iterable):
                self.funcs = func
            else:
                self.funcs = iter_inf(func)
            self.unique = False
        self.cond = cond

    def __iter__(self):
        if self.unique:
            yield self
        elif self.cond:
            first_point = None
            for point, get, rel, func in zip(self.points,
                                             self.gets,
                                             self.rels,
                                             self.funcs):
                point = self.coord(point)
                if not first_point:
                    first_point = point
                if self.cond(get(*point)):
                    c = cell(point, get, rel=rel, func=func)
                    c.first_point = first_point
                    yield c
        else:
            first_point = None
            for point, get, rel, func in zip(self.points,
                                             self.gets,
                                             self.rels,
                                             self.funcs):
                point = self.coord(point)
                if not first_point:
                    first_point = point
                c = cell(point, get, rel=rel, func=func)
                c.first_point = first_point
                yield c

    @staticmethod
    def coord(point):
        if isinstance(point, str):
            i = 0
            while point[i] not in "0123456789":
                i += 1
            row = int(point[i:]) - 1
            col = -1
            factor = 1
            for l in point[:i].upper()[::-1]:
                col += factor * (ord(l) - 64)
                factor *= 26
            return col, row
        return point

    def value(self):
        try:
            return self.func(self.get(*self.point))
        except IndexError:
            return None

    def set(self, t):
        if isinstance(t, cell):
            if t.rel or self.rel:
                return cell(tuple(
                    t.point[i] + self.point[i] - self.first_point[i]
                    for i in range(len(t.point))),
                            self.get, rel=t.rel,
                            func=t.func)
            else:
                if not t.get:
                    t.get = self.get
                return t
        if isinstance(t, dict):
            return { self.set(k): self.set(v) for k, v in expand(t) }
        if isinstance(t, set):
            return { self.set(v) for v in expand(t) }
        if isinstance(t, list):
            return [ self.set(v) for v in expand(t) ]
        if isinstance(t, tuple):
            return tuple( self.set(v) for v in expand(t) )
        return t


def expand(template):
    if isinstance(template, dict):
        for k, v in template.items():
            if isinstance(k, cell):
                for item in k:
                    yield item, item.set(v)
            else:
                yield k, v
    elif isinstance(template, Iterable):
        for v in template:
            if isinstance(v, cell):
                for item in v:
                    yield item
            else:
                yield v


def fill(template):
    if isinstance(template, cell):
        return template.value()
    if isinstance(template, dict):
        return { fill(k): fill(v) for k, v in expand(template) }
    if isinstance(template, set):
        return { fill(v) for v in expand(template) }
    if isinstance(template, list):
        return [ fill(v) for v in expand(template) ]
    if isinstance(template, tuple):
        print(template)
        return tuple( fill(v) for v in expand(template) )
    return template

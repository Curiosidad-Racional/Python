from collections import Iterable

class cell:
    def __init__(self, point, get, rel=False, func=lambda x: x):
        self.col, self.row = self.coord(point)
        self.get = get
        self.rel = rel
        self.func = func

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
            return self.func(self.get(
                self.col, self.row))
        except IndexError:
            return None

    def set(self, template):
        if isinstance(template, cell):
            if template.rel:
                return cell((template.col + self.col, template.row + self.row),
                            self.get, rel=template.rel,
                            func=template.func)
            else:
                return template
        if isinstance(template, dict):
            return { self.set(k): self.set(v) for k, v in template.items() }
        if isinstance(template, set):
            return { self.set(v) for v in template }
        if isinstance(template, list):
            return [ self.set(v) for v in template ]
        if isinstance(template, tuple):
            return tuple( self.set(v) for v in template )
        return template


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
                beg_col, beg_row = cell.coord(last)
                end_col, end_row = cell.coord(item)
                col_inc = 1 if beg_col < end_col else -1
                row_inc = 1 if beg_row < end_row else -1
                for x in range(beg_col, end_col + col_inc, col_inc):
                    for y in range(beg_row, end_row + row_inc, row_inc):
                        yield x, y
            else:
                yield item
            last = item


class cells:
    def __init__(self, points, gets, rels=False, funcs=lambda x: x, cond=None):
        self.points = iter_ell(points)
        if isinstance(gets, Iterable):
            self.gets = gets
        else:
            self.gets = iter_inf(gets)
        if isinstance(rels, Iterable):
            self.rels = rels
        else:
            self.rels = iter_inf(rels)
        if isinstance(funcs, Iterable):
            self.funcs = funcs
        else:
            self.funcs = iter_inf(funcs)
        self.cond = cond

    def __iter__(self):
        if self.cond:
            for point, get, rel, func in zip(self.points,
                                             self.gets,
                                             self.rels,
                                             self.funcs):
                col, row = self.coord(point)
                if self.cond(get(col, row)):
                    yield cell(point, get, rel=rel, func=func)
        else:
            for point, get, rel, func in zip(self.points,
                                             self.gets,
                                             self.rels,
                                             self.funcs):
                yield cell(point, get, rel=rel, func=func)


def expand(template):
    if isinstance(template, dict):
        for k, v in template.items():
            if isinstance(k, cells):
                for item in k:
                    yield item, item.set(v)
            else:
                yield k, v
    elif isinstance(template, Iterable):
        for v in template:
            if isinstance(v, cells):
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
        return tuple( fill(v) for v in expand(template) )
    if isinstance(template, Iterable):
        return ( fill(v) for v in expand(template) )
    return template

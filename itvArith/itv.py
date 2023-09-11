import logging

log = logging.getLogger(__name__)

class Type:
    """
    Type racine
    """
    pass

class Ellipsis(Type):
    """
    Type de paramètre variadic dans les appels de fonctions
    """

    def __repr__(self):
        return "..."

class TypeNamed(Type):
    """
    Type nommé opaque
    """
    def __init__(self, name):
        self._name = name

    def __repr__(self):
        return self._name

class TypeVar(Type):
    """
    Type variable pour les génériques
    """
    def __init__(self, name):
        self._name = name

    def __repr__(self):
        return f"${self._name}"

class itvInt(Type):
    """
    Type interval entier
    """
    def __init__(self, a, b):
        # translate as ordered list of interval
        self.min = min(a, b)
        self.max = max(a, b)

    def __repr__(self):
        return f"{self.min}>...<{self.max}"

    # basic ordering operator
    def __lt__(self, oth):
        if type(oth) is int:
            return self.min < oth
        if isinstance(oth, itvInt):
            #log.info(f"INF {self} {oth}: {self.min < oth.min}")
            return self.min < oth.min
        raise RuntimeError(f"Unhandled case")

    def __gt__(self, oth):
        if type(oth) is int:
            return self.max > oth
        if isinstance(oth, itvInt):
            return self.max > oth.max
        raise RuntimeError(f"Unhandled case")

    def __eq__(self, oth):
        if type(oth) is int:
            return self.min == oth and self.max == oth
        if isinstance(oth, itvInt):
            return oth.min == self.min and oth.max == self.max
        raise RuntimeError(f"Unhandled case")


    # in
    def __contains__(self, oth):
        if type(oth) is int:
            return oth >= self.min and oth <= self.max
        if isinstance(oth, itvInt):
            return oth.min >= self.min and oth.max <= self.max
        raise RuntimeError(f"Unhandled case")

    # + - / * %
    def __add__(self, oth):
        if type(oth) is int:
            return itvInt(self.min + oth, self.max + oth)
        if isinstance(oth, itvInt):
            return itvInt(self.min + oth.min, self.max + oth.max)
        raise RuntimeError(f"Unhandled case")

    def __sub__(self, oth):
        if type(oth) is int:
            return itvInt(self.min - oth, self.max - oth)
        if isinstance(oth, itvInt):
            return itvInt(self.min - oth.min, self.max - oth.max)
        raise RuntimeError(f"Unhandled case")

    def __mul__(self, oth):
        if type(oth) is int:
            intmin = min(self.min * oth, self.max * oth)
            intmax = max(self.min * oth, self.max * oth)
            return itvInt(intmin, intmax)
        if isinstance(oth, itvInt):
            intmin = min(self.min * oth.min, self.min * oth.max, self.max * oth.min, self.max * oth.max)
            intmax = max(self.min * oth.min, self.min * oth.max, self.max * oth.min, self.max * oth.max)
            return itvInt(intmin, intmax)
        raise RuntimeError(f"Unhandled case")

    def __truediv__(self, oth):
        if oth == 0:
            raise RuntimeError("Divide by zero")
        if type(oth) is int:
            intmin = min(self.min // oth, self.max // oth)
            intmax = max(self.min // oth, self.max // oth)
            return itvInt(intmin, intmax)
        if isinstance(oth, itvInt):
            intmin = min(self.min // oth.min, self.min // oth.max, self.max // oth.min, self.max // oth.max)
            intmax = max(self.min // oth.min, self.min // oth.max, self.max // oth.min, self.max // oth.max)
            return itvInt(intmin, intmax)
        raise RuntimeError(f"Unhandled case")

    def __floordiv__(self, oth):
        return self.__truediv__(oth)

    def __mod__(self, oth):
        if oth == 0:
            raise RuntimeError("Modulo by zero")
        if type(oth) is int:
            intmin = min(self.min % oth, self.max % oth)
            intmax = max(self.min % oth, self.max % oth)
            return itvInt(intmin, intmax)
        if isinstance(oth, itvInt):
            intmin = min(self.min % oth.min, self.min % oth.max, self.max % oth.min, self.max % oth.max)
            intmax = max(self.min % oth.min, self.min % oth.max, self.max % oth.min, self.max % oth.max)
            return itvInt(intmin, intmax)
        raise RuntimeError(f"Unhandled case")

    # pow
    def __pow__(self, oth):
        if type(oth) is int:
            intmin = min(self.min ** oth, self.max ** oth)
            intmax = max(self.min ** oth, self.max ** oth)
            return itvInt(intmin, intmax)
        if isinstance(oth, itvInt):
            intmin = min(self.min ** oth.min, self.min ** oth.max, self.max ** oth.min, self.max ** oth.max)
            intmax = max(self.min ** oth.min, self.min ** oth.max, self.max ** oth.min, self.max ** oth.max)
            return itvInt(intmin, intmax)
        raise RuntimeError(f"Unhandled case")

    # unary -, abs and ~
    def __neg__(self):
        intmin = min(-self.min, -self.max)
        intmax = max(-self.min, -self.max)
        return itvInt(intmin, intmax)

    def __abs__(self):
        intmin = min(abs(self.min), abs(self.max))
        intmax = max(abs(self.min), abs(self.max))
        return itvInt(intmin, intmax)

    def __invert__(self):
        intmin = min(~self.min, ~self.max)
        intmax = max(~self.min, ~self.max)
        return itvInt(intmin, intmax)

    # << >>
    # binary logic for each value
    def __lshift__(self, oth):
        if type(oth) is int:
            intmin = min(self.min << oth, self.max << oth)
            intmax = max(self.min << oth, self.max << oth)
            return itvInt(intmin, intmax)
        if isinstance(oth, itvInt):
            intmin = min(self.min << oth.min, self.min << oth.max, self.max << oth.min, self.max << oth.max)
            intmax = max(self.min << oth.min, self.min << oth.max, self.max << oth.min, self.max << oth.max)
            return itvInt(intmin, intmax)
        raise RuntimeError(f"Unhandled case")

    def __rshift__(self, oth):
        if type(oth) is int:
            intmin = min(self.min >> oth, self.max >> oth)
            intmax = max(self.min >> oth, self.max >> oth)
            return itvInt(intmin, intmax)
        if isinstance(oth, itvInt):
            intmin = min(self.min >> oth.min, self.min >> oth.max, self.max >> oth.min, self.max >> oth.max)
            intmax = max(self.min >> oth.min, self.min >> oth.max, self.max >> oth.min, self.max >> oth.max)
            return itvInt(intmin, intmax)
        raise RuntimeError(f"Unhandled case")


    # TODO __bool__
    # & | ^
    # TODO: translate as list of interval

    ## other comparison operator
    def __ne__(self, oth):
        return not self.__eq__(oth)

    def __le__(self, oth):
        return self.__lt__(oth) or self.__eq__(oth)

    def __ge__(self, oth):
        return self.__gt__(oth) or self.__eq__(oth)

class itvAndList(list):
    def __init__(self, *arg):
        ls = None
        log.info(f"ADD {arg}")
        if len(arg) == 0:
            return
        elif len(arg) > 1:
            ls = list(arg)
        elif type(arg[0]) is list:
            ls = arg[0]
        elif type(arg[0]) is itvInt:
            ls = [arg[0]]
        for it in ls:
            log.info(f"ADD! {it}")
            self.append(it)

    def append(self, oth):
        log.info(f"IT {oth}")
        def insert_before_current(oth, current, new_list):
            if oth.max > current.min:
                # propagate to max interval
                while oth.max > current.min:
                    oth.max = max(oth.max, current.max)
                    current = next(it_current)
                new_list.append(oth)
                new_list.append(current)
                return True
            else:
                new_list.append(oth)
                new_list.append(current)
                return True
            return False

        # my inner list is ordered
        # lower/upper bound of oth is ordered
        # new_list = []
        # for current in self:
        #   if oth.lower < current.lower
        #         new_list.append(oth)
        #         if oth.upper > current.lower
        #             merged oth and current (oth.upper = max(oth.upper, current.upper))
        #             continue merge while oth.upper > current.lower
        #   else new_list.append(current)
        new_list = []
        it_current = iter(self)
        try:
            oth_appended = False
            idx_current = 0
            log.info(f"begin iter {it_current}")
            while True:
                current = next(it_current)
                idx_current += 1
                log.info(f"CMP OTH {oth} CURRENT {current}")
                if oth.min < current.min:
                    log.info(f"yes < insert here")
                    #new_list.append(oth)
                    #if oth.max > current.min:
                    #    # propagate to max interval
                    #    while oth.max > current.min:
                    #        oth.max = max(oth.max, current.max)
                    #        current = next(it_current)
                    #    new_list.append(oth)
                    #    oth_appended = True
                    #    new_list.append(current)
                    #    continue
                    #else:
                    #    new_list.append(oth)
                    #    oth_appended = True
                    #    new_list.append(current)
                    #    continue
                    if not insert_before_current(oth, current, new_list):
                        raise RuntimeError(f"Can't insert {oth} before {current} in {new_list}")
                    oth_appended = True
                else:
                    log.info(f"not < go next")
                    new_list.append(current)
                # check last in list
                if new_list[-1].max > oth.min:
                    log.info(f"merge last")
                    # merge
                    new_list[-1].max = max(new_list[-1].max, oth.max)
                    oth_appended = True
                    # extend rest
                    new_list.extend(self[idx_current:])
                    break
        except StopIteration:
            log.info(f"end iter")
            if not oth_appended:
                log.info(f"add finally")
                if len(new_list) and new_list[-1].max > oth.min:
                    new_list[-1].max = max(new_list[-1].max, oth.max)
                else:
                    new_list.append(oth)
        self.clear()
        self.extend(new_list)

    def __eq__(self, oth):
        return list.__eq__(self, oth)

def itvSigned(nbit):
    return itvInt(-(2**(nbit - 1))-1, 2**(nbit - 1))

def itvUnsigned(nbit):
    return itvInt(0, 2**nbit)

def itvI8():
    return itvSigned(8)
def itvI16():
    return itvSigned(16)
def itvI32():
    return itvSigned(32)
def itvI64():
    return itvSigned(64)

def itvUI8():
    return itvUnsigned(8)
def itvUI16():
    return itvUnsigned(16)
def itvUI32():
    return itvUnsigned(32)
def itvUI64():
    return itvUnsigned(64)

class itvExpr:
    # build expr with itvInt for abstract interpretation
    def __init__(self, itvInt):
        self.itv = itvInt

    def __repr__(self):
        return f"eval {self.itv}"

    def __lt__(self, oth):
        if type(oth) is int:
            return itvExprLt(self, itvInt(oth, oth))
        if isinstance(oth, itvExpr):
            return itvExprLt(self, oth)
        raise RuntimeError(f"Unhandled case")

class itvExprBinary(itvExpr):
    pass

class itvExprLt(itvExpr):
    def __init__(self, lhs, rhs):
        self.lhs = lhs
        self.rhs = rhs

    def __repr__(self):
        return f"eval {self.lhs} < {self.rhs}"

    # TODO eval

    def eval(self):
        return 

__all__ = ['itvInt', 'itvAndList', 'itvSigned', 'itvUnsigned', 'itvI8', 'itvI16', 'itvI32', 'itvI64', 'itvUI8', 'itvUI16', 'itvUI32', 'itvUI64',
        'itvExpr', 'itvExprBinary', 'itvExprLt', 'Type', 'TypeNamed', 'TypeVar']

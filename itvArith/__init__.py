class itvInt:
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

    def __inv__(self):
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

def itvSigned(nbit):
    return itvInt(-(2**(nbit - 1))-1, 2**(nbit - 1))

def itvUnsigned(nbit):
    return itvInt(0, 2**nbit)

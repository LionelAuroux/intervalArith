class itvInt:
    def __init__(self, intmin, intmax):
        # TODO translate as ordered list of interval
        self.min = intmin
        self.max = intmax

    def __repr__(self):
        return f"{self.min}>...<{self.max}"

    def __lt__(self, oth):
        if type(oth) is int:
            return self.min < oth
        raise RuntimeError(f"Unhandled case")

    def __gt__(self, oth):
        if type(oth) is int:
            return self.max > oth
        raise RuntimeError(f"Unhandled case")

    def __eq__(self, oth):
        if type(oth) is int:
            return self.min == oth and self.max == oth
        if isinstance(oth, itvInt):
            return oth.min == self.min and oth.max == self.max
        raise RuntimeError(f"Unhandled case")

    def __contains__(self, oth):
        if type(oth) is int:
            return oth >= self.min and oth <= self.max
        if isinstance(oth, itvInt):
            return oth.min == self.min and oth.max == self.max
        raise RuntimeError(f"Unhandled case")
    # & | ^
    # + - / * %


    ## composed logic
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

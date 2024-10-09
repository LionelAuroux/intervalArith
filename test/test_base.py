from itvArith import *
import logging

log = logging.getLogger(__name__)

def test_syntax():
    """
    Utilise une approche d'EDSL pour éviter d'avoir à faire le parseur d'un langage.
    Formalise les concepts fondamentaux d'un Type System d'un compilo.
    """
    # TODO: not clearly finish -> need Interval Arithmetic
    d = Def().globals(
        # a = 2600:I16
        _1 = Var("a", 2600, itvI16()),
        # `=`(T)->T
        _2 = Fun("=", Param(t=TypeVar('T')), Param(t=TypeVar('T'))),
        # f(I8)->t1
        _3 = Fun("f", Param(t=TypeNamed("t1")), Param(t=TypeNamed("t2"))),
        # f(i16)->t2
        _4 = Fun("f", Param(t=TypeNamed("t2")), Param(t=itvI16())),
        # x:t2
        _5 = Var("x", None, TypeNamed("t2")),
    ).block([
        ["=", "a", Val(12, itvI8())], # a = 12:I8
        ["f", "b", "x"], # b = f(x)
    ])
    log.info(f"DECL {d._decls}")
    assert "a" in d._decls, "Failed to found `a` in context."
    assert "x" in d._decls, "Failed to found `x` in context."
    assert "f" in d._decls, "Failed to found `f` in context."
    assert "=" in d._decls, "Failed to found `=` in context."
    typed_ast = d.check() # check ast and return typed AST
    for idx, t in enumerate(typed_ast):
        log.info(f"Typed AST {idx}: {t}")
    # type de l'affectation est le type de a
    assert typed_ast[0].is_typed
    log.info(f"EXPR {type(typed_ast[0])}")
    log.info(f"EXPR2 {type(typed_ast[0].reftype)}")
    assert type(typed_ast[0].reftype) is itvInt

def test_opebase():
    """
    Test les opérations fondamentales de l'arithmétique d'interval.
    """
    log.info("Here!!!")
    a = itvInt(3, 6)
    log.info(f"A = {a}")
    assert a == itvInt(3, 6)
    assert a != itvInt(0, 0)
    assert a < itvInt(4, 6)
    assert not (a <= itvInt(3, 8))
    assert a <= itvInt(3, 6)
    assert itvInt(2, 8) <= a
    assert itvInt(2, 7) > a
    # equality
    assert itvInt(1, 1) == 1
    # interval inclusion
    assert a in itvInt(0, 10)
    assert a not in itvInt(4, 5)
    # itvInt constructor arrange in correct order
    assert a < itvInt(6, 4)
    assert itvInt(7, 2) > a
    # add
    assert a + 1 == itvInt(4, 7)
    # sub
    assert a - 1 == itvInt(2, 5)
    # mul
    assert a * 2 == itvInt(6, 12)
    # div
    assert a / 3 == itvInt(1, 2)
    # mod
    assert a % 1 == 0
    assert a % 2 == itvInt(0, 1)
    # pow
    assert a ** 2 == itvInt(9, 36)
    # neg
    assert -a == itvInt(-6, -3)
    b = itvInt(-3, 20)
    # abs
    assert abs(b) == itvInt(3, 20)
    # inv
    assert ~b == itvInt(~-3, ~20)
    # << & >>
    c = itvInt(4, 16)
    assert c >> 1 == itvInt(2, 8)
    assert c << 1 == itvInt(8, 32)

def test_ls():
    """
    Test l'union de plusieurs interval
    """
    a = itvAndList()
    assert len(a) == 0
    a.append(itvInt(1, 5))
    a.append(itvInt(7, 10))
    assert a == [itvInt(1, 5), itvInt(7, 10)]
    a = itvAndList()
    a.append(itvInt(1, 7))
    a.append(itvInt(5, 10))
    assert a == [itvInt(1, 10)]

def test_nbit():
    """
    Test les bornes d'un interval sur un nombre finit de bit pour simuler char,short,int,long.
    Le code itvSigned et itvUnsigned s'adapte au nombre de bit.
    Tester juste les bornes pour 8bit devrait suffire.
    """
    b = itvSigned(8)
    log.info(f"B = {b}")
    assert b >= -128
    assert b <= 127
    assert b >= -128 and b <= 127
    assert not (b < -129)
    assert not (b > 128)
    c = itvUnsigned(8)
    log.info(f"C = {c}")
    assert c >= 0
    assert not (c < 0)
    assert c < 256
    assert not (c >= 256)

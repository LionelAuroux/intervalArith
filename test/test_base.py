from itvArith import *
import logging

log = logging.getLogger(__name__)

def test_opebase():
    log.info("Here!!!")
    a = itvInt(3, 6)
    log.info(f"A = {a}")

def test_nbit():
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

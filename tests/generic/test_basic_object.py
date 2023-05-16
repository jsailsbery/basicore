import logging
from universal.generic import Basic

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_bfail():
    """Test Basic._bfail method"""
    basic = Basic()
    assert basic._bfail() is False
    assert basic._bfail(info="Info message") is False
    assert basic._bfail(error="Error message") is False
    assert basic._bfail(info="Info message", error="Error message") is False

def test_bpass():
    """Test Basic._bpass method"""
    basic = Basic()
    assert basic._bpass() is True
    assert basic._bpass(info="Info message") is True

def test_bfail_classmethod():
    """Test Basic.bfail class method"""
    assert Basic.bfail() is False
    assert Basic.bfail(info="Info message") is False
    assert Basic.bfail(error="Error message") is False
    assert Basic.bfail(info="Info message", error="Error message") is False

def test_sfail():
    """Test Basic.sfail class method"""
    assert Basic.sfail() == ""
    assert Basic.sfail(info="Info message") == ""

def test_ifail():
    """Test Basic.ifail class method"""
    assert Basic.ifail() == -1
    assert Basic.ifail(info="Info message") == -1

def test_nfail():
    """Test Basic.nfail class method"""
    assert Basic.nfail() is None
    assert Basic.nfail(info="Info message") is None

def test_bpass_classmethod():
    """Test Basic.bpass class method"""
    assert Basic.bpass() is True
    assert Basic.bpass(info="Info message") is True

def test_spass():
    """Test Basic.spass class method"""
    assert Basic.spass("Value") == "Value"
    assert Basic.spass("Value", info="Info message") == "Value"

def test_ipass():
    """Test Basic.ipass class method"""
    assert Basic.ipass(42) == 42
    assert Basic.ipass(42, info="Info message") == 42

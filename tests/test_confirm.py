import pytest
from ternexar.confirm import confirm_engine, ConfirmationMode

def test_confirm_minimal():
    result = confirm_engine.evaluate("ls")
    assert result.mode == ConfirmationMode.MINIMAL_CONFIRMATION.value

def test_confirm_standard():
    result = confirm_engine.evaluate("pip install rich")
    assert result.mode == ConfirmationMode.STANDARD_CONFIRMATION.value

def test_confirm_strong():
    result = confirm_engine.evaluate("sudo rm file")
    assert result.mode == ConfirmationMode.STRONG_CONFIRMATION.value

def test_confirm_refused():
    result = confirm_engine.evaluate("rm -rf /")
    assert result.mode == ConfirmationMode.REFUSED.value

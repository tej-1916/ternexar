import pytest
from unittest.mock import patch, MagicMock
from ternexar.do import handle_do, STRICT_ALLOWLIST

@pytest.fixture
def mock_ui():
    with patch("ternexar.do.ui") as mock:
        yield mock

@pytest.fixture
def mock_audit():
    with patch("ternexar.do.audit_manager") as mock:
        yield mock

@pytest.fixture
def mock_run():
    with patch("subprocess.run") as mock:
        mock.return_value = MagicMock(returncode=0, stdout="Success", stderr="")
        yield mock

def test_do_allowlisted(mock_run, mock_ui, mock_audit):
    # Test a clearly allowlisted command
    handle_do("ls -la")
    
    # Verify subprocess.run was called with shell=False
    mock_run.assert_called_once()
    args, kwargs = mock_run.call_args
    assert args[0] == ["ls", "-la"]
    assert kwargs["shell"] is False
    
    # Verify UI render
    mock_ui.render_execution_result.assert_called_once()

def test_do_not_allowlisted(mock_run, mock_ui, mock_audit):
    # Test a command NOT in allowlist
    handle_do("touch newfile")
    
    # Verify subprocess.run was NOT called
    mock_run.assert_not_called()
    
    # Verify refusal UI
    mock_ui.render_refusal.assert_called_once()
    args = mock_ui.render_refusal.call_args[0]
    assert "not in the strict v1.0 allowlist" in args[1]

def test_do_dangerous_risk(mock_run, mock_ui, mock_audit):
    # Test a MEDIUM risk command
    handle_do("pip install rich")
    
    mock_run.assert_not_called()
    mock_ui.render_refusal.assert_called_once()
    args = mock_ui.render_refusal.call_args[0]
    assert "Risk detected: MEDIUM" in args[1]

def test_do_blocked_risk(mock_run, mock_ui, mock_audit):
    # Test a BLOCKED command
    handle_do("rm -rf /")
    
    mock_run.assert_not_called()
    mock_ui.render_refusal.assert_called_once()
    args = mock_ui.render_refusal.call_args[0]
    assert "Risk detected: BLOCKED" in args[1]

def test_do_shell_injection(mock_run, mock_ui, mock_audit):
    # Test shell chaining
    handle_do("ls; rm -rf /")
    
    mock_run.assert_not_called()
    mock_ui.render_refusal.assert_called_once()
    args = mock_ui.render_refusal.call_args[0]
    assert "forbidden shell characters" in args[1]

def test_do_timeout(mock_run, mock_ui, mock_audit):
    import subprocess
    mock_run.side_effect = subprocess.TimeoutExpired(cmd="ls", timeout=10)
    
    handle_do("ls")
    
    mock_ui.render_execution_result.assert_called_once()
    args = mock_ui.render_execution_result.call_args[0]
    assert "timed out" in args[2] # stderr

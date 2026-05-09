import pytest
from unittest.mock import MagicMock, patch
from ternexar.version_check import handle_version_check, CheckStatus, version_check_registry
from ternexar.router import router, Intent

def test_version_check_registry_aliases():
    """Verify alias normalization in the registry."""
    assert version_check_registry.get_profile("python").id == "python3"
    assert version_check_registry.get_profile("python 3").id == "python3"
    assert version_check_registry.get_profile("node").id == "nodejs"
    assert version_check_registry.get_profile("npm").id == "npm"

def test_version_check_needs_verification():
    """Verify Codex and Claude Code return NEEDS_VERIFICATION."""
    with patch("ternexar.ui.ui.render_version_check_result") as mock_render:
        handle_version_check("codex")
        args, _ = mock_render.call_args
        assert args[0]["status"] == CheckStatus.NEEDS_VERIFICATION
        
        handle_version_check("claude code")
        args, _ = mock_render.call_args
        assert args[0]["status"] == CheckStatus.NEEDS_VERIFICATION

def test_version_check_unknown_tool():
    """Verify unknown tools return UNKNOWN_TOOL and execute nothing."""
    with patch("ternexar.ui.ui.render_version_check_result") as mock_render:
        handle_version_check("some-random-tool")
        args, _ = mock_render.call_args
        assert args[0]["status"] == CheckStatus.UNKNOWN_TOOL

@patch("shutil.which")
@patch("subprocess.run")
def test_version_check_installed(mock_run, mock_which):
    """Verify successful version check for installed tool."""
    mock_which.return_value = "/usr/bin/python3"
    mock_run.return_value = MagicMock(returncode=0, stdout="Python 3.12.3\n", stderr="")
    
    with patch("ternexar.ui.ui.render_version_check_result") as mock_render:
        handle_version_check("python3")
        args, _ = mock_render.call_args
        assert args[0]["status"] == CheckStatus.INSTALLED
        assert args[0]["version_output"] == "Python 3.12.3"
        assert args[0]["command"] == "python3 --version"
        
        # Verify safety constraints
        mock_run.assert_called_once_with(
            ["python3", "--version"],
            shell=False,
            capture_output=True,
            text=True,
            timeout=5
        )

@patch("shutil.which")
def test_version_check_not_installed(mock_which):
    """Verify behavior when tool is not installed."""
    mock_which.return_value = None
    
    with patch("ternexar.ui.ui.render_version_check_result") as mock_render:
        handle_version_check("python3")
        args, _ = mock_render.call_args
        assert args[0]["status"] == CheckStatus.NOT_INSTALLED

def test_router_version_check_classification():
    """Verify router classifies version check intents correctly."""
    assert router.classify_intent("check python version") == Intent.VERSION_CHECK
    assert router.classify_intent("is node installed?") == Intent.VERSION_CHECK
    assert router.classify_intent("check npm version") == Intent.VERSION_CHECK
    
    # Negative cases
    assert router.classify_intent("install python 3") == Intent.INSTALL_REQUEST
    assert router.classify_intent("ls -la") == Intent.DO

def test_router_extract_version_tool():
    """Verify tool extraction for version checks."""
    assert router.extract_version_check_tool("check python 3 version") == "python 3"
    assert router.extract_version_check_tool("is nodejs installed") == "nodejs"
    assert router.extract_version_check_tool("npm version") == "npm"

@patch("ternexar.operator.handle_version_check")
def test_operator_routing_version_check(mock_handle):
    """Verify operator routes version check intent correctly."""
    from ternexar.operator import route_operator_input
    
    with patch("ternexar.ui.ui.render_operator_routing_feedback"):
        route_operator_input("check python version")
        mock_handle.assert_called_once_with("python")

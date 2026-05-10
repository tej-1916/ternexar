import pytest
from unittest.mock import MagicMock, patch
from ternexar.installer_execute import installer_executor, InstallStatus
from ternexar.installer_profiles import ProfileStatus, InstallerProfile, PlatformProfile
from ternexar.version_check import CheckStatus
from ternexar.install_preflight import PreflightVerdict

@pytest.fixture
def mock_ui():
    with patch("ternexar.installer_execute.ui") as mock:
        yield mock

@pytest.fixture
def mock_subprocess():
    with patch("ternexar.installer_execute.subprocess.run") as mock:
        mock.return_value = MagicMock(returncode=0)
        yield mock

@pytest.fixture
def mock_typer():
    with patch("ternexar.installer_execute.typer") as mock:
        yield mock

@pytest.fixture
def mock_version_check():
    with patch("ternexar.installer_execute.get_version_check_data") as mock:
        yield mock

@pytest.fixture
def mock_profile_registry():
    with patch("ternexar.installer_execute.profile_registry") as mock:
        yield mock

def test_install_already_installed(mock_ui, mock_version_check, mock_profile_registry):
    mock_version_check.return_value = {
        "status": CheckStatus.INSTALLED,
        "normalized_tool": "Python 3",
        "version_output": "Python 3.10.12"
    }
    profile = MagicMock()
    profile.name = "Python 3"
    mock_profile_registry.get_profile.return_value = profile
    
    installer_executor.execute_install("python3")
    
    mock_ui.info.assert_any_call("Tool 'Python 3' is already installed (Python 3.10.12).")
    mock_ui.render_install_execution_header.assert_not_called()

def test_install_refused_unknown_tool(mock_ui, mock_version_check, mock_profile_registry):
    mock_version_check.return_value = {
        "status": CheckStatus.NOT_INSTALLED,
        "normalized_tool": "Unknown",
        "version_output": None,
        "notes": None
    }
    mock_profile_registry.get_profile.return_value = None
    
    installer_executor.execute_install("unknown-tool")
    
    mock_ui.error.assert_any_call("Installation refused: NOT_READY_UNKNOWN_TOOL")

def test_install_refused_needs_verification(mock_ui, mock_version_check, mock_profile_registry):
    mock_version_check.return_value = {
        "status": CheckStatus.NOT_INSTALLED,
        "normalized_tool": "OpenAI Codex",
        "version_output": None,
        "notes": None
    }
    profile = MagicMock(id="codex", name="OpenAI Codex", status=ProfileStatus.NEEDS_VERIFICATION)
    mock_profile_registry.get_profile.return_value = profile
    
    installer_executor.execute_install("codex")
    
    mock_ui.error.assert_any_call("Installation refused: NOT_READY_NEEDS_VERIFICATION")

def test_install_cancelled_at_first_confirmation(mock_ui, mock_version_check, mock_profile_registry, mock_typer):
    mock_version_check.return_value = {
        "status": CheckStatus.NOT_INSTALLED,
        "normalized_tool": "Python 3",
        "version_output": None,
        "notes": None
    }
    profile = MagicMock(id="python3", name="Python 3", status=ProfileStatus.AVAILABLE)
    profile.platforms = {"linux-apt": MagicMock(commands=["sudo apt update"])}
    mock_profile_registry.get_profile.return_value = profile
    mock_profile_registry.detect_os_key.return_value = "linux-apt"
    
    mock_typer.confirm.return_value = False
    
    installer_executor.execute_install("python3")
    
    mock_ui.info.assert_any_call("\n[dim]Installation cancelled by user.[/]")

def test_install_cancelled_at_strong_confirmation(mock_ui, mock_version_check, mock_profile_registry, mock_typer):
    mock_version_check.return_value = {
        "status": CheckStatus.NOT_INSTALLED,
        "normalized_tool": "Python 3",
        "version_output": None,
        "notes": None
    }
    profile = MagicMock(id="python3", name="Python 3", status=ProfileStatus.AVAILABLE)
    profile.platforms = {"linux-apt": MagicMock(commands=["sudo apt update"])}
    mock_profile_registry.get_profile.return_value = profile
    mock_profile_registry.detect_os_key.return_value = "linux-apt"
    
    mock_typer.confirm.return_value = True
    mock_typer.prompt.return_value = "WRONG STRING"
    
    installer_executor.execute_install("python3")
    
    mock_ui.error.assert_any_call("Confirmation string mismatch.")

def test_install_success_flow(mock_ui, mock_version_check, mock_profile_registry, mock_typer, mock_subprocess):
    # Setup
    mock_version_check.side_effect = [
        {"status": CheckStatus.NOT_INSTALLED, "normalized_tool": "Python 3", "version_output": None, "notes": None}, # Initial
        {"status": CheckStatus.INSTALLED, "normalized_tool": "Python 3", "version_output": "Python 3.10.12", "notes": None} # Post-install
    ]
    profile = MagicMock(id="python3", name="Python 3", status=ProfileStatus.AVAILABLE)
    profile.platforms = {"linux-apt": MagicMock(commands=["sudo apt update", "sudo apt install python3"])}
    mock_profile_registry.get_profile.return_value = profile
    mock_profile_registry.detect_os_key.return_value = "linux-apt"
    
    mock_typer.confirm.return_value = True
    mock_typer.prompt.return_value = "INSTALL PYTHON3"
    
    # Run
    installer_executor.execute_install("python3")
    
    # Assert
    assert mock_subprocess.call_count == 2
    mock_subprocess.assert_any_call(["sudo", "apt", "update"], shell=False, check=False, timeout=600)
    mock_subprocess.assert_any_call(["sudo", "apt", "install", "python3"], shell=False, check=False, timeout=600)
    mock_ui.render_install_result.assert_called_once()
    args, kwargs = mock_ui.render_install_result.call_args
    assert args[0] == InstallStatus.SUCCESS

def test_install_failure_stops_sequence(mock_ui, mock_version_check, mock_profile_registry, mock_typer, mock_subprocess):
    # Setup
    mock_version_check.return_value = {"status": CheckStatus.NOT_INSTALLED, "normalized_tool": "Python 3", "version_output": None, "notes": None}
    profile = MagicMock(id="python3", name="Python 3", status=ProfileStatus.AVAILABLE)
    profile.platforms = {"linux-apt": MagicMock(commands=["sudo apt update", "sudo apt install python3"])}
    mock_profile_registry.get_profile.return_value = profile
    mock_profile_registry.detect_os_key.return_value = "linux-apt"
    
    mock_typer.confirm.return_value = True
    mock_typer.prompt.return_value = "INSTALL PYTHON3"
    
    # Mock failure on first command
    mock_subprocess.return_value = MagicMock(returncode=1)
    
    # Run
    installer_executor.execute_install("python3")
    
    # Assert
    assert mock_subprocess.call_count == 1 # Stopped after first failure
    mock_ui.render_install_result.assert_called_once()
    args, kwargs = mock_ui.render_install_result.call_args
    assert args[0] == InstallStatus.FAILED

def test_install_safety_violation_in_profile(mock_ui, mock_version_check, mock_profile_registry, mock_typer, mock_subprocess):
    # This shouldn't happen with verified profiles, but test the guard anyway
    mock_version_check.return_value = {"status": CheckStatus.NOT_INSTALLED, "normalized_tool": "Python 3", "version_output": None, "notes": None}
    profile = MagicMock(id="python3", name="Python 3", status=ProfileStatus.AVAILABLE)
    profile.platforms = {"linux-apt": MagicMock(commands=["sudo apt update && rm -rf /"])} # Unsafe metacharacter
    mock_profile_registry.get_profile.return_value = profile
    mock_profile_registry.detect_os_key.return_value = "linux-apt"
    
    mock_typer.confirm.return_value = True
    mock_typer.prompt.return_value = "INSTALL PYTHON3"
    
    installer_executor.execute_install("python3")
    
    # It fails at preflight because gate_engine detects the block
    mock_ui.error.assert_any_call("Installation refused: REFUSED")
    mock_subprocess.assert_not_called()

import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch
from ternexar.workspace_config import WorkspaceConfig
from ternexar.router import Router, Intent

@pytest.fixture
def workspace_config():
    return WorkspaceConfig()

@pytest.fixture
def router():
    return Router()

def test_validate_path_safe(workspace_config, tmp_path):
    # Mock Path.home() to return a temp directory
    with patch("pathlib.Path.home", return_value=tmp_path):
        project_dir = tmp_path / "my-project"
        project_dir.mkdir()
        is_safe, reason = workspace_config.validate_path(str(project_dir))
        assert is_safe
        assert "safe" in reason.lower()

def test_validate_path_outside_home(workspace_config, tmp_path):
    home_dir = tmp_path / "home"
    home_dir.mkdir()
    other_dir = tmp_path / "other"
    other_dir.mkdir()
    
    with patch("pathlib.Path.home", return_value=home_dir):
        is_safe, reason = workspace_config.validate_path(str(other_dir))
        assert not is_safe
        assert "home directory" in reason

def test_validate_path_system(workspace_config, tmp_path):
    with patch("pathlib.Path.home", return_value=tmp_path):
        is_safe, reason = workspace_config.validate_path("/etc")
        assert not is_safe
        assert "protected" in reason

def test_validate_path_hidden(workspace_config, tmp_path):
    with patch("pathlib.Path.home", return_value=tmp_path):
        hidden_dir = tmp_path / ".hidden"
        hidden_dir.mkdir()
        is_safe, reason = workspace_config.validate_path(str(hidden_dir))
        assert not is_safe
        assert "Hidden" in reason

def test_validate_path_sensitive_pattern(workspace_config, tmp_path):
    with patch("pathlib.Path.home", return_value=tmp_path):
        node_modules_dir = tmp_path / "project" / "node_modules"
        node_modules_dir.mkdir(parents=True)
        is_safe, reason = workspace_config.validate_path(str(node_modules_dir))
        assert not is_safe
        assert "node_modules" in reason

def test_router_locate_intent(router):
    assert router.classify_intent("find my project") == Intent.LOCATE
    assert router.classify_intent("where is my website") == Intent.LOCATE
    assert router.classify_intent("locate ternexar") == Intent.LOCATE
    assert router.classify_intent("show files in car-rental") == Intent.LOCATE

def test_router_not_locate_intent(router):
    assert router.classify_intent("what is a project?") == Intent.ASK
    assert router.classify_intent("ls -la") == Intent.DO

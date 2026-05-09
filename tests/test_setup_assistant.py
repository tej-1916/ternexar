import pytest
from pathlib import Path
from ternexar.setup_assistant import setup_assistant

def test_python_setup_preview(tmp_path):
    (tmp_path / "pyproject.toml").write_text("[project]")
    (tmp_path / "README.md").write_text("# Test Project")
    
    preview = setup_assistant.get_preview(str(tmp_path))
    assert preview["project_type"] == "PYTHON"
    assert "pyproject.toml" in preview["important_files"]
    
    commands = [s["command"] for s in preview["steps"]]
    assert "python3 -m venv .venv" in commands
    assert "source .venv/bin/activate" in commands
    assert "pip install -e ." in commands
    
    # Check risk levels
    pip_step = next(s for s in preview["steps"] if "pip install" in s["command"])
    assert pip_step["risk_level"] == "MEDIUM"
    assert pip_step["status"] == "PREVIEW_ONLY"
    
    source_step = next(s for s in preview["steps"] if "source " in s["command"])
    assert source_step["status"] == "SHELL_INSTRUCTION"

def test_node_setup_preview(tmp_path):
    (tmp_path / "package.json").write_text('{"scripts": {"test": "jest", "dev": "vite"}}')
    
    preview = setup_assistant.get_preview(str(tmp_path))
    assert preview["project_type"] == "NODE"
    
    commands = [s["command"] for s in preview["steps"]]
    assert "npm install" in commands
    assert "npm test" in commands
    assert "npm run dev" in commands
    
    install_step = next(s for s in preview["steps"] if "npm install" in s["command"])
    assert install_step["risk_level"] == "MEDIUM"

def test_rust_setup_preview(tmp_path):
    (tmp_path / "Cargo.toml").write_text("[package]")
    
    preview = setup_assistant.get_preview(str(tmp_path))
    assert preview["project_type"] == "RUST"
    assert "cargo build" in [s["command"] for s in preview["steps"]]

def test_static_web_setup_preview(tmp_path):
    (tmp_path / "index.html").write_text("<html></html>")
    
    preview = setup_assistant.get_preview(str(tmp_path))
    assert preview["project_type"] == "STATIC_WEB"
    recommendation = next(s for s in preview["steps"] if s["status"] == "RECOMMENDATION")
    assert "index.html" in recommendation["command"]

def test_unsafe_path_refusal():
    preview = setup_assistant.get_preview("/etc")
    assert "error" in preview
    assert "protected or unsafe" in preview["error"]

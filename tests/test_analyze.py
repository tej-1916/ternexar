import pytest
from pathlib import Path
from ternexar.analyze import Analyzer

@pytest.mark.parametrize("task,expected_module", [
    ("ModuleNotFoundError: No module named requests", "requests"),
    ("ModuleNotFoundError: No module named 'requests'", "requests"),
    ("ImportError: No module named requests", "requests"),
    ("ImportError: No module named 'requests'", "requests"),
    ("ImportError: No module named \"flask\"", "flask"),
])
def test_analyzer_detect_missing_module_variants(task, expected_module):
    analyzer = Analyzer()
    result = analyzer.analyze(task)
    
    assert result.detected_issue is not None
    assert expected_module in result.detected_issue
    assert result.proposed_file.name == "requirements.txt"
    assert expected_module in result.proposed_content
    assert result.safety_verdict == "SAFE"

def test_analyzer_vague_import_error():
    analyzer = Analyzer()
    task = "fix import error in app.py"
    result = analyzer.analyze(task)
    
    # Should not detect a module and thus not propose a requirements.txt patch
    assert result.detected_issue == "No deterministic fix found for this issue."
    assert result.safety_verdict == "REFUSED"
    assert result.proposed_content is None

def test_analyzer_blocked_action():
    analyzer = Analyzer()
    task = "delete all files in src"
    result = analyzer.analyze(task)
    
    assert result.safety_verdict == "BLOCKED"
    assert "deletion" in result.reason

def test_analyzer_unsupported_fix():
    analyzer = Analyzer()
    task = "Optimize my database queries"
    result = analyzer.analyze(task)
    
    assert result.safety_verdict == "REFUSED"
    assert "only supports simple Python dependency fixes" in result.reason

def test_analyzer_generate_requirements_patch(tmp_path):
    analyzer = Analyzer(project_root=tmp_path)
    req_file = tmp_path / "requirements.txt"
    req_file.write_text("flask==2.0.1\n")
    
    new_content = analyzer._generate_requirements_patch("requests")
    assert "flask==2.0.1" in new_content
    assert "requests" in new_content
    assert new_content.endswith("\n")

def test_analyzer_generate_requirements_patch_new_file(tmp_path):
    analyzer = Analyzer(project_root=tmp_path)
    # requirements.txt does not exist
    
    new_content = analyzer._generate_requirements_patch("requests")
    assert new_content == "requests\n"

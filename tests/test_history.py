import pytest
from unittest.mock import patch, mock_open
from pathlib import Path
from ternexar.history import redact_command, read_bash_history, read_zsh_history, get_recent_history

def test_redact_command():
    # Password redaction
    assert redact_command("git login -p secret123") == "git login -p [REDACTED]"
    assert redact_command("mysql --password=mypass") == "mysql --password=[REDACTED]"
    
    # API Key redaction
    assert redact_command("export API_KEY=sk-12345") == "export API_KEY=[REDACTED]"
    assert redact_command("set token: abcdef") == "set token: [REDACTED]"
    
    # Auth header redaction
    assert redact_command("curl -H 'Authorization: Bearer xyz123' http://api.com") == "curl -H 'Authorization: Bearer [REDACTED]' http://api.com"
    
    # Mix
    cmd = "curl -H 'Authorization: Bearer xyz' -p pass123"
    redacted = redact_command(cmd)
    assert "[REDACTED]" in redacted
    assert "xyz" not in redacted
    assert "pass123" not in redacted

@patch("pathlib.Path.home")
def test_read_bash_history_missing(mock_home):
    mock_home.return_value = Path("/nonexistent")
    assert read_bash_history() == []

@patch("pathlib.Path.home")
@patch("builtins.open", new_callable=mock_open, read_data="ls -la\ncd src\nexport KEY=secret\n")
def test_read_bash_history_success(mock_file, mock_home):
    mock_home.return_value = Path("/home/user")
    # Mocking Path.exists for the history file
    with patch("pathlib.Path.exists") as mock_exists:
        mock_exists.return_value = True
        history = read_bash_history(limit=5)
        assert len(history) == 3
        assert history[0] == "ls -la"
        assert history[2] == "export KEY=[REDACTED]"

@patch("pathlib.Path.home")
@patch("builtins.open", new_callable=mock_open, read_data=b": 1686300000:0;ls\n: 1686300001:0;git commit -m 'feat'\n")
def test_read_zsh_history_success(mock_file, mock_home):
    mock_home.return_value = Path("/home/user")
    with patch("pathlib.Path.exists") as mock_exists:
        mock_exists.return_value = True
        history = read_zsh_history(limit=5)
        assert len(history) == 2
        assert history[0] == "ls"
        assert history[1] == "git commit -m 'feat'"

def test_get_recent_history_integration():
    with patch("ternexar.history.read_bash_history") as mock_bash, \
         patch("ternexar.history.read_zsh_history") as mock_zsh:
        mock_bash.return_value = ["bash1", "bash2"]
        mock_zsh.return_value = ["zsh1", "zsh2"]
        
        history = get_recent_history(limit=3)
        assert len(history) == 3
        # Should take last 3 from combined [bash1, bash2, zsh1, zsh2]
        assert history == ["bash2", "zsh1", "zsh2"]

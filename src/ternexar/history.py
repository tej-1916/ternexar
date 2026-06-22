import os
import re
from pathlib import Path
from typing import List

# Common patterns for sensitive data
REDACTION_PATTERNS = [
    # Passwords in commands
    (r"(-p\s+|--password[= ])([^\s]+)", r"\1[REDACTED]"),
    # API Keys and Tokens (generic assignment)
    (r"(?i)(api[_-]?key|token|secret|password|auth|key)([=:][\s]*)([^\s&\"']+)", r"\1\2[REDACTED]"),
    # Authorization headers
    (r"(?i)(Authorization:\s*)(Bearer|Basic)\s+([^\s\"']+)", r"\1\2 [REDACTED]"),
    # Private keys (simplified)
    (r"-----BEGIN [A-Z ]+ PRIVATE KEY-----[\s\S]+?-----END [A-Z ]+ PRIVATE KEY-----", "[PRIVATE KEY REDACTED]"),
    # Common cloud provider CLI secrets
    (r"(--access-key|--secret-key|--api-key)([= ])([^\s]+)", r"\1\2[REDACTED]"),
]

def redact_command(command: str) -> str:
    """Redacts sensitive information from a command string."""
    redacted = command
    for pattern, replacement in REDACTION_PATTERNS:
        redacted = re.sub(pattern, replacement, redacted)
    return redacted

def read_bash_history(limit: int = 20) -> List[str]:
    """Reads the last N commands from ~/.bash_history."""
    history_path = Path.home() / ".bash_history"
    if not history_path.exists():
        return []
    
    try:
        with open(history_path, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()
            return [redact_command(line.strip()) for line in lines[-limit:] if line.strip()]
    except Exception:
        return []

def read_zsh_history(limit: int = 20) -> List[str]:
    """Reads the last N commands from ~/.zsh_history.
    Handles ZSH extended history format ': 1686300000:0;command'.
    """
    history_path = Path.home() / ".zsh_history"
    if not history_path.exists():
        return []

    try:
        commands = []
        with open(history_path, "rb") as f:
            # ZSH history can contain null bytes or weird encoding
            content = f.read().decode("utf-8", errors="ignore")
            lines = content.splitlines()
            
            for line in lines[-limit:]:
                if not line.strip():
                    continue
                # Match ': 1234567890:0;command'
                match = re.match(r"^:\s*\d+:\d+;(.*)$", line)
                if match:
                    cmd = match.group(1)
                else:
                    cmd = line
                commands.append(redact_command(cmd.strip()))
        return commands
    except Exception:
        return []

def get_recent_history(limit: int = 10) -> List[str]:
    """Combines and returns recent history from available shells."""
    # We take slightly more than limit from each to ensure we have enough after merging/filtering
    # but for now simple concatenation is fine as a heuristic
    bash = read_bash_history(limit)
    zsh = read_zsh_history(limit)
    
    # Return zsh first as it's more common on macOS/modern Linux, then bash
    # and truncate to the requested limit from the end
    combined = (bash + zsh)[-limit:]
    return combined

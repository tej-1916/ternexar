import re
import os
from enum import Enum
from typing import Optional, List, Tuple
from pathlib import Path

from ternexar.risk import risk_engine, RiskLevel
from ternexar.do import is_in_allowlist
from ternexar.ui import ui

SAFE_EXTENSIONS = {".py", ".md", ".toml", ".txt", ".json", ".yaml", ".yml"}
SENSITIVE_KEYWORDS = {"secret", "token", "key", "password"}
MAX_FILE_SIZE = 100 * 1024  # 100 KB

class Intent(Enum):
    DO = "DO"
    ASK = "ASK"
    PLAN = "PLAN"
    PREVIEW = "PREVIEW"
    LOCATE = "LOCATE"
    REFUSE = "REFUSE"
    UNKNOWN = "UNKNOWN"

class Router:
    def __init__(self):
        self.question_starters = {"what", "how", "explain", "why", "who", "where", "when", "can", "is", "are"}
        self.install_keywords = {"install", "setup", "build", "npm", "pip", "cargo", "yarn", "brew", "apt"}
        self.locate_keywords = {"find", "locate", "where", "search", "show project", "show files"}

    def classify_intent(self, text: str) -> Intent:
        """Classify user intent based on heuristics and safety checks."""
        clean_text = text.strip().lower()
        if not clean_text:
            return Intent.UNKNOWN

        # 1. Check for dangerous (HIGH/BLOCKED) input first
        analysis = risk_engine.analyze(text)
        if analysis.level in [RiskLevel.HIGH, RiskLevel.BLOCKED]:
            return Intent.REFUSE

        # 2. Check for locate keywords
        if any(clean_text.startswith(kw) for kw in self.locate_keywords):
            return Intent.LOCATE
        if "my" in clean_text and "project" in clean_text:
            return Intent.LOCATE

        # 3. Check for raw LOW allowlisted command
        if is_in_allowlist(text):
            return Intent.DO

        # 4. Check for install/setup keywords (route to PREVIEW)
        if any(keyword in clean_text for keyword in self.install_keywords):
            return Intent.PREVIEW

        # 5. Check for questions
        first_word = clean_text.split()[0] if clean_text.split() else ""
        if first_word in self.question_starters or clean_text.endswith("?"):
            return Intent.ASK

        # 6. Default to PLAN for general tasks
        return Intent.PLAN

    def resolve_context(self, text: str) -> Tuple[str, List[str]]:
        """Extract @file references and validate them for safety."""
        pattern = r"(?:^|\s)@([\w\.\-/]+)"
        matches = re.findall(pattern, text)
        
        valid_context = []
        cleaned_text = text
        
        for path_str in matches:
            file_path = Path(path_str).resolve()
            
            # Remove the @path from the text to avoid redundancy
            cleaned_text = cleaned_text.replace(f"@{path_str}", "").strip()

            # Safety Checks
            if not file_path.exists():
                ui.warning(f"File not found: @{path_str}")
                continue
            
            if not file_path.is_file():
                ui.warning(f"Not a file: @{path_str}")
                continue

            # 1. Hidden files / sensitive folders
            if file_path.name.startswith(".") or ".git" in file_path.parts or ".ssh" in file_path.parts:
                ui.warning(f"Access denied to hidden or sensitive path: @{path_str}")
                continue

            # 2. Extension check
            if file_path.suffix.lower() not in SAFE_EXTENSIONS:
                ui.warning(f"Unsupported file type: @{path_str} (Allowed: {', '.join(SAFE_EXTENSIONS)})")
                continue

            # 3. Sensitive keywords in filename
            if any(kw in file_path.name.lower() for kw in SENSITIVE_KEYWORDS):
                ui.warning(f"Sensitive filename blocked: @{path_str}")
                continue

            # 4. Size limit
            if file_path.stat().st_size > MAX_FILE_SIZE:
                ui.warning(f"File too large: @{path_str} (Max 100KB)")
                continue

            # 5. Outside project check (basic check against CWD)
            try:
                file_path.relative_to(Path.cwd())
            except ValueError:
                ui.warning(f"Access denied: @{path_str} is outside the project directory.")
                continue

            # Read content
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    valid_context.append(f"[CONTEXT: @{path_str}]\n{content}")
            except Exception as e:
                ui.warning(f"Failed to read @{path_str}: {str(e)}")

        return cleaned_text, valid_context

router = Router()

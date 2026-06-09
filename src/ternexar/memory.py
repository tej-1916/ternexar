import json
import os
import copy
from pathlib import Path
from typing import List, Dict, Optional, Any

MEMORY_DIR = Path(".ternexar")
MEMORY_FILE = MEMORY_DIR / "error-memory.json"

DEFAULT_MEMORY = {
    "project": "TERNEXAR",
    "engine": "AutoFix Engine v1",
    "errors": []
}

class ErrorMemory:
    def __init__(self, memory_file: Optional[Path] = None):
        self.memory_file = memory_file or MEMORY_FILE
        self._data: Dict[str, Any] = copy.deepcopy(DEFAULT_MEMORY)
        self.load()

    def load(self) -> bool:
        """Loads memory from JSON file. Returns True if successful."""
        if not self.memory_file.exists():
            self._ensure_dir()
            self.save()
            return True

        try:
            with open(self.memory_file, "r") as f:
                data = json.load(f)
                if self._validate(data):
                    self._data = data
                    return True
                else:
                    # If invalid but readable, we keep defaults but don't overwrite yet
                    return False
        except (json.JSONDecodeError, IOError):
            # Return False on broken JSON
            return False

    def save(self) -> bool:
        """Saves current memory to JSON file."""
        try:
            self._ensure_dir()
            with open(self.memory_file, "w") as f:
                json.dump(self._data, f, indent=2)
            return True
        except IOError:
            return False

    def _ensure_dir(self):
        """Ensures the memory directory exists."""
        self.memory_file.parent.mkdir(parents=True, exist_ok=True)

    def _validate(self, data: Any) -> bool:
        """Validates the basic structure of the memory JSON."""
        if not isinstance(data, dict):
            return False
        if "errors" not in data or not isinstance(data["errors"], list):
            return False
        return True

    def search_errors(self, query: str) -> List[Dict[str, Any]]:
        """Searches for errors by type, command, or error text (partial match)."""
        query = query.lower()
        results = []
        for err in self._data.get("errors", []):
            if (query in err.get("type", "").lower() or 
                query in err.get("command", "").lower() or 
                query in err.get("error", "").lower()):
                results.append(err)
        return results

    def append_error(self, error_type: str, command: str, error_msg: str, 
                     safe_checks: Optional[List[str]] = None, 
                     avoid: Optional[List[str]] = None):
        """Appends a new error record to the memory."""
        new_record = {
            "type": error_type,
            "command": command,
            "error": error_msg,
            "safe_checks": safe_checks or [],
            "avoid": avoid or []
        }
        self._data["errors"].append(new_record)
        self.save()

    @property
    def data(self) -> Dict[str, Any]:
        return self._data

import os
from pathlib import Path
from typing import List, Tuple
from ternexar.config import config_manager

UNSAFE_PATHS = [
    "/", "/etc", "/usr", "/var", "/proc", "/sys", "/dev", "/bin", "/sbin", "/lib", "/root", "/boot"
]

FORBIDDEN_PATTERNS = [".git", "node_modules", "venv", ".venv", ".ssh", ".gnupg"]

class WorkspaceConfig:
    def validate_path(self, path_str: str) -> Tuple[bool, str]:
        """Strictly validate if a path is safe to be added as a workspace root."""
        try:
            path = Path(path_str).expanduser().resolve()
        except Exception as e:
            return False, f"Invalid path format: {str(e)}"

        # 1. Existence and Type
        if not path.exists():
            return False, "Path does not exist."
        if not path.is_dir():
            return False, "Path is not a directory."

        abs_path = str(path)
        home_path = str(Path.home().resolve())

        # 2. System Paths
        for unsafe in UNSAFE_PATHS:
            if abs_path == unsafe or abs_path.startswith(f"{unsafe}/"):
                # Always refuse system paths, even if they are under /home (unlikely but safe)
                if not abs_path.startswith(home_path):
                    return False, f"System path '{unsafe}' is protected and refused."

        # 3. Home Directory Restriction (Strict for v1.4)
        if not abs_path.startswith(home_path):
            return False, "Workspace roots must be located within the user's home directory."

        # 4. Sensitive/Hidden Directories
        if path.name.startswith(".") or any(part.startswith(".") for part in path.parts):
             return False, "Hidden directories are refused for safety."

        for pattern in FORBIDDEN_PATTERNS:
            if pattern in path.parts or any(pattern in part for part in path.parts):
                return False, f"Paths containing '{pattern}' are sensitive and refused."

        return True, "Path is safe."

    def add_root(self, path_str: str) -> Tuple[bool, str]:
        """Add a validated path to the workspace roots."""
        is_safe, reason = self.validate_path(path_str)
        if not is_safe:
            return False, reason

        path = Path(path_str).expanduser().resolve()
        abs_path = str(path)

        config = config_manager.load()
        roots = config.get("workspaces", {}).get("roots", [])

        if abs_path in roots:
            return False, "Path is already a workspace root."

        # Check for redundancy (is it a subpath of an existing root or vice versa?)
        for existing in roots:
            existing_path = Path(existing)
            if path == existing_path:
                return False, "Path is already a workspace root."
            if path in existing_path.parents:
                # New path is a parent of an existing root. We could replace it, but for safety, just skip.
                return False, f"Path is a parent of existing root: {existing}"
            if existing_path in path.parents:
                return False, f"Path is already covered by root: {existing}"

        roots.append(abs_path)
        config["workspaces"]["roots"] = roots
        config_manager.save(config)
        return True, abs_path

    def remove_root(self, path_str: str) -> Tuple[bool, str]:
        """Remove a path from workspace roots."""
        try:
            path = Path(path_str).expanduser().resolve()
            abs_path = str(path)
        except Exception:
            abs_path = path_str

        config = config_manager.load()
        roots = config.get("workspaces", {}).get("roots", [])

        if abs_path not in roots:
            return False, "Path not found in workspace roots."

        roots.remove(abs_path)
        config["workspaces"]["roots"] = roots
        config_manager.save(config)
        return True, abs_path

    def get_roots(self) -> List[str]:
        """Return the current list of workspace roots."""
        config = config_manager.load()
        return config.get("workspaces", {}).get("roots", [])

    def clear_roots(self):
        """Clear all custom workspace roots."""
        config = config_manager.load()
        config["workspaces"]["roots"] = []
        config_manager.save(config)

workspace_config = WorkspaceConfig()

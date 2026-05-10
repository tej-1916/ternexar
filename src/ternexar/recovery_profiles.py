from enum import Enum
from typing import List, Optional, Dict, Pattern
import re

class RecoveryDomain(Enum):
    APT = "APT_PACKAGE_MANAGER"
    NPM = "NPM_NODE"
    PYTHON = "PYTHON_PIP"
    GIT = "GIT"
    FILESYSTEM = "FILESYSTEM_PATH"
    PERMISSION = "PERMISSION"
    PORT = "PORT_IN_USE"
    SERVICE = "SERVICE_FAILURE"
    INSTALLER = "INSTALLER_FAILURE"
    UNKNOWN = "UNKNOWN"
    DESTRUCTIVE = "BLOCKED_DESTRUCTIVE_REQUEST"

class RecoveryProfile:
    def __init__(
        self,
        id: str,
        domain: RecoveryDomain,
        signatures: List[str],
        explanation: str,
        repair_plan: List[str],
        diff_template: Optional[str] = None
    ):
        self.id = id
        self.domain = domain
        self.signatures = signatures
        self.explanation = explanation
        self.repair_plan = repair_plan
        self.diff_template = diff_template

    def matches(self, text: str) -> bool:
        for sig in self.signatures:
            if re.search(sig, text, re.IGNORECASE):
                return True
        return False

RECOVERY_PROFILES = [
    # 1. APT Profiles
    RecoveryProfile(
        id="APT_SIGNED_BY_CONFLICT",
        domain=RecoveryDomain.APT,
        signatures=[
            r"Conflicting values set for option Signed-By",
            r"The list of sources could not be read"
        ],
        explanation="APT repository appears more than once with conflicting Signed-By keyring paths. This usually happens when a third-party repo is added multiple times with different security settings.",
        repair_plan=[
            "Locate matching source entries in /etc/apt/sources.list.d/",
            "Identify the duplicate entry with the conflicting 'signed-by' flag",
            "Comment out or remove the duplicate line",
            "Run 'sudo apt update' to verify"
        ],
        diff_template="- deb [signed-by=/usr/share/keyrings/old.gpg] https://repo.example.com/ stable main\n+ # deb [signed-by=/usr/share/keyrings/old.gpg] https://repo.example.com/ stable main"
    ),
    RecoveryProfile(
        id="APT_MALFORMED_ENTRY",
        domain=RecoveryDomain.APT,
        signatures=[
            r"Malformed entry",
            r"Malformed line \d+ in source list"
        ],
        explanation="A line in your APT sources list has a syntax error (e.g., missing components or incorrect format).",
        repair_plan=[
            "Identify the file and line number mentioned in the error",
            "Review the syntax (deb [options] url suite components)",
            "Correct the malformed line or comment it out",
            "Run 'sudo apt update' to verify"
        ]
    ),

    # 2. Python Profiles
    RecoveryProfile(
        id="PYTHON_MODULE_NOT_FOUND",
        domain=RecoveryDomain.PYTHON,
        signatures=[
            r"ModuleNotFoundError: No module named",
            r"ImportError: No module named"
        ],
        explanation="The application is trying to import a Python module that is not installed in the current environment.",
        repair_plan=[
            "Identify the missing package name",
            "Use 'tx analyze' to safely propose a requirements.txt update",
            "Manually install the package if not using a venv: pip install <package>"
        ]
    ),

    # 3. NPM Profiles
    RecoveryProfile(
        id="NPM_MISSING_PACKAGE_JSON",
        domain=RecoveryDomain.NPM,
        signatures=[
            r"npm ERR! enoent Could not read package.json",
            r"no such file or directory, open .*package.json"
        ],
        explanation="The npm command was executed in a directory that does not contain a package.json file.",
        repair_plan=[
            "Ensure you are in the correct project root directory",
            "Use 'tx locate' to find your project if you are lost",
            "Run 'npm init' if you intended to start a new project"
        ]
    ),
    RecoveryProfile(
        id="NPM_DEPENDENCY_CONFLICT",
        domain=RecoveryDomain.NPM,
        signatures=[
            r"npm ERR! ERESOLVE",
            r"could not resolve dependency",
            r"Conflicting peer dependency"
        ],
        explanation="npm cannot resolve a version conflict between project dependencies or peer dependencies.",
        repair_plan=[
            "Review the dependency tree mentioned in the error",
            "Consider using --force or --legacy-peer-deps if the conflict is minor",
            "Update package.json to use compatible versions"
        ]
    ),

    # 4. Git Profiles
    RecoveryProfile(
        id="GIT_NOT_REPOSITORY",
        domain=RecoveryDomain.GIT,
        signatures=[
            r"fatal: not a git repository"
        ],
        explanation="The current folder is not managed by Git, or you are outside the repository tree.",
        repair_plan=[
            "Use 'tx locate' to find the actual repository root",
            "Run 'git init' if you want to start tracking this folder"
        ]
    ),
    RecoveryProfile(
        id="GIT_MERGE_CONFLICT",
        domain=RecoveryDomain.GIT,
        signatures=[
            r"CONFLICT \(content\): Merge conflict",
            r"Automatic merge failed; fix conflicts and then commit"
        ],
        explanation="Git found overlapping changes during a merge or pull that it cannot resolve automatically.",
        repair_plan=[
            "Identify unmerged paths using 'git status'",
            "Open conflicted files and look for '<<<<<<<', '=======', and '>>>>>>>' markers",
            "Resolve the markers and 'git add' the fixed files",
            "Run 'git commit' to complete the merge"
        ]
    ),

    # 5. Permission & System Profiles
    RecoveryProfile(
        id="PERMISSION_DENIED",
        domain=RecoveryDomain.PERMISSION,
        signatures=[
            r"Permission denied",
            r"EACCES",
            r"operation not permitted"
        ],
        explanation="The current user does not have sufficient permissions to read, write, or execute the requested path.",
        repair_plan=[
            "Check current file ownership: ls -l <path>",
            "Review if you should be running the command with 'sudo' (use caution)",
            "Do NOT use 'chmod 777'; instead, adjust ownership or specific permissions"
        ]
    ),
    RecoveryProfile(
        id="PORT_IN_USE",
        domain=RecoveryDomain.PORT,
        signatures=[
            r"address already in use",
            r"EADDRINUSE",
            r"port \d+ already in use"
        ],
        explanation="The network port the application is trying to bind to is already occupied by another process.",
        repair_plan=[
            "Identify the process using the port (e.g., 'ss -lptn 'port <number>')",
            "Stop the conflicting service or use a different port in your application configuration",
            "Do not kill processes unless you are sure they are safe to stop"
        ]
    ),
    RecoveryProfile(
        id="FILE_NOT_FOUND",
        domain=RecoveryDomain.FILESYSTEM,
        signatures=[
            r"No such file or directory",
            r"FileNotFoundError"
        ],
        explanation="The application tried to access a file or path that does not exist.",
        repair_plan=[
            "Verify the path spelling and absolute/relative context",
            "Use 'tx view' or 'tx scan' to explore the current workspace structure",
            "Ensure required configuration or data files have been created"
        ]
    )
]

def classify_error(text: str) -> RecoveryProfile:
    """Matches text against deterministic recovery profiles."""
    for profile in RECOVERY_PROFILES:
        if profile.matches(text):
            return profile
    
    return RecoveryProfile(
        id="UNKNOWN_FAILURE",
        domain=RecoveryDomain.UNKNOWN,
        signatures=[],
        explanation="No verified recovery profile matches this error. It may be a unique failure or outside current deterministic scope.",
        repair_plan=[
            "Review the error message carefully",
            "Check project documentation or online resources",
            "Consult 'tx ask' for general troubleshooting advice"
        ]
    )

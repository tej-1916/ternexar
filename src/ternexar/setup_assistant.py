import json
from typing import List, Dict
from pathlib import Path
from ternexar.workspace import workspace_manager
from ternexar.gate import gate_engine

class SetupAssistant:
    def get_preview(self, path: str) -> Dict:
        """Analyze project and generate a safe setup preview."""
        scan_data = workspace_manager.scan(path)
        if "error" in scan_data:
            return scan_data

        project_type = scan_data.get("project_type", "UNKNOWN")
        important_files = scan_data.get("important_files", [])
        root_path = Path(scan_data["path"])
        
        steps = []
        
        if project_type == "PYTHON":
            if "pyproject.toml" in important_files:
                steps.append("python3 -m venv .venv")
                steps.append("source .venv/bin/activate")
                steps.append("pip install -e .")
            elif "requirements.txt" in important_files:
                steps.append("python3 -m venv .venv")
                steps.append("source .venv/bin/activate")
                steps.append("pip install -r requirements.txt")
        elif project_type == "NODE":
            if "package.json" in important_files:
                steps.append("npm install")
                
                # Simple script detection
                pkg_path = root_path / "package.json"
                if workspace_manager.is_file_safe(pkg_path):
                    try:
                        pkg_data = json.loads(pkg_path.read_text())
                        scripts = pkg_data.get("scripts", {})
                        if "test" in scripts:
                            steps.append("npm test")
                        if "dev" in scripts:
                            steps.append("npm run dev")
                    except Exception:
                        pass
        elif project_type == "RUST":
            steps.append("cargo build")
            steps.append("cargo test")
        elif project_type == "GO":
            steps.append("go mod download")
            steps.append("go test ./...")
        elif project_type == "JAVA":
            if "pom.xml" in important_files:
                steps.append("mvn test")
            elif "build.gradle" in important_files:
                steps.append("./gradlew test")
        elif project_type == "STATIC_WEB":
            steps.append("# Recommendation: Open index.html manually in your browser.")
            
        evaluated_steps = []
        for cmd in steps:
            if cmd.startswith("#"):
                evaluated_steps.append({
                    "command": cmd,
                    "risk_level": "INFO",
                    "gate_decision": "PASS",
                    "status": "RECOMMENDATION"
                })
                continue
                
            gate_result = gate_engine.evaluate(cmd)
            
            # source .venv/bin/activate is informational shell instruction
            status = "PREVIEW_ONLY"
            if cmd.startswith("source "):
                status = "SHELL_INSTRUCTION"
            
            evaluated_steps.append({
                "command": cmd,
                "risk_level": gate_result.risk_level.value,
                "gate_decision": gate_result.gate_decision.value,
                "status": status
            })
            
        return {
            "path": scan_data["path"],
            "project_type": project_type,
            "important_files": scan_data["important_files"],
            "steps": evaluated_steps
        }

setup_assistant = SetupAssistant()

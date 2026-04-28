import shutil
import requests
from dataclasses import dataclass
from typing import Optional

@dataclass
class StatusResult:
    name: str
    success: bool
    message: str
    fix_command: Optional[str] = None
    warning: bool = False
    skipped: bool = False

class HealthChecker:
    def check_ollama_binary(self) -> StatusResult:
        """Checks if ollama is in the system $PATH."""
        path = shutil.which("ollama")
        if path:
            return StatusResult("Ollama Binary", True, f"Found at {path}")
        return StatusResult(
            "Ollama Binary", 
            False, 
            "Ollama binary not found in PATH", 
            "curl -fsSL https://ollama.com/install.sh | sh"
        )

    def check_ollama_service(self) -> StatusResult:
        """Checks if the server is responding on localhost:11434."""
        try:
            response = requests.get("http://localhost:11434/api/tags", timeout=2)
            if response.status_code == 200:
                return StatusResult("Ollama Service", True, "Service is running on localhost:11434")
            return StatusResult("Ollama Service", False, f"Service returned status {response.status_code}", "ollama serve")
        except requests.exceptions.ConnectionError:
            return StatusResult("Ollama Service", False, "Could not connect to localhost:11434", "ollama serve")

    def check_model(self, model_name: str) -> StatusResult:
        """Verifies if the specified model is available in the local Ollama library."""
        try:
            response = requests.get("http://localhost:11434/api/tags", timeout=2)
            if response.status_code == 200:
                models = response.json().get("models", [])
                # Check if model_name or model_name:latest is in the list
                available_models = [m["name"] for m in models]
                if model_name in available_models or f"{model_name}:latest" in available_models:
                    return StatusResult(f"Model: {model_name}", True, f"Model '{model_name}' is available")
                return StatusResult(
                    f"Model: {model_name}", 
                    False, 
                    f"Model '{model_name}' not found locally", 
                    f"ollama pull {model_name}"
                )
            return StatusResult(f"Model: {model_name}", False, "Failed to fetch tags from Ollama service")
        except Exception as e:
            return StatusResult(f"Model: {model_name}", False, f"Error checking model: {str(e)}")

health_checker = HealthChecker()

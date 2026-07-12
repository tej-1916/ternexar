import re
from typing import Optional, List, Tuple

from ternexar.config import config_manager
from ternexar.health import health_checker
from ternexar.ollama_client import OllamaError, ollama_client
from ternexar.ui import ui

RISKY_PATTERNS: List[Tuple[str, str]] = [
    ("sudo", r"\bsudo\b"),
    ("rm -rf", r"rm\s+-rf"),
    ("curl pipe shell", r"curl\s+.*\|\s*sh"),
    ("wget pipe shell", r"wget\s+.*\|\s*sh"),
    ("chmod 777", r"chmod\s+777"),
    ("open all ports", r"open\s+all\s+ports"),
    ("delete", r"\bdelete\b"),
    ("wipe", r"\bwipe\b"),
    ("format", r"\bformat\b"),
    ("firewall", r"\bfirewall\b"),
    ("secrets", r"\bsecrets\b"),
    (".env", r"\.env\b")
]

STRENGTHENED_SAFETY_INSTRUCTION = """
CRITICAL: High-risk terms detected. 
When high-risk terms are detected, produce a BLOCKED plan. 
Do not include executable destructive or security-weakening commands. 
Do not include sudo commands. Do not include firewall-changing commands. 
Provide explanation and safe alternatives only.

Use this format for BLOCKED plans:
## Task
Briefly restate the task.
## Risk
BLOCKED
## Commands
No executable commands provided for this task.
## Verify
Explain safe verification or assessment steps only, without commands that change the system.
## Warnings
Explain why the task is unsafe and list safer alternatives.
"""

PLANNING_SYSTEM_PROMPT = """You are TERNEXAR Planner.
Create a short safe terminal plan.
Do not execute commands.
Do not claim anything was done.
Use this format:
## Task
## Risk
## Commands
## Verify
## Warnings
Keep it under 180 words."""

def scan_safety(text: str) -> List[str]:
    """Scans text for deterministic risky patterns and returns readable labels."""
    found = []
    for label, pattern in RISKY_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            found.append(label)
    return found

def handle_plan(
    task: str, 
    model_override: Optional[str] = None, 
    temperature_override: Optional[float] = None
):
    """
    Orchestrates the 'plan' flow: 
    Validation -> Health Check -> Pre-Inference Safety Scan -> Inference -> Post-Inference Safety Scan -> UI Rendering
    """
    # 1. Validation
    if not task or not task.strip():
        ui.error("Empty task. Please describe what you want to plan.")
        ui.hint("Example: [cyan]tx plan \"install nodejs and git\"[/]")
        return

    # 2. Config Loading
    default_model = config_manager.get("model", "default", "qwen2.5-coder:latest")
    default_temp = config_manager.get("model", "temperature", 0.7)
    
    model = model_override or default_model
    temp = temperature_override if temperature_override is not None else default_temp

    # 3. Silent Health Checks
    service_res = health_checker.check_ollama_service()
    if not service_res.success:
        ui.error(service_res.message)
        return

    model_res = health_checker.check_model(model)
    if not model_res.success:
        ui.error(model_res.message)
        return

    # 4. Inference Preparation
    ui.info(f"TERNEXAR PLAN • [dim]model: {model}[/]")
    ui.info(f"Task: [bold white]{task}[/]")
    
    # Pre-Ollama Safety Scan
    risky_task_labels = scan_safety(task)
    combined_prompt = f"{PLANNING_SYSTEM_PROMPT}\n\nUser Task: {task}"
    
    if risky_task_labels:
        ui.warning_panel(
            f"Risky terms detected in the task before planning: {', '.join(risky_task_labels)}.\n"
            "TERNEXAR will not execute anything. The generated plan must be reviewed carefully.",
            title="PRE-PLANNING SAFETY ALERT"
        )
        combined_prompt += f"\n\n{STRENGTHENED_SAFETY_INSTRUCTION}"
    
    try:
        with ui.status(f"Architecting plan with {model}..."):
            plan_text = ollama_client.generate(
                model=model,
                prompt=combined_prompt,
                options={
                    "temperature": temp,
                    "num_predict": 250
                }
            )
        
        # 5. Post-Response Safety Scan
        risky_plan_labels = scan_safety(plan_text)
        if risky_plan_labels:
            ui.warning_panel(
                f"This generated plan contains potentially sensitive commands or keywords: {', '.join(risky_plan_labels)}.\n"
                "Review the proposed commands carefully before execution.",
                title="DETERMINISTIC SAFETY ALERT"
            )
        
        # 6. Render Response
        ui.ai_response(plan_text, model, title="TERMINAL ACTION PLAN")
        
    except OllamaError as e:
        ui.error(e.message)
    except Exception as e:
        ui.error(f"An unexpected error occurred during planning: {str(e)}")

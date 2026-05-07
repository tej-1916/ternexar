# TERNEXAR

**Safe, local-first terminal intelligence.**

TERNEXAR is a command-line interface designed to bridge the gap between local LLMs and terminal automation. It focuses on a high-integrity workflow: understanding a task, planning the steps, and assessing the risk—all before a single character is typed into your shell.

## Safety & Philosophy

TERNEXAR operates on a strict **Ask → Plan → Risk → Execute** pipeline. We believe terminal automation should be transparent and verifiable. 

## Features

*   **v0.9: The Execution Bridge** – Safely execute real-world LOW-risk commands from a strict allowlist. Features include `subprocess` integration (shell=False), timeout protection, and automated pre/post execution audit logging.
*   **v0.8: Audit & Runner Simulation** – Complete observability for safety decisions. Simulate the full execution pipeline with `tx runner-check` and view detailed safety logs with `tx audit`.
*   **v0.7: Confirmation Protocol** – Defined how future execution would request confirmation based on risk and policy.
*   **v0.6: Execution Policy Gate** – Established deterministic PASS/HOLD/BLOCK logic for all staged commands.
*   **v0.5: Preview Mode** – A high-fidelity dry-run environment. Simulate the full execution lifecycle (understanding, planning, and risk assessment) without running any shell commands.
*   **v0.4: Risk Engine** – A deterministic, rule-based system that classifies command risk levels (LOW, MEDIUM, HIGH, BLOCKED) using local safety heuristics.
*   **v0.3: Plan Mode** – Generates structured, multi-step terminal action plans using local Ollama models.
*   **v0.2: Ask Mode** – One-shot technical questions and command lookups via `tx ask`.
*   **v0.1: The Foundation** – Environment diagnostics (`tx doctor`), local configuration management, and a high-fidelity terminal UI.

## Installation

Ensure you have [Ollama](https://ollama.ai/) installed and running locally.

```bash
# Clone the repository and install in editable mode
pip install -e .
```

## Usage

### Ask
Query local models for quick answers or command syntax.
```bash
tx ask "How do I list all files larger than 100MB in the current directory?"
```

### Plan
Transform a natural language goal into a structured sequence of commands.
```bash
tx plan "Set up a local postgres container with a persistent volume"
```

### Preview
Dry-run a task to see exactly which commands would be staged, their risk levels, and which ones would be blocked.
```bash
tx preview "Install docker and run hello-world"
```

### Do
Safely execute a LOW-risk, allowlisted command after safety validation.
```bash
tx do "ls -la"
tx do "git status"
```

### Risk
Analyze the generated plan using the deterministic risk engine. This identifies potentially destructive commands (like `rm -rf` or `mkfs`) before they are staged.
```bash
tx risk "rm -rf /"
```

### Gate
Evaluate a specific command against the execution safety gate to see its policy decision.
```bash
tx gate "sudo apt update"
```

### Confirm
Simulate how future execution would request confirmation based on risk and policy.
```bash
tx confirm "sudo apt update"
```

### Diagnostics
```bash
tx doctor         # Validate local environment and Ollama connectivity
tx config view    # Inspect active configuration
tx config path    # Locate configuration files
```

## Project Status

TERNEXAR is currently in **v0.9 (Beta)**. 
- All LLM interactions are handled locally via Ollama.
- The Risk Engine is entirely local and rule-based; it does not use LLMs to assess safety.
- **Execution is limited to LOW-risk, allowlisted commands.**

## Future Direction
The next phase of development focuses on the **Interactive Execution** module, which will provide secure confirmation prompts for MEDIUM and HIGH risk commands.

---
*Built for the local-first era.*

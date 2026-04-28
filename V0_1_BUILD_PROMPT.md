This is the final build prompt for TERNEXAR v0.1, 
  TERNEXAR v0.1 
  1. Role
  You are a Senior Python Software Architect and CLI Specialist. Your goal is to implement the foundation of
  TERNEXAR, a premium, terminal-native AI command center. You write surgical, modular, and highly polished code.

  2. Project Context
  TERNEXAR is a local-first developer tool powered by Ollama. v0.1 ("The Foundation") focuses on the boot
  sequence, environment validation, and visual identity. It must feel like a high-end binary tool (e.g., Docker,
  Git, or Stripe CLI) from the first command.

  3. Strict Scope
   * Version: v0.1 only.
   * Core Logic: Environment health checks (Ollama, Config, Models) and CLI routing.
   * UI: Rich-based "Live" terminal feedback.
   * Constraints: No AI interaction (no ask/chat), no database, and no project scanning yet.

  4. Required Folder Structure

    1 ternexar/
    2 ├── pyproject.toml
    3 ├── src/
    4 │   └── tx/
    5 │       ├── __init__.py
    6 │       ├── main.py        # Entry point
    7 │       ├── cli.py         # Typer command routing
    8 │       ├── boot.py        # Boot sequence orchestrator
    9 │       ├── ui.py          # Centralized Rich UI engine
   10 │       ├── health.py      # Diagnostic logic & Status objects
   11 │       └── config.py      # TOML management (~/.config/ternexar/)
   12 └── tests/

  5. Required Files
   * pyproject.toml: Python 3.10+ dependencies: typer[all], rich, toml.
   * src/tx/ui.py: The exclusive source of terminal output. Defines theme colors (Deep Purple #8A2BE2 and Cyan
     #00FFFF).
   * src/tx/health.py: Logic for system checks. Returns StatusResult objects.
   * src/tx/cli.py: Typer application and command definitions.
   * src/tx/main.py: Minimal entry point that invokes the CLI.

  6. Module Responsibilities
   * ui.py: Handles all rendering (Gradients, Spinners, Panels, Symbols). Strict rule: No other module may use
     print() or rich.print().
   * cli.py: Maps CLI commands to boot.py or config.py logic.
   * boot.py: Orchestrates the order of operations: Splash → Config Check → Ollama Check → Model Check.
   * health.py: Performs logic-only tests (is binary in PATH? is port 11434 open? is model pulled?).
   * config.py: Manages file I/O for ternexar.toml and ensures the config directory exists.

  7. UI Requirements
   * Gradient Banner: A multi-line ASCII logo with a horizontal Purple-to-Cyan gradient.
   * Motion: Use rich.status.Status for non-blocking spinners during health checks.
   * Status Symbols:
       * [bold green]✔[/] Success
       * [bold red]✘[/] Fail
       * [bold blue]?[/] Skipped
       * [bold yellow]![/] Warning
   * Panels: All terminal states (READY or BLOCKED) must be displayed in a centered, padded rich.panel.Panel.

  8. Health Check Requirements
   1. Ollama Binary: Check if ollama is in the system $PATH.
   2. Ollama Service: Check if the server is responding on localhost:11434.
   3. Required Model: Verify the model specified in ternexar.toml (default llama3) is available in the local
      Ollama library.

  9. Config Requirements
   * Path: ~/.config/ternexar/ternexar.toml.
   * Default Schema:

   1     [model]
   2     default = "llama3"
   3     temperature = 0.7
   4
   5     [ui]
   6     show_splash = true

  10. Commands
   * tx: Runs the standard boot sequence and health check.
   * tx doctor: Explicit deep-dive diagnostic with live-updating progress.
   * tx config: Manage config (subcommands: init, view, reset).
   * tx --help: Rich-formatted help system with categorized commands.

  11. Error States & F

  TERNEXAR v0.1 Build Prompt: "The Foundation"

  1. Role
  You are a Senior Python Software Architect and CLI Specialist. Your goal is to implement the foundation of
  TERNEXAR, a premium, terminal-native AI command center. You write surgical, modular, and highly polished code.

  2. Project Context
  TERNEXAR is a local-first developer tool powered by Ollama. v0.1 ("The Foundation") focuses on the boot
  sequence, environment validation, and visual identity. It must feel like a high-end binary tool (e.g., Docker,
  Git, or Stripe CLI) from the first command.

  3. Strict Scope
   * Version: v0.1 only.
   * Core Logic: Environment health checks (Ollama, Config, Models) and CLI routing.
   * UI: Rich-based "Live" terminal feedback.
   * Constraints: No AI interaction (no ask/chat), no database, and no project scanning yet.

  4. Required Folder Structure

    1 ternexar/
    2 ├── pyproject.toml
    3 ├── src/
    4 │   └── tx/
    5 │       ├── __init__.py
    6 │       ├── main.py        # Entry point
    7 │       ├── cli.py         # Typer command routing
    8 │       ├── boot.py        # Boot sequence orchestrator
    9 │       ├── ui.py          # Centralized Rich UI engine
   10 │       ├── health.py      # Diagnostic logic & Status objects
   11 │       └── config.py      # TOML management (~/.config/ternexar/)
   12 └── tests/

  5. Required Files
   * pyproject.toml: Python 3.10+ dependencies: typer[all], rich, toml.
   * src/tx/ui.py: The exclusive source of terminal output. Defines theme colors (Deep Purple #8A2BE2 and Cyan
     #00FFFF).
   * src/tx/health.py: Logic for system checks. Returns StatusResult objects.
   * src/tx/cli.py: Typer application and command definitions.
   * src/tx/main.py: Minimal entry point that invokes the CLI.

  6. Module Responsibilities
   * ui.py: Handles all rendering (Gradients, Spinners, Panels, Symbols). Strict rule: No other module may use
     print() or rich.print().
   * cli.py: Maps CLI commands to boot.py or config.py logic.
   * boot.py: Orchestrates the order of operations: Splash → Config Check → Ollama Check → Model Check.
   * health.py: Performs logic-only tests (is binary in PATH? is port 11434 open? is model pulled?).
   * config.py: Manages file I/O for ternexar.toml and ensures the config directory exists.

  7. UI Requirements
   * Gradient Banner: A multi-line ASCII logo with a horizontal Purple-to-Cyan gradient.
   * Motion: Use rich.status.Status for non-blocking spinners during health checks.
   * Status Symbols:
       * [bold green]✔[/] Success
       * [bold red]✘[/] Fail
       * [bold blue]?[/] Skipped
       * [bold yellow]![/] Warning
   * Panels: All terminal states (READY or BLOCKED) must be displayed in a centered, padded rich.panel.Panel.

  8. Health Check Requirements
   1. Ollama Binary: Check if ollama is in the system $PATH.
   2. Ollama Service: Check if the server is responding on localhost:11434.
   3. Required Model: Verify the model specified in ternexar.toml (default llama3) is available in the local
      Ollama library.

  9. Config Requirements
   * Path: ~/.config/ternexar/ternexar.toml.
   * Default Schema:

   1     [model]
   2     default = "llama3"
   3     temperature = 0.7
   4
   5     [ui]
   6     show_splash = true

  10. Commands
   * tx: Runs the standard boot sequence and health check.
   * tx doctor: Explicit deep-dive diagnostic with live-updating progress.
   * tx config: Manage config (subcommands: init, view, reset).
   * tx --help: Rich-formatted help system with categorized commands.

  11. Error States & Fixes
  If a check fails, the UI must show a BLOCKED panel with an Exact Fix Command:
   * Ollama Missing: curl -fsSL https://ollama.com/install.sh | sh
   * Service Down: ollama serve
   * Model Missing: ollama pull [model_name]
   * Config Error: tx config --reset

  12. Acceptance Checklist
   * [ ] tx command renders the gradient banner correctly.
   * [ ] ui.py handles 100% of terminal output.
   * [ ] Spinners appear during checks and are replaced by status symbols.
   * [ ] tx doctor provides a clear "Fix Command" on failure.
   * [ ] The system terminates with a clear READY or BLOCKED panel.
   * [ ] "Hint: type tx --help to explore" is present at the bottom.

  13. What NOT to build
   * No AI chat logic (tx ask/tx chat).
   * No Project Scanning (tx scan).
   * No Agent/Persona system.
   * No SQLite or vector database.
   * No TUI components (Textual) or curses.

  14. Expected Final Response Format
   1. Full code for pyproject.toml.
   2. Full source code for all files in src/tx/.
   3. Installation command (pip install -e .).
   4. Verification of how the "Zero raw print" requirement was met.


                                                                                         

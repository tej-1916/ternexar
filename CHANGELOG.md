# Changelog

All notable changes to this project will be documented in this file.

## [1.0.0] - 2026-05-08
### Added
- **Stable Safe Operator Release**
- Comprehensive test suite for risk, gate, and execution safety.
- Formal project documentation (LICENSE, SECURITY, CONTRIBUTING, CHANGELOG, ROADMAP).
- Safety examples and walkthroughs.
- GitHub-ready repository structure.

### Changed
- Refined `tx do` allowlist for v1.0 stability.
- Improved audit logging integrity.
- Updated README to reflect stable status.

---

## [0.9.0] - 2026-04-30
### Added
- **v0.9: The Execution Bridge**
- Strict allowlist-based execution for LOW-risk commands.
- `shlex` and `subprocess` integration (shell=False).
- Timeout protection for executed commands.
- Pre and post-execution audit logging.

## [0.8.0] - 2026-04-15
### Added
- **v0.8: Audit & Runner Simulation**
- `tx audit` command for viewing safety logs.
- `tx runner-check` for simulating the full safety pipeline.

## [0.7.0] - 2026-04-01
### Added
- **v0.7: Confirmation Protocol**
- Defined confirmation requirements based on risk levels.

## [0.6.0] - 2025-03-20
### Added
- **v0.6: Execution Policy Gate**
- Deterministic PASS/HOLD/BLOCK logic.

## [0.5.0] - 2025-03-05
### Added
- **v0.5: Preview Mode**
- High-fidelity dry-run environment.

## [0.4.0] - 2025-02-15
### Added
- **v0.4: Risk Engine**
- Rule-based risk classification.

## [0.3.0] - 2025-02-01
### Added
- **v0.3: Plan Mode**
- Structured task planning.

## [0.2.0] - 2025-01-15
### Added
- **v0.2: Ask Mode**
- One-shot technical Q&A.

## [0.1.0] - 2025-01-01
### Added
- **v0.1: The Foundation**
- `tx doctor`, config management, and base UI.

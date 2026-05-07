# Contributing to TERNEXAR

Welcome! We are excited that you want to contribute to the safe terminal AI revolution.

## Code of Conduct
Please be respectful and professional in all interactions.

## How to Contribute
1.  **Fork the Repository:** Create your own branch for changes.
2.  **Strict Safety:** Any changes to `risk.py`, `gate.py`, or `do.py` must include comprehensive tests demonstrating that safety is maintained or improved.
3.  **Local Development:**
    ```bash
    pip install -e ".[all]"
    pytest
    ```
4.  **Submit a PR:** Provide a clear description of the change and the rationale behind it.

## Safety Guidelines
*   **NEVER** change `shell=False` to `shell=True` in execution logic.
*   **NEVER** add remote API calls to the core safety pipeline.
*   **ALWAYS** add a test case for new risk rules.

## Issues
Use GitHub Issues to report bugs or suggest features. For bug reports, include the output of `tx doctor`.

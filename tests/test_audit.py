import json
import pytest
from pathlib import Path
from ternexar.audit import AuditManager

def test_audit_logging(tmp_path):
    # Setup AuditManager with a temp path
    manager = AuditManager()
    manager.base_dir = tmp_path
    manager.log_file = tmp_path / "audit.jsonl"
    manager._ensure_dir()

    # Log an event
    manager.log_event(
        command="ls",
        risk_level="LOW",
        gate_decision="PASS",
        policy="ALLOW_PREVIEW",
        confirmation_mode="MINIMAL",
        action_type="EXECUTION_START",
        result="STARTED",
        notes="Test note"
    )

    # Verify record
    records = manager.get_records()
    assert len(records) == 1
    assert records[0]["command"] == "ls"
    assert records[0]["notes"] == "Test note"

def test_audit_clear(tmp_path):
    manager = AuditManager()
    manager.base_dir = tmp_path
    manager.log_file = tmp_path / "audit.jsonl"
    manager._ensure_dir()

    manager.log_event("ls", "LOW", "PASS", "ALLOW", "MIN", "START", "OK")
    assert len(manager.get_records()) == 1

    manager.clear_logs()
    assert len(manager.get_records()) == 0

import pytest
import json
from pathlib import Path
from unittest.mock import patch, mock_open
from ternexar.memory import ErrorMemory, DEFAULT_MEMORY

def test_memory_load_default(tmp_path):
    mem_file = tmp_path / "test-memory.json"
    mem = ErrorMemory(memory_file=mem_file)
    assert mem.data == DEFAULT_MEMORY
    assert mem_file.exists()

def test_memory_load_existing(tmp_path):
    mem_file = tmp_path / "test-memory.json"
    existing_data = {
        "project": "TERNEXAR",
        "engine": "AutoFix Engine v1",
        "errors": [{"type": "test_err", "command": "echo", "error": "fail"}]
    }
    mem_file.write_text(json.dumps(existing_data))
    
    mem = ErrorMemory(memory_file=mem_file)
    assert mem.data == existing_data
    assert len(mem.data["errors"]) == 1

def test_memory_load_broken(tmp_path):
    mem_file = tmp_path / "broken.json"
    mem_file.write_text("{ broken json")
    
    mem = ErrorMemory(memory_file=mem_file)
    # Should fall back to default if broken
    assert mem.data == DEFAULT_MEMORY

def test_memory_search(tmp_path):
    mem_file = tmp_path / "test-memory.json"
    mem = ErrorMemory(memory_file=mem_file)
    mem.append_error("git_fail", "git push", "remote rejected")
    mem.append_error("npm_fail", "npm install", "enoent")
    
    results = mem.search_errors("git")
    assert len(results) == 1
    assert results[0]["type"] == "git_fail"
    
    results = mem.search_errors("rejected")
    assert len(results) == 1
    assert results[0]["type"] == "git_fail"

def test_memory_append(tmp_path):
    mem_file = tmp_path / "test-memory.json"
    mem = ErrorMemory(memory_file=mem_file)
    mem.append_error(
        "custom", "do something", "it broke",
        safe_checks=["check1"], avoid=["action1"]
    )
    
    # Reload to verify persistence
    mem2 = ErrorMemory(memory_file=mem_file)
    assert len(mem2.data["errors"]) == 1
    assert mem2.data["errors"][0]["safe_checks"] == ["check1"]
    assert mem2.data["errors"][0]["avoid"] == ["action1"]

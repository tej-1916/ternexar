import os
import pytest
from pathlib import Path
from ternexar.router import router, Intent

def test_intent_classification_do():
    assert router.classify_intent("ls") == Intent.DO
    assert router.classify_intent("git status") == Intent.DO
    # python --version is now VERSION_CHECK
    assert router.classify_intent("python --version") == Intent.VERSION_CHECK
def test_intent_classification_ask():
    assert router.classify_intent("What is Python?") == Intent.ASK
    assert router.classify_intent("How do I use git?") == Intent.ASK
    assert router.classify_intent("Explain recursion") == Intent.ASK
    assert router.classify_intent("Tell me a joke?") == Intent.ASK

def test_intent_classification_setup():
    assert router.classify_intent("setup this project") == Intent.SETUP
    assert router.classify_intent("prepare this project") == Intent.SETUP
    assert router.classify_intent("install dependencies for this project") == Intent.SETUP

def test_intent_classification_install_request():
    assert router.classify_intent("install python 3") == Intent.INSTALL_REQUEST
    assert router.classify_intent("install nodejs") == Intent.INSTALL_REQUEST
    assert router.classify_intent("install claude code") == Intent.INSTALL_REQUEST

def test_intent_classification_refuse():
    assert router.classify_intent("rm -rf /") == Intent.REFUSE
    assert router.classify_intent("cat .env") == Intent.REFUSE
    assert router.classify_intent("wipe disk") == Intent.REFUSE

def test_intent_classification_plan():
    assert router.classify_intent("Create a backup script") == Intent.PLAN
    assert router.classify_intent("Configure nginx") == Intent.PLAN

def test_resolve_context_valid(tmp_path):
    # Create a dummy file
    test_file = tmp_path / "test.txt"
    test_file.write_text("Hello World")
    
    # Change CWD to tmp_path for the test
    old_cwd = os.getcwd()
    os.chdir(tmp_path)
    
    try:
        text = "explain @test.txt"
        clean_text, context = router.resolve_context(text)
        
        assert clean_text == "explain"
        assert len(context) == 1
        assert "[CONTEXT: @test.txt]" in context[0]
        assert "Hello World" in context[0]
    finally:
        os.chdir(old_cwd)

def test_resolve_context_blocked_sensitive(tmp_path):
    # Create a sensitive file
    secret_file = tmp_path / "secrets.txt"
    secret_file.write_text("mysecret")
    
    old_cwd = os.getcwd()
    os.chdir(tmp_path)
    
    try:
        text = "show @secrets.txt"
        clean_text, context = router.resolve_context(text)
        
        assert len(context) == 0
    finally:
        os.chdir(old_cwd)

def test_resolve_context_blocked_hidden(tmp_path):
    # Create a hidden file
    hidden_file = tmp_path / ".env"
    hidden_file.write_text("KEY=VALUE")
    
    old_cwd = os.getcwd()
    os.chdir(tmp_path)
    
    try:
        text = "show @.env"
        clean_text, context = router.resolve_context(text)
        
        assert len(context) == 0
    finally:
        os.chdir(old_cwd)

def test_resolve_context_blocked_large(tmp_path):
    # Create a large file
    large_file = tmp_path / "large.txt"
    large_file.write_text("A" * (101 * 1024))
    
    old_cwd = os.getcwd()
    os.chdir(tmp_path)
    
    try:
        text = "show @large.txt"
        clean_text, context = router.resolve_context(text)
        
        assert len(context) == 0
    finally:
        os.chdir(old_cwd)

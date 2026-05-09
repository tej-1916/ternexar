import pytest
from ternexar.router import Router, Intent

@pytest.fixture
def router():
    return Router()

def test_classify_intent_refuse(router):
    assert router.classify_intent("rm -rf /") == Intent.REFUSE
    assert router.classify_intent("cat .env") == Intent.REFUSE

def test_classify_intent_install_request(router):
    assert router.classify_intent("install python 3") == Intent.INSTALL_REQUEST
    assert router.classify_intent("install claude code") == Intent.INSTALL_REQUEST
    assert router.classify_intent("install nodejs") == Intent.INSTALL_REQUEST

def test_classify_intent_setup(router):
    assert router.classify_intent("setup this project") == Intent.SETUP
    assert router.classify_intent("install dependencies for this project") == Intent.SETUP
    assert router.classify_intent("prepare this project") == Intent.SETUP

def test_classify_intent_locate(router):
    assert router.classify_intent("find my ternexar project") == Intent.LOCATE
    assert router.classify_intent("where is my website project") == Intent.LOCATE
    assert router.classify_intent("locate indexproject") == Intent.LOCATE

def test_classify_intent_scan(router):
    assert router.classify_intent("scan this project") == Intent.SCAN
    assert router.classify_intent("inspect this project") == Intent.SCAN
    assert router.classify_intent("analyze project structure") == Intent.SCAN

def test_classify_intent_view(router):
    assert router.classify_intent("show files in this project") == Intent.VIEW
    assert router.classify_intent("view this project") == Intent.VIEW
    assert router.classify_intent("list files in my project") == Intent.VIEW

def test_classify_intent_analyze(router):
    assert router.classify_intent("analyze broken python app") == Intent.ANALYZE
    assert router.classify_intent("fix ModuleNotFoundError: No module named requests") == Intent.ANALYZE
    assert router.classify_intent("debug import error") == Intent.ANALYZE

def test_classify_intent_do(router):
    assert router.classify_intent("ls -la") == Intent.DO
    assert router.classify_intent("pwd") == Intent.DO
    assert router.classify_intent("git status") == Intent.DO

def test_classify_intent_ask(router):
    assert router.classify_intent("what is recursion?") == Intent.ASK
    assert router.classify_intent("how do I use git?") == Intent.ASK

def test_extract_target(router):
    assert router.extract_target("setup this project") == "."
    assert router.extract_target("scan my ternexar project") == "ternexar"
    assert router.extract_target("show files in my website project") == "website"
    assert router.extract_target("locate indexproject") == "indexproject"
    assert router.extract_target("find my awesome-app") == "awesome-app"

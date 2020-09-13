import pytest

from prunner.main import Executor

CONFIG_DIR = "example"


@pytest.fixture
def executor():
    return Executor(CONFIG_DIR, {})


def test_execute_pipeline(executor):
    executor.execute_pipeline("structural")

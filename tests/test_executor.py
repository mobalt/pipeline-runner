import pytest

from prunner.main import Executioner

CONFIG_DIR = "example"


@pytest.fixture
def executor():
    return Executioner(CONFIG_DIR, {})


def test_execute_pipeline(executor):
    executor.execute_pipeline("structural")

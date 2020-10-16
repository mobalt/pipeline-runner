import os

import pytest
from prunner.tasks.set_from_env import SetFromEnvTask

@pytest.fixture
def task():
    return SetFromEnvTask()

def test_nothing(task):
    expected_result = os.environ['USER']
    output = task.execute({"USER": "$USER"}, {"USER": "previous"})
    # shellexpand should occur
    assert output['USER'] != "$USER", "shellexpand is not occurring"
    assert output['USER'] != "previous", "os.environ should take higher precedence than variables dict"
    assert output['USER'] == expected_result


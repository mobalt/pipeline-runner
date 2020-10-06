import os

import pytest

from prunner.tasks.dump_variables import standardize_param, generate_sh, DumpVarsTask


@pytest.fixture
def test_str():
    return "test.sh"


def test_standardize_param_str(test_str):
    filename, var = standardize_param(test_str)
    assert filename.endswith(test_str)


def test_standardize_param_abspath_used(test_str):
    filename, var = standardize_param(test_str)
    assert len(filename) > len(test_str)
    assert filename.startswith("/")


def test_standardize_param_dryrun(test_str):
    filename, var = standardize_param(test_str, dryrun=False)
    assert "\\" not in filename

    filename2, var2 = standardize_param(test_str, dryrun=True)
    assert "\\" in filename2


def test_standardize_param_empty_dict():
    with pytest.raises(ValueError):
        standardize_param({})


def test_standardize_param_dict(test_str):
    test_dict = {"filename": test_str, "variable": "OUTPUT_FILE"}
    filename, var = standardize_param(test_dict)
    assert filename.endswith(test_str)
    assert var == "OUTPUT_FILE"


def test_standardize_param_non_str_or_dict():
    with pytest.raises(TypeError):
        standardize_param(None)
    with pytest.raises(TypeError):
        standardize_param(True)
    with pytest.raises(TypeError):
        standardize_param(False)
    with pytest.raises(TypeError):
        standardize_param([])
    with pytest.raises(TypeError):
        standardize_param(9)

def test_generate_sh():
    actual = generate_sh({"V1": "TEST"})
    assert "export " in actual

def test_dump_vars_task():
    task = DumpVarsTask()
    output = task.execute({"filename":"test.sh", "variable": "DUMP_FILE"}, {"V1": "yes", "V2": False, "DRYRUN": True})
    filename = output.get("DUMP_FILE")
    print("FILE", filename)
    assert os.path.exists(filename)
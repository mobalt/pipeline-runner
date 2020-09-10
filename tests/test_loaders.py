import importlib.util
import pytest

import main

CONFIG_DIR = "example"


def test_load_existing_yaml():
    pipelines = main.load_yaml(f"{CONFIG_DIR}/pipelines.yaml")
    assert type(pipelines) == dict
    assert len(pipelines) == 5


def test_load_nonexisting_yaml():
    nonexistant = main.load_yaml(f"{CONFIG_DIR}/nonexistent.yaml")
    assert type(nonexistant) == dict
    assert len(nonexistant) == 0


def test_with_default_value_not_added_to_result():
    function_name = 'example_function'
    variables = {"REQUIRED": True}
    f = main.Functions(f"{CONFIG_DIR}/functions.py")
    actual = f.execute(function_name, variables)
    expected = {
        "REQUIRED": True,
        "SET_THIS_VARIABLE": "1",
        "DEFAULTED": "default"
    }
    assert actual == expected

def test_function_with_required_and_defaulted_value():
    function_name = 'example_function'
    variables = {"REQUIRED": True,
                 "WITH_DEFAULT_VALUE": "new value"}
    f = main.Functions(f"{CONFIG_DIR}/functions.py")
    actual = f.execute(function_name, variables)
    expected = {
        "REQUIRED": True,
        "SET_THIS_VARIABLE": "1",
        "WITH_DEFAULT_VALUE": "new value",
        "DEFAULTED": "new value",
    }
    assert actual == expected

def test_missing_function():
    function_name = 'nonexistent_function'
    variables = {"REQUIRED": True}
    f = main.Functions(f"{CONFIG_DIR}/functions.py")
    with pytest.raises(main.FunctionNotDefined):
        f.execute(function_name, variables)

def test_missing_variables():
    function_name = 'example_function'
    variables = {}
    f = main.Functions(f"{CONFIG_DIR}/functions.py")
    with pytest.raises(main.VariableNotSet):
        f.execute(function_name, variables)

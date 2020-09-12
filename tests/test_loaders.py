import importlib.util
import pytest
from jinja2 import TemplateNotFound, Environment, FileSystemLoader

from prunner import main

CONFIG_DIR = "example"


def test_with_default_value_not_added_to_result():
    function_name = "example_function"
    variables = {"REQUIRED": True}
    f = main.FunctionLoader(f"{CONFIG_DIR}/functions.py")
    actual = f.execute(function_name, variables)
    expected = {"SET_THIS_VARIABLE": "1", "DEFAULTED": "default"}
    assert actual == expected


def test_function_with_required_and_defaulted_value():
    function_name = "example_function"
    variables = {"REQUIRED": True, "WITH_DEFAULT_VALUE": "new value"}
    f = main.FunctionLoader(f"{CONFIG_DIR}/functions.py")
    actual = f.execute(function_name, variables)
    expected = {
        "SET_THIS_VARIABLE": "1",
        "DEFAULTED": "new value",
    }
    assert actual == expected


def test_missing_function():
    function_name = "nonexistent_function"
    variables = {"REQUIRED": True}
    f = main.FunctionLoader(f"{CONFIG_DIR}/functions.py")
    with pytest.raises(main.FunctionNotDefined):
        f.execute(function_name, variables)


def test_missing_variables():
    function_name = "example_function"
    variables = {}
    f = main.FunctionLoader(f"{CONFIG_DIR}/functions.py")
    with pytest.raises(main.VariableNotSet):
        f.execute(function_name, variables)


def test_load_template():
    template_name = "pbs_head.jinja2"
    template_env = main.TemplateLoader(f"{CONFIG_DIR}/templates")
    variables = {"PBS_NODES": "99"}
    results = template_env.render(template_name, variables)
    expected = "#PBS -S /bin/bash\n#PBS -l nodes=99:ppn=1,walltime=4:00:00,mem=4gb\n"
    assert results == expected


def test_load_template_doesnt_exist():
    template_name = "nonexistent.jinja2"
    template_env = main.TemplateLoader(f"{CONFIG_DIR}/templates")
    with pytest.raises(TemplateNotFound):
        template_env.render(template_name, {})


def test_load_template_config_doesnt_exist():
    template_env = main.TemplateLoader(f"{CONFIG_DIR}/nonexistent")
    with pytest.raises(TemplateNotFound):
        template_env.render("_unimportant_.j2", {})

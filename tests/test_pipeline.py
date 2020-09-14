import os

import prunner.loader.variable_loader
from prunner.exec import ExecutionEnvironment
import pytest

CONFIG_DIR = "example"


@pytest.fixture
def env():
    execution_env = ExecutionEnvironment.from_config_dir(CONFIG_DIR)
    execution_env.variables["FOO"] = "bar"
    return execution_env


def test_executor_load_variables(env):
    results = env.load_variables("functional")
    assert 0 < len(results)


def test_executor_load_variables_has_expansion(env):
    raw_input = "$HOME/XNAT_BUILD_DIR/$USER"
    loaded_variables = env.load_variables("functional")
    actual = loaded_variables["XNAT_PBS_JOBS_BUILD_DIR"]
    assert raw_input != actual


def test_executor_load_variables_bad_argument(env):
    with pytest.raises(TypeError):
        env.load_variables(None)


def test_executor_load_variables_nonexistent_set_throws_error(env):
    with pytest.raises(prunner.loader.variable_loader.VariableSetNotDefined):
        env.load_variables("not exist")


def test_generate_file_receives_str_param(env):
    with pytest.raises(TypeError):
        env.generate_file(
            "template = nope.jinja",
            dryrun=True,
        )


def test_shellexpanded_generated_filepath(env):
    updates = env.generate_file(
        {
            "template": "pbs_head.jinja2",
            "filepath": "~/delete_me.$FOO.sh",
        },
        dryrun=True,
    )
    filepath = updates["OUTPUT_FILE"]
    assert filepath.endswith("delete_me.bar.sh")
    assert filepath.startswith("/home/")


def test_saving_generated_file(env):
    result = env.generate_file(
        {
            "template": "pbs_head.jinja2",
            "filepath": "delete_me.sh",
            "variable": "script_path",
        }
    )
    expected_excerpt = (
        "#PBS -S /bin/bash\n#PBS -l nodes=1:ppn=1,walltime=4:00:00,mem=4gb\n"
    )

    filepath = result["script_path"]
    assert os.path.exists(filepath)

    with open(filepath, "r") as fd:
        actual_content = fd.read()

    assert expected_excerpt in actual_content

    # clean up generated file
    os.remove(filepath)
    assert not os.path.exists(filepath)


def test_call_function(env):
    env.variables["SUBJECT"] = "proj:x:y:z"
    expected = {
        "PROJECT": "proj",
        "SUBJECT_ID": "x",
        "SUBJECT_CLASSIFIER": "y",
        "SUBJECT_EXTRA": "z",
        "SESSION": "x_y",
    }
    actual = env.function("split_subject")
    assert expected == actual


def test_function_receives_non_str_param(env):
    with pytest.raises(TypeError):
        env.function({})


def test_calling_function_throws_error(env):
    env.variables["SUBJECT"] = "missing_stuff:x"
    with pytest.raises(ValueError):
        actual = env.function("split_subject")


def test_set_variables(env):
    value = "New User Account"
    result = env.set_variables({"USER": value})
    assert result["USER"] == value


def test_set_variables_receives_param_of_wrong_type(env):
    with pytest.raises(TypeError):
        env.set_variables([])

    with pytest.raises(TypeError):
        env.set_variables(" Noop ")

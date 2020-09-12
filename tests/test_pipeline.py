import os

from pipeline import main
import pytest

CONFIG_DIR = "example"


def test_load_pipeline():
    pipelines = main.Pipelines(f"{CONFIG_DIR}/pipelines.yaml")
    assert pipelines.tasks("structural") != []


@pytest.fixture
def exec():
    executor = main.Executor.from_config_dir(CONFIG_DIR)
    executor.variables["FOO"] = "bar"
    return executor


def test_executor_load_variables(exec):
    before = dict(exec.variables)
    exec.load_variables("functional")
    after = dict(exec.variables)
    assert len(before) < len(after)


def test_executor_load_variables_has_expansion(exec):
    exec.load_variables("functional")
    raw = "$HOME/XNAT_BUILD_DIR/$USER"
    actual = exec.variables["XNAT_PBS_JOBS_BUILD_DIR"]
    assert raw != actual


def test_executor_load_variables_bad_argument(exec):
    with pytest.raises(TypeError):
        exec.load_variables(None)


def test_executor_load_variables_nonexistent_set_throws_error(exec):
    with pytest.raises(main.VariableSetNotDefined):
        exec.load_variables("not exist")


def test_generate_file_filepath_default_variable_set(exec):
    before = dict(exec.variables)
    exec.generate_file(
        {
            "template": "pbs_head.jinja2",
            "filepath": "~/delete_me.sh",
            "variable": "OUT",
        },
        dryrun=True,
    )
    after = dict(exec.variables)

    assert "OUT" not in before
    assert "OUT" in after


def test_shellexpanded_generated_filepath(exec):
    exec.generate_file(
        {
            "template": "pbs_head.jinja2",
            "filepath": "~/delete_me.$FOO.sh",
        },
        dryrun=True,
    )
    filepath = exec.variables["OUTPUT_FILE"]
    assert filepath.endswith("delete_me.bar.sh")
    assert filepath.startswith("/home/")


def test_generated_output_content(exec):
    result = exec.generate_file(
        {
            "template": "pbs_head.jinja2",
            "filepath": "~/delete_me.$USER.sh",
        },
        dryrun=True,
    )
    expected = "#PBS -S /bin/bash\n#PBS -l nodes=1:ppn=1,walltime=4:00:00,mem=4gb\n"
    assert expected in result


def test_saving_generated_file(exec):
    expected_content = exec.generate_file(
        {
            "template": "pbs_head.jinja2",
            "filepath": "delete_me.sh",
            "variable": "script_path",
        }
    )
    expected_excerpt = (
        "#PBS -S /bin/bash\n#PBS -l nodes=1:ppn=1,walltime=4:00:00,mem=4gb\n"
    )

    filepath = exec.variables["script_path"]
    assert os.path.exists(filepath)

    with open(filepath, "r") as fd:
        actual_content = fd.read()

    assert expected_excerpt in actual_content
    assert expected_content == actual_content

    # clean up generated file
    os.remove(filepath)
    assert not os.path.exists(filepath)


def test_call_function(exec):
    exec.variables["SUBJECT"] = "proj:x:y:z"
    expected = {
        "PROJECT": "proj",
        "SUBJECT_ID": "x",
        "SUBJECT_CLASSIFIER": "y",
        "SUBJECT_EXTRA": "z",
        "SESSION": "x_y",
    }
    actual = exec.function("split_subject")
    all_vars = exec.variables
    assert expected == actual
    # check that expected items are a subset of all_vars
    assert expected.items() <= all_vars.items()


def test_calling_function_throws_error(exec):
    exec.variables["SUBJECT"] = "missing_stuff:x"
    with pytest.raises(ValueError):
        actual = exec.function("split_subject")


def test_set_variables(exec):
    before = dict(exec.variables)
    exec.set_variables({"USER": "New User Account"})
    after = dict(exec.variables)
    assert before["USER"] != after["USER"]


@pytest.fixture
def exec_with_pipeline(exec):
    exec.variables["PIPELINE_NAME"] = "structural"
    return exec


def test_execute_pipeline(exec_with_pipeline):
    exec = exec_with_pipeline
    main.execute_pipeline(exec)

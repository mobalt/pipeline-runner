import os

import main
import pytest

CONFIG_DIR = "example"


def test_load_pipeline():
    pipelines = main.Pipelines(f"{CONFIG_DIR}/pipelines.yaml")
    assert pipelines.tasks("structural") != []


@pytest.fixture
def exec():
    return main.Executor.from_config_dir(CONFIG_DIR)


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
    exec.variables["FOO"] = "bar"
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

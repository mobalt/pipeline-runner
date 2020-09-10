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

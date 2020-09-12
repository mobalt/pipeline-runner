from pipeline import main
import pytest


@pytest.fixture
def exec():
    input = [
        "-c",
        "example",
        "-v",
        "pipeline",
        "--dryrun",
        "rest",
        "of",
        "args",
        "--FOO=bar",
        "more",
    ]
    exec = main.parse_arguments(input)
    return exec


def test_set_config_directory(exec):
    assert exec.config_dir.endswith("example")
    assert exec.config_dir.startswith("/home")


def test_detects_flags_before_pipeline(exec):
    assert exec.verbose


def test_ignores_flags_after_pipeline(exec):
    assert exec.dry_run == False


def test_detects_pipeline(exec):
    assert exec.variables["PIPELINE_NAME"] == "pipeline"


def test_detect_rest_of_positionals(exec):
    rest_of_args = ["--dryrun", "rest", "of", "args", "--FOO=bar", "more"]
    expected = {
        "_0": "rest of args more",
        "_1": "rest",
        "_2": "of",
        "_3": "args",
        "_4": "more",
    }
    actual = main.parse_rest_of_args(rest_of_args)
    assert expected.items() < actual.items()


def test_detect_rest_of_name_args(exec):
    rest_of_args = ["--dryrun", "rest", "of", "args", "--FOO=bar", "more"]
    expected = {
        "dryrun": "",
        "FOO": "bar",
    }
    actual = main.parse_rest_of_args(rest_of_args)
    assert expected.items() < actual.items()
